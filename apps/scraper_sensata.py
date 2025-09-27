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

class SensataNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        self.root = 'https://www.sensata.com/'

    def get_soup(self):
        print(f'📰Opening: Sensata')
        try:
            self.driver.get(self.url)
            button = self.driver_wait(EC.element_to_be_clickable((By.CLASS_NAME,'CybotCookiebotBannerCloseButton')))
            if button:
                button.click()
                print('Pop-up has been closed.')
            html = self.driver.page_source
            soup = BeautifulSoup(html,'html.parser')
            news_section = soup.find('div',class_='newsroom__content')
            news_blocks = soup.find_all('div',class_='listing-item')
            self.get_news(news_blocks)
        except AttributeError:
            print('Triggered CAPTCHA, unable to visit the site.')
    
    def get_news(self,bs4_blocks):
        for news in bs4_blocks:
            parsed_date = news.find('div',class_='listing-item__info').text.strip()
            parsed_date = parsed_date.replace('Press Release |','').strip()
            parsed_date_obj = datetime.strptime(parsed_date,'%B %d, %Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj >= self.date_limit:
                link = news.find('a').get('href')
                link = urljoin(self.root,link)
                title = news.find('a').text.strip()
                paragraphs = news.find_all('p')
                para_lists = news.find_all('li')
                separator = ' '
                all_paragraph = []
                if para_lists:
                    for li in para_lists:
                        list = li.text.strip()
                        all_paragraph.append(list)
                if paragraphs:
                    for p in paragraphs:
                        para = p.text.strip()
                        all_paragraph.append(para)
                summary = separator.join(all_paragraph)
                self.append(publish_date,title,summary,link)

    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source': 'Sensata',
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
def get_sensata(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://www.sensata.com/newsroom'
    news = SensataNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/sensata_news.csv',index=False)