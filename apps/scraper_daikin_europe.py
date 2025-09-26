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

class DaikinEUNews:
    def __init__(self,driver,coverage_days,url,source):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        self.source = source
        
    def get_soup(self):
        print(f'📰Opening: {self.source}')
        self.driver.get(self.url)
        time.sleep(10)
        button = self.driver_wait(EC.element_to_be_clickable((By.CLASS_NAME,'cta-button--accept')))
        try:
            button.click()
            print('Cookies Accepted.')
        except:
            print('No cookie pop-up found.')
            pass
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_section = soup.find('div',class_='search-results__content')
        news_blocks = news_section.find_all('div',class_='search-results__results__item')
        self.get_news(news_blocks)
    
    def get_news(self,blocks):
        for news in blocks:
            parsed_date = news.find('span',class_='search-results__result__tag').get_text(strip=True)
            parsed_date_obj = datetime.strptime(parsed_date,'%d/%m/%Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj >= self.date_limit:
                link = news.find('a',class_='knowledge-center-results__result__readmore').get('href')
                title = news.find('h3',class_='knowledge-center-results__result__title').get_text(strip=True)
                summary = news.find('p',class_='knowledge-center-results__result__description').get_text(strip=True)
                self.append(publish_date,title,summary,link)
        
    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source': self.source,
            'Type': 'Company News',
            'Title': title,
            'Summary': summary,
            'Link': link
            }
        )
    
    def driver_wait(self,condition):
        try:
            button = WebDriverWait(self.driver,5).until(condition)
            return button
        except:
            pass
        
    def scrape(self):
        self.get_soup()

sites = [
    {'url':'https://www.daikin.eu/en_us/press-releases.html#!?s=recent&offset=0&language=en&includeArchived=false', 'source':'Daikin-EU'},
    {'url':'https://www.daikin.co.uk/en_gb/press-releases.html#!?s=recent&offset=0&language=en&includeArchived=false', 'source':'Daikin-UK'}
]

all_news = []
def get_daikin_EU(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    for site in sites:
        url = site.get('url')
        src = site.get('source')
        news = DaikinEUNews(driver,coverage_days,url,src)
        news.scrape()
        all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/daikin_europe_news.csv',index=False)