from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.window import WindowTypes
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime
import pandas as pd

class RefIndustryNews:
    def __init__(self,driver,coverage_days,news_url):
        self.driver = driver
        self.coverage_days = coverage_days
        self.news_url = news_url
        self.latest_news = []
        self.page_num = 1
        self.today = datetime.today()
        self.yesterday = datetime.today()-timedelta(days=1)
        
    def get_soup(self):
        while True:
            try:
                if self.page_num == 1:
                    self.driver.get(self.news_url)
                    print(f'Accessing: {self.news_url}')
                else:
                    try:
                        cookie_accept = WebDriverWait(self.driver,3).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, 'ok')) 
                        )
                        cookie_accept.click()
                        print('Cookies Accepted.')
                    except:
                        print('No cookie block found.')
                    self.next_page()
                
                WebDriverWait(self.driver,5).until(
                    EC.presence_of_element_located((By.CLASS_NAME,'posts_new'))
                )
                html = self.driver.page_source
                self.soup = BeautifulSoup(html,'html.parser')
                article_section = self.soup.find('div',class_='posts_new')
                self.article_blocks = article_section.find_all('a', class_='_post_news_status')
                if not self.get_news():
                    break
                self.page_num += 1
                
            except Exception as e:
                print(f'An error has occured: {e}')
            
            
    def next_page(self):
        self.element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//div[@onclick='goToPage({self.page_num})']"))
            )
        print(f'Page: {self.page_num}')
        self.element.click()

    def get_news(self):
        for news in self.article_blocks:
            parsed_date = news.find('div',class_='post_bot_text').text.strip()
            if parsed_date == 'today':
                parsed_date_obj = self.today
            elif parsed_date == 'yesterday':
                parsed_date_obj = self.yesterday
            else:
                parsed_date_obj = datetime.strptime(parsed_date,'%d %b %Y')
            self.publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj < self.today-timedelta(days=self.coverage_days):
                return False
            self.title = news.find('div',class_='post_title').text.strip()
            self.summary = news.find('div',class_='post_descr').text.strip()
            self.link = news.get('href')
            self.latest_news.append(
                {
                'PublishDate': self.publish_date,
                'Source': 'Ref Industry',
                'Title': self.title,
                'Summary': self.summary,
                'Link': self.link
                }
            )
        return True
    
        
    def scrape(self):
        self.get_soup()

all_news = []
def get_refindustry_news(driver, coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://refindustry.com/news/'
    news = RefIndustryNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/ref_industry_news.csv', index=False)
    return all_news

