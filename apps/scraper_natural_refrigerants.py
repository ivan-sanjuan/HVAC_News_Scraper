from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime
import pandas as pd
import time


class NaturalRefrigerants:
    def __init__(self,driver,coverage_date,news_url):
        self.driver = driver
        self.coverage_date = coverage_date
        self.news_url = news_url
        self.today = date.today()
        self.latest_news = []
        self.page_num = 1
        
    def get_soup(self):
        url = self.news_url
        print(f'Current URL: {url}')
        self.driver.delete_all_cookies()
        self.driver.get(url)
        WebDriverWait(self.driver,timeout=5).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'elementor-grid-item'))
        )
        self.html = self.driver.page_source
        self.soup = BeautifulSoup(self.html,'html.parser')
        self.news_section = self.soup.find('div', class_='elementor-posts-container')
        self.news_blocks = self.news_section.find_all('article', class_='elementor-grid-item')
        
    def get_news(self):
        for news in self.news_blocks:
            parsed_date = news.find('span', class_='elementor-post-info__item').find('time').text.strip()
            parsed_date_obj = datetime.strptime(parsed_date,'%B %d, %Y')
            self.publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj.date() < self.today - timedelta(days=self.coverage_date):
                self.link = news.find('h2', class_='elementor-heading-title').find('a').get('href')
                self.title = news.find('h2', class_='elementor-heading-title').find('a')
                self.summary = news.find('div', class_='elementor-widget-theme-post-excerpt').find('div', class_='elementor-widget-container')
            
                self.latest_news.append(
                    {
                    'PublishDate': self.publish_date,
                    'Source': 'Natural Refrigerants',
                    'Title': self.title.text.strip(),
                    'Summary': self.summary.text.strip(),
                    'Link': self.link
                    }
                )
    
    def scrape(self):
        self.get_soup()
        self.get_news()
        
all_news = []
def get_natural_refrigerants_news(driver, coverage_date):
    url = 'https://naturalrefrigerants.com/news/'
    news = NaturalRefrigerants(driver,coverage_date,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/natural_refrigerants_news.csv', index=False)
    
    return all_news