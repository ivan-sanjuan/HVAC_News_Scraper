from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
from urllib.parse import urljoin
import pandas as pd
import time

class ContractingBusinessNews:
    def __init__(self,driver,coverage_days,url,source):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.source = source
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        self.root = 'https://www.contractingbusiness.com/'

    def get_soup(self):
        self.driver.get(self.url)
        print(f'Getting: {self.source}')
        try:
            continue_button = self.driver_wait(EC.element_to_be_clickable((By.CLASS_NAME,'continue')))
            self.driver.execute_script("arguments[0].click();",continue_button)
            print('Ads Closed.')
        except:
            print('Ads not found.')
            pass
        WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.CLASS_NAME,'item-row')))
        news_blocks_sel = self.driver.find_elements(By.CLASS_NAME,'item-row')
        self.scroll_each_news()
        time.sleep(1)
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_blocks = soup.find_all('div',class_='item-row')
        self.get_news(news_blocks,news_blocks_sel)
        
    def scroll_each_news(self):
        bottom = self.driver.find_element(By.CLASS_NAME,'load-more')
        self.driver.execute_script("arguments[0].scrollIntoView();",bottom)
        print('Mimicking a human scrolling through the news.')
        time.sleep(1)
        try:
            blocks = self.driver.find_elements(By.CLASS_NAME,'item-row')
        except StaleElementReferenceException:
            time.sleep(1)
            blocks = self.driver.find_elements(By.CLASS_NAME,'item-row')
        for news in blocks:
            link_sel = news.find_element(By.CLASS_NAME,'title-wrapper')
            self.driver.execute_script("arguments[0].scrollIntoView();",link_sel)
            time.sleep(0.5)

    def clean_date(self,date_str):
        cleaned = date_str.replace('.','')
        if cleaned.startswith('Sept'):
            cleaned = cleaned.replace('Sept','Sep')
        else:
            pass
        date_formats = ['%b %d, %Y', '%B %d, %Y']
        for format in date_formats:
            try:
                cleaned_date = datetime.strptime(cleaned,format)
                return cleaned_date
            except ValueError:
                continue
            
    def get_details(self,publish_date,sel_block):
        link_sel = sel_block.find_element(By.CLASS_NAME,'title-wrapper')
        link = link_sel.get_attribute('href')
        link = urljoin(self.root,link)
        self.driver.execute_script("arguments[0].scrollIntoView();",link_sel)
        current_tabs = self.driver.window_handles
        self.driver.switch_to.new_window('tab')
        self.driver.get(link)
        standard_news = self.get_news_details()
        title = standard_news.get('title')
        summary = standard_news.get('summary')
        self.append(publish_date,title,summary,link)
            
    def get_news(self,section,section_sel):
        for news, sect in zip(section,section_sel):
            parsed_date = news.find('div',class_='date')
            if parsed_date:
                parsed_date = parsed_date.text.strip()
                parsed_date_obj = self.clean_date(parsed_date)
                publish_date = parsed_date_obj.strftime('%Y-%m-%d')
                if parsed_date_obj >= self.date_limit:
                    self.get_details(publish_date,sect)
            
    def get_label(self,soup):
        label = soup.find('div',class_='above-line')
        sponsor_tag = label.find('div',class_='sponsored-label')
        if sponsor_tag:
            return True
        else:
            return False
                        
    def get_news_details(self):
        self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'title-text')))
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        sponsor_tag = self.get_label(soup)
        extracted_title = soup.find('h1',class_='title-text').text.strip()
        summary = None
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            para = p.text.strip()
            if len(para) > 200:
                summary = para
                break
        if not summary:
            summary = 'Unable to parse summary, please visit the news page instead.'
        if sponsor_tag == True:
            title = f'(SPONSORED NEWS POST) {extracted_title}'
        else:
            title = extracted_title
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])
        return ({'title':title,'summary':summary})
    
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

    def driver_wait(self,condition):
        try:
            return WebDriverWait(self.driver,5).until(condition)
        except:
            pass
        
    def scrape(self):
        self.get_soup()

sites = [    
    {'url':'https://www.contractingbusiness.com/residential-hvac','source':'Contracting Business - Residential'},
    {'url':'https://www.contractingbusiness.com/commercial-hvac','source':'Contracting Business - Commercial'},
    {'url':'https://www.contractingbusiness.com/refrigeration','source':'Contracting Business - Refrigeration'},
    {'url':'https://www.contractingbusiness.com/industry-news','source':'Contracting Business - IndustryNews'},
    {'url':'https://www.contractingbusiness.com/technology','source':'Contracting Business - Technology'},
    {'url':'https://www.contractingbusiness.com/product-news','source':'Contracting Business - Product News'},
]

all_news = []        
def get_contracting_business(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    for site in sites:
        url = site.get('url')
        source = site.get('source')
        news = ContractingBusinessNews(driver,coverage_days,url,source)
        news.scrape()
        all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df = df.drop_duplicates(subset=['Link'])
    df.to_csv('csv/contracting_business_news.csv',index=False)

options = Options()
options.add_argument('--headless=new')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920x1080')
options.add_argument('--log-level=3')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115 Safari/537.36")
options.page_load_strategy = 'eager'
driver = webdriver.Chrome(options=options)
get_contracting_business(driver,coverage_days=10)

time.sleep(5)
driver.quit()
