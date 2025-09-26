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

class MideaNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        self.root = 'https://mbt.midea.com/'
        
    def get_soup(self):
        print(f'📰Opening: Midea')
        self.driver.get(self.url)
        button = self.driver_wait(EC.element_to_be_clickable((By.ID,'onetrust-accept-btn-handler')))
        if button:
            self.driver.execute_script("arguments[0].click();",button)
            print('Pop-up closed.')
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_section = soup.find('ul',class_='news-list')
        news_blocks = news_section.find_all('li',class_='news-item')
        self.get_news(news_blocks)
    
    def get_news(self,blocks):
        for news in blocks:
            try:
                parsed_date = news.find('span',class_='news-item-date').text.replace(' - News','').strip()
                parsed_date_obj = datetime.strptime(parsed_date,'%Y/%m/%d')
                publish_date = parsed_date_obj.strftime('%Y-%m-%d')
                if parsed_date_obj >= self.date_limit:
                    title = news.find('h4',class_='news-item-title').text.strip()
                    link = news.find('a',class_='news-item-link').get('href')
                    link = urljoin(self.root,link)
                    self.driver.switch_to.new_window('tab')
                    self.driver.get(link)
                    self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'rich-text-main')))
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
            except Exception as e:
                print(f'An error has occured: {e}')

    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source': 'Midea',
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
def get_midea(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://mbt.midea.com/global/news'
    news = MideaNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/midea_news.csv',index=False)