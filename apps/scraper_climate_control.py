from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
from urllib.parse import urljoin
import re
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
import pandas as pd
import time

class ClimateControlNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        self.root = 'https://www.climatecontrolnews.com.au/'
        self.news_list = []

    def get_soup(self):
        self.driver.get(self.url)
        self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'landing-wrap')))
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_section = soup.find('div',class_='landing-wrap')
        headline_link = news_section.find('a', class_='gallery-link').get('href')
        landing_cards = soup.find_all('div',class_='landing-card')
        self.get_news(headline_link)
        for url in landing_cards:
            try:
                link = url.find('p',class_='pull-right').find('a').get('href')
                status = self.get_news(link)
                if status == False:
                    break
            except Exception as e:
                print(f'An error has occured: {e}')

    def get_news(self,link):
        try:
            link = urljoin(self.root,link)
            self.driver.switch_to.new_window('tab')
            self.driver.get(link)
            self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'article')))
            html = self.driver.page_source
            soup = BeautifulSoup(html,'html.parser')
            parsed_date = soup.find('div',class_='article-author').text.strip().split(maxsplit=3)[3]
            parsed_date = parsed_date.replace('| ','').strip()
            parsed_date_obj = datetime.strptime(parsed_date,'%d %B %Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj >= self.date_limit:
                title = soup.find('h1',class_='article-title').text.strip()
                paragraphs = soup.find_all('p')
                summary = None
                for p in paragraphs:
                    para = p.text.strip()
                    if len(para) > 200:
                        summary = para
                        break
                if not summary:
                    summary = 'Unable to parse summary, please visit the news page instead.'
                self.append(publish_date,title,summary,link)
                return True
            else:
                return False
        finally:
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            
    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source': 'Climate Control News',
            'Type': 'Industry News',
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

all_news = []
def get_climate_control_news(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://www.climatecontrolnews.com.au/news/latest'
    news = ClimateControlNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df = df.drop_duplicates(subset=['Link'])
    df.to_csv('csv/climate_control_news.csv',index=False)