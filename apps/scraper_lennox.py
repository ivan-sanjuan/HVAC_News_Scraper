from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime
import pandas as pd
import time

class LennoxNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.today = datetime.today()
    
    def get_soup(self):
        print(f'📰Opening: Lennox')
        self.driver.get(self.url)
        WebDriverWait(self.driver,5).until(
            EC.presence_of_element_located((By.CLASS_NAME,'nir-widget--list'))
        )
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_section = soup.find('div',class_='nir-widget--list')
        self.news_blocks = news_section.find_all('article')
        self.toggle_buttons = self.driver.find_elements(By.TAG_NAME,'article')
        
    def get_news(self):
        for news, toggle in zip(self.news_blocks, self.toggle_buttons):
            parsed_date = news.find('div',class_='nir-widget--news--date-time').text.strip()
            parsed_date_obj = datetime.strptime(parsed_date,'%B %d, %Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj >= self.today-timedelta(days=self.coverage):
                button = toggle.find_element(By.CLASS_NAME,'nir-widget--news--accordion-toggle')
                self.driver.execute_script("arguments[0].scrollIntoView();", button)
                button_clicked = False
                if not button_clicked:
                    button.click()
                    button_clicked = True
                    title = news.find('a',class_='nir-widget--news--accordion-toggle').text.strip()
                    print(title)
                    summary_section = news.find('div','nir-widget--news--teaser')
                    p_tag = summary_section.find('p')
                    if p_tag:
                        summary = news.find('div','nir-widget--news--teaser').find('p').text.strip()
                    else:
                        summary = news.find('div','nir-widget--news--teaser').text.strip()
                    link = news.find('div',class_='nir-widget--news--read-more').find('a').get('href')
                    root_link = 'https://investor.lennox.com'
                    self.latest_news.append(
                        {
                        'PublishDate': publish_date,
                        'Source': 'Lennox',
                        'Type': 'Company News',
                        'Title': title,
                        'Summary': summary,
                        'Link': f'{root_link}{link}'
                        }
                    )
                
    def scrape(self):
        self.get_soup()
        self.get_news()

all_news = []
def get_lennox_news(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://investor.lennox.com/news-events/news-releases'
    news = LennoxNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/lennox_news.csv', index=False)

