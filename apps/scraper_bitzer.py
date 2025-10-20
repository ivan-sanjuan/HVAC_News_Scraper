from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from urllib.parse import urljoin
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
        self.root = 'https://www.bitzer.de/'
    
    def get_soup(self):
        print(f'📰Opening: Bitzer')
        self.driver.get(self.url)
        try:
            accept_cookie = self.driver_wait(EC.element_to_be_clickable((By.ID,'uc-btn-accept-banner')))
            self.driver.execute_script("arguments[0].scrollIntoView();",accept_cookie)
            accept_cookie.click()
        except Exception as e:
            print(f'An error has occured: {e}')
            pass
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_section = soup.find('div', id='paging-content')
        news_blocks = news_section.find_all('section',class_='news')
        news_blocks_sel = self.driver.find_elements(By.CLASS_NAME, 'news')
        self.get_news(news_blocks,news_blocks_sel)
    
    def get_news(self,bs4_block,sel_block):
        for news, section in zip(bs4_block,sel_block):
            parsed_date = news.find('span',class_='press-news-span').text.strip()
            parsed_date_obj = datetime.strptime(parsed_date,'%d.%m.%Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj >= self.date_limit:
                self.driver.execute_script("arguments[0].scrollIntoView();",section)
                link_sel = section.find_element(By.LINK_TEXT,'Read more')
                link = news.find('a',class_='primary-color')
                if link:
                    link = link.get('href')
                    link = urljoin(self.root,link)
                title = news.find('h2',class_='news-headline').text.strip()
                summary = news.find('p').text.strip()
                self.append(publish_date,title,summary,link)
    
    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source': 'Bitzer',
            'Type': 'Company News',
            'Title': title,
            'Summary': summary,
            'Link': link
            }
        )
    
    def driver_wait(self,condition):
        try:
            return WebDriverWait(self.driver,5).until(condition)
        except:
            pass
    
    def scrape(self):
        self.get_soup()

all_news = []
def get_bitzer_news(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url='https://www.bitzer.de/gb/en/press/'
    news = BitzerNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df = df.drop_duplicates(subset=['Link'])
    df.to_csv('csv/bitzer_news.csv',index=False)