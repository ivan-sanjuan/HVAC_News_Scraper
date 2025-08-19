from selenium import webdriver
import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd
import threading
import time
from selenium.common.exceptions import NoSuchElementException

class DanfossNews:
    def __init__(self,driver,coverage_days,news_url):
        self.driver = driver
        self.coverage_days = coverage_days
        self.news_url = news_url
        self.interval = 2
        self.today = datetime.today()
        self.latest_news = []
        
    def popup_watcher(self):
        def watch():
            while True:
                try:
                    pop_up=WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, 'close animatedCloseButton__AV-vN'))
                    )
                    self.driver.execute_script("arguments[0].click();", pop_up)
                    print('Popup dismissed.')
                except NoSuchElementException:
                    pass
                time.sleep(self.interval)
        threading.Thread(target=watch, daemon=True).start()
        
    def get_soup(self):
        self.driver.get(self.news_url)
        pop_up = WebDriverWait(driver,5).until(
            EC.presence_of_element_located((By.CLASS_NAME,'coi-banner__accept'))
        )
        if pop_up:
            pop_up.click()
        else:
            pass
        WebDriverWait(driver,5).until(
            EC.presence_of_element_located((By.CLASS_NAME,'news-list-items'))
        )
        html = self.driver.page_source
        self.soup = BeautifulSoup(html,'html.parser')
        article_section = self.soup.find('ul',class_='news-list-items')
        self.news_blocks = article_section.find_all('div',class_='tile__text')

    def get_news(self):
        for news in self.news_blocks:
            parsed_date = news.find('div',class_='tile__text-details_item').text.split(maxsplit=1)[1].strip()
            parsed_date_obj = datetime.strptime(parsed_date,'%B %d, %Y')
            self.publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj >= self.today-timedelta(days=self.coverage_days):
                self.title = news.find('div',class_='tile__text-title').text.strip()
                self.link = news.find('a',class_='tile__link').get('href')
                summary = news.find('div',class_='tile__text-description')
                if summary:
                    self.summary = news.find('div',class_='tile__text-description').find('span').find('p').text.strip()
                else:
                    self.summary = 'NO SUMMARY'
                root_url = 'https://www.danfoss.com/'
                self.latest_news.append(
                    {
                    'PublishDate': self.publish_date,
                    'Source': 'Danfoss',
                    'Title': self.title,
                    'Summary': self.summary,
                    'Link': f'{root_url}{self.link}'
                    }
                )

    def scrape(self):
        self.get_soup()
        self.get_news()
        

all_news=[]
def get_danfoss_news(driver, coverage_days):
    url='https://www.danfoss.com/en/about-danfoss/news/?pageSize=15&sort=startDate_desc'
    news = DanfossNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/danfoss_news.csv', index=False)
    
    return all_news
    

