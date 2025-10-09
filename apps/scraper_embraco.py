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

class EmbracoNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        
    def get_soup(self):
        print(f'📰Opening: Embraco')
        self.driver.get(self.url)
        self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'col1')))
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_section = soup.find('div',class_='col1')
        news_blocks = news_section.find_all('a',class_='type-post')
        self.get_news(news_blocks)

    def get_news(self,blocks):
        for news in blocks:
            parsed_date = news.find('time',class_='entry-date').text.strip()
            parsed_date_obj = datetime.strptime(parsed_date,'%m/%d/%Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj >= self.date_limit:
                link = news.get('href')
                title = news.find('h4').text.strip()
                self.driver.switch_to.new_window('tab')
                self.driver.get(link)
                self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'col1')))
                html = self.driver.page_source
                soup = BeautifulSoup(html,'html.parser')
                summary_block = soup.find('div',class_='row2')
                paragraphs = summary_block.find_all('p')
                for sum in paragraphs:
                    para = sum.get_text(strip=True)
                    if len(para) > 200:
                        summary = para
                        break
                    else:
                        continue
                else:
                    summary = 'Unable to parse summary, please visit the news page instead.'
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                self.append(publish_date,title,summary, link)

    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source': 'Embraco',
            'Type': 'Company News',
            'Title': title,
            'Summary': summary,
            'Link': link
            }
        )
    
    def driver_wait(self,condition):
        try:
            button = WebDriverWait(self.driver,5).until(condition)
            return button
        except:
            pass
        
    def scrape(self):
        self.get_soup()
        
all_news = []
def get_embraco(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url='https://www.embraco.com/en/news-and-media/'
    news = EmbracoNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/embraco_news.csv',index=False)
    
options = Options()
options.add_argument('--headless=new')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920x1080')
options.add_argument('--log-level=3')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H321 Safari/600.1.4")
options.page_load_strategy = 'eager'
driver = webdriver.Chrome(options=options)
get_climate_control_news(driver,coverage_days=15)