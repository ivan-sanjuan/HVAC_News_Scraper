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

class RheemNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        
    def get_soup(self):
        self.driver.get(self.url)
        self.driver_wait(EC.presence_of_all_elements_located((By.CLASS_NAME,'rmc-blog__item')))
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_blocks = soup.find_all('a',class_='rmc-blog__item')
        self.get_news(news_blocks)
    
    def get_news(self,blocks):
        for news in blocks:
            parsed_date = news.find('div',class_='rmc-story__content__actions').get_text(strip=True)
            parsed_date_obj = datetime.strptime(parsed_date,'%B %d, %Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj >= self.date_limit:
                link = news.get('href')
                self.driver.switch_to.new_window('tab')
                self.driver.get(link)
                self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'rmc-blog__article_preview__content-wrapper')))
                html = self.driver.page_source
                soup = BeautifulSoup(html,'html.parser')
                title = soup.find('h1',class_='rmc-ty-display-sm').get_text(strip=True)
                paragraphs = soup.find_all('p')
                summary = None
                for p in paragraphs:
                    para = p.get_text(strip=True)
                    if len(para) > 200:
                        summary = para
                        break
                if not summary:
                    summary = 'Unable to parse summary, please visit the news page instead.'
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                self.append(publish_date,title,summary,link)
        
    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source': 'Rheem',
            'Type': 'Company News',
            'Title': title,
            'Summary': summary,
            'Link': link
            }
        )

    def driver_wait(self,condition):
        try:
            return WebDriverWait(self.driver,3).until(condition)
        except:
            pass
    
    def scrape(self):
        self.get_soup()

all_news = []
def get_rheem(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://www.rheem.com/about/news-releases/'
    news = RheemNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/rheem_news.csv',index=False)

options = Options()
# options.add_argument('--headless=new')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920x1080')
options.add_argument('--log-level=3')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115 Safari/537.36")
driver = webdriver.Chrome(options=options)
get_rheem(driver,coverage_days=360)

time.sleep(10)
driver.quit()