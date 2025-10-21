from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException, NoSuchWindowException, WebDriverException
from selenium.webdriver.common.keys import Keys
import requests
import re
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
import pandas as pd
from dateutil.parser import parse
import time
import pyautogui
import pyperclip

class LGHVACNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        self.strike = 0
    
    def get_soup(self):
        print(f'📰Opening: LG HVAC')
        while True:
            self.driver.get(self.url)
            self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'tab-content')))
            html = self.driver.page_source
            soup = BeautifulSoup(html,'html.parser')
            news_blocks = soup.find_all('div',class_='space')
            status = self.get_news(news_blocks)
            if status == False:
                break
    
    def get_news(self,blocks):
        for news in blocks:
            parsed_date = news.find('time').text.strip()
            parsed_date = self.clean_date(parsed_date)
            publish_date = parsed_date.strftime('%Y-%m-%d')
            if parsed_date >= self.date_limit:
                title = news.find('h4',class_='title').text.strip()
                link = news.find('a',class_='learn-more-link').get('href')
                paragraph = news.find_all('p')
                summary = None
                if paragraph:
                    for p in paragraph:
                        para = p.text.strip()
                        if len(para) > 20:
                            summary = para
                            break
                if not summary:
                    summary = 'Unable to parse summary, please visit the news page instead.'
                self.append(publish_date,title,summary,link)
            else:
                self.strike += 1
                if self.strike == 3:
                    return False
    
    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source':'LG HVAC NA',
            'Type':'Company News',
            'Title':title,
            'Summary':summary,
            'Link':link
            }
        )
            
    def clean_date(self,date_str):
        parsed_date = parse(date_str,fuzzy=False)
        return parsed_date
        
    def driver_wait(self,condition):
        try:
            return WebDriverWait(self.driver,5).until(condition)
        except:
            pass

    def scrape(self):
        self.get_soup()

all_news=[]
def get_LGHVAC_NA(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://lghvac.com/about-lg/'
    news = LGHVACNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df = df.drop_duplicates(subset=['Link'])
    df.to_csv('csv/LG_HVAC_NA_news.csv',index=False)