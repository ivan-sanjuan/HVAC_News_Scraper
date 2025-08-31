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

class DeltaTrakNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
    
    def get_soup(self):
        self.driver.get(self.url)
        WebDriverWait(self.driver,5).until(EC.presence_of_element_located((By.CLASS_NAME,'container')))
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        self.news_blocks = soup.find_all('div',class_='News-container')
        self.news_blocks_sel = self.driver.find_elements(By.CLASS_NAME,'News-container')
        
    def open_in_new_tab(self,driver_link):
        ActionChains(self.driver)\
            .key_down(Keys.CONTROL)\
            .click(driver_link)\
            .key_up(Keys.CONTROL)\
            .perform()
            
    def extract_page_soup(self):
        WebDriverWait(self.driver,5).until(EC.presence_of_element_located((By.CLASS_NAME,'container')))
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        self.title = soup.find('div',class_='news-detail-header').text.strip()
        self.summary = soup.find('p',class_='1stpara').text.strip()

    def get_news(self):
        for news, sect in zip(self.news_blocks,self.news_blocks_sel):
            parsed_date = news.find('p',class_='date').text.strip()
            parsed_date_obj = datetime.strptime(parsed_date,'%B %d %Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj >= self.date_limit:
                driver_link = sect.find_element(By.CLASS_NAME,'News-link')
                self.driver.execute_script("arguments[0].scrollIntoView();",sect)
                link = news.find('a',class_='News-link').get('href')
                self.open_in_new_tab(driver_link)
                self.driver.switch_to.window(self.driver.window_handles[1])
                self.extract_page_soup()
                self.latest_news.append(
                    {
                    'PublishDate':publish_date,
                    'Source': 'DeltaTrak',
                    'Type': 'Company News',
                    'Title': self.title,
                    'Summary': self.summary,
                    'Link': link
                    }
                )
                time.sleep(1)
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                
    
    def scrape(self):
        self.get_soup()
        self.get_news()

all_news = []
def get_delta_trak_news(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url='https://deltatrak.com/about-us/news-and-insights/'
    news = DeltaTrakNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/deltatrak_news.csv',index=False)

options = Options()
# options.add_argument('--headless=new')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920x1080')
options.add_argument('--log-level=3')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115 Safari/537.36")
driver = webdriver.Chrome(options=options)
get_delta_trak_news(driver,coverage_days=100)

time.sleep(10)
driver.quit()