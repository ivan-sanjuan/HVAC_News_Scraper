from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
from urllib.parse import urljoin
import pandas as pd
import requests
import time

class TraneCommercialNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        self.root = 'https://www.trane.com/'
        
    def get_soup(self):
        print(f'📰Opening: Trane - Commercial')
        self.driver.get(self.url)
        time.sleep(10)
        section = self.driver.find_elements(By.CSS_SELECTOR,'[data-component="Card"]')
        print(section)
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_blocks = soup.find_all('div',{'data-prop':'result'})
        news_blocks_sel = self.driver.find_elements(By.CSS_SELECTOR,'[data-component="Card"]')
        link_list = self.driver.find_elements(By.CSS_SELECTOR,'[data-eventtype="TITLE_CLICK"]')
        # link_list = soup.find_all('a')
        for url in link_list:
            link = url.get_attribute('href')
            if link:
                if link.startswith('/commercial/north-america/us/en/about-us/newsroom/') or link.startswith(f'https://www.trane.com/commercial/north-america/us/en/about-us/newsroom/'):
                    link = urljoin(self.root,link)
                    print(link)
        # self.get_news(news_blocks)

    def get_news(self,blocks):
        for news in blocks:
            link = news.find('a',{'data-evettype':'TITLE_CLICK'}).get('href')
            link = urljoin(self.root,link)
            self.driver.switch_to.new_window('tab')
            self.driver.get(link)
            self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'featured-article')))
            html = self.driver.page_source
            soup = BeautifulSoup(html,'html.parser')
            parsed_date = soup.find('p',class_='story-hero__date').text.replace('Published: ','').strip()
            parsed_date_obj = datetime.strptime(parsed_date,'%B %d, %Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj < self.date_limit:
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                break
            title = soup.find('h1',class_='story-hero__headline').text.strip()
            paragraphs = soup.find_all('p')
            summary = None
            for p in paragraphs:
                para = p.text.strip()
                if len(para) > 200:
                    summary = para
                    break
            if not summary:
                summary = 'Unable to parse summary, please visit the news page instead.'
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            self.append(publish_date,title,summary,link)

    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source': 'Rees Scientific',
            'Type': 'Company News',
            'Title': title,
            'Summary': summary,
            'Link': link
            }
        )

    def driver_wait(self,condition):
        try:
            return WebDriverWait(self.driver,5).until(condition)
        except:
            pass
    
    def scrape(self):
        self.get_soup()

all_news=[]
def get_trane_commercial(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://www.trane.com/commercial/north-america/us/en/about-us/newsroom.html'
    news = TraneCommercialNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/trane_commercial_news.csv',index=False)
    
options = Options()
# options.add_argument('--headless=new')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920x1080')
options.add_argument('--log-level=3')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115 Safari/537.36")
options.page_load_strategy = 'eager'
driver = webdriver.Chrome(options=options)
get_trane_commercial(driver,coverage_days=30)

time.sleep(5)
driver.quit()
