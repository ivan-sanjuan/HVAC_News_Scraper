from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from dateutil.parser import parse
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime
import pandas as pd
import time

class HoneywellNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage_days = coverage_days
        self.url = url
        self.today = datetime.today()
        self.latest_news = []
    
    def get_soup(self):
        print(f'📰Opening: Honeywell')
        self.driver.get(self.url)
        self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'root')))
        time.sleep(10)
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_blocks = soup.find_all('div',class_='center-top')
        self.get_news(news_blocks)
    
    def get_news(self,blocks):
        for news in blocks:
            parsed_date = news.find('div',{'data-property':'articlepublicationdate'}).text.strip()
            parsed_date = self.clean_date(parsed_date)
            publish_date = parsed_date.strftime('%Y-%m-%d')
            print(publish_date)
        
    def clean_date(self,date_str):
        parsed_date = parse(date_str,fuzzy=True)
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
            'PublishDate': publish_date,
            'Source': 'Honeywell',
            'Type': 'Company News',
            'Title': title,
            'Summary': summary,
            'Link': link
            }
        )
        
    def scrape(self):
        self.get_soup()
        
all_news = []
def get_honeywell_news(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://www.honeywell.com/us/en/press?tab=View+All'
    news = HoneywellNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df = df.drop_duplicates(subset=['Link'])
    df.to_csv('csv/honeywell_news.csv',index=False)
  
options = Options()
options.add_argument('--headless=new')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920x1080')
options.add_argument('--log-level=3')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H321 Safari/600.1.4")
# options.page_load_strategy = 'eager'
driver = webdriver.Chrome(options=options)
get_honeywell_news(driver,coverage_days=15)

time.sleep(5)
driver.quit()