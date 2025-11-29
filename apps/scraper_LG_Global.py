from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime
from urllib.parse import urljoin
import pandas as pd
import time

class LGNews:
    def __init__(self,driver,coverage_days,news_url,source):
        self.driver = driver
        self.coverage_days = coverage_days
        self.news_url = news_url
        self.latest_news = []
        self.today = datetime.today()
        self.source = source

    def get_highlight_soup(self):
        self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'page_content')))
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        article = soup.find('div',class_='page_content')
        parsed_date = article.find('div',class_='date').text
        parsed_date_obj = datetime.strptime(parsed_date,'%B %d, %Y')
        publish_date = parsed_date_obj.strftime('%Y-%m-%d')
        if parsed_date_obj >= self.today-timedelta(days=self.coverage_days):
            title = article.find('h2',class_='st_title').text.strip()
            summary_block = article.find('p',style='text-align: justify;')
            summary_block.strong.decompose()
            summary = summary_block.text.strip()
            self.news_append(publish_date,title,summary)
        self.driver.back()
        
    def news_append(self,date,title,summary):
        print(f'Fetching News: {title}')
        self.latest_news.append({
            'PublishDate': date,
            'Source': self.source,
            'Type': 'Company News',
            'Title': title,
            'Summary': summary,
            'Link': self.hlink
        })
        
    def get_blocks_soup(self):
        home_html=self.driver.page_source
        home_soup=BeautifulSoup(home_html,'html.parser')
        news_section = home_soup.find('div', class_='bs_psbx')
        news_blocks = news_section.find_all('a', class_='post')
        for news in news_blocks:
            self.link = news.get('href')
            self.driver.switch_to.new_window('tab')
            self.driver.get(self.link)
            self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'page_content')))
            html = self.driver.page_source
            soup = BeautifulSoup(html,'html.parser')
            article = soup.find('div',class_='page_content')
            parsed_date = article.find('div',class_='date').text.strip()
            parsed_date_obj = datetime.strptime(parsed_date,'%B %d, %Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj >= self.today-timedelta(days=self.coverage_days):
                title = article.find('h2',class_='st_title').text.strip()
                print(f'Scraping summary: {title}')
                paragraphs = soup.find_all('p')
                summary = None
                for p in paragraphs:
                    ptext = p.text.strip()
                    if len(ptext) >= 378:
                        summary = ptext
                        break
                if not summary:
                    summary = 'Unable to parse summary, please visit the news page instead.'
                self.latest_news.append(
                    {
                    'PublishDate': publish_date,
                    'Source': self.source,
                    'Type': 'Company News',
                    'Title': title,
                    'Summary': summary,
                    'Link': self.link
                    }
                )
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            
    def get_news(self):
        self.driver.get(self.news_url)
        highlighted_news = self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'itembx')))
        self.hlink = highlighted_news.get_attribute('href')
        highlighted_news.click()
        self.get_highlight_soup()
        self.get_blocks_soup()
        
    def driver_wait(self,condition):
        try:
            WebDriverWait(self.driver,5).until(condition)
        except:
            pass
        
    def scrape(self):
        self.get_news()

sources = (
    {'url':'https://www.lgnewsroom.com/category/news/corporate/','source':'LG-Corporate'},
    {'url':'https://www.lgnewsroom.com/category/news/home-appliances-solution/','source':'LG-ApplianceSolution'},
    {'url':'https://www.lgnewsroom.com/category/news/media-entertainment-solution/','source':'LG-Entertainment'},
    {'url':'https://www.lgnewsroom.com/category/news/vehicle-solution/','source':'LG-VehicleSolutions'},
    {'url':'https://www.lgnewsroom.com/category/news/eco-solution/','source':'LG-EcoSolutions'},
    {'url':'https://www.lgnewsroom.com/category/news/statements/','source':'LG-Statements'}
)

all_news = []
def get_LG_news(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    for item in sources:
        url = item['url']
        src = item['source']
        news = LGNews(driver,coverage_days,url,src)
        news.scrape()
        all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.drop_duplicates(subset=['Link'])
    df.to_csv('csv/LG_News.csv', index=False)
    
options = Options()
options.add_argument('--headless=new')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920x1080')
options.add_argument('--log-level=3')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H321 Safari/600.1.4")
options.page_load_strategy = 'eager'
driver = webdriver.Chrome(options=options)
get_LG_news(driver,coverage_days=15)

time.sleep(5)
driver.quit()