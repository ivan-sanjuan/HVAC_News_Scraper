from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException, NoSuchWindowException
from selenium.webdriver.common.keys import Keys
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
        self.root = 'https://www.ecobee.com'
    
    def get_soup(self):
        print(f'📰Opening: Ecobee')
        self.driver.get(self.url)
        cookie_popup = self.driver_wait(EC.element_to_be_clickable((By.ID,'onetrust-accept-btn-handler')))
        cookie_popup.click()
        if cookie_popup:
            print('Cookies accepted.')
        press_release = self.driver.find_elements(By.TAG_NAME,'h2')
        num = 0
        for sections in press_release:
            num += 1
            self.driver.execute_script("arguments[0].scrollIntoView();",sections)
            if sections.text.strip() == 'Press Releases':
                print(f'Press Releases found.')
                break
        time.sleep(10)
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_sections = soup.find_all('div',class_='content-container')
        news_blocks = news_sections[3].find_all('div',class_='blog-post-card')
        self.get_news(news_blocks)
    
    def get_news(self,blocks):
        for news in blocks:
            partial_link = news.find('a',class_='blog-post-card__title-link').get('href')
            link = f'{self.root}{partial_link}'
            self.driver.switch_to.new_window('tab')
            self.driver.get(link)
            self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'content-container')))
            html = self.driver.page_source
            soup = BeautifulSoup(html,'html.parser')
            summary_block = soup.find('div',class_='rich-text')
            paragraphs = summary_block.find_all('p')
            parsed_date = paragraphs[0].find('strong').text.split(maxsplit=1)[1]
            self.clean_date(parsed_date)
            
    def clean_date(self,date_str):
        date_format = '%B %d, %Y'
        if date_str:
            date_str = date_str.split(maxsplit=1)[1]
            print(f'Level 1 string: {date_str}')
            cleaned_date = datetime.strptime(date_str,date_format)
            print(f'Level 1 cleaned: {cleaned_date}')
        elif ValueError:
            date_str = date_str.strip('–')
            print(f'Level 2 string: {date_str}')
            cleaned_date = datetime.strptime(date_str,date_format)
            print(f'Level 2 cleaned: {cleaned_date}')
        else:
            date_str = date_str.strip('–').split(maxsplit=1)[1]
            print(f'Level 3 string: {date_str}')
            # date_str = date_str.strip('–')
            cleaned_date = datetime.strptime(date_str,date_format)
            print(f'Level 3 cleaned: {cleaned_date}')
            
            
    def driver_wait(self,condition):
        try:
            button = WebDriverWait(self.driver,5).until(condition)
            return button
        except:
            pass
        
    def scrape(self):
        self.get_soup()

all_news = []
def get_ecobee(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url='https://www.ecobee.com/en-ca/newsroom/'
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