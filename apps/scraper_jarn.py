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

class JarnNews:
    def __init__(self,driver,coverage_days,url,source):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        self.source = source
        self.page_num = 1

    def get_soup(self):
        while True:
            if self.page_num == 1: 
                self.driver.get(self.url) 
            else: 
                try:
                    page = page_section.find_element(By.LINK_TEXT,f'{self.page_num}')
                    page.click()
                except:
                    print(f'No such page found.')
            news_section = WebDriverWait(self.driver,5).until(EC.presence_of_element_located((By.CLASS_NAME,'article-list')))
            self.news_blocks = news_section.find_elements(By.CLASS_NAME,'article-box')
            page_section = self.driver.find_element(By.CLASS_NAME,'js-pagerSeparate')
            if not self.check_dates():
                break
            self.page_num += 1

            
        
    def open_new_tab(self,link):
        ActionChains(self.driver)\
            .key_down(Keys.CONTROL)\
                .click(link)\
                    .key_up(Keys.CONTROL)\
                        .perform()
                        
    def get_news(self):
        WebDriverWait(self.driver,2).until(EC.presence_of_element_located((By.CLASS_NAME,'article-detail-wrap')))
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        title = soup.find('h1',class_='articleTitle').text.strip()
        print(f'Fetching: {title}')
        summary_block = soup.find('div', class_='article-detail-main')
        if not summary_block:
            return ({'title': title, 'summary': 'Summary block not found.'})

        for child in summary_block.descendants:
            if child.name in ['em', 'div', 'img', 'br', 'a']:
                continue
            text = child.get_text(strip=True) if hasattr(child, 'get_text') else str(child).strip()
            if len(text) > 150:
                return ({'title': title, 'summary': text})
        
        return ({'title': title, 'summary': 'No suitable summary found.'})

        
    def check_dates(self):
        for dates in self.news_blocks:
            try:
                parsed_date = dates.find_element(By.CLASS_NAME,'data').text.strip()
                parsed_date_obj = datetime.strptime(parsed_date,'%Y.%m.%d')
                publish_date = parsed_date_obj.strftime('%Y-%m-%d')
                if parsed_date_obj < self.date_limit:
                    return False
                link_sel = dates.find_element(By.CLASS_NAME,'article-box-in')
                self.driver.execute_script("arguments[0].scrollIntoView();", dates)
                self.open_new_tab(link_sel)
                link = link_sel.get_attribute('href')
                self.driver.switch_to.window(self.driver.window_handles[1])
                before_tab = self.driver.window_handles
                try:
                    WebDriverWait(self.driver,2).until(lambda e: len(e.window_handles) > len(before_tab))
                except:
                    pass
                news = self.get_news()
                title = news.get('title')
                summary = news.get('summary')
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
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
            except Exception as e:
                print(f'An error has occured: {e}')
        return True
                
    def scrape(self):
        try:
            self.get_soup()
        except:
            pass          

sources = [
    {'url':'https://www.ejarn.com/category/eJarn_news_index','source':'JARN News'},
    {'url':'https://www.ejarn.com/category/interview_index','source':'JARN Interviews'}
]

all_news=[]
def get_jarn(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    for news in sources:
        url = news.get('url')
        source = news.get('source')
        site = JarnNews(driver,coverage_days,url,source)
        site.scrape()
        all_news.extend(site.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/jarn_news.csv',index=False)