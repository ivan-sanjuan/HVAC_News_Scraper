from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime
import pandas as pd

class CopelandNews:
    def __init__(self,driver,coverage_days,news_url,source):
        self.driver = driver
        self.coverage_days = coverage_days
        self.news_url = news_url
        self.source = source
        self.today = datetime.today()
        self.latest_news = []

    def get_soup(self):
        self.driver.get(self.news_url)
        print(f'Getting {self.source}')
        try:
            accept_cookies = WebDriverWait(self.driver,10).until(
                EC.element_to_be_clickable((By.ID,'onetrust-accept-btn-handler'))
            )
            accept_cookies.click()
            print('Accepted cookies.')
        except:
            print('No cookie pop-up found.')
            pass
        try:
            WebDriverWait(self.driver,10).until(
                EC.presence_of_element_located((By.CLASS_NAME,'ddl-carousel__container'))
            )
        except:
            pass
        html = self.driver.page_source
        self.soup = BeautifulSoup(html,'html.parser')
        news_section = self.soup.find('div',class_='ddl-carousel__container')
        self.news_blocks = news_section.find_all('div',class_='ddl-carousel__slide')
        
    def get_news(self):
        for news in self.news_blocks:
            parsed_date = news.find('div',class_='ddl-card__date').text.strip().split(maxsplit=1)[1]
            parsed_date_obj = datetime.strptime(parsed_date,'%b %d %Y')
            self.publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj > self.today-timedelta(days=self.coverage_days):
                heading = news.find('a', class_='ddl-card__heading')
                self.title = heading.text.strip()
                self.link = heading.get('href')
                self.summary = news.find('div', class_='ddl-card__description').find('p').text.strip()
                root_url = 'https://www.copeland.com'
                self.latest_news.append(
                    {
                    'PublishDate': self.publish_date,
                    'Source': self.source,
                    'Type': 'Company News',
                    'Title': self.title,
                    'Summary': self.summary,
                    'Link': f'{root_url}{self.link}'
                    }
                )
                
            # print(self.latest_news)
        
    def scrape(self):
        self.get_soup()
        self.get_news()

all_news = []
def get_copeland_news(driver, coverage_days):
    driver.set_window_size(1920, 1080)
    url_us = 'https://www.copeland.com/en-us/news'
    url_asia = 'https://www.copeland.com/en-sg/news'
    src_us = 'Copeland-US'
    src_asia = 'Copeland-Asia'
    news_us = CopelandNews(driver,coverage_days,url_us,src_us)
    news_asia = CopelandNews(driver,coverage_days,url_asia,src_asia)
    news_us.scrape()
    news_asia.scrape()
    all_news.extend(news_us.latest_news)
    all_news.extend(news_asia.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/copeland_news.csv', index=False)
    
    return all_news
    
    
# options = Options()
# # options.add_argument('--headless=new')
# options.add_argument('--disable-gpu')
# options.add_argument('--window-size=1920x1080')
# options.add_argument('--log-level=3')
# options.add_argument("--disable-blink-features=AutomationControlled")
# options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115 Safari/537.36")
# driver = webdriver.Chrome(options=options)
# get_copeland_news(driver,coverage_days=90)