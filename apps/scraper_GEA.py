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

class GEANews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        self.root = 'https://www.gea.com'
        
    def get_soup(self):
        print(f'📰Opening: GEA')
        self.driver.get(self.url)
        self.driver_wait(EC.element_to_be_clickable((By.ID,'onetrust-accept-btn-handler')))
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_blocks = soup.find_all('a',{'data-testid':'press-release-listing-row'})
        self.get_news(news_blocks)
    
    def get_news(self,blocks):
        for news in blocks:
            parsed_date = news.find('p',class_='text-14').get_text(strip=True)
            parsed_date_obj = datetime.strptime(parsed_date,'%B %d, %Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj >= self.date_limit:
                partial_link = news.get('href')
                link = f'{self.root}{partial_link}'
                title = news.find('p',class_='text-20').get_text(strip=True)
                summary = news.find('p',class_='text-16').get_text(strip=True)
                self.append(publish_date,title,summary,link)

    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source': 'GEA',
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
        
all_news = []
def get_GEA(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url='https://www.gea.com/en/company/media/press-releases/'
    news = GEANews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/GEA_news.csv',index=False)