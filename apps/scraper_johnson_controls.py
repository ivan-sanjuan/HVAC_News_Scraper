from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime
from urllib.parse import urljoin
from dateutil.parser import parse
import datefinder
import pandas as pd
import time

class JohnsonControlsNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage_days = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage_days)
        self.root = 'https://www.johnsoncontrols.com/'
    
    def get_soup(self):
        print(f'📰Opening: Johnson Controls')
        self.driver.get(self.url)
        popup = self.driver_wait(EC.element_to_be_clickable((By.LINK_TEXT,'Accept All')))
        if popup:
            print(f'Cookie pop-up closed.')
            self.driver.execute_script("arguments[0].click();",popup)
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        links = soup.find_all('a')
        for url in links:
            url = url.get('href')
            if url and url.startswith('https://www.johnsoncontrols.com/media-center/news/press-releases/'):
                link = urljoin(self.root,url)
                status = self.get_news(link)
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                if status == False:
                    break
                
    def get_news(self,link):
        try:
            self.driver.switch_to.new_window('tab')
            self.driver.get(link)
            time.sleep(10)
            self.driver_wait(EC.presence_of_element_located((By.ID,'content')))
            html = self.driver.page_source
            soup = BeautifulSoup(html,'html.parser')
            date_block = soup.find('div',class_='universalrichtext-text')
            parsed_date = self.clean_date(date_block)
            paragraphs = soup.find_all('p')
            title = soup.find('h1').text.strip()
            summary = None
            for p in paragraphs:
                para = p.text.strip()
                if len(para) > 250:
                    summary = para
                    break
            if not summary:
                summary = 'Unable to parse summary, please visit the news page instead.'
            if parsed_date <= self.date_limit:
                return False
            self.append(parsed_date,title,summary,link)
            return True
        except Exception as e:
            print(f'An error has occured: {e}')
    
    def clean_date(self,date_block):
        try:
            block = date_block.find('strong').text.strip()
            parsed_date = parse(block,fuzzy=True)
        except:
            block = date_block.find_all('span',class_='legendSpanClass')[1].text.strip()
            parsed_date = parse(block,fuzzy=True)
        return parsed_date
    
    def driver_wait(self,condition):
        try:
            return WebDriverWait(self.driver,5).until(condition)
        except:
            pass
        
    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source':'Johnson Controls',
            'Type':'Company News',
            'Title':title,
            'Summary':summary,
            'Link':link
            }
        )
    
    def scrape(self):
        self.get_soup()
        
all_news = []
def get_johnsonControls_news(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://www.johnsoncontrols.com/media-center/news#sort=%40insightdate%20descending'
    news = JohnsonControlsNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df = df.drop_duplicates(subset=['Link'])
    df.to_csv('csv/johnson_controls_news.csv',index=False)