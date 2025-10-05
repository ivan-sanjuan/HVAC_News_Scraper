from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
from urllib.parse import urljoin
from dateutil.parser import parse
import pandas as pd
import requests
import time

class TraneCommercialNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        self.root = 'https://www.trane.com/'
        
    def get_soup(self):
        print(f'📰Opening: Trane - Commercial')
        self.driver.get(self.url)
        time.sleep(20)
        self.driver_wait(EC.presence_of_all_elements_located((By.CLASS_NAME,'HitchhikerProductProminentImage-titleLink')))
        news_blocks = self.driver.find_elements(By.CLASS_NAME,'HitchhikerProductProminentImageClickable-body')
        for block in news_blocks:
            self.driver.execute_script("arguments[0].scrollIntoView();",block)
            time.sleep(0.5)
            link = block.find_element(By.CLASS_NAME,'HitchhikerProductProminentImage-titleLink').get_attribute('href')
            print(link)
            time.sleep(0.5)

        
    def get_news(self,link):
        try:
            self.driver.switch_to.new_window('tab')
            self.driver.get(link)
            self.driver_wait(EC.presence_of_element_located((By.ID,'content')))
            html = self.driver.page_source
            soup = BeautifulSoup(html,'html.parser')
            parsed_date = soup.find('p',class_='story-hero__date').text.strip()
            parsed_date = self.clean_date(parsed_date)
            print(parsed_date)
        except Exception as e:
            print(f'An error has occured: {e}')
        finally:
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])

    def clean_date(self,date_str):
        parsed_date = parse(date_str,fuzzy=False)
        return parsed_date

    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source': 'Trane Commercial',
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

all_news=[]
def get_trane_commercial(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://www.trane.com/commercial/north-america/us/en/about-us/newsroom.html'
    news = TraneCommercialNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/trane_commercial_news.csv',index=False)

options = Options()
# options.add_argument('--headless=new')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920x1080')
options.add_argument('--log-level=3')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115 Safari/537.36")
# options.page_load_strategy = 'eager'
driver = webdriver.Chrome(options=options)
get_trane_commercial(driver,coverage_days=10)

driver.quit()
time.sleep(5)