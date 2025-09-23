from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
from urllib.parse import urljoin
import re
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
import pandas as pd
import time

class PHCPprosNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news =[]
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        self.root = 'https://www.phcppros.com/'

    def get_soup(self):
        self.driver.get(self.url)
        self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'records')))
        records = self.driver.find_elements(By.CLASS_NAME,'article-summary')
        print('Scrolling through the news, making sure all articles are loaded.')
        for record in records:
            self.driver.execute_script("arguments[0].scrollIntoView();",record)
            time.sleep(0.5)
        self.get_news(records)
        
    def get_news(self,blocks):
        for news in blocks:
            try:
                parsed_date = news.find_element(By.CLASS_NAME,'article-summary__post-date').get_attribute("textContent")
                parsed_date_obj = datetime.strptime(parsed_date,'%B %d, %Y')
                publish_date = parsed_date_obj.strftime('%Y-%m-%d')
                if parsed_date_obj >= self.date_limit:
                    clickable_link = news.find_element(By.CLASS_NAME,'article-summary__headline').find_element(By.CSS_SELECTOR,'a')
                    self.driver.execute_script("arguments[0].scrollIntoView();",news)
                    link = clickable_link.get_attribute('href')
                    link = urljoin(self.root,link)
                    self.driver.execute_script("arguments[0].scrollIntoView();",clickable_link)
                    self.open_to_new_tab(clickable_link)
                    self.driver_wait(lambda e: len(e.window_handles) > 1)
                    self.driver.switch_to.window(self.driver.window_handles[1])
                    self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'page-articles-show')))
                    html = self.driver.page_source
                    soup = BeautifulSoup(html,'html.parser')
                    title = soup.find('h1',class_='page-articles-show__headline').text.strip()
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
                    self.append(publish_date,link,title,summary)
            except Exception as e:
                print(f'An error has occured: {e}')
                
    def append(self,publish_date,link,title,summary):
        print(f'Fetching: {title}')
        self.latest_news.append(
                {
                'PublishDate':publish_date,
                'Source': 'PHCP Pros',
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
    
    def open_to_new_tab(self,link):
        ActionChains(self.driver)\
            .key_down(Keys.CONTROL)\
                .click(link)\
                    .key_up(Keys.CONTROL)\
                        .perform()
        
    def scrape(self):
        self.get_soup()

all_news = []
def get_PHCP_pros(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://www.phcppros.com/articles/topic/249-hvac'
    news = PHCPprosNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df = df.drop_duplicates(subset=['Link'])
    df.to_csv('csv/phcp_pros_news.csv',index=False)