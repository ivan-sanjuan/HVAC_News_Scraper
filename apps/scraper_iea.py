from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
import re
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
import pandas as pd
import time

class IEANews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
    
    def get_soup(self):
        self.driver.get(self.url)
        self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'m-grid--news-detailed')))
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_blocks_bs4 = soup.find_all('div',class_='m-news-detailed-listing')
        news_blocks_sel = self.driver.find_elements(By.CLASS_NAME,'m-news-detailed-listing')
        self.get_news(news_blocks_bs4,news_blocks_sel)

    def get_news(self,bs4,sel):
        for news,sect in zip(bs4,sel):
            parsed_date = news.find('div',class_='m-news-detailed-listing__date').get_text(strip=True)
            parsed_date_obj = datetime.strptime(parsed_date,'%d %B %Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj >= self.date_limit:
                button = sect.find_element(By.CLASS_NAME,'m-news-detailed-listing__link')
                link = button.get_attribute('href')
                self.driver.execute_script("arguments[0].scrollIntoView",button)
                self.open_in_new_tab(button)
                self.driver_wait(lambda e: len(e.window_handles) > 1)
                self.driver.switch_to.window(self.driver.window_handles[1])
                self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'content')))
                html = self.driver.page_source
                soup = BeautifulSoup(html,'html.parser')
                try:
                    title = soup.find('h1',class_='o-hero-news__title').text.strip()
                except AttributeError:
                    title = soup.find('header',class_='o-hero-article__title').find('h1').get_text(strip=True)
                summary_block = soup.find('div',class_='m-block--text')
                paragraphs = summary_block.find_all('p')
                for sum in paragraphs:
                    para = sum.get_text(strip=True)
                    if len(para) > 150:
                        summary = para
                        break
                    else:
                        continue
                else:
                    summary = paragraphs[0].get_text(strip=True)
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                self.append(publish_date,title,summary,link)
    
    def append(self,publish_date,title,summary,link):
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source': 'IEA News',
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


    def driver_wait(self,condition):
        try:
            WebDriverWait(self.driver,5).until(condition)
        except:
            pass
    
    def scrape(self):
        self.get_soup()

all_news = []
def get_IEA(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://www.iea.org/news'
    news = IEANews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/iea_news.csv',index=False)

