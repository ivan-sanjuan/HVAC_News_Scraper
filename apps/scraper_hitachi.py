from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException, NoSuchWindowException
from selenium.webdriver.common.keys import Keys
from dateutil.parser import parse
import re
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
import pandas as pd
import time

class HitachiNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)

    def get_soup(self):
        print(f'📰Opening: Hitachi')
        self.driver.get(self.url)
        time.sleep(5)
        self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'container')))
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_blocks = soup.find_all('div',class_='news-card')
        self.get_news(news_blocks)
    
    def get_news(self,blocks):
        for news in blocks:
            try:
                time.sleep(3)
                parsed_date = news.find('div',class_='news-card__date').text.strip()
                parsed_date = self.clean_date(parsed_date)
                link = news.find('a').get('href')
                if parsed_date >= self.date_limit:
                    self.driver.switch_to.new_window('tab')
                    self.driver.get(link)
                    self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'detail__content')))
                    html = self.driver.page_source
                    soup = BeautifulSoup(html,'html.parser')
                    title = soup.find('h1',class_='title--title3').text.strip()
                    paragraphs = soup.find_all('p')
                    summary = None
                    for p in paragraphs:
                        para = p.text.strip()
                        if len(para) > 200:
                            summary = para
                            break
                    if not summary:
                        summary = 'Unable to parse summary, please visit the news page instead.'
                    self.driver.close()
                    handles = self.driver.window_handles
                    if handles:
                        self.driver.switch_to.window(handles[0])
                    else:
                        print("No window handles found. Possibly redirected or closed.")
                    self.append(parsed_date,title,summary,link)
                    
            except Exception as e:
                print(f'An error has occured: {e}')

    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source': 'Hitachi AC',
            'Type':'Company News',
            'Title': title,
            'Summary': summary,
            'Link':link
            }
        )
    
    def clean_date(self,date_str):
        parsed_date = parse(date_str,fuzzy=True)
        return parsed_date

    def driver_wait(self,condition):
        try:
            return WebDriverWait(self.driver,10).until(condition)
        except:
            pass
    
    def scrape(self):
        self.get_soup()

all_news = []
def get_hitachi(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://www.hitachiaircon.com/newsroom/en/news'
    news = HitachiNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/hitachi_news.csv',index=False)