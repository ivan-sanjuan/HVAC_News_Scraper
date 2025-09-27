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

class TecumsehNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        self.root = 'https://www.tecumseh.com/'
        
    def get_soup(self):
        print(f'📰Opening: Tecumseh')
        self.driver.get(self.url)
        old_url = self.driver.current_url
        time.sleep(5)
        button = self.driver_wait(EC.element_to_be_clickable((By.CSS_SELECTOR,'[data-test-selector="cookiePolicy_AcceptCookies"]')))
        if button:
            button.click()
            print('Pop-up closed; waiting for the page to reload.')
        self.driver_wait(lambda d: d.current_url != old_url)
        self.driver_wait(EC.presence_of_element_located((By.CSS_SELECTOR,'[data-test-selector="newslist_pagetitle"]')))
        link_blocks = self.driver.find_elements(By.CSS_SELECTOR,'[data-test-selector="newslist_pagetitle"]')
        for links in link_blocks:
            try:
                link = links.get_attribute('href')
                if link:
                    self.driver.switch_to.new_window('tab')
                    parsed_date_obj = self.get_date(link)
                    if parsed_date_obj < self.date_limit:
                        break
                    title = self.driver.find_element(By.CSS_SELECTOR,'[data-test-selector="PageTitle"]').text.strip()
                    paragraphs = self.driver.find_elements(By.TAG_NAME,'p')
                    summary = None
                    for p in paragraphs:
                        para = p.text.strip()
                        if len(para) > 200:
                            summary = para
                            break
                    if not summary:
                        summary = 'Unable to parse summary, please visit the news page instead.'
                    
                    self.append(self.publish_date,title,summary,link)
            finally:
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
            
    def get_date(self,link):
        self.driver.get(link)
        self.driver_wait(lambda e: len(e.window_handles) > 1)
        self.driver_wait(EC.presence_of_element_located((By.CSS_SELECTOR,'[data-test-selector="page_NewsPage"]')))
        parsed_date = self.driver.find_element(By.CSS_SELECTOR,'[data-test-selector="newslist_publishdate"]').text.strip()
        parsed_date_obj = datetime.strptime(parsed_date,'%m/%d/%Y')
        self.publish_date = parsed_date_obj.strftime('%Y-%m-%d')
        return parsed_date_obj
            

    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source': 'Tecumseh',
            'Type': 'Company News',
            'Title': title,
            'Summary': summary,
            'Link': link
            }
        )

    def driver_wait(self,condition):
        try:
            return WebDriverWait(self.driver,10).until(condition)
        except:
            pass
    
    def scrape(self):
        self.get_soup()

all_news = []
def get_tecumseh(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://www.tecumseh.com/NewsAndEvents/News'
    news = TecumsehNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df = df.drop_duplicates(subset=['Link'])
    df.to_csv('csv/tecumseh_news.csv',index=False)