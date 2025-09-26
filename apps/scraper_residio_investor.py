from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException, NoSuchWindowException
from selenium.webdriver.common.keys import Keys
import re
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
import pandas as pd
import time

class ResideoInvestorNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        self.root = 'https://investor.resideo.com'
    
    def get_soup(self):
        print(f'📰Opening: Resideo - Investor')
        self.driver.get(self.url)
        self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'evergreen-news-content-list')))
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_section = soup.find('div',class_='evergreen-news-content-list')
        news_block = news_section.find_all('div',{'role':'listitem'})
        self.get_news(news_block)
    
    def get_news(self,block):
        for news in block:
            try:
                parsed_date = news.find('div',class_='evergreen-news-date').get_text(strip=True)
                parsed_date_obj = datetime.strptime(parsed_date,'%B %d, %Y')
                publish_date = parsed_date_obj.strftime('%Y-%m-%d')
                if parsed_date_obj >= self.date_limit:
                    partial_link = news.find('a',class_='evergreen-news-link').get('href')
                    link = f'{self.root}{partial_link}'
                    self.driver.switch_to.new_window('tab')
                    self.driver.get(link)
                    self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'evergreen-news-details-item')))
                    html = self.driver.page_source
                    soup = BeautifulSoup(html,'html.parser')
                    title = soup.find('h3',class_='evergreen-item-detail-title').get_text(strip=True)
                    summary_block = soup.find('div',class_='evergreen-news-body')
                    paragraphs = summary_block.find_all('p')
                    summary = None
                    for p in paragraphs:
                        para = p.get_text(strip=True)
                        if len(para) > 350:
                            summary = para
                            break
                    if not summary:
                        summary = 'Unable to parse summary, please visit the news page instead.'
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
                    self.append(publish_date,title,summary,link)
            except Exception as e:
                print(f'Error while parsing the news entry: {e}')

    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source': 'Resideo-Investor',
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
def get_resideo_investor(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://investor.resideo.com/news/default.aspx'
    news = ResideoInvestorNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/resideo_investor_news.csv',index=False)

