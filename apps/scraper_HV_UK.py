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
from urllib.parse import urljoin
import pandas as pd
import time

class HVUKNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.news_links = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        self.root = 'https://www.hvnplus.co.uk/'
    
    def get_soup(self):
        print(f'📰Opening: HV UK')
        self.driver.get(self.url)
        try:
            self.driver_wait(EC.element_to_be_clickable((By.CLASS_NAME,'fc-primary-button'))).click()
            print('Pop-up closed.')
        except:
            pass
        print('Waiting for a banner blocking the news blocks to close..')
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        main = soup.find_all('div',class_='cat-box-content')
        news_blocks_main = main[0].find_all('li')
        news_blocks_secondary = main[1].find_all('li')
        self.iterate_link_list(news_blocks_main)
        self.iterate_link_list(news_blocks_secondary)
        self.get_news()
    
    def get_news(self):
        for news in self.news_links:
            try:
                self.driver.switch_to.new_window('tab')
                self.driver.get(news)
                self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'content-inner-wrap')))
                html = self.driver.page_source
                soup = BeautifulSoup(html,'html.parser')
                parsed_date = soup.find('span',class_='tie-date').text.strip()
                parsed_date = self.clean_ordinal_suffix(parsed_date)
                parsed_date_obj = datetime.strptime(parsed_date,'%d %B %Y')
                publish_date = parsed_date_obj.strftime('%Y-%m-%d')
                if parsed_date_obj <= self.date_limit:
                    break
                title = soup.find('h1',class_='entry-title').find('span',{'itemprop':'name'}).text.strip()
                paragraphs = soup.find_all('p')
                summary = None
                for p in paragraphs:
                    para = p.text.strip()
                    if len(para) > 200:
                        summary = para
                        break
                if not summary:
                    summary = 'Unable to parse summary, please visit the news page instead.'
                
                self.append(publish_date,title,summary,news)
            except Exception as e:
                print(f'An error has occured: {e}')
            finally:
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
    
    def iterate_link_list(self,link_list):
        for news in link_list:
            link = news.find('a').get('href')
            if link:
                link = urljoin(self.root,link)
                self.news_links.append(link)
        
    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source': 'HV UK',
            'Type': 'Industry News',
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
            
    def clean_ordinal_suffix(self,date_str):
        return re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)

    def scrape(self):
        self.get_soup()

all_news = []
def get_HV_UK(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://www.hvnplus.co.uk/news/'
    news = HVUKNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df = df.drop_duplicates(subset=['Link'])
    df.to_csv('csv/HV_UK_news.csv',index=False)