from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException, NoSuchWindowException
from selenium.webdriver.common.keys import Keys
from urllib.parse import urljoin
import re
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
import pandas as pd
import time

class SchottNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        self.root = 'https://www.schott.com/'
        
    def get_soup(self):
        print(f'📰Opening: Schott')
        self.driver.get(self.url)
        time.sleep(5)
        button = self.driver_wait(EC.element_to_be_clickable((By.XPATH,"//button[text()='Accept all']")))
        if button:
            button.click()
            print('Pop-up closed.')
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_section = soup.find('div',class_='filter-results')
        news_blocks = news_section.find_all('div',class_='text-image-list-template__item')
        self.get_news(news_blocks)
    
    def get_news(self,blocks):
        for news in blocks:
            parsed_date = news.find('p',class_='text-image-list-template__heading-top').text.strip()
            parsed_date = self.clean_date(parsed_date)
            parsed_date_obj = datetime.strptime(parsed_date,'%B %d, %Y,')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj >= self.date_limit:
                title = news.find('h6',class_='text-image-list-template__heading').text.strip()
                link = news.find('a',class_='text-image-list-template__button').get('href')
                link = urljoin(self.root,link)
                summary_block = news.find_all('li')
                summary_block_list = []
                for list in summary_block:
                    text = list.text.strip()
                    summary_block_list.append(text)
                separator = ' '
                summary = separator.join(summary_block_list)
                self.append(publish_date,title,summary,link)
        
    def clean_date(self,date_str):
        days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        for day in days:
            date_str = date_str.replace(day,'').strip(",")
        date_str = date_str.split(maxsplit=4)[0:3]
        separator = ' '
        date_str = separator.join(date_str)
        return date_str

    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source': 'Schott',
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
def get_schott(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://www.schott.com/en-us/news-and-media/media-releases'
    news = SchottNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/schott_news.csv',index=False)