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

class ParkerSporlanNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        self.root = 'https://www.parker.com/'
        
    def get_soup(self):
        self.driver.get(self.url)
        self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'cmp-news-v2-component__container')))
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_section = soup.find('div',class_='cmp-news-v2-component__container')
        news_blocks = news_section.find_all('div',class_='cmp-news-v2-component__list')
        self.get_news(news_blocks)
    
    def get_news(self,blocks):
        for news in blocks:
            try:
                parsed_date = news.find('span',class_='cmp-news-v2-component__author-date').text.strip()
                parsed_date_obj = datetime.strptime(parsed_date,'%B %d, %Y')
                publish_date = parsed_date_obj.strftime('%Y-%m-%d')
                if parsed_date_obj >= self.date_limit:
                    title_block = news.find('a',class_='cmp-news-v2-component__list-title-link')
                    title = title_block.text.strip()
                    link = title_block.get('href')
                    if link.startswith('/'):
                        link = urljoin(self.root,link)
                    if link.startswith(self.root):
                        self.driver.switch_to.new_window('tab')
                        self.driver.get(link)
                        self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'aem-container')))
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
                    else:
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
            'Source': 'Parker Sporlan',
            'Type': 'Company News',
            'Title': title,
            'Summary': summary,
            'Link': link
            }
        )

    def driver_wait(self,condition):
        try:
            return WebDriverWait(self.driver,3).until(condition)
        except:
            pass
    
    def scrape(self):
        self.get_soup()

all_news = []
def get_parker_sporlan(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://www.parker.com/us/en/about-parker/newsroom/news-release-details.html'
    news = ParkerSporlanNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/parker_sporlan_news.csv',index=False)