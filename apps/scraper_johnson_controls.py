from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime
from urllib.parse import urljoin
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
            if url and url.startswith('/media-center/news/press-releases/'):
                link = urljoin(self.root,url)
                status = self.get_news(link)
                if status == False:
                    break
    
    def get_news(self,link):
        try:
            self.driver.switch_to.new_window('tab')
            self.driver.get(link)
            self.driver_wait(EC.presence_of_element_located((By.ID,'content')))
            html = self.driver.page_source
            soup = BeautifulSoup(html,'html.parser')
            paragraphs = soup.find_all('p')
            title = soup.find('h1').text.strip()
            summary = None
            for p in paragraphs:
                para = p.text.strip()
                if len(para) > 250:
                    summary = para
                    parsed_date = self.clean_date(para)
                    break
            if not summary:
                summary = 'Unable to parse summary, please visit the news page instead.'
            if parsed_date <= self.date_limit:
                return False
            self.append(parsed_date,title,summary,link)
            return True
        except Exception as e:
            print(f'An error has occured: {e}')
        finally:
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
    
    def clean_date(self,date_str):
        matches = datefinder.find_dates(date_str)
        parsed_date = list(matches)
        for text in parsed_date:
            print(text)
    
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
    df.to_csv('csv/johnson_control_news.csv',index=False)

options = Options()
# options.add_argument('--headless=new')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920x1080')
options.add_argument('--log-level=3')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115 Safari/537.36")
options.page_load_strategy = 'eager'
driver = webdriver.Chrome(options=options)
get_johnsonControls_news(driver,coverage_days=15)

driver.quit()
time.sleep(10)