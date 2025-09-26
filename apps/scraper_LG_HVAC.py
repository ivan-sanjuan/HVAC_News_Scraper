from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException, NoSuchWindowException
from selenium.webdriver.common.keys import Keys
import re
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
import pandas as pd
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
    
    def get_soup(self):
        print(f'📰Opening: LG HVAC')
        self.driver.get(self.url)
        self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'articles-list')))
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_section_bs4 = soup.find('ol',class_='articles-list')
        blocks_bs4 = news_section_bs4.find_all('li',class_='item')
        self.get_news(blocks_bs4)
        
    def get_news(self,blocks_bs4):
        for news in blocks_bs4:
            parsed_date = news.find('time').text.strip().split(maxsplit=1)[1]
            parsed_date_obj = datetime.strptime(parsed_date,'%B %d, %Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj >= self.date_limit:
                link = news.find('a',class_='learn-more-link').get('href')
                title = news.find('h4',class_='title').text.strip()
                summary = 'LG HVAC News link always leads to 3rd party site - please visit the site instead.'
                self.append(publish_date,title,summary,link)

    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source': 'LG HVAC - NA',
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

all_news=[]
def get_LGHVAC_NA(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://lghvac.com/about-lg/'
    news = LGHVACNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/LG_HVAC_NA_news.csv',index=False)