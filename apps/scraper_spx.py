from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException, NoSuchWindowException
from selenium.webdriver.common.keys import Keys
import re
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
import pandas as pd
import time

class SPXNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        
    def get_soup(self):
        print(f'📰Opening: SPX')
        self.driver.get(self.url)
        self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'et_pb_tab_content')))
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_section = soup.find('div',class_='et_pb_tab_2')
        news_blocks = news_section.find_all('div',class_='news_library_excerpt')
        self.get_news(news_blocks)
        
    def get_news(self,blocks):
        for news in blocks:
            parsed_date = news.find('p',class_='entry-date').text.replace('By: SPX Engineering Staff | Posted On:','').strip()
            parsed_date_obj = datetime.strptime(parsed_date,'%B %d, %Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj >= self.date_limit:
                title_block = news.find('span',class_='entry-title-newsposts')
                title = title_block.text.strip()
                link = title_block.get('href')
                summary = news.find('div',class_='entry-summary').text.strip()
                self.append(publish_date,title,summary,link)

    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source': 'SPX',
            'Type': 'Company News',
            'Title': title,
            'Summary': summary,
            'Link': link
            }
        )

    def driver_wait(self,condition):
        try:
            return WebDriverWait(self.driver,3).until(condition)
        except:
            pass
    
    def scrape(self):
        self.get_soup()

all_news = []
def get_SPX(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://spxcooling.com/news/#news|2'
    news = SPXNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/spx_news.csv',index=False)