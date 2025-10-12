from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
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
    
    def prepare_page(self):
        print(f'📰Opening: Honeywell')
        self.driver.get(self.url)
        WebDriverWait(self.driver,5).until(EC.presence_of_element_located((By.ID,'swiftype-result')))
        time.sleep(5)
        news_date = self.driver.find_elements(By.CLASS_NAME,'search-result-details__doc-type')
        dates_list = []
        try:
            for dates in news_date:
                publish_date = dates.text
                publish_date_obj = datetime.strptime(publish_date[:10],'%Y-%m-%d')
                dates_list.append(publish_date_obj)
        finally:
            if min(dates_list) > self.today-timedelta(days=self.coverage_days):
                load_more = WebDriverWait(self.driver,10).until(EC.element_to_be_clickable((By.ID,'load-more')))
                self.driver.execute_script("arguments[0].scrollIntoView();", load_more)
                load_more.click()
            else:
                pass
                
    def get_soup(self):
        time.sleep(3)
        WebDriverWait(self.driver,5).until(EC.presence_of_element_located((By.CLASS_NAME,'mb-3')))
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_section = soup.find('div',id='swiftype-search-results-v2')
        self.news_blocks = news_section.find_all('div',class_='mb-3')
        
    def get_news(self):
        for news in self.news_blocks:
            publish_date = news.find('div',class_='search-result-details__doc-type').text.strip()
            publish_date_obj = datetime.strptime(publish_date[:10],'%Y-%m-%d')
            if publish_date_obj >= self.today-timedelta(days=self.coverage_days):
                title_section = news.find('a',class_='result-name')
                title = title_section.text.strip()
                link = title_section.get('href')
                summary = news.find('div',class_='search-result-details__result-description').text.strip()
                self.latest_news.append(
                    {
                    'PublishDate': publish_date_obj,
                    'Source': 'Honeywell',
                    'Type': 'Company News',
                    'Title': title,
                    'Summary': summary,
                    'Link': link
                    }
                )
        
    def scrape(self):
        self.prepare_page()
        self.get_soup()
        self.get_news()
        
all_news = []
def get_honeywell_news(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://www.honeywell.com/us/en/press?tab=View+All'
    news = HoneywellNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/honeywell_news.csv',index=False)
  
options = Options()
options.add_argument('--headless=new')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920x1080')
options.add_argument('--log-level=3')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H321 Safari/600.1.4")
options.page_load_strategy = 'eager'
driver = webdriver.Chrome(options=options)
get_honeywell_news(driver,coverage_days=15)

time.sleep(5)
driver.quit()