from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd
import threading
import time
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver

class DanfossNews:
    def __init__(self,driver,coverage_days,news_url):
        self.driver = driver
        self.coverage_days = coverage_days
        self.news_url = news_url
        self.interval = 2
        self.today = datetime.today()
        self.latest_news = []
        self.page_num = 1
        
    def popup_watcher(self):
        def watch():
            while True:
                try:
                    pop_up=WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, 'close animatedCloseButton__AV-vN'))
                    )
                    self.driver.execute_script("arguments[0].click();", pop_up)
                    print('Popup dismissed.')
                except NoSuchElementException:
                    pass
                time.sleep(self.interval)
        threading.Thread(target=watch, daemon=True).start()
    
    def goTo_next_page(self):
        next = WebDriverWait(self.driver,5).until(
                    EC.element_to_be_clickable((By.CLASS_NAME,'next-button'))
                )
        next.click()
    
    def get_soup(self):
        print(f'📰Opening: Danfoss')
        while True:
            try:
                if self.page_num == 1:
                    self.driver.get(self.news_url)
                    pop_up = WebDriverWait(self.driver,10).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept')]"))
                        )
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", pop_up)
                    if pop_up:
                        pop_up.click()
                        print('Accepted Cookies.')
                    else:
                        pass
                else:
                    self.goTo_next_page()
                    print(f'Danfoss News, Page:{self.page_num}')
                    
                WebDriverWait(self.driver,5).until(
                    EC.presence_of_element_located((By.CLASS_NAME,'news-list-items'))
                )
                html = self.driver.page_source
                self.soup = BeautifulSoup(html,'html.parser')
                article_section = self.soup.find('ul',class_='news-list-items')
                self.news_blocks = article_section.find_all('div',class_='tile__text')
                if not self.get_news():
                    break
                self.page_num += 1
                
            except Exception as e:
                print(f'Error has occured: {e}')

    def get_news(self):
        for news in self.news_blocks:
            parsed_date = news.find('div',class_='tile__text-details_item').text.split(maxsplit=1)[1].strip()
            parsed_date_obj = datetime.strptime(parsed_date,'%B %d, %Y')
            self.publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj < self.today-timedelta(days=self.coverage_days):
                return False
            self.title = news.find('div',class_='tile__text-title').text.strip()
            self.link = news.find('a',class_='tile__link').get('href')
            summary = news.find('div',class_='tile__text-description')
            if summary:
                self.summary = news.find('div',class_='tile__text-description').find('span').find('p').text.strip()
            else:
                self.summary = 'NO SUMMARY'
            self.root_url = 'https://www.danfoss.com/'
            self.latest_news.append(
                {
                'PublishDate': self.publish_date,
                'Source': 'Danfoss',
                'Type': 'Company News',
                'Title': self.title,
                'Summary': self.summary,
                'Link': f'{self.root_url}{self.link}'
                }
            )
        return True

    def scrape(self):
        self.get_soup()
        

all_news=[]
def get_danfoss_news(driver, coverage_days):
    driver.set_window_size(1920, 1080)
    url='https://www.danfoss.com/en/about-danfoss/news/?pageSize=15&sort=startDate_desc'
    news = DanfossNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/danfoss_news.csv', index=False)
    

