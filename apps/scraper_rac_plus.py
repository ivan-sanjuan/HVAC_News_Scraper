from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
import re
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
import pandas as pd
import time

class RACNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
    
    def soup(self):
        self.driver.get(self.url)
        try:
            WebDriverWait(self.driver,5).until(EC.element_to_be_clickable((By.CLASS_NAME,'fc-primary-button'))).click()
            print('Pop-up closed.')
        except:
            pass
        print('Waiting for a banner blocking the news blocks to close..')
        time.sleep(10)
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        all_news_list = soup.find_all('div',class_='cat-box-content')
        news_blocks_1 = all_news_list[0].find_all('li')
        self.get_news_1(news_blocks_1)
        
    def get_news_1(self,news_list):
        for news in news_list:
            link = news.find('div',class_='post-box-title').find('a').get('href')
            details = self.get_details(link)
            self.append(details)
            
    def append(self,details):
        title = details.get('title')
        summary = details.get('summary')
        link = details.get('link')
        publish_date = details.get('publish_date')
        self.latest_news.append(
                {
                'PublishDate':publish_date,
                'Source': 'RAC Plus',
                'Type': 'Industry News',
                'Title': title,
                'Summary': summary,
                'Link': link
                }
            )      
            
    def get_details(self,link):
        WebDriverWait(self.driver,5).until(lambda e: len(e.window_handles) == 1)
        self.driver.switch_to.new_window('tab')
        self.driver.get(link)
        try:
            WebDriverWait(self.driver,5).until(EC.presence_of_element_located((By.ID,'main-content')))
        except:
            pass
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        parsed_date = soup.find('span',class_='tie-date').text.strip()
        parsed_date_cleaned = self.clean_ordinal_suffix(parsed_date)
        parsed_date_obj = datetime.strptime(parsed_date_cleaned,'%d %B %Y')
        publish_date = parsed_date_obj.strftime('%Y-%m-%d')
        if parsed_date_obj >= self.date_limit:
            title = soup.find('h1',class_='entry-title').text.strip()
            print(f'Fetching News: {title}')
            summary_block = soup.find('div',class_='post-inner')
            paragraphs = summary_block.find_all('p')
            for p in paragraphs:
                para = p.get_text(strip=True)
                if len(para) > 150:
                    summary = para
                    break
                else:
                    continue
            else:
                summary = paragraphs[0].get_text(strip=True)
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
                
        return ({'publish_date':publish_date, 'title':title, 'summary':summary, 'link':link})
            
    def clean_ordinal_suffix(self,date_str):
        return re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
        
    def scrape(self):
        self.soup()

all_news = []
def get_rac_plus(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url='https://www.racplus.com/news/'
    news = RACNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/rac_plus_news.csv',index=False)

