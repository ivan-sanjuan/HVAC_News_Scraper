from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import date, timedelta, datetime
import pandas as pd
import time

class CopelandNews:
    def __init__(self,driver,coverage_days,news_url,source):
        self.driver = driver
        self.coverage_days = coverage_days
        self.news_url = news_url
        self.source = source
        self.today = datetime.today()
        self.root = 'https://www.copeland.com/'
        self.latest_news = []

    def get_soup(self):
        self.driver.get(self.news_url)
        print(f'Getting {self.source}')
        try:
            accept_cookies = self.driver_wait(EC.element_to_be_clickable((By.ID,'onetrust-accept-btn-handler')))
            self.driver.execute_script("arguments[0].click();",accept_cookies)
            print('Accepted cookies.')
        except:
            print('No cookie pop-up found.')
            pass
        self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'ddl-carousel__container')))
        html = self.driver.page_source
        self.soup = BeautifulSoup(html,'html.parser')
        news_section = self.soup.find('div',class_='ddl-carousel__container')
        news_blocks = news_section.find_all('div',class_='ddl-carousel__slide')
        self.get_news(news_blocks)
        
    def get_news(self,blocks):
        for news in blocks:
            parsed_date = news.find('div',class_='ddl-card__date').text.strip().split(maxsplit=1)[1]
            parsed_date_obj = datetime.strptime(parsed_date,'%b %d %Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj > self.today-timedelta(days=self.coverage_days):
                heading = news.find('a', class_='ddl-card__heading')
                title = heading.text.strip()
                link = heading.get('href')
                link = urljoin(self.root,link)
                summary = news.find('div', class_='ddl-card__description').find('p').text.strip()
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
            return WebDriverWait(self.driver,5).until(condition)
        except:
            pass
        
    def scrape(self):
        try:
            self.get_soup()
        except Exception as e:
            print(f'An error has occured: {e}')

sites = [
    {'url':'https://www.copeland.com/en-us/news','source':'Copeland-US'},
    {'url':'https://www.copeland.com/en-sg/news','source':'Copeland-Asia'}
]

all_news = []
def get_copeland_news(driver, coverage_days):
    driver.set_window_size(1920, 1080)
    for details in sites:
        url = details.get('url')
        src = details.get('source')
        news = CopelandNews(driver,coverage_days,url,src)
        news.scrape()
        all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df = df.drop_duplicates(subset=['Link'])
    df.to_csv('csv/copeland_news.csv', index=False)