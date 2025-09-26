from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
from urllib.parse import urljoin
import re
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
import pandas as pd
import time

class DOENews:
    def __init__(self,driver,coverage_days,url,source):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        self.source = source
        self.page_num = 1
        self.root = 'https://www.energy.gov/'
    
    def get_soup(self):
        print(f'📰Opening: {self.source}')
        while True:
            if self.page_num == 1:
                self.driver.get(self.url)
            else:
                pass
            self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'MuiList-root')))
            news_blocks = self.driver.find_elements(By.CLASS_NAME,'MuiListItem-root')
            for block in news_blocks:
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView();",block)
                    button = block.find_element(By.TAG_NAME,'a')
                    link = button.get_attribute('href')
                    link = urljoin(self.root,link)
                    self.driver_wait(lambda e: len(e.window_handles) == 1)
                    self.open_in_new_tab(button)
                    self.driver.switch_to.window(self.driver.window_handles[1])
                    self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'beneath-title')))
                    html = self.driver.page_source
                    soup = BeautifulSoup(html,'html.parser')
                    parsed_date = soup.find('span',class_='display-date').text.strip()
                    parsed_date_obj = datetime.strptime(parsed_date,'%B %d, %Y')
                    publish_date = parsed_date_obj.strftime('%Y-%m-%d')
                    if parsed_date_obj >= self.date_limit:
                        title = soup.find('div',class_='page-title-outside-hero').text.strip()
                        paragraphs = soup.find_all('p')
                        summary = None
                        for p in paragraphs:
                            para = p.text.strip()
                            if len(para) > 200:
                                summary = para
                        if not summary:
                            summary = 'Unable to parse summary, please visit the news page instead.'
                        self.append(publish_date,title,summary,link)
                    else:
                        return False
                finally:
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
            self.page_num += 1
            page = self.driver.find_element(By.CSS_SELECTOR,f'[aria-label="Go to page {self.page_num}"]')
            self.driver.execute_script("arguments[0].scrollIntoView();",page)
            time.sleep(1)
            self.driver.execute_script("arguments[0].click();",page)
            
    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source': self.source,
            'Type': 'Industry News',
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
    
    def scrape(self):
        self.get_soup()

    def driver_wait(self,condition):
        try:
            WebDriverWait(self.driver,10).until(condition)
        except:
            pass

sites = [
    {'url':'https://www.energy.gov/search?page=0&sort_by=date&f%5B0%5D=article_type%3A1&f%5B1%5D=content_type_rest%3Aarticle', 'source':'DOE - Press Release'},
    {'url':'https://www.energy.gov/search?page=0&f%5B0%5D=article_type%3A430939', 'source':'DOE - Testimony'},
    {'url':'https://www.energy.gov/search?page=0&f%5B0%5D=article_type%3A1380643', 'source':'DOE - Latest OpEds'}
]

all_news = []
def get_DOE(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    for site in sites:
        url = site.get('url')
        src = site.get('source')
        news = DOENews(driver,coverage_days,url,src)
        news.scrape()
        all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df = df.drop_duplicates(subset=['Link'])
    df.to_csv('csv/DOE_news.csv',index=False)