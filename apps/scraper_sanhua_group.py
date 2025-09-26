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

class SanhuaGroupNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        self.root = 'https://www.sanhuagroup.com/en/'
        
    def get_soup(self):
        print(f'📰Opening: Sanhua Group')
        self.driver.get(self.url)
        self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'job_box4')))
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_section = soup.find('div',class_='job_box4')
        links = news_section.find_all('a')
        for url in links:
            try:
                link = url.get('href')
                link = urljoin(self.root,link)
                if link.startswith('https://www.sanhuagroup.com/en/newslist'):
                    details = self.get_news(link)
                    if details:
                        title = details.get('title')
                        summary = details.get('summary')
                        publish_date = details.get('date')
                        self.append(publish_date,title,summary,link)
                    else:
                        break
            except Exception as e:
                print(f'An error has occured: {e}')
                
    def get_news(self,link):
        try:
            self.driver.switch_to.new_window('tab')
            self.driver.get(link)
            self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'newslistbox')))
            html = self.driver.page_source
            soup = BeautifulSoup(html,'html.parser')
            section = soup.find('div',class_='newslistbox')
            parsed_date = section.find('div',class_='newslist_date').text.strip()
            parsed_date_obj = datetime.strptime(parsed_date,'%b %d %Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj >= self.date_limit:
                title = section.find('h2').text.strip()
                paragraphs = section.find_all('p')
                summary = None
                for p in paragraphs:
                    para = p.text.strip()
                    if len(para) > 200:
                        summary = para
                        break
                if not summary:
                    summary = 'Unable to parse summary, please visit the news page instead.'
                return ({'date':publish_date,'title':title,'summary':summary})
        except Exception as e:
            print(f'An error has occured: {e}')
        finally:
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])

    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source': 'Sanhua-Group',
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
def get_sanhua_group(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://www.sanhuagroup.com/en/news.html'
    news = SanhuaGroupNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/sanhua_group_news.csv',index=False)