from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
from urllib.parse import urljoin
import pandas as pd
import time

class CarelNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage_days = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage_days)
        self.root = 'https://www.carel.com/'

    def get_soup(self):
        print(f'📰Opening: Carel')
        self.driver.get(self.url)
        self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'portlet-body')))
        time.sleep(5)
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_blocks = soup.find_all('div',class_='asset-news-content')
        self.get_news(news_blocks)

    def get_news(self,blocks):
        for news in blocks:
            parsed_date = news.find('div',class_='news-date').text.strip()
            parsed_date_obj = datetime.strptime(parsed_date,'%d/%m/%Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj >= self.date_limit:
                title_section = news.find('div',class_='news-title')
                title = title_section.find('a').text.strip()
                link = title_section.find('a').get('href')
                link = urljoin(self.root,link)
                summary = news.find('div',class_='news-summary').find('a').text.strip()
                self.append(publish_date,title,summary,link)
                
    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source': 'Carel',
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
def get_carel(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url='https://www.carel.com/news'
    news = CarelNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df = df.drop_duplicates(subset=['Link'])
    df.to_csv('csv/carel_news.csv',index=False)