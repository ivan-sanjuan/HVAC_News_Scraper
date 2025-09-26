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

class GCCANews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)

    def get_soup(self):
        print(f'📰Opening: GCCA')
        self.driver.get(self.url)
        self.driver_wait(EC.presence_of_all_elements_located((By.CLASS_NAME,'feed-item-right')))
        # time.sleep(5)
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_blocks_bs4 = soup.find_all('div',class_='fl-post-feed-post')
        news_blocks_sel = self.driver.find_elements(By.CLASS_NAME,'fl-post-feed-post')
        self.get_news(news_blocks_bs4,news_blocks_sel)

    def get_news(self,blocks_bs4,blocks_sel):
        for news,sect in zip(blocks_bs4,blocks_sel):
            link = news.find('h2',class_='fl-post-title').find('a').get('href')
            self.driver.switch_to.new_window('tab')
            self.driver.get(link)
            self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'fl-col-content')))
            date = self.driver.find_element(By.CLASS_NAME,'fl-heading')
            self.driver.execute_script("arguments[0].scrollIntoView();",date)
            html = self.driver.page_source
            soup = BeautifulSoup(html,'html.parser')
            container = soup.find('div',class_='fl-col-group')
            parsed_date = container.find('div',class_='fl-rich-text').find('p').text.strip() 
            parsed_date_obj = datetime.strptime(parsed_date,'%B %d, %Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj >= self.date_limit:
                title = soup.find('span',class_='fl-heading-text').get_text(strip=True)
                summary_block = soup.find('div',class_='fl-module-content')
                paragraphs = summary_block.find_all('p')
                try:
                    for sum in paragraphs:
                        para = sum.get_text(strip=True)
                        if len(para) > 150:
                            summary = para
                            break
                        else:
                            continue
                    else:
                        summary = paragraphs[0].get_text(strip=True)
                except IndexError:
                    summary = 'Unable to parse summary, please visit the site instead.'
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                self.append(publish_date,title,summary,link)
    
    def append(self,publish_date,title,summary,link):
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source': 'GCCA News',
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
            WebDriverWait(self.driver,5).until(condition)
        except:
            pass

all_news = []
def get_GCCA(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://www.gcca.org/resources/news-and-media/'
    news = GCCANews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/gcca_news.csv',index=False)

# options = Options()
# # options.add_argument('--headless=new')
# options.add_argument('--disable-gpu')
# options.add_argument('--window-size=1920x1080')
# options.add_argument('--log-level=3')
# options.add_argument("--disable-blink-features=AutomationControlled")
# options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115 Safari/537.36")
# driver = webdriver.Chrome(options=options)
# get_GCCA(driver,coverage_days=30)

# time.sleep(10)
# driver.quit()