from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
from urllib.parse import urljoin
import pandas as pd
import time

class RefIndustryNews:
    def __init__(self,driver,coverage_days,news_url):
        self.driver = driver
        self.coverage = coverage_days
        self.news_url = news_url
        self.latest_news = []
        self.page_num = 1
        self.today = datetime.today()
        self.yesterday = datetime.today()-timedelta(days=1)
        self.date_limit = self.today-timedelta(days=self.coverage)
        self.root = 'https://refindustry.com/'
        
    def get_soup(self):
        while True:
            try:
                if self.page_num == 1:
                    self.driver.get(self.news_url)
                else:
                    try:
                        cookie_accept = self.driver_wait(EC.element_to_be_clickable((By.CLASS_NAME, 'ok')))
                        self.driver.execute_script("arguments[0].click();",cookie_accept)
                        print('Cookies Accepted.')
                    except:
                        print('No cookie block found.')
                    self.next_page()
                self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'posts_new')))
                html = self.driver.page_source
                soup = BeautifulSoup(html,'html.parser')
                article_section = soup.find('div',class_='posts_new')
                self.article_blocks = article_section.find_all('a', class_='_post_news_status')
                if not self.get_news():
                    break
                self.page_num += 1
            except Exception as e:
                print(f'An error has occured: {e}')
            
    def next_page(self):
        element = self.driver_wait(EC.element_to_be_clickable((By.XPATH, f"//div[@onclick='goToPage({self.page_num})']")))
        print(f'RefIndustry News, Page: {self.page_num}')
        self.driver.execute_script("arguments[0].click();",element)

    def get_news(self):
        for news in self.article_blocks:
            parsed_date = news.find('div',class_='post_bot_text').text.strip()
            if parsed_date == 'today':
                parsed_date_obj = self.today
            elif parsed_date == 'yesterday':
                parsed_date_obj = self.yesterday
            else:
                parsed_date_obj = datetime.strptime(parsed_date,'%d %b %Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj < self.date_limit:
                return False
            title = news.find('div',class_='post_title').text.strip()
            summary = news.find('div',class_='post_descr').text.strip()
            link = news.get('href')
            link = urljoin(self.root,link)
            self.append(publish_date,title,summary,link)
        return True
    
    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source': 'RefIndustry',
            'Type': 'Industry News',
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
        
    def scrape(self):
        self.get_soup()

all_news = []
def get_refindustry_news(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://refindustry.com/news/'
    news = RefIndustryNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df = df.drop_duplicates(subset=['Link'])
    df.to_csv('csv/ref_industry_news.csv', index=False)
