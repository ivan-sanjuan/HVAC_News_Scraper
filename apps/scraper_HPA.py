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
import pyautogui
import pyperclip

class HPANews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)

    def get_soup(self):
        self.driver.get(self.url)
        try:
            time.sleep(5)
            self.close_popup()
        except NoSuchWindowException:
            pass
        self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'et_pb_posts')))
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        section = soup.find('div',class_='et_pb_posts')
        news_blocks = section.find_all('article',class_='et_pb_post')
        self.get_news(news_blocks)
        
    def close_popup(self):
        ActionChains(self.driver)\
            .key_down(Keys.TAB)\
                .key_down(Keys.TAB)\
                    .key_down(Keys.TAB)\
                        .click()\
                            .perform()
        
    def get_news(self,blocks):
        news_list = []
        for news in blocks:
            parsed_date = news.find('span',class_='published').text.strip('')
            parsed_date_obj = datetime.strptime(parsed_date,'%b %d, %Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            title_block = news.find('a',class_='abs-url')
            title = title_block.text.strip()
            link = title_block.get('href')
            if parsed_date_obj >= self.date_limit:
                self.driver.switch_to.new_window('tab')
                self.driver.get(link)
                self.driver_wait(lambda e: len(e.window_handles) > 1)
                self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'et_pb_text_inner')))
                time.sleep(3)
                html = self.driver.page_source
                soup = BeautifulSoup(html,'html.parser')
                summary_block = soup.find('div',class_='et_pb_row')
                # print(summary_block)
                paragraphs = soup.find_all('p')
                summary = None
                for sum in paragraphs:
                    para = sum.text.strip()
                    if len(para) > 150:
                        summary = para
                        break
                if not summary:
                    summary = 'Unable to parse summary, please visit the news page instead.'
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                self.append(publish_date,title,summary,link)
            
    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source': 'HPA News',
            'Type': 'Industry News',
            'Title': title,
            'Summary': summary,
            'Link': link
            }
        )
    
    def driver_wait(self,condition):            
        try:
            WebDriverWait(self.driver,20).until(condition)
        except:
            pass
        
    def scrape(self):
        self.get_soup()

all_news = []
def get_HPA(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://www.heatpumps.org.uk/news-events/'
    news = HPANews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df = df.drop_duplicates(subset=['Link'])
    df.to_csv('csv/hpa_news.csv',index=False) 
    
# options = Options()
# # options.add_argument('--headless=new')
# options.add_argument('--disable-gpu')
# options.add_argument('--window-size=1920x1080')
# options.add_argument('--log-level=3')
# options.add_argument("--disable-blink-features=AutomationControlled")
# options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36")
# options.page_load_strategy = 'eager'
# driver = webdriver.Chrome(options=options)
# get_HPA(driver,coverage_days=60)

# time.sleep(5)
# driver.quit()