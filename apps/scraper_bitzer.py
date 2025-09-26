from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
import pandas as pd
import time

class BitzerNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
    
    def get_soup(self):
        print(f'📰Opening: Bitzer')
        self.driver.get(self.url)
        try:
            accept_cookie = WebDriverWait(self.driver,5).until(EC.element_to_be_clickable((By.ID,'uc-btn-accept-banner')))
            self.driver.execute_script("arguments[0].scrollIntoView();",accept_cookie)
            accept_cookie.click()
        except Exception as e:
            print(f'An error has occured: {e}')
            pass
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_section = soup.find('div', id='paging-content')
        self.news_blocks = news_section.find_all('section',class_='news')
        self.news_blocks_sel = self.driver.find_elements(By.CLASS_NAME, 'news')
    
    def open_to_new_tab(self,link):
        ActionChains(self.driver)\
        .key_down(Keys.CONTROL)\
        .click(link)\
        .key_up(Keys.CONTROL)\
        .perform()
    
    def get_summary(self):
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        title = soup.find('h1',class_='overview-headline').text.strip()
        summary_block = soup.find('div',class_='press-information-content')
        paragraphs = summary_block.find_all('p')
        print(f'Fetching News: {title}')
        for sum in paragraphs:
            if len(sum.text.strip()) < 150:
                pass
            else:
                summary = sum.text.strip()
                
        return ({'title':title,'summary':summary})
    
    def get_news(self):
        for news, section in zip(self.news_blocks,self.news_blocks_sel):
            parsed_date = news.find('span',class_='press-news-span').text.strip()
            parsed_date_obj = datetime.strptime(parsed_date,'%d.%m.%Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj >= self.date_limit:
                self.driver.execute_script("arguments[0].scrollIntoView();",section)
                link_sel = section.find_element(By.LINK_TEXT,'Read more')
                link = news.find('a',class_='primary-color').get('href')
                self.open_to_new_tab(link_sel)
                self.driver.switch_to.window(self.driver.window_handles[1])
                current_tabs = self.driver.window_handles
                try:
                    WebDriverWait(self.driver,3).until(lambda e: len(e.window_handles) > len(current_tabs))
                except:
                    pass
                page = self.get_summary()
                title = page.get('title')
                summary = page.get('summary')
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                root_url='https://www.bitzer.de'
                self.latest_news.append(
                    {
                    'PublishDate':publish_date,
                    'Source': 'Bitzer',
                    'Type': 'Company News',
                    'Title': title,
                    'Summary': summary,
                    'Link': f'{root_url}{link}'
                    }
                )
    
    def scrape(self):
        self.get_soup()
        self.get_news()

all_news = []
def get_bitzer_news(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url='https://www.bitzer.de/gb/en/press/'
    news = BitzerNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/bitzer_news.csv',index=False)

