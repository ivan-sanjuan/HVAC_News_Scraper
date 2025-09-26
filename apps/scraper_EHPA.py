from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
from urllib.parse import urljoin
import pandas as pd
import time

class EHPANews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        self.page_num = 1
        self.root = 'https://www.ehpa.org/'
    
    def get_summary(self):
        self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'elementor-widget-container')))
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        paragraphs = soup.find_all('p')
        summary = None
        for p in paragraphs:
            para = p.text.strip()
            if len(para) > 200:
                summary = para
                break
        if not summary:
            summary = 'Unable to parse summary, please visit the news page instead.'
        return summary
        
                
    def get_soup(self):
        print(f'📰Opening: EHPA')
        self.driver.get(self.url)
        try:
            print('Waiting for the cookie pop-up.')
            cookies = self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'cky-btn-accept')))
            if cookies:
                self.driver.execute_script("argumens[0].click();",cookies)
                print('Accepted cookies.')
        except:
            print("Cookie pop-up did not show up.")
            pass
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_section = soup.find('div',class_='jet-listing-grid')
        news_block = news_section.find_all('div',class_='jet-equal-columns')
        news_block_sel = self.driver.find_elements(By.CLASS_NAME,'jet-equal-columns')
        self.get_news(news_block,news_block_sel)

    def get_news(self,bs4_blocks,sel_blocks):
        for news, section in zip(bs4_blocks,sel_blocks):
            parsed_date = news.find('div',class_='elementor-widget-heading').get_text(strip=True)
            parsed_date_obj = datetime.strptime(parsed_date,'%d %b %Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj >= self.date_limit:
                self.driver.execute_script("arguments[0].scrollIntoView();",section)
                link = news.find('div',class_='elementor-widget-image').find('div').find('a').get('href')
                link = urljoin(self.root,link)
                title = news.find('div',class_='title-block-card').text.strip()
                self.driver.switch_to.new_window('tab')
                self.driver.get(link)
                summary = self.get_summary()
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                self.append(publish_date,title,summary,link)

    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source': 'EHPA',
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
def get_EHPA(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url='https://www.ehpa.org/news-and-resources/'
    news=EHPANews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df = df.drop_duplicates(subset=['Link'])
    df.to_csv('csv/ehpa_news.csv',index=False)