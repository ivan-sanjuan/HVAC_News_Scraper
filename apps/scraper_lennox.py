from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from dateutil.parser import parse
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime
import pandas as pd
import time

class LennoxNews:
    def __init__(self,driver,coverage,url):
        self.driver = driver
        self.coverage = coverage
        self.url = url
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        self.latest_news = []
        self.root = 'https://investor.lennox.com/'
    
    def get_soup(self):
        self.driver.get(self.url)
        self.driver_wait(EC.presence_of_element_located((By.ID,'content-header')))
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_blocks = soup.find_all('article')
        news_blocks_sel = self.driver.find_elements(By.TAG_NAME,'article')
        self.get_news(news_blocks,news_blocks_sel)
    
    def get_news(self,blocks,blocks_sel):
        for news, sect in zip(blocks,blocks_sel):
            parsed_date = news.find('div',class_='nir-widget--news--date-time').text.strip()
            parsed_date = self.get_date(parsed_date)
            publish_date = parsed_date.strftime('%Y-%m-%d')
            if parsed_date >= self.date_limit:
                title = news.find('a').text.strip()
                link = sect.find_element(By.LINK_TEXT,'Read More').get_attribute('href')
                link = urljoin(self.root,link)
                summary = None
                summary = news.find('div',class_='nir-widget--news--teaser').text.strip()
                if not summary:
                    summary = 'Unable to parse summary, please visit the news page instead.'
                self.append(publish_date,title,summary,link)
    
    def get_date(self,date_str):
        parsed_date = parse(date_str,fuzzy=True)
        return parsed_date

    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source':'Lennox',
            'Type':'Company News',
            'Title':title,
            'Summary':summary,
            'Link':link
            }
        )
    
    def scrape(self):
        self.get_soup()
    
    def driver_wait(self,condition):
        try:
            return WebDriverWait(self.driver,5).until(condition)
        except:
            pass

all_news = []
def get_lennox_news(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://investor.lennox.com/news-events/news-releases'
    news = LennoxNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df = df.drop_duplicates(subset=['Link'])
    df.to_csv('csv/lennox_news.csv',index=False)