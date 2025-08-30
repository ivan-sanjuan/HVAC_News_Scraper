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

class BDRthermeaNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage_days = coverage_days
        self.url = url
        self.today = datetime.today()
        self.latest_news = []
    
    def get_soup(self):
        self.driver.get(self.url)
        try:
            accept_cookie = WebDriverWait(self.driver,5).until(EC.element_to_be_clickable((By.ID,'onetrust-accept-btn-handler')))
            accept_cookie.click()
        except Exception as e:
            print(f'An error has occured: {e}')
        WebDriverWait(self.driver,5).until(EC.presence_of_element_located((By.CLASS_NAME,'cards-container')))
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_section = soup.find('div',class_='cards-container')
        self.news_blocks = news_section.find_all('div',class_='rounded-cards')
        
    def get_news(self):
        for news in self.news_blocks:
            parsed_date = news.find('p',class_='card-date').text.strip()
            parsed_date_obj = datetime.strptime(parsed_date,'%d/%m/%Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj >= self.today-timedelta(days=self.coverage_days):
                title = news.find('div',class_='title-container').find('h3').text.strip()
                summary = news.find('div',class_='card-description').text.strip()
                link = news.find('div',class_='card__button-containers').find('a').get('href')
                root_link = 'https://www.bdrthermeagroup.com'
                self.latest_news.append(
                    {
                    'PublishDate': publish_date,
                    'Source': 'BDR Thermea',
                    'Type': 'Company News',
                    'Title': title,
                    'Summary': summary,
                    'Link': f'{root_link}{link}'
                    }
                )
            
    def scrape(self):
        self.get_soup()
        self.get_news()

all_news = []
def get_BDRthermea_news(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://www.bdrthermeagroup.com/stories'
    news = BDRthermeaNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/BDR_Thermea_news.csv',index=False)

