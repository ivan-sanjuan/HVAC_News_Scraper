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

class LGElectronicsNA:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)

    def get_soup(self):
        print(f'📰Opening: LG Electronics - NA')
        self.driver.get(self.url)
        self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'notice-list')))
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_section = soup.find('ul',class_='notice-list')
        news_blocks = news_section.find_all('li',class_='list')
        self.get_news(news_blocks)

    def get_news(self,blocks):
        for news in blocks:
            parsed_date = news.find('p',class_='date').text.strip()
            parsed_date_obj = datetime.strptime(parsed_date,'%m/%d/%Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj >= self.date_limit:
                title = news.find('div',class_='head-title').find('a').get_text(strip=True)
                button = self.driver.find_element(By.PARTIAL_LINK_TEXT,f'{title}')
                link = button.get_attribute('href')
                self.driver.execute_script("arguments[0].scrollIntoView();",button)
                self.open_in_new_tab(button)
                self.driver_wait(lambda e: len(e.window_handles) > 1)
                self.driver.switch_to.window(self.driver.window_handles[1])
                self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'contents')))
                html = self.driver.page_source
                soup = BeautifulSoup(html,'html.parser')
                summary_block = soup.find('div',class_='contents')
                paragraphs = summary_block.find_all('p')
                for sum in paragraphs:
                    para = sum.get_text(strip=True)
                    if len(para) > 150:
                        summary = para
                        break
                    else:
                        continue
                else:
                    summary = 'Unable to parse summary, please visit the news page instead.'
                self.append(publish_date,title,summary,link)
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
    
    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source': 'LG Electronics - NA',
            'Type': 'Company News',
            'Title': title,
            'Summary': summary,
            'Link': link
            }
        )
             
    def open_in_new_tab(self,button):
        ActionChains(self.driver)\
            .key_down(Keys.CONTROL)\
                .click(button)\
                    .key_up(Keys.CONTROL)\
                        .perform()
        
    def driver_wait(self,condition):
        try:
            WebDriverWait(self.driver,5).until(condition)
        except:
            pass
        
    def scrape(self):
        try:
            self.get_soup()
        except:
            time.sleep(10)
            self.get_soup()
            

all_news = []
def get_LG_Electronics_NA(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = "https://www.lg.com/us/press-release"
    news = LGElectronicsNA(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/LG_Electronics_NA.csv',index=False)
    
