from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException, NoSuchWindowException
from selenium.webdriver.common.keys import Keys
import re
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
import pandas as pd
import time

class AtmosZeroNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        
    def get_soup(self):
        print(f'📰Opening: Atmos Zero')
        self.driver.get(self.url)
        self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'elementor-widget-container')))
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_blocks = soup.find_all('div',{'data-elementor-type':'loop-item'})
        self.get_news(news_blocks)

    def get_news(self,blocks):
        for news in blocks:
            try:
                parsed_date = news.find('div',class_='date-change')
                if parsed_date:
                    parsed_date = parsed_date.find('p',class_='elementor-size-default').get_text(strip=True)
                    parsed_date_obj = datetime.strptime(parsed_date,'%B %d, %Y')
                    publish_date = parsed_date_obj.strftime('%Y-%m-%d')
                    link = news.find('a').get('href')
                    if parsed_date_obj >= self.date_limit:
                        if link.startswith('https://atmoszero.energy/press-release/'):
                            self.driver.switch_to.new_window('tab')
                            self.driver.get(link)
                            self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'site-main')))
                            html = self.driver.page_source
                            soup = BeautifulSoup(html,'html.parser')
                            title = soup.find('h1',class_='elementor-heading-title').get_text(strip=True)
                            paragraphs = soup.find_all('p')
                            summary = None
                            for p in paragraphs:
                                para = p.get_text(strip=True)
                                if len(para) > 200:
                                    summary = para
                                    break
                            if not summary:
                                summary = 'Unable to parse summary, please visit the news page instead.'
                            self.driver.close()
                            self.driver.switch_to.window(self.driver.window_handles[0])
                        else:
                            title = news.find('div',{'data-widget_type':'text-editor.default'}).get_text(strip=True)
                            summary = 'Article leads to a 3rd-Party site, please visit the news page instead.'
                        self.append(publish_date,title,summary,link)
            except Exception as e:
                print(f'An error has occured: {e}')

    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source': 'AtmosZero',
            'Type': 'Company News',
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
def get_atmoszero(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://atmoszero.energy/newsroom/'
    news = AtmosZeroNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/atmoszero_news.csv',index=False)