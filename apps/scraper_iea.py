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

class IEANews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        self.root = 'https://www.iea.org/'
    
    def get_soup(self):
        self.driver.get(self.url)
        self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'m-grid--news-detailed')))
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_blocks = soup.find_all('div',class_='m-news-detailed-listing')
        self.get_news(news_blocks)

    def get_news(self,blocks):
        for news in blocks:
            try:
                parsed_date = news.find('div',class_='m-news-detailed-listing__date').text.strip()
                parsed_date_obj = datetime.strptime(parsed_date,'%d %B %Y')
                publish_date = parsed_date_obj.strftime('%Y-%m-%d')
                if parsed_date_obj >= self.date_limit:
                    link = news.find('a',class_='m-news-detailed-listing__link').get('href')
                    link = urljoin(self.root,link)
                    self.driver_wait(lambda e: len(e.window_handles) == 1)
                    self.driver.switch_to.new_window('tab')
                    self.driver.get(link)
                    self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'content')))
                    html = self.driver.page_source
                    soup = BeautifulSoup(html,'html.parser')
                    title = soup.find('h1')
                    if title:
                        title = title.text.strip()
                    paragraphs = soup.find_all('p')
                    for p in paragraphs:
                        para = p.text.strip()
                        if len(para) > 230:
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
            'Source': 'IEA News',
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
def get_IEA(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://www.iea.org/news'
    news = IEANews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/iea_news.csv',index=False)