from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime
import pandas as pd
import re

class CoolingPostNews:
    def __init__(self, news_link, coverage_days, driver, name, source):
        self.news_link = news_link
        self.coverage_days = coverage_days
        self.driver = driver
        self.soup = None
        self.news_block = []
        self.latest_news = []
        self.page_num = 1
        self.conditions_met = False
        self.today = date.today()
        self.name = name
        self.source = source
    
    def get_soup(self):
        try:
            while True:
                url = self.news_link if self.page_num == 1 else f'https://www.coolingpost.com/{self.name}/page/{self.page_num}/'
                self.driver.get(url)
                WebDriverWait(self.driver,timeout=5).until(
                    EC.presence_of_element_located((By.ID,'main-content'))
                )
                html = self.driver.page_source
                self.soup = BeautifulSoup(html,'html.parser')
                if not self.get_news_blocks():
                    break
                self.page_num+=1
                print(f'CoolingPost News, Page: {self.page_num}')
        except Exception as e:
            print(f'An error has occured: {e}')
        
    def get_news_blocks(self):
        news_section = self.soup.find('div', id='main-content')
        news_blocks = news_section.find_all('div', class_='cl-element-section')
        print(f'Getting {self.source}')
        for news in news_blocks:
            parsed_date = news.find('div', class_='cl-element-published_date').text
            parsed_date_obj = datetime.strptime(re.sub(r'(\d+)(st|nd|rd|th)', r'\1', parsed_date), '%d %B %Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj.date() < self.today-timedelta(days=self.coverage_days):
                return False
            self.title = news.find('a', class_='cl-element-title__anchor')
            self.link = self.title.get('href')
            self.summary = news.find('div', class_='cl-element-excerpt')
            self.latest_news.append(
                {
                'PublishDate': publish_date,
                'Source': self.source,
                'Type': 'Industry News',
                'Title': self.title.text.strip(),
                'Summary': self.summary.text.strip(),
                'Link': self.link
                }
            )
        return True
                
    def scrape(self):
        self.get_soup()

all_news = []        
def get_cooling_post_news(driver, coverage_days):
    world = 'https://www.coolingpost.com/world-news/'
    uk = 'https://www.coolingpost.com/uk-news/'
    products = 'https://www.coolingpost.com/products/'
    features = 'https://www.coolingpost.com/features/'
    blog = 'https://www.coolingpost.com/blog/'
    train_events = 'https://www.coolingpost.com/training/'
    world_news = CoolingPostNews(world,coverage_days, driver,'world-news','CoolingPost-World')
    uk_news = CoolingPostNews(uk,coverage_days,driver,'uk-news','CoolingPost-UK')
    product_news = CoolingPostNews(products,coverage_days,driver,'products','CoolingPost-Products')
    feature_news = CoolingPostNews(features,coverage_days,driver,'features','CoolingPost-Features')
    blog_news = CoolingPostNews(blog,coverage_days,driver,'blog','CoolingPost-Blog')
    train_events_news = CoolingPostNews(train_events,coverage_days,driver,'training','CoolingPost-T&E')
    world_news.scrape()
    uk_news.scrape()
    product_news.scrape()
    feature_news.scrape()
    blog_news.scrape()
    train_events_news.scrape()
    all_news.extend(world_news.latest_news)
    all_news.extend(uk_news.latest_news)
    all_news.extend(product_news.latest_news)
    all_news.extend(blog_news.latest_news)
    all_news.extend(train_events_news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/cooling_post_news.csv', index=False)
    
    return all_news
