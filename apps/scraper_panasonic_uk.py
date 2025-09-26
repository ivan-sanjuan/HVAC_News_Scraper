from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException, NoSuchWindowException
from selenium.webdriver.common.keys import Keys
from urllib.parse import urljoin
import threading
import re
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
import pandas as pd
import time

class PanasonicUKNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        self.root = 'https://www.aircon.panasonic.eu/'
        
    def get_soup(self):
        print(f'📰Opening: Panasonic - UK')
        self.driver.get(self.url)
        button = self.driver_wait(EC.element_to_be_clickable((By.ID,'onetrust-accept-btn-handler')))
        if button:
            button.click()
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_section = soup.find('div',class_='container')
        news_blocks = news_section.find_all('div',class_='row')[1].find_all('div',class_='row')
        self.get_news(news_blocks)
    
    def get_news(self,blocks):
        for news in blocks:
            parsed_date = news.find('span',{'style':'font-weight: 500;'})
            if parsed_date:
                parsed_date = parsed_date.get_text(strip=True)
                parsed_date_obj = datetime.strptime(parsed_date,'%d/%m/%Y')
                publish_date = parsed_date_obj.strftime('%Y-%m-%d')
                if parsed_date_obj >= self.date_limit:
                    title = news.find('h3',{'style':'color: black;'})
                    if title:
                        title = title.get_text(strip=True)
                        link = news.find('a').get('href')
                        summary = news.find('p',{'style':'color: black;'}).get_text(strip=True)
                        self.append(publish_date,title,summary,link)

    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source': 'Panasonic-UK',
            'Type': 'Company News',
            'Title': title,
            'Summary': summary,
            'Link': link
            }
        )

    def driver_wait(self,condition):
        try:
            return WebDriverWait(self.driver,20).until(condition)
        except:
            pass
    
    def scrape(self):
        self.get_soup()

all_news = []
def get_panasonic_uk(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://www.aircon.panasonic.eu/GB_en/news/more/'
    news = PanasonicUKNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/panasonic_uk_news.csv',index=False)