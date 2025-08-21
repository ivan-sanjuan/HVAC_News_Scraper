from selenium import webdriver
import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime
import pandas as pd
import time

class TraneNews:
    def __init__(self,driver,coverage_days,news_url):
        self.driver = driver
        self.coverage_days = coverage_days
        self.news_url = news_url
        self.today = date.today()
        self.latest_news = []
        
    def get_soup(self):
        self.driver.get(self.news_url)
        WebDriverWait(self.driver,5).until(
            EC.presence_of_element_located((By.CLASS_NAME,'newspromo__promos'))
        )
        html = self.driver.page_source
        self.soup = BeautifulSoup(html,'html.parser')
        self.news_section = self.soup.find('div', class_='newspromo__promos')
        self.news_blocks = self.news_section.find_all('div', 'newspromo__promo-wrap')
        
    def get_news(self):
        for news in self.news_blocks:
            parsed_date = news.find('p', class_='newspromo__date').text
            parsed_date_obj = datetime.strptime(parsed_date,'%B %d, %Y')
            self.publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj.date() >= self.today-timedelta(days=self.coverage_days):
                link_tag = news.find('a', 'newspromo__link')
                link_target = link_tag.get('target')
                self.link = link_tag.get('href')
                self.title = link_tag.text.strip()
                if link_target == '_self':
                    self.driver.switch_to.new_window('tab')
                    print(f'getting summary of: {self.title}')
                    self.driver.get(self.link)
                    self.summary = self.driver.find_element(By.XPATH,'//*[@id="_ctrl0_ctl70_divModuleContainer"]/div/div/div/div[3]/div/p[1]').text.strip()
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
                else:
                    self.summary = 'NO SUMMARY - LINK LEADS TO A DIFFERENT SITE; Visit the site for more information.'
                    
                self.latest_news.append(
                    {
                    'PublishDate': self.publish_date,
                    'Source': 'TRANE',
                    'Title': self.title,
                    'Summary': self.summary,
                    'Link': self.link
                    }
                )
                    
    def scrape(self):
        self.get_soup()
        self.get_news()

all_news = []
def get_trane_news(driver, coverage_days):
    news_url = 'https://www.tranetechnologies.com/en/index/news/news-archive.html'
    news = TraneNews(driver,coverage_days,news_url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/trane_technologies_news.csv', index=False)
    return all_news
    