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

class MitsubishiGlobalNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        self.root = 'https://www.mitsubishielectric.com/'
        
    def get_soup(self):
        self.driver.get(self.url)
        self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'list-news')))
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_section = soup.find('ul',class_='list-news')
        news_blocks = news_section.find_all('li')
        self.get_news(news_blocks)
    
    def get_news(self,blocks):
        for news in blocks:
            try:
                parsed_date = news.find('time',class_='news-article__date')
                if parsed_date:
                    parsed_date = parsed_date.get_text(strip=True)
                    parsed_date_obj = datetime.strptime(parsed_date,'%b %d, %Y')
                    publish_date = parsed_date_obj.strftime('%Y-%m-%d')
                    if parsed_date_obj >= self.date_limit:
                        link = news.find('a',class_='news-article--thumb').get('href')
                        link = urljoin(self.root,link)
                        title = news.find('div',class_='news-article__subject').get_text(strip=True)
                        if link.endswith('.pdf'):
                            summary = 'Unable to parse summary. link leads to a PDF file, please click visit instead.'
                        elif link.endswith('/'):
                            self.driver.switch_to.new_window('tab')
                            self.driver.get(link)
                            self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'news-article')))
                            html = self.driver.page_source
                            soup = BeautifulSoup(html,'html.parser')
                            summary = None
                            paragraphs = soup.find_all('p')
                            if not paragraphs:
                                summary = 'Unable to parse summary. news page doesnt have a valid paragraph.'
                            for p in paragraphs:
                                para = p.get_text(strip=True)
                                if len(para) > 250:
                                    summary = para
                                    break
                            self.driver.close()
                            self.driver.switch_to.window(self.driver.window_handles[0])
                            if not summary:
                                summary = 'Unable to parse summary, please visit the news page instead.'
                        else:
                            summary = 'Unable to parse summary, please visit the news page instead.'
                        self.append(publish_date,title,summary,link)
            except Exception as e:
                print(f'An error has occured: {e}')
        
    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source': 'Mitsubishi Electric-Global',
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
def get_mitsubishi_electric_global(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://www.mitsubishielectric.com/en/pr/'
    news = MitsubishiGlobalNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/mitsubishi_electric_global_news.csv',index=False)