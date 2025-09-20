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

class SecopNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        self.root = 'https://www.secop.com/'
        
    def get_soup(self):
        self.driver.get(self.url)
        button = self.driver_wait(EC.element_to_be_clickable((By.XPATH,'r_button--accept-all')))
        if button:
            button.click()
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_blocks = soup.find_all('li',class_='r_grid__item')
        self.get_news(news_blocks)

    def get_news(self,blocks):
        for news in blocks:
            try:
                parsed_date = news.find('div',class_='r_rich-text')
                if parsed_date:
                    parsed_date = parsed_date.find('time').get('datetime')
                    publish_date = datetime.strptime(parsed_date,'%Y-%m-%d')
                    if publish_date >= self.date_limit:
                        title_block = news.find('a',class_='r_card__link')
                        title = title_block.text.strip()
                        link = title_block.get('href')
                        link = urljoin(self.root,link)
                        self.driver.switch_to.new_window('tab')
                        self.driver.get(link)
                        self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'r_section__wrap')))
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
            'Source': 'Secop',
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
def get_secop(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://www.secop.com/updates/news'
    news = SecopNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/secop_news.csv',index=False)