from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
import pandas as pd
import time

class EHPANews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        self.page_num = 1
        
    def open_new_tab(self,link):
        ActionChains(self.driver)\
            .key_down(Keys.CONTROL)\
                .click(link)\
                    .key_up(Keys.CONTROL)\
                        .perform()
    
    def get_soup(self):
        self.driver.get(self.url)
        try:
            WebDriverWait(self.driver,5).until(EC.element_to_be_clickable((By.CLASS_NAME,'cky-btn-accept'))).click()
        except:
            pass
        time.sleep(5)
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_section = soup.find('div',class_='jet-listing-grid')
        self.news_block = news_section.find_all('div',class_='jet-listing-grid__items')
        self.news_block_sel = self.driver.find_elements(By.CLASS_NAME,'jet-listing-grid__items')

    def get_news(self):
        for news, section in zip(self.news_block,self.news_block_sel):
            area = section.find_element(By.CLASS_NAME,'elementor-heading-title')
            clickable_area = area.find_element(By.CSS_SELECTOR,'a')
            self.driver.execute_script("arguments[0].click();",section)
            self.open_new_tab(clickable_area)
            # containers = news.find_all('div',class_='elementor-heading-title')
            # print(containers)
            # parsed_date = news.find('div',class_='elementor-heading-title').text.strip()
            # print(parsed_date)
            # parsed_date_obj = datetime.strptime(parsed_date,'%d %b %Y')
            # publish_date = parsed_date_obj.strftime('%Y-%m-%d')
                
    def scrape(self):
        self.get_soup()

def get_EHPA(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url='https://www.ehpa.org/news-and-resources/'
    news=EHPANews(driver,coverage_days,url)
    news.scrape()

options = Options()
# options.add_argument('--headless=new')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920x1080')
options.add_argument('--log-level=3')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115 Safari/537.36")
driver = webdriver.Chrome(options=options)
get_EHPA(driver,coverage_days=20)

time.sleep(10)
driver.quit()