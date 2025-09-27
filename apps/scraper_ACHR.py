from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
from urllib.parse import urljoin
import pandas as pd
import time

class ACHRNews:
    def __init__(self,driver,coverage_days,url,source):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.source = source
        self.page_num = 1
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        self.root = 'https://www.achrnews.com/'
    
    def get_soup(self):
        print(f'📰Opening: {self.source}')
        while True:
            if self.page_num == 1:
                self.driver.get(self.url)
                input = self.driver_wait(EC.element_to_be_clickable((By.CLASS_NAME,'checkbox')))
                if input:
                    self.driver.execute_script("arguments[0].click();",input)
                    time.sleep(10)
                try:
                    cookies = self.driver_wait(EC.element_to_be_clickable,(By.ID,'onetrust-accept-btn-handler'))
                    self.driver.execute_script("arguments[0].scrollIntoView();",cookies)
                    self.driver.execute_script("arguments[0].click();",cookies)
                except:
                    pass
                signal = self.driver_wait(EC.element_to_be_clickable((By.ID,'onesignal-slidedown-cancel-button')))
                if signal:
                    self.driver.execute_script("arguments[0].click();",signal)
            else:
                time.sleep(1)
            html = self.driver.page_source
            soup = BeautifulSoup(html,'html.parser')
            news_section = soup.find('div',class_='records')
            self.news_blocks = news_section.find_all('article',class_='article-summary')
            self.news_blocks_sel = self.driver.find_elements(By.CLASS_NAME,'article-summary')
            if not self.get_news():
                break
            self.page_num += 1
            pagination = self.driver.find_element(By.CLASS_NAME,'pagination')
            next_page = pagination.find_element(By.LINK_TEXT,f'{self.page_num}')
            self.driver.execute_script("arguments[0].click();",next_page)
        
    def get_news(self):
        for news, sect in zip(self.news_blocks,self.news_blocks_sel):
            parsed_date = news.find('div',class_='article-summary__post-date').text.strip()
            parsed_date_obj = datetime.strptime(parsed_date,'%B %d, %Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj < self.date_limit:
                return False
            self.driver.execute_script("arguments[0].scrollIntoView();",sect)
            title_block = news.find('h2',class_='article-summary__headline').find('a')
            title = title_block.text.strip()
            link = title_block.get('href')
            link = urljoin(self.root,link)
            summary_block = news.find('div',class_='article-summary__teaser')
            p_tag = summary_block.find('p')
            if p_tag:
                summary = summary_block.find('p').text.strip()
            else:
                summary = summary_block.text.strip()
            self.append(publish_date,title,summary,link)
        return True
        
    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source': self.source,
            'Type': 'Industry News',
            'Title': title,
            'Summary': summary,
            'Link': link
            }
        )

    def driver_wait(self,condition):
        try:
            return WebDriverWait(self.driver,20).until(condition)
        except:
            pass

    def scrape(self):
        try:
            self.get_soup()
        except Exception as e:
            print(f'An error has occured: {e}')

sections = [
    {'url':'https://www.achrnews.com/articles/topic/2722','source':'ACHR-Breaking News'},
    {'url':'https://www.achrnews.com/articles/topic/2733','source':'ACHR-New HVAC Products'},
    {'url':'https://www.achrnews.com/articles/topic/2660','source':'ACHR-Manufacturer Reports'}
]

all_news = []
def get_ACHR(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    for news in sections:
        url = news.get('url')
        source = news.get('source')
        content = ACHRNews(driver,coverage_days,url,source)
        content.scrape()
        all_news.extend(content.latest_news)
    df = pd.DataFrame(all_news)
    df = df.drop_duplicates(subset=['Link'])
    df.to_csv('csv/achr_news.csv',index=False)