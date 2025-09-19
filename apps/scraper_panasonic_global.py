from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException, NoSuchWindowException
from selenium.webdriver.common.keys import Keys
from urllib.parse import urljoin
import threading
import re
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
import pandas as pd
import time

class PanasonicNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        self.root = 'https://news.panasonic.com/'
        
    def get_soup(self):
        self.driver.get(self.url)
        self.popup_thread()
        time.sleep(5)
        self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'p-grid__row')))
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_section = soup.find('div',class_='p-grid__row')
        news_blocks = news_section.find_all('article',class_='p-card')
        news_section_sel = self.driver.find_element(By.CLASS_NAME,'p-grid__row')
        news_blocks_sel = news_section_sel.find_elements(By.CLASS_NAME,'p-card')
        self.get_news(news_blocks,news_blocks_sel)
    
    def get_news(self,bs4_blocks,sel_blocks):
        for bs4,sel in zip(bs4_blocks,sel_blocks):
            try:
                parsed_date = bs4.find('p',class_='p-card__date').get_text(strip=True)
                parsed_date_obj = datetime.strptime(parsed_date,'%m/%d/%Y')
                publish_date = parsed_date_obj.strftime('%Y-%m-%d')
                if parsed_date_obj >= self.date_limit:
                    link = bs4.find('a',class_='p-card__link').get('href')
                    title = bs4.find('h3',class_='p-card__heading').get_text(strip=True)
                    if not link.startswith(self.root):
                        link = urljoin(self.root,link)
                    try:
                        button = sel.find_element(By.CLASS_NAME,'p-card__link')
                        self.driver.execute_script("arguments[0].scrollIntoView();",button)
                        self.open_in_new_tab(button)
                        self.driver_wait(lambda e: len(e.window_handles) > 1)
                        self.driver.switch_to.window(self.driver.window_handles[1])
                    except IndexError:
                        self.driver.switch_to.new_window('tab')
                        self.driver.get(link)
                    html = self.driver.page_source
                    soup = BeautifulSoup(html,'html.parser')
                    self.driver_wait(EC.presence_of_element_located((By.ID,'TextItem__body')))
                    # title = soup.find('h1',class_='p-detailHeader__heading').get_text(strip=True)
                    summary_block = soup.find('div',class_='TextItem__body')
                    summary = None
                    paragraphs = soup.find_all('p')
                    if paragraphs:
                        for p in paragraphs:
                            para = p.get_text(strip=True)
                            if len(para) > 200:
                                summary = para
                                break
                        if not summary:
                            summary = 'Unable to parse summary, please visit the news page instead.'
                    else:
                        summary = 'Unable to parse summary, please visit the news page instead.'
                    self.append(publish_date,title,summary,link)
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
            except Exception as e:
                print(f'An error has occured: {e}')
    
    def open_in_new_tab(self,button):
        ActionChains(self.driver)\
            .key_down(Keys.CONTROL)\
                .click(button)\
                    .key_up(Keys.CONTROL)\
                        .perform()
            
    def popup_thread(self):
        print('Popup watcher launched.')
        threading.Thread(
            target=self.popup_watcher,
            daemon=True
        ).start()
            
    def popup_watcher(self):
        while True:  
            popup = self.driver_wait(EC.element_to_be_clickable((By.ID,'close-pc-btn-handler')))
            if popup:
                try:
                    popup.click()
                    print('Pop-up found and closed.')
                    time.sleep(1)
                    break
                except:
                    pass
            time.sleep(1)
        
    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source': 'Panasonic-Global',
            'Type': 'Company News',
            'Title': title,
            'Summary': summary,
            'Link': link
            }
        )

    def driver_wait(self,condition):
        try:
            return WebDriverWait(self.driver,3).until(condition)
        except:
            pass
    
    def scrape(self):
        self.get_soup()

all_news = []
def get_panasonic_global(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://news.panasonic.com/global/'
    news = PanasonicNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/panasonic_global_news.csv',index=False)