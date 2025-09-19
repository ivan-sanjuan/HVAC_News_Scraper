from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException, NoSuchWindowException
from selenium.webdriver.common.keys import Keys
from urllib.parse import urljoin
import threading
import re
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
import pandas as pd
import time

class PanasonicNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        self.root = 'https://www.panasonic.com/'
        
    def get_soup(self):
        self.driver.get(self.url)
        self.popup_thread()
        time.sleep(3)
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_section = soup.find('div',class_='sectionContents')
        news_blocks = soup.find_all('div',class_='flexlayoutcomponent')
        self.get_news(news_blocks)
    
    def get_news(self,blocks):
        for news in blocks:
            try:
                parsed_date = news.find('div',class_='richtext').get_text(strip=True)
                parsed_date_obj = datetime.strptime(parsed_date,'%m-%d-%Y')
                publish_date = parsed_date_obj.strftime('%Y-%m-%d')
                if parsed_date_obj >= self.date_limit:
                    link = news.find('div',class_='linklist').find('a').get('href')
                    link = urljoin(self.root,link)
                    title = news.find('div',class_='linklist').find('span',class_='text').get_text(strip=True)
                    self.driver_wait(lambda e: len(e.window_handles) == 1)
                    self.driver.switch_to.new_window('tab')
                    self.driver.get(link)
                    if link.startswith('https://www.panasonic.com/global/hvac/'):
                        self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'parsys')))
                        html = self.driver.page_source
                        soup = BeautifulSoup(html,'html.parser')
                        summary_block = soup.find_all('span',class_='ops-15')
                        summary = None
                        for text in summary_block:
                            para = text.get_text(strip=True)
                            if len(para) > 200:
                                summary = para
                                break
                        if not summary:
                            summary = 'Unable to parse summary, please visit the news page instead.'
                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])
                    elif link.startswith('https://news.panasonic.com/global/press/'):
                        self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'TextItem__body')))
                        html = self.driver.page_source
                        soup = BeautifulSoup(html,'html.parser')
                        summary_block = soup.find('div',class_='TextItem__body')
                        paragraphs = summary_block.find_all('p')
                        summary = None
                        for p in paragraphs:
                            para = p.get_text(strip=True)
                            if len(para) > 200:
                                summary = para
                                break
                        if not summary:
                            summary = 'Unable to parse summary, please visit the news page instead.'
                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])
                    else:
                        summary = 'Unable to parse summary, please visit the news page instead.'
                    self.append(publish_date,title,summary,link)
            except Exception as e:
                print(f'An error has occured: {e}')
    
    def popup_thread(self):
        threading.Thread(
            target=self.popup_watcher,
            daemon=True
        ).start()
    
    def popup_watcher(self):
        while True:
            button = self.driver_wait(EC.element_to_be_clickable((By.ID,'close-pc-btn-handler')))
            if button:
                try:
                    button.click()
                    print('Pop-up found and closed.')
                    time.sleep(2)
                except Exception as e:
                    print(f'Error has occured: {e}')
            time.sleep(1)
        
    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source': 'Panasonic-HVAC',
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
def get_panasonic_hvac(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://www.panasonic.com/global/hvac/news.html'
    news = PanasonicNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/panasonic_hvac_news.csv',index=False)

