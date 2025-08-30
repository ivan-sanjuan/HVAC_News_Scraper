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
import requests
import json

class TraneCommercial:
    def __init__(self,driver,coverage_days):
        self.driver = driver
        self.coverage_days = coverage_days
        self.latest_news = []
        self.today = datetime.today()

    def fetch_news_from_api(self):
        url = "https://prod-cdn.us.yextapis.com/v2/accounts/me/search/vertical/query"
        params = {
            "experienceKey": "tc-newsroom--en",
            "api_key": "27e22603a683c838c1cb79efe4e5e892",
            "v": "20220511",
            "version": "PRODUCTION",
            "locale": "en",
            "input": "",
            "verticalKey": "newsroom",
            "limit": 21,
            "offset": 0,
            "retrieveFacets": "true",
            "facetFilters": "{}",
            "session_id": "e57dd3b0-9396-464b-b743-91b7753ba094",
            "sessionTrackingEnabled": "true",
            "sortBys": "[]",
            "referrerPageUrl": "",
            "source": "STANDARD",
            "jsLibVersion": "v1.17.9"
        }
        response = requests.get(url,params=params)
        self.data = response.json()

    def get_link(self):
        self.news_links = []
        data = self.data.get('response',{}).get('results',[])
        for news in data:
            item = news.get('data')
            self.publish_date = item.get('c_publishedDate')
            publish_date_obj = datetime.strptime(self.publish_date,'%Y-%m-%d')
            if publish_date_obj >= self.today-timedelta(days=self.coverage_days):
                link = item.get('landingPageUrl')
                self.news_links.append(link)
        return self.news_links
    
    def get_soup(self):
        self.driver.get('https://www.google.com/')
        links = self.get_link()
        for link in links:
            self.driver.switch_to.new_window('tab')
            self.driver.get(link)
            WebDriverWait(self.driver,5).until(EC.presence_of_element_located((By.CLASS_NAME,'featured-article__content')))
            html = self.driver.page_source
            soup = BeautifulSoup(html,'html.parser')
            title = soup.find('h1',class_='featured-article__headline').text.strip()
            print(f'Fetching news: {title}')
            summary_section = soup.find('div',class_='cmp-text')
            p_tag = summary_section.find('p')
            if p_tag:
                summary = soup.find('div',class_='cmp-text').find('p').text.strip()
            else:
                summary = soup.find('div',class_='cmp-text').text.strip()
            self.latest_news.append(
                {
                'PublishDate': self.publish_date,
                'Source': 'Trane-Commercial',
                'Type': 'Company News',
                'Title': title,
                'Summary': summary,
                'Link': link
                }
            )
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            
    def scrape(self):
        self.fetch_news_from_api()
        self.get_soup()

all_news=[]
def get_trane_commercial(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    news = TraneCommercial(driver,coverage_days)
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
driver = webdriver.Chrome(options=options)
get_trane_commercial(driver,coverage_days=124)