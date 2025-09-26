from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
import pandas as pd
import time
import re

class ThermokingNewsEurope:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage_days = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage_days)
    
    def open_in_new_tab(self,button):
        print('opening in new tab')
        ActionChains(self.driver)\
            .key_down(Keys.CONTROL)\
            .click(button)\
            .key_up(Keys.CONTROL)\
            .perform()
    
    def get_news(self):
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        title = soup.find('h1',class_='wp-block-heading').text.strip()
        summary_block = soup.find('section',class_='wp-block-group')
        paragraphs = summary_block.find_all('p')
        for p in paragraphs:
            text = p.text.strip()
            if len(text) > 150:
                summary = text
            else:
                pass
        return ({'summary':summary, 'title':title})
        
    def clean_ordinal_suffix(self,date_str):
        return re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)

    def get_soup(self):
        print(f'📰Opening: ThermoKing - Europe')
        self.driver.get(self.url)
        WebDriverWait(self.driver,5).until(EC.element_to_be_clickable((By.ID,'hs-eu-confirmation-button'))).click()
        news_blocks = self.driver.find_elements(By.CLASS_NAME,'block-card')
        for news in news_blocks:
            self.driver.execute_script("arguments[0].scrollIntoView();", news)
            link = news.get_attribute('href')
            WebDriverWait(news,5).until(EC.visibility_of_element_located,'block-card')
            self.open_in_new_tab(news)
            self.driver.switch_to.window(self.driver.window_handles[1])
            WebDriverWait(self.driver,5).until(EC.presence_of_element_located((By.CLASS_NAME,'wp-block-cover__inner-container')))
            parsed_date = self.driver.find_element(By.CLASS_NAME,'before-h1').text.strip()
            parsed_date_cleaned = self.clean_ordinal_suffix(parsed_date)
            parsed_date_cleaned_obj = datetime.strptime(parsed_date_cleaned,'%d %B %Y')
            parsed_date_obj = datetime.strptime(parsed_date_cleaned,'%d %B %Y')
            publish_date = parsed_date_cleaned_obj.strftime('%Y-%m-%d')
            if parsed_date_obj >= self.date_limit:
                get_news = self.get_news()
                title = get_news.get('title')
                print(f'Fetching: {title}')
                summary = get_news.get('summary')
                self.latest_news.append(
                    {
                    'PublishDate':publish_date,
                    'Source': 'ThermoKing-EU',
                    'Type': 'Company News',
                    'Title': title,
                    'Summary': summary,
                    'Link': link
                    }
                )
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
            else:
                break
        
    def scrape(self):
        self.get_soup()

all_news=[]
def get_thermoking_europe(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://europe.thermoking.com/media-room'
    news = ThermokingNewsEurope(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/thermoking_EU_news.csv',index=False)