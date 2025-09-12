from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
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
        self.root = 'https://www.climatecontrolnews.com.au'

    def get_soup(self):
        self.driver.get(self.url)
        self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'landing-area')))
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        head_block = soup.find('div',class_='gallery-feature')
        news_section = soup.find('div',class_='container-bg')
        news_blocks = soup.find_all('div',class_='landing-card')
        self.get_headline(head_block)
        self.get_news_blocks(news_blocks)
        
    def get_news_blocks(self,blocks):
        for news in blocks:
            parsed_date = news.find('span',class_='landing-card-date-alt').get_text(strip=True)        
            parsed_date_obj = datetime.strptime(parsed_date,'%d %b %Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj >= self.date_limit:
                badge = news.find('span',class_='badge')
                if badge:
                    continue
                else:
                    rel_url = news.find('h3',class_='h4').find('a').get('href')
                    link = f'{self.root}{rel_url}'
                    self.driver_wait(lambda e: len(e.window_handles) == 1)
                    self.driver.switch_to.new_window('tab')
                    self.driver.get(link)
                    details = self.get_details()
                    title = details.get('title')
                    summary = details.get('summary')
                    self.append(publish_date,title,summary,link)
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
        
    def get_headline(self,block):
        parsed_date = block.find('small',class_='text-hint').get_text(strip=True)        
        parsed_date_obj = datetime.strptime(parsed_date,'%d %b %Y')
        publish_date = parsed_date_obj.strftime('%Y-%m-%d')
        if parsed_date_obj >= self.date_limit:
            rel_url = block.find('a',class_='gallery-link').get('href')
            link = f'{self.root}{rel_url}'
            self.driver.switch_to.new_window('tab')
            self.driver.get(link)
            details = self.get_details()
            title = details.get('title')
            summary = details.get('summary')
            self.append(publish_date,title,summary,link)
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

    def get_details(self):
        self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'article')))
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        title = soup.find('h1',class_='article-title').get_text(strip=True)
        summary_block = soup.find('div',class_='article-content')
        paragraphs = summary_block.find_all('p')
        for sum in paragraphs:
            para = sum.text.strip()
            if len(para) > 160:
                summary = para
                break
            else:
                continue
        else:
            summary = paragraphs[0].text.strip()
        return ({'title':title,'summary':summary})
        
    
    def append(self,publish_date,title,summary,link):
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
    df.to_csv('csv/climate_control_news.csv',index=False)