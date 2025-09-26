from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime
from urllib.parse import urljoin
import pandas as pd
import time

class NaturalRefrigerants:
    def __init__(self,driver,coverage_days,news_url):
        self.driver = driver
        self.coverage_days = coverage_days
        self.news_url = news_url
        self.today = date.today()
        self.latest_news = []
        self.page_num = 1
        self.root = 'https://naturalrefrigerants.com/'
        
    def get_soup(self):
        print(f'📰Opening: Natural Refrigerants')
        url = self.news_url
        self.driver.delete_all_cookies()
        self.driver.get(url)
        WebDriverWait(self.driver,timeout=5).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'elementor-grid-item'))
        )
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_section = soup.find('div', class_='elementor-posts-container')
        news_blocks = news_section.find_all('article', class_='elementor-grid-item')
        self.get_news(news_blocks)
        
    def get_news(self,blocks):
        for news in blocks:
            parsed_date = news.find('span', class_='elementor-post-info__item').find('time').text.strip()
            parsed_date_obj = datetime.strptime(parsed_date,'%B %d, %Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj.date() >= self.today - timedelta(days=self.coverage_days):
                link = news.find('h2', class_='elementor-heading-title').find('a').get('href')
                link = urljoin(self.root,link)
                title = news.find('h2',class_='elementor-heading-title').text.strip()
                summary = news.find('div', class_='elementor-widget-theme-post-excerpt').text.strip()
                self.append(publish_date,title,summary,link)
    
    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source': 'Natural Refrigerants',
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
        
all_news = []
def get_natural_refrigerants_news(driver, coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://naturalrefrigerants.com/news/'
    news = NaturalRefrigerants(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df = df.drop_duplicates(subset=['Link'])
    df.to_csv('csv/natural_refrigerants_news.csv', index=False)