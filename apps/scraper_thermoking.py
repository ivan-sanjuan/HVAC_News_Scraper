from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
from urllib.parse import urljoin
from dateutil.parser import parse
import pandas as pd
import time

class ThermokingNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage_days = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage_days)
        self.root = 'https://www.thermoking.com/'
    
    def get_soup(self):
        print(f'📰Opening: ThermoKing')
        self.driver.get(self.url)
        self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'newspromo__content')))
        blocks = self.driver.find_elements(By.CLASS_NAME,'newspromo__promo')
        self.get_news(blocks)

    def get_news(self,blocks):
        for news in blocks:
            parsed_date = news.find_element(By.CLASS_NAME,'newspromo__date').text.strip()
            if parsed_date:
                parsed_date = self.clean_date(parsed_date)
                publish_date = parsed_date.strftime('%Y-%m-%d')
                if parsed_date >= self.date_limit:
                    title = news.find_element(By.CLASS_NAME,'newspromo__title').text.strip()
                    link = news.find_element(By.CLASS_NAME,'newspromo__link').get_attribute('href')
                    link = urljoin(self.root,link)
                    summary = news.find_element(By.CLASS_NAME,'newspromo__description').text.strip()
                    self.append(publish_date,title,summary,link)
                    
    def clean_date(self,date_str):
        parsed_date = parse(date_str,fuzzy=True)
        return parsed_date
    
    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
                    {
                    'PublishDate':publish_date,
                    'Source': 'ThermoKing',
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
            
all_news=[]
def get_thermoking(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url='https://www.thermoking.com/na/en/newsroom.html'
    news = ThermokingNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df = df.drop_duplicates(subset=['Link'])
    df.to_csv('csv/thermoking_news.csv',index=False)