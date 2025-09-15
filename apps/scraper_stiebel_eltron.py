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

class StiebelEltronNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        self.root = 'https://www.stiebel-eltron.com'
        
    def get_soup(self):
        self.driver.get(self.url)
        button = self.driver_wait(EC.element_to_be_clickable((By.CLASS_NAME,'ppms_cm_agree-to-all')))
        try:
            button.click()
            print('Cookies accepted.')
        except:
            print('No cookie pop-up found.')
            pass
        sel_blocks = self.driver.find_elements(By.CLASS_NAME,'files')
        print('scrolling through the news..')
        time.sleep(5)
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_section = soup.find('div',class_='tableContentContainer')
        news_blocks = soup.find_all('a',class_='files')
        self.get_news(news_blocks,sel_blocks)

    def get_news(self,bs4_blocks,sel_blocks):
        for news,sect in zip(bs4_blocks,sel_blocks):
            parsed_date = news.find('p',title='Date').get_text(strip=True)
            publish_date = datetime.strptime(parsed_date,'%Y-%m-%d')
            if publish_date >= self.date_limit:
                partial_link = news.get('href')
                link = f'{self.root}{partial_link}'
                self.driver.switch_to.new_window('tab')
                self.driver.get(link)
                self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'main-content')))
                html = self.driver.page_source
                soup = BeautifulSoup(html,'html.parser')
                title = soup.find('div',class_='content-header').find('h1').get_text(strip=True)
                summary = soup.find('div',class_='content-image-text__copy').find('p').get_text(strip=True)
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                self.append(publish_date,title,summary,link)

    def open_new_tab(self,button):
        ActionChains(self.driver)\
            .key_down(Keys.CONTROL)\
                .click(button)\
                    .key_up(Keys.CONTROL)\
                        .perform()
    
    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source': 'Stiebel Eltron',
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
def get_stiebel_eltron(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url='https://www.stiebel-eltron.com/en/home/company/press/press-releases.html'
    news = StiebelEltronNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/stiebel_eltron_news.csv',index=False)

# options = Options()
# # options.add_argument('--headless=new')
# options.add_argument('--disable-gpu')
# options.add_argument('--window-size=1920x1080')
# options.add_argument('--log-level=3')
# options.add_argument("--disable-blink-features=AutomationControlled")
# options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115 Safari/537.36")
# driver = webdriver.Chrome(options=options)
# get_stiebel_eltron(driver,coverage_days=360)

# time.sleep(10)
# driver.quit()