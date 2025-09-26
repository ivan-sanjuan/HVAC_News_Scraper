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

class NidecNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        self.root = 'https://www.nidec.com'
        
    def get_soup(self):
        print(f'📰Opening: Nidec')
        self.driver.get(self.url)
        self.driver_wait(EC.presence_of_element_located((By.ID,'main')))
        # button = self.driver.find_element(By.CLASS_NAME,'title-lv2')
        # self.driver.execute_script("arguments[0].scrollIntoView();",button)
        time.sleep(15)
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        all_sections = []
        for month in months:
            section = soup.find('section',id=f'{month}')
            if section:
                news = section.find_all('li')
                all_sections.extend(news)
        self.get_news(all_sections)

    def get_news(self,blocks):
        for news in blocks:
            parsed_date = news.find('time',class_='date').get_text(strip=True)
            parsed_date_obj = datetime.strptime(parsed_date,'%d/%m/%Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj >= self.date_limit:
                title_block = news.find('a',class_='description')
                title = title_block.get_text(strip=True)
                link = title_block.get('href')
                if not link:
                    continue
                elif not link.startswith('http'):
                    link=f'{self.root}{link}'
                summary = 'Unable to parse summary, please visit the news page instead.'
                self.append(publish_date,title,summary,link)

    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source': 'Nidec',
            'Type': 'Company News',
            'Title': title,
            'Summary': summary,
            'Link': link
            }
        )
    
    def driver_wait(self,condition):
        try:
            button = WebDriverWait(self.driver,5).until(condition)
            return button
        except:
            pass
        
    def scrape(self):
        self.get_soup()
        
all_news = []
def get_nidec(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url='https://www.nidec.com/en/corporate/news/'
    news = NidecNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/nidec_news.csv',index=False)