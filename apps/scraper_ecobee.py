from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException, NoSuchWindowException
from selenium.webdriver.common.keys import Keys
from urllib.parse import urljoin
import datefinder
import requests
import re
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
import pandas as pd
import time
import pyautogui
import pyperclip

class EcobeeNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        self.root = 'https://www.ecobee.com/'

    def get_soup(self):
        print(f'📰Opening: Ecobee')
        self.driver.get(self.url)
        cookies = self.driver_wait(EC.element_to_be_clickable((By.ID,'onetrust-accept-btn-handler')))
        if cookies:
            self.driver.execute_script("arguments[0].click();",cookies)
        self.driver_wait(EC.presence_of_element_located((By.ID,'maincontent')))
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_blocks = soup.find_all('div',class_='blog-post-card')
        for url in news_blocks:
            link = url.find('a').get('href')
            if link.startswith('/en-ca/newsroom/'):
                link = urljoin(self.root,link)
                status = self.get_news(link)
                if status == False:
                    break
                
    def get_news(self,link):
        try:
            self.driver.switch_to.new_window('tab')
            self.driver.get(link)
            self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'single-post-press')))
            html = self.driver.page_source
            soup = BeautifulSoup(html,'html.parser')
            paragraphs = soup.find_all('p')
            summary = None
            title = soup.find('h1',id='page-heading').text.strip()
            for p in paragraphs:
                para = p.text.strip()
                if len(para) > 200:
                    summary = para
                    parsed_date = self.find_date(summary)
                    break
            if not summary:
                pass
            if parsed_date <= self.date_limit:
                return False
            self.append(parsed_date,title,summary,link)
            return True
        except Exception as e:
            print(f'An error has occured: {e}')
        finally:
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            
    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source':'Ecobee',
            'Type':'Company News',
            'Title':title,
            'Summary':summary,
            'Link':link
            }
        )
            
    def find_date(self,date_paragraph):
        matches = datefinder.find_dates(date_paragraph)
        parsed_date = list(matches)[0]
        return parsed_date
        
    def driver_wait(self,condition):
        try:
            return WebDriverWait(self.driver,5).until(condition)
        except:
            pass

    def scrape(self):
        self.get_soup()

all_news = []
def get_ecobee(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://www.ecobee.com/en-ca/newsroom/'
    news = EcobeeNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df = df.drop_duplicates(subset=['Link'])
    df.to_csv('csv/ecobee_news.csv',index=False)