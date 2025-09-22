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

class SanhuaNews:
    def __init__(self,driver,coverage_days,url,source):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.source = source
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        self.root = 'https://www.sanhuaeurope.com/en/news'
        
    def get_soup(self):
        self.driver.get(self.url)
        self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'flickity-slider')))
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_section = soup.find('div',class_='flickity-slider')
        if self.source == 'Sanhua-US':
            news_blocks = soup.find_all('article',class_='news-module-item')
        else:
            news_blocks = news_section.find_all('article',class_='news-module-item')
        self.get_news(news_blocks)
    
    def get_news(self,blocks):
        for news in blocks:
            try:
                parsed_date = news.find('div',class_='product-card__data').find('p').text.strip()
                try:
                    parsed_date_obj = datetime.strptime(parsed_date,'%d %b. %Y')
                except ValueError:
                    parsed_date_obj = datetime.strptime(parsed_date,'%d %b %Y')
                publish_date = parsed_date_obj.strftime('%Y-%m-%d')
                if parsed_date_obj >= self.date_limit:
                    title_block = news.find('h3',class_='product-card__title')
                    title = title_block.find('a').text.strip()
                    link = title_block.find('a').get('href')
                    summary = news.find('p',class_='news-module-item__text').text.strip()
                    if not summary:
                        try:
                            self.driver.switch_to.new_window('tab')
                            self.driver.get(link)
                            self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'news-detail-content__text')))
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
                        except Exception as f:
                            print(f'An error has occured: {f}')
                        finally:
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
            'Source': self.source,
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
        try:
            self.get_soup()
        except Exception as e:
            print(f'An error has occured: {e}')

sites = [
    {'url':'https://www.sanhuausa.com/us/en/news','source':'Sanhua-US'},
    {'url':'https://www.sanhuaeurope.com/en/news','source':'Sanhua-Europe'}
]

all_news = []
def get_sanhua(driver,coverage_days):
    for site in sites:
        url = site.get('url')
        source = site.get('source')
        driver.set_window_size(1920, 1080)
        news = SanhuaNews(driver,coverage_days,url,source)
        news.scrape()
        all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/sanhua_news.csv',index=False)