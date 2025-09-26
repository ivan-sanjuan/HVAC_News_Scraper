from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime
import pandas as pd
import time


class ViessmannNews:
    def __init__(self,driver,coverage_days,news_url):
        self.driver = driver
        self.coverage_days = coverage_days
        self.news_url = news_url
        self.latest_news = []
        self.today = datetime.today()
        self.page_num = 1

    def get_soup(self):
        print(f'📰Opening: Viessmann')
        self.driver.get(self.news_url)
        try:
            button = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="uc-accept-all-button"]')
            self.driver.execute_script("arguments[0].click();", button)
            WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="uc-accept-all-button"]'))
            ).click()
            print('Accepted cookies.')
        except:
            print('No cookie pop-up detected.')
        
        try:
            WebDriverWait(self.driver,5).until(
                EC.presence_of_element_located((By.CLASS_NAME,'vic-m-page-overview__results'))
            )
        except:
            pass
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_block = soup.find('div',class_='vic-m-page-overview__results')
        self.news_list = news_block.find_all('div',class_='vic-m-search-result-teaser')
        
    def get_news(self):
        for news in self.news_list:
            parsed_date = news.find('span',class_='vic-m-search-result-teaser__date').text.strip()
            parsed_date_obj = datetime.strptime(parsed_date,'%B %d, %Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj > self.today-timedelta(days=self.coverage_days):
                title_block = news.find('a',class_='vic-m-search-result-teaser__headline-link')
                title = title_block.find('h3',class_='vic-m-search-result-teaser__headline').text.strip()
                link = title_block.get('href')
                summary = news.find('p',class_='vic-m-search-result-teaser__text').text.strip()
                self.latest_news.append(
                    {
                    'PublishDate': publish_date,
                    'Source': 'Viessmann',
                    'Type': 'Company News',
                    'Title': title,
                    'Summary': summary,
                    'Link': link
                    }
                )
    
    def scrape(self):
        self.get_soup()
        self.get_news()

all_news = []
def get_viessmann_news(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://www.viessmann-climatesolutions.com/en/newsroom.html'
    news = ViessmannNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/viessman_news.csv', index=False)
    

