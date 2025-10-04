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
                self.get_news(link)
                
    def get_news(self,link):
        try:
            self.driver.switch_to.new_window('tab')
            self.driver.get(link)
            self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'single-post-press')))
            html = self.driver.page_source
            soup = BeautifulSoup(html,'html.parser')
            article_block = soup.find('div',class_='content-container')
            parsed_date = article_block.find('p')
            parsed_date = self.find_date(parsed_date)
            print(parsed_date)
        except Exception as e:
            print(f'An error has occured: {e}')
        finally:
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            
    def find_date(self,date_paragraphs):
        parsed_date = None
        para = date_paragraphs.text.strip()
        matches = datefinder.find_dates(para)
        dates = list(matches)
        for text in dates:
            print(text)
        
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
    df.to_csv('csv/ecobee_news.csv',index=False)
    
options = Options()
options.add_argument('--headless=new')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920x1080')
options.add_argument('--log-level=3')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115 Safari/537.36")
driver = webdriver.Chrome(options=options)
get_ecobee(driver,coverage_days=3)

time.sleep(10)
driver.quit()