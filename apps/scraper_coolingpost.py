from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime
from urllib.parse import urljoin
import time
import pandas as pd
import re

class CoolingPostNews:
    def __init__(self,driver,coverage_days,news_url,name,source):
        self.news_url = news_url
        self.coverage = coverage_days
        self.driver = driver
        self.soup = None
        self.news_block = []
        self.latest_news = []
        self.page_num = 1
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        self.root = 'https://www.coolingpost.com/'
        self.name = name
        self.source = source
    
    def get_soup(self):
        print(f'📰Opening: {self.source}')
        try:
            while True:
                url = self.news_url if self.page_num == 1 else f'https://www.coolingpost.com/{self.name}/page/{self.page_num}/'
                self.driver.get(url)
                self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'cl-layout__item')))
                html = self.driver.page_source
                self.soup = BeautifulSoup(html,'html.parser')
                if not self.get_news_blocks():
                    break
                self.page_num += 1
                print(f'CoolingPost News, Page: {self.page_num}')
        except Exception as e:
            print(f'An error has occured: {e}')
        
    def get_news_blocks(self):
        news_section = self.soup.find('div', class_='cl-layout')
        news_blocks = news_section.find_all('div', class_='cl-layout__item')
        for news in news_blocks:
            parsed_date = news.find('div', class_='cl-element-published_date').text
            parsed_date_obj = datetime.strptime(re.sub(r'(\d+)(st|nd|rd|th)', r'\1', parsed_date), '%d %B %Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj < self.date_limit:
                return False
            title_block = news.find('a', class_='cl-element-title__anchor')
            title = title_block.text.strip()
            link = title_block.get('href')
            link = urljoin(self.root,link)
            summary = news.find('div', class_='cl-element-excerpt').text.strip()
            self.append(publish_date,title,summary,link)
        return True
    
    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source': self.source,
            'Type': 'Industry News',
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

sites = [
    {'url':'https://www.coolingpost.com/world-news/','name':'world-news','source':'CoolingPost-World'},
    {'url':'https://www.coolingpost.com/uk-news/','name':'uk-news','source':'CoolingPost-UK'},
    {'url':'https://www.coolingpost.com/products/','name':'products','source':'CoolingPost-Products'},
    {'url':'https://www.coolingpost.com/features/','name':'features','source':'CoolingPost-Features'},
    {'url':'https://www.coolingpost.com/blog/','name':'blog','source':'CoolingPost-Blog'},
    {'url':'https://www.coolingpost.com/training/','name':'training','source':'CoolingPost-T&E'},
]

all_news = []        
def get_cooling_post(driver,coverage_days):
    for details in sites:
        url = details.get('url')
        name = details.get('name')
        src = details.get('source')
        news = CoolingPostNews(driver,coverage_days,url,name,src)
        news.scrape()
        all_news.extend(news.latest_news)
        # return CoolingPostNews.news_url
    df = pd.DataFrame(all_news)
    df = df.drop_duplicates(subset=['Link'])
    df.to_csv('csv/cooling_post_news.csv', index=False)