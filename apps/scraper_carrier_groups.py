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

class CarrierGroupNews:
    def __init__(self,driver,coverage_days,news_url,source):
        self.driver = driver
        self.coverage_days = coverage_days
        self.news_url = news_url
        self.source = source
        self.date_limit = datetime.today()-timedelta(days=self.coverage_days)
        self.root = 'https://www.carrier.com/'
        self.latest_news = []

    def get_soup(self):
        self.driver.get(self.news_url)
        print(f'📰Opening: {self.source}')
        self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'ct-news-list')))
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_section = soup.find('div',class_='list-group')
        news_blocks = news_section.find_all('div',class_='pb-4')
        self.get_news(news_blocks)
    
    def get_news(self,blocks):
        for news in blocks:
            parsed_date = news.find('time',class_='date')
            if parsed_date:
                parsed_date = parsed_date.text.replace('.','')
                parsed_date = parsed_date.strip()
                parsed_date_obj = datetime.strptime(parsed_date,'%b %d, %Y')
                publish_date = parsed_date_obj.strftime('%Y-%m-%d')
                if parsed_date_obj >= self.date_limit:
                    link = news.find('a').get('href')
                    try:
                        if link.startswith('/'):
                            link = urljoin(self.root,link)
                        self.driver.switch_to.new_window('tab')
                        self.driver.get(link)
                        self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'container')))
                        html = self.driver.page_source
                        soup = BeautifulSoup(html,'html.parser')
                        title = soup.find('h1').text.strip()
                        paragraphs = soup.find_all('p')
                        summary = None
                        for p in paragraphs:
                            para = p.text.strip()
                            if len(para) > 200:
                                summary = para
                                break
                        if not summary:
                            summary = 'Unable to parse summary, please visit the news page instead.'
                        if not any(item['Link']==link for item in self.latest_news):
                            self.append(publish_date,title,summary,link)
                    finally:
                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])
    
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
            WebDriverWait(self.driver,5).until(condition)
        except:
            pass                   
            
    def scrape(self):
        self.get_soup()
        
all_news = []
def get_carrier_group_news(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    sources = [
        {'url':'https://www.carrier.com/residential/en/us/news/','src':'Carrier-Residential'},
        {'url':'https://www.carrier.com/commercial/en/us/news/','src':'Carrier-Commercial'},
        {'url':'https://www.carrier.com/truck-trailer/en/eu/news/','src':'Carrier-Transicold'}
        ]
    for news in sources:
        try:
            run = CarrierGroupNews(driver,coverage_days,news['url'],news['src'])
            run.scrape()
            all_news.extend(run.latest_news)
        except Exception as e:
            print(f'Error scraping {news['src']}: {e}')
    df = pd.DataFrame(all_news)
    df = df.drop_duplicates(subset=['Link'])
    df.to_csv('csv/carrier_group_news.csv',index=False)