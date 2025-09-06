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

    def get_soup(self):
        self.driver.get(self.url)
        print(f'Opening: {self.source}')
        try:
            WebDriverWait(self.driver,10).until(EC.element_to_be_clickable((By.CLASS_NAME,'continue'))).click()
            print('Ads Closed.')
        except:
            print('Ads not found.')
            pass
        WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.CLASS_NAME,'item-row')))
        news_blocks_sel = self.driver.find_elements(By.CLASS_NAME,'item-row')
        self.scroll_each_news()
        time.sleep(5)
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
            time.sleep(1)

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
        self.driver.execute_script("arguments[0].scrollIntoView();",link_sel)
        current_tabs = self.driver.window_handles
        self.driver.switch_to.new_window('tab')
        self.driver.get(link)
        WebDriverWait(self.driver,10).until(lambda e: len(e.window_handles) > len(current_tabs))
        self.driver.switch_to.window(self.driver.window_handles[1])
        standard_news = self.get_news_details()
        title = standard_news.get('title')
        print(f'Fetching News: {title}')
        summary = standard_news.get('summary')
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
            
    def get_news(self,section,section_sel):
        page_num = 1
        for news, sect in zip(section,section_sel):
            WebDriverWait(self.driver,10).until(lambda e: len(e.window_handles) == 1)
            try:
                parsed_date = news.find('div',class_='date').get_text(strip=True)
                parsed_date_obj = self.clean_date(parsed_date)
                publish_date = parsed_date_obj.strftime('%Y-%m-%d')
                if page_num == 1:
                    if parsed_date_obj >= self.date_limit:
                        self.get_details(publish_date,sect)
                    continue
                else:
                    if parsed_date_obj >= self.date_limit:
                        self.get_details(publish_date,sect)
            except:
                pass
            
            page_num += 1
            
    def get_label(self):
        label = self.soup.find('div',class_='above-line')
        sponsor_tag = label.find('div',class_='sponsored-label')
        if sponsor_tag:
            return True
        else:
            return False
        
    def open_new_tab(self,link):
        ActionChains(self.driver)\
            .key_down(Keys.CONTROL)\
                .click(link)\
                    .key_up(Keys.CONTROL)\
                        .perform()
                        
    def get_news_details(self):
        try:
            WebDriverWait(self.driver,3).until(EC.element_to_be_clickable((By.CLASS_NAME,'continue'))).click()
            WebDriverWait(self.driver,3).until(EC.visibility_of_element_located((By.CLASS_NAME,'title-text')))
            print('Making sure the page is fully loaded...')
        except:
            pass
        time.sleep(3)
        html = self.driver.page_source
        self.soup = BeautifulSoup(html,'html.parser')
        sponsor_tag = self.get_label()
        extracted_title = self.soup.find('h1',class_='title-text').text.strip()
        summary = self.soup.find('div',class_='html').find('p').get_text(strip=True)
        if sponsor_tag == True:
            title = f'(SPONSORED NEWS POST) {extracted_title}'
        else:
            title = extracted_title
        return ({'title':title,'summary':summary})
        
    def scrape(self):
        self.get_soup()

sites = [
    {'url':'https://www.contractingbusiness.com/residential-hvac','source':'Contracting Business - Residential'},
    {'url':'https://www.contractingbusiness.com/commercial-hvac','source':'Contracting Business - Commercial'},
    {'url':'https://www.contractingbusiness.com/refrigeration','source':'Contracting Business - Refrigeration'},
    {'url':'https://www.contractingbusiness.com/industry-news','source':'Contracting Business - IndustryNews'},
    {'url':'https://www.contractingbusiness.com/technology','source':'Contracting Business - Technology'},
    {'url':'https://www.contractingbusiness.com/product-news','source':'Contracting Business - Product News'}
]

all_news = []        
def get_contracting_business(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    for news in sites:
        url = news.get('url')
        source = news.get('source')
        news = ContractingBusinessNews(driver,coverage_days,url,source)
        news.scrape()
        all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/contracting_business_news.csv',index=False)

options = Options()
# options.add_argument('--headless=new')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920x1080')
options.add_argument('--log-level=3')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115 Safari/537.36")
driver = webdriver.Chrome(options=options)
get_contracting_business(driver,coverage_days=10)

time.sleep(20)
driver.quit()