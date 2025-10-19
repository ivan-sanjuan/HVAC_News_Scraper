from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
from urllib.parse import urljoin
import pandas as pd
import time

class DeltaTrakNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        self.root = 'https://deltatrak.com/'
    
    def get_soup(self):
        print(f'📰Opening: DeltaTrak')
        self.driver.get(self.url)
        self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'container')))
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_blocks = soup.find_all('div',class_='News-container')
        news_blocks_sel = self.driver.find_elements(By.CLASS_NAME,'News-container')
        self.get_news(news_blocks,news_blocks_sel)

    def get_news(self,bs4_block,sel_block):
        for news, sect in zip(bs4_block,sel_block):
            parsed_date = news.find('p',class_='date').text.strip()
            parsed_date_obj = datetime.strptime(parsed_date,'%B %d %Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj >= self.date_limit:
                driver_link = sect.find_element(By.CLASS_NAME,'News-link')
                self.driver.execute_script("arguments[0].scrollIntoView();",sect)
                link = news.find('a',class_='News-link').get('href')
                link = urljoin(self.root,link)
                before_tabs = self.driver.window_handles
                self.open_in_new_tab(driver_link)
                self.driver.switch_to.window(self.driver.window_handles[1])
                self.driver_wait(lambda d: len(d.window_handles) > len(before_tabs))
                news = self.extract_page_soup()
                title = news['title']
                summary = news['summary']
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                self.append(publish_date,title,summary,link)

    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source': 'DeltaTrak',
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
    
    def open_in_new_tab(self,driver_link):
        ActionChains(self.driver)\
            .key_down(Keys.CONTROL)\
            .click(driver_link)\
            .key_up(Keys.CONTROL)\
            .perform()
            
    def extract_page_soup(self):
        self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'container')))
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        title = soup.find('div',class_='news-detail-header').text.strip()
        summary = soup.find('p',class_='1stpara').text.strip()
        return ({'title':title,'summary':summary})

    def scrape(self):
        self.get_soup()

all_news = []
def get_delta_trak_news(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url='https://deltatrak.com/about-us/news-and-insights/'
    news = DeltaTrakNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df = df.drop_duplicates(subset=['Link'])
    df.to_csv('csv/deltatrak_news.csv',index=False)
    
options = Options()
# options.add_argument('--headless=new')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920x1080')
options.add_argument('--log-level=3')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H321 Safari/600.1.4")
options.page_load_strategy = 'eager'
driver = webdriver.Chrome(options=options)
get_delta_trak_news(driver,coverage_days=365)

time.sleep(5)
driver.quit()