from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
import pandas as pd
import time

class ThermokingNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage_days = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage_days)
    
    def get_soup(self):
        print(f'📰Opening: ThermoKing')
        self.driver.get(self.url)
        WebDriverWait(self.driver,5).until(EC.presence_of_element_located((By.CLASS_NAME,'newspromo__content')))
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_section = soup.find('div',class_='newspromo__content')
        self.news_blocks = news_section.find_all('div',class_='newspromo__promo')

    def get_news(self):
        for news in self.news_blocks:
            parsed_date = news.find('p',class_='newspromo__date').text.strip()
            parsed_date_obj = datetime.strptime(parsed_date,'%B %d, %Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj >= self.date_limit:
                title = news.find('p',class_='newspromo__title').text.strip()
                link_segment = news.find('a',class_='newspromo__link').get('href')
                root_url = 'https://www.thermoking.com'
                summary = news.find('div',class_='newspromo__description').text.strip()
                self.latest_news.append(
                    {
                    'PublishDate':publish_date,
                    'Source': 'ThermoKing',
                    'Type': 'Company News',
                    'Title': title,
                    'Summary': summary,
                    'Link': f'{root_url}{link_segment}'
                    }
                )
    
    def scrape(self):
        self.get_soup()
        self.get_news()
            

all_news=[]
def get_thermoking(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url='https://www.thermoking.com/na/en/newsroom.html'
    news = ThermokingNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/thermoking_news.csv',index=False)

