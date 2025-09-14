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

class GeneracNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        self.root = 'https://www.generac.com'
        
    def get_soup(self):
        self.driver.get(self.url)
        button = self.driver_wait(EC.element_to_be_clickable((By.ID,'onetrust-accept-btn-handler')))
        try:
            button.click()
        except:
            pass
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_section = soup.find('ul',class_='list-unstyled')
        news_blocks = news_section.find_all('div',class_='modal-wrapper')
        self.get_news(news_blocks)

    def get_news(self,blocks):
        for news in blocks:
            parsed_date = news.find_all('p',class_='flex-column')[1].text.strip()
            parsed_date_obj = datetime.strptime(parsed_date,'%B %d, %Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj >= self.date_limit:
                partial_link = news.find('div',id='CtaBlock').find('a').get('href')
                link = f'{self.root}{partial_link}'
                self.driver.switch_to.new_window('tab')
                self.driver.get(link)
                self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'container-text-block-spacing')))
                html = self.driver.page_source
                soup = BeautifulSoup(html,'html.parser')
                title = soup.find('h3').text.strip()
                summary_block = soup.find_all('div',class_='container-text-block-spacing')[1]
                paragraphs = summary_block.find_all('p')
                for sum in paragraphs:
                    para = sum.get_text(strip=True)
                    if len(para) > 200:
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
            'Source': 'Generac',
            'Type': 'Company News',
            'Title': title,
            'Summary': summary,
            'Link': link
            }
        )
    
    def driver_wait(self,condition):
        try:
            button = WebDriverWait(self.driver,5).until(condition)
            return button
        except:
            pass
        
    def scrape(self):
        self.get_soup()
        
all_news = []
def get_generac(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url='https://www.generac.com/about/news/'
    news = GeneracNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/generac_news.csv',index=False)