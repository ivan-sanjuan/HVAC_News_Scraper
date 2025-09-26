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


class ViessmannNews:
    def __init__(self,driver,coverage_days,news_url):
        self.driver = driver
        self.coverage_days = coverage_days
        self.news_url = news_url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage_days)
        self.page_num = 1
        self.root = 'https://www.viessmann-climatesolutions.com/'

    def get_soup(self):
        print(f'📰Opening: Viessmann')
        self.driver.get(self.news_url)
        try:
            button = self.driver.find_element(By.ID, 'uc-accept-all-button')
            if button:
                self.driver.execute_script("arguments[0].click();", button)
                print('Accepted cookies.')
        except:
            print('No cookie pop-up detected.')
        time.sleep(10)
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_block = soup.find('div',class_='vic-m-page-overview__results')
        news_list = soup.find_all('div',class_='vic-m-search-result-teaser__content')
        self.get_news(news_list)
        
    def get_news(self,blocks):
        for news in blocks:
            parsed_date = news.find('span',class_='vic-m-search-result-teaser__date').text.strip()
            parsed_date_obj = datetime.strptime(parsed_date,'%B %d, %Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj >= self.date_limit:
                title = news.find('h2',class_='vic-m-search-result-teaser__headline').text.strip()
                link = news.find('a',class_='vic-m-search-result-teaser__link').get('href')
                link = urljoin(self.root,link)
                summary = news.find('p',class_='vic-m-search-result-teaser__text').text.strip()
                self.append(publish_date,title,summary,link)
                
    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source': 'Viessmann',
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
def get_viessmann_news(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://www.viessmann-climatesolutions.com/en/newsroom.html'
    news = ViessmannNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/viessman_news.csv', index=False)