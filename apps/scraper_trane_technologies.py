from selenium import webdriver
import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime
from urllib.parse import urljoin
import pandas as pd
import time

class TraneNews:
    def __init__(self,driver,coverage_days,news_url):
        self.driver = driver
        self.coverage_days = coverage_days
        self.news_url = news_url
        self.date_limit = datetime.today()-timedelta(days=self.coverage_days)
        self.latest_news = []
        self.root = 'https://investors.tranetechnologies.com/'
        
    def get_soup(self):
        print(f'📰Opening: Trane Technologies')
        self.driver.get(self.news_url)
        self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'newspromo__promos')))
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_section = soup.find('div', class_='newspromo__promos')
        news_blocks = soup.find_all('div', 'newspromo__text')
        self.get_news(news_blocks)
        
    def get_news(self,blocks):
        for news in blocks:
            try:
                parsed_date = news.find('p', class_='newspromo__date').text.strip()
                parsed_date_obj = datetime.strptime(parsed_date,'%B %d, %Y')
                publish_date = parsed_date_obj.strftime('%Y-%m-%d')
                if parsed_date_obj >= self.date_limit:
                    link_tag = news.find('a')
                    link = link_tag.get('href')
                    title = link_tag.text.strip()
                    if link and link.startswith(self.root):
                        try:
                            self.driver.switch_to.new_window('tab')
                            self.driver.get(link)
                            self.driver_wait(EC.presence_of_element_located((By.ID,'maincontent')))
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
                        except Exception as e:
                            print(f'An error has occured: {e}')
                        finally:
                            self.driver.close()
                            self.driver.switch_to.window(self.driver.window_handles[0])
                    else:
                        self.summary = 'NO SUMMARY - LINK LEADS TO A DIFFERENT SITE; Visit the site for more information.'
                    self.append(publish_date,title,summary,link)
            except Exception as e:
                print(f'An error has occured: {e}')
                
    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate': publish_date,
            'Source': 'TRANE-Corporate',
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
def get_trane_news(driver, coverage_days):
    driver.set_window_size(1920, 1080)
    news_url = 'https://www.tranetechnologies.com/en/index/news/news-archive.html'
    news = TraneNews(driver,coverage_days,news_url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df = df.drop_duplicates(subset=['Link'])
    df.to_csv('csv/trane_technologies_news.csv', index=False)    