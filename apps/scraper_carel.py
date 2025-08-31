from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
import pandas as pd
import time

class CarelNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage_days = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage_days)

    def get_soup(self):
        self.driver.get(self.url)
        WebDriverWait(self.driver,5).until(EC.presence_of_element_located((By.CLASS_NAME,'portlet-body')))
        time.sleep(5)
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        self.news_blocks = soup.find_all('div',class_='asset-news-content')

    def get_news(self):
        for news in self.news_blocks:
            parsed_date = news.find('div',class_='news-date').text.strip()
            parsed_date_obj = datetime.strptime(parsed_date,'%d/%m/%Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj >= self.date_limit:
                title_section = news.find('div',class_='news-title')
                title = title_section.find('a').text.strip()
                link = title_section.find('a').get('href')
                summary = news.find('div',class_='news-summary').find('a').text.strip()
                self.latest_news.append(
                    {
                    'PublishDate':publish_date,
                    'Source': 'Carel',
                    'Type': 'Company News',
                    'Title': title,
                    'Summary': summary,
                    'Link': link
                    }
                )
    
    def scrape(self):
        self.get_soup()
        self.get_news()
        

all_news=[]
def get_carel(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url='https://www.carel.com/news'
    news = CarelNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/carel_news.csv',index=False)

# options = Options()
# # options.add_argument('--headless=new')
# options.add_argument('--disable-gpu')
# options.add_argument('--window-size=1920x1080')
# options.add_argument('--log-level=3')
# options.add_argument("--disable-blink-features=AutomationControlled")
# options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115 Safari/537.36")
# driver = webdriver.Chrome(options=options)
# get_carel(driver,coverage_days=250)

# time.sleep(10)
# driver.quit()