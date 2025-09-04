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

class EHPANews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        self.page_num = 1
        
    def open_new_tab(self,link):
        ActionChains(self.driver)\
            .key_down(Keys.CONTROL)\
                .click(link)\
                    .key_up(Keys.CONTROL)\
                        .perform()
    
    def get_summary(self):
        try:
            WebDriverWait(self.driver,2).until(EC.text_to_be_present_in_element((By.CLASS_NAME,'elementor-widget-theme-post-content')))
        except:
            pass
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        title = soup.find('h1',class_='elementor-heading-title').text.strip()
        summary_block = soup.find('div',class_='elementor-widget-theme-post-content')
        print(f'Fetching News: {title}')
        paragraphs = summary_block.find_all('p')
        for sum in paragraphs:
            if len(sum.text.strip()) > 150:
                summary = sum.text.strip()
                return ({'title':title,'summary':summary})
            else:
                pass
        summary = paragraphs[0].text.strip()
        return ({'title':title,'summary':summary})
        
                
    def get_soup(self):
        self.driver.get(self.url)
        try:
            print('Waiting for the cookie pop-up.')
            WebDriverWait(self.driver,5).until(EC.presence_of_element_located((By.CLASS_NAME,'cky-btn-accept'))).click()
            print('Accepted cookies.')
        except:
            print("Cookie pop-up did not show up.")
            pass
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_section = soup.find('div',class_='jet-listing-grid')
        self.news_block = news_section.find_all('div',class_='jet-equal-columns')
        self.news_block_sel = self.driver.find_elements(By.CLASS_NAME,'jet-equal-columns')

    def get_news(self):
        for news, section in zip(self.news_block,self.news_block_sel):
            parsed_date = news.find('div',class_='elementor-widget-heading').get_text(strip=True)
            parsed_date_obj = datetime.strptime(parsed_date,'%d %b %Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj >= self.date_limit:
                self.driver.execute_script("arguments[0].scrollIntoView();",section)
                link = news.find('div',class_='elementor-widget-image').find('div').find('a').get('href')
                self.driver.switch_to.new_window('tab')
                self.driver.get(link)
                current_tab = self.driver.window_handles
                WebDriverWait(self.driver,3).until(lambda e: len(e.window_handles) > 0)
                news = self.get_summary()
                title = news.get('title')
                summary = news.get('summary')
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                self.latest_news.append(
                    {
                    'PublishDate':publish_date,
                    'Source': 'EHPA',
                    'Type': 'Industry News',
                    'Title': title,
                    'Summary': summary,
                    'Link': link
                    }
                )

    def scrape(self):
        self.get_soup()
        self.get_news()

all_news = []
def get_EHPA(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url='https://www.ehpa.org/news-and-resources/'
    news=EHPANews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/ehpa_news.csv',index=False)
