from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys
import threading
from threading import Event, Lock
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
from urllib.parse import urljoin
import pandas as pd
import time

class ACRJournal:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.page_num = 1
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        self.root = 'https://www.acrjournal.uk/'

    def get_soup(self):
        print(f'📰Opening: ACR Journal')
        while True:
            if self.page_num == 1:
                self.driver.get(self.url)
                cookies = self.driver_wait(EC.element_to_be_clickable((By.ID,'accept-btn')))
                if cookies:
                    self.driver.execute_script("arguments[0].click();",cookies)
                    print('Pop-up closed.')
            else:
                self.driver.get(f'https://www.acrjournal.uk/news/?CurrentPage={self.page_num}')
                print(f'Opening: Page {self.page_num}')
            self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'paged-list-news')))
            html = self.driver.page_source
            soup = BeautifulSoup(html,'html.parser')
            news_section = soup.find('div',class_='paged-list-news')
            news_blocks = news_section.find_all('div',class_='card-body')
            if not self.get_news(news_blocks):
                break
            self.page_num += 1
    
    def get_news(self,blocks):
        for news in blocks:
            parsed_date = news.find('p').text.strip()
            parsed_date_obj = datetime.strptime(parsed_date,'%d %B %Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj <= self.date_limit:
                return False
            title_block = news.find('h5').find('a')
            title = title_block.text.strip()
            link = title_block.get('href')
            link = urljoin(self.root,link)
            self.driver.switch_to.new_window('tab')
            self.driver.get(link)
            self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'post-body-container')))
            html = self.driver.page_source
            soup = BeautifulSoup(html,'html.parser')
            paragraphs = soup.find_all('p')
            summary = None
            for p in paragraphs:
                para = p.text.strip()
                if len(para) > 200:
                    summary = para
                    break
            if not summary:
                summary = 'Unable to parse summary, please visit the news page instead.'
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            self.append(publish_date,title,summary,link)
        return True
            
    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source': 'ACR Journal',
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
def get_acr_journal(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url='https://www.acrjournal.uk/news'
    news = ACRJournal(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df = df.drop_duplicates(subset=['Link'])
    df.to_csv('csv/acr_journal_news.csv',index=False)