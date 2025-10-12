from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime
from urllib.parse import urljoin
import pandas as pd
import time

class BDRthermeaNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage_days = coverage_days
        self.url = url
        self.date_limit = datetime.today()-timedelta(days=self.coverage_days)
        self.latest_news = []
        self.root = 'https://www.bdrthermeagroup.com/'
    
    def get_soup(self):
        print(f'📰Opening: BDR Thermea')
        self.driver.get(self.url)
        try:
            accept_cookie = self.driver_wait(EC.element_to_be_clickable((By.ID,'onetrust-accept-btn-handler')))
            if accept_cookie:
                self.driver.execute_script("arguments[0].click();",accept_cookie)
        except Exception as e:
            print(f'An error has occured: {e}')
        self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'cards-container')))
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_section = soup.find('div',class_='cards-container')
        news_blocks = soup.find_all('div',class_='rounded-cards')
        self.get_news(news_blocks)
        
    def get_news(self,blocks):
        for news in blocks:
            parsed_date = news.find('p',class_='card-date')
            if parsed_date:
                parsed_date = parsed_date.text.strip()
                parsed_date_obj = datetime.strptime(parsed_date,'%d/%m/%Y')
                publish_date = parsed_date_obj.strftime('%Y-%m-%d')
                if parsed_date_obj >= self.date_limit:
                    title = news.find('h3').text.strip()
                    summary = None
                    summary = news.find('div',class_='card-description').text.strip()
                    if not summary:
                        summary = 'Unable to parse summary, please visit the news page instead.'
                    link = news.find('div',class_='card__button-containers').find('a').get('href')
                    link = urljoin(self.root,link)
                    self.append(publish_date,title,summary,link)
    
    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate': publish_date,
            'Source': 'BDR Thermea',
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
def get_BDRthermea_news(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://www.bdrthermeagroup.com/stories'
    news = BDRthermeaNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df = df.drop_duplicates(subset=['Link'])
    df.to_csv('csv/BDR_Thermea_news.csv',index=False)