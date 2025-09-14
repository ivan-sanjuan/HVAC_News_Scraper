from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException, NoSuchWindowException
from selenium.webdriver.common.keys import Keys
import re
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
import pandas as pd
import time
import pyautogui
import pyperclip

class LGElectronicsNA:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)

    def get_soup(self):
        self.driver.get(self.url)
        self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'notice-list')))
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_section = soup.find('ul',class_='notice-list')
        news_blocks = news_section.find_all('li',class_='list')

    def get_news(self,blocks):
        for news in blocks:
            parsed_date = news.find('p',class_='date').text.strip()
            parsed_date_obj = datetime.strptime(parsed_date,'%m/%d/%Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj >= self.date_limit:
                
    def open_in_new_tab(self,button):
        
    def driver_wait(self,condition):
        try:
            WebDriverWait(self.driver,5).until(condition)
        except:
            pass
        
    def scrape(self):
        self.get_soup()

all_news = []
def get_LG_Electronics_NA(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = "https://www.lg.com/us/press-release"
    news = LGElectronicsNA(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/LG_Electronics_NA.csv',index=False)
    
options = Options()
# options.add_argument('--headless=new')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920x1080')
options.add_argument('--log-level=3')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115 Safari/537.36")
options.page_load_strategy = 'eager'
driver = webdriver.Chrome(options=options)
get_LG_Electronics_NA(driver,coverage_days=120)

time.sleep(10)
driver.quit()