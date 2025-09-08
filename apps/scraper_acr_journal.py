from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys
import threading
from threading import Event, Lock
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
import pandas as pd
import time

class ACRJournal:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.page_num = 1
        self.date_limit = datetime.today()-timedelta(days=self.coverage)

    def get_soup(self):
        threading.Thread(target=self.popup_watcher,args=((By.CLASS_NAME,'modal-content'),),daemon=True).start()
        while True:
            if self.page_num == 1:
                self.driver.get(self.url)
            else:
                pagination = self.driver.find_element(By.CLASS_NAME,'pagination-container')
                try:
                    time.sleep(2)
                    self.driver.execute_script("arguments[0].scrollIntoView();",pagination)
                    pagination.find_element(By.LINK_TEXT,f'{self.page_num}').click()
                except ElementClickInterceptedException:
                    time.sleep(2)
                    self.driver.execute_script("arguments[0].scrollIntoView();",pagination)
                    pagination.find_element(By.LINK_TEXT,f'{self.page_num}').click()
            try:
                WebDriverWait(self.driver,5).until(EC.element_to_be_clickable((By.ID,'accept-btn'))).click()
            except:
                pass
            try:
                news_section_sel = WebDriverWait(self.driver,5).until(EC.presence_of_element_located((By.CLASS_NAME,'paged-list-news')))
            except:
                pass
            html = self.driver.page_source
            soup = BeautifulSoup(html,'html.parser')
            news_section = soup.find('div',class_='paged-list-news')
            self.news_blocks = news_section.find_all('div',class_='card')
            self.news_blocks_sel = news_section_sel.find_elements(By.CLASS_NAME,'card')
            if not self.get_news():
                break
            self.page_num += 1

    def get_news(self):
        for news, sect in zip(self.news_blocks,self.news_blocks_sel):
            parsed_date = news.find('p',class_='text-muted').get_text(strip=True)
            parsed_date_obj = datetime.strptime(parsed_date,'%d %B %Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj < self.date_limit:
                return False
            link_segment = news.find('h5',class_='card-title').find('a').get('href')
            root_url = 'https://www.acrjournal.uk'
            self.scroll_and_click(sect)
            WebDriverWait(self.driver,5).until(lambda e: len(e.window_handles) > 1)
            self.driver.switch_to.window(self.driver.window_handles[1])
            news = self.get_details()
            title = news.get('title')
            summary = news.get('summary')
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            WebDriverWait(self.driver,5).until(lambda e: len(e.window_handles) == 1)
            self.latest_news.append(
                {
                'PublishDate':publish_date,
                'Source': 'ACR Journal',
                'Type': 'Industry News',
                'Title': title,
                'Summary': summary,
                'Link': f'{root_url}{link_segment}'
                }
            )
        return True
    
    def get_details(self):
        try:
            WebDriverWait(self.driver,5).until(EC.presence_of_element_located((By.CLASS_NAME,'post-body-container')))
        except:
            pass
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        title = soup.find('h1',class_='page-title').text.strip()
        summary_block = soup.find('div',class_='post-body')
        paragraphs = summary_block.find_all('p')
        for p in paragraphs:
            para = p.get_text(strip=True)
            if len(para) > 150:
                summary = para
                break
            else:
                continue
        else:
            summary = paragraphs[0].get_text(strip=True)
        return ({'title':title,'summary':summary})
    
    def scroll_and_click(self,sect):
        link = sect.find_element(By.CLASS_NAME,'card-title').find_element(By.CSS_SELECTOR,'a')
        self.driver.execute_script("arguments[0].scrollIntoView();",link)
        self.click_to_new_tab(link)
       
    def click_to_new_tab(self,link):
        ActionChains(self.driver)\
            .key_down(Keys.CONTROL)\
                .click(link)\
                    .key_up(Keys.CONTROL)\
                        .perform()
    
    def popup_watcher(self,selector):
        watcher = True
        while watcher == True:
            try:
                popup = self.driver.find_element(*selector)
                if popup.is_displayed():
                    print('Pop-up detected.')
                    close_btn = popup.find_element(By.LINK_TEXT,'Dismiss')
                    close_btn.click()
                print('Pop-up closed.')
                watcher = False
            except (NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException):
                pass
            time.sleep(1)
        
    def scrape(self):
        self.get_soup()

all_news = []
def get_acr_journal(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url='https://www.acrjournal.uk/news'
    news = ACRJournal(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/acr_journal_news.csv',index=False)

options = Options()
# options.add_argument('--headless=new')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920x1080')
options.add_argument('--log-level=3')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115 Safari/537.36")
driver = webdriver.Chrome(options=options)
get_acr_journal(driver,coverage_days=10)

time.sleep(10)
driver.quit()