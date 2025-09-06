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

class ContractingBusinessNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)

    def get_soup(self):
        self.driver.get(self.url)
        try:
            WebDriverWait(self.driver,10).until(EC.element_to_be_clickable((By.CLASS_NAME,'continue'))).click()
        except:
            pass
        WebDriverWait(self.driver,5).until(EC.presence_of_element_located((By.CLASS_NAME,'grid-row')))
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        # self.get_headline()
        news_section = soup.find('div',class_='grid-row')
        news_blocks = soup.find_all('div',class_='item-row')
        news_section_sel = self.driver.find_element(By.CLASS_NAME,'standard-blocks')
        news_blocks_sel = self.driver.find_elements(By.CLASS_NAME,'item-row')
        self.get_news(news_blocks,news_blocks_sel)
        
    # def get_headline(self):
    #     section = self.soup.find('div',class_='content-list')
    #     parsed_date = section.find('div',class_='date').text.strip()
    #     parsed_date_obj = datetime.strptime(parsed_date,'%b. %d, %Y')
    #     publish_date = parsed_date_obj.strftime('%Y-%m-%d')
    #     if parsed_date_obj >= self.date_limit:
    #         lock = self.get_label(section)
    #         link = self.driver.find_element(By.CLASS_NAME,'title-wrapper')
    #         hlink = link.get_attribute('href')
    #         self.open_new_tab(link)
    #         WebDriverWait(self.driver,3).until(lambda e: len(e.window_handles)>1)
    #         headline = self.get_news_details(lock)
    #         title = headline.get('title')
    #         summary = headline.get('summary')
    #         self.driver.close()
    #         self.driver.switch_to.window(self.driver.window_handles[0])
    #         self.latest_news.append(
    #             {
    #             'PublishDate':publish_date,
    #             'Source': 'Contracting Business - Residential',
    #             'Type': 'Industry News',
    #             'Title': title,
    #             'Summary': summary,
    #             'Link': hlink
    #             }
    #         )
    
    def clean_date(self,date_str):
        cleaned = date_str.strip()
        cleaned = cleaned.replace('.','')
        if cleaned.startswith('Sept'):
            cleaned = cleaned.replace('Sept','Sep')
        else:
            pass
        date_formats = [
            '%b %d, %Y',
            '%B %d, %Y',
        ]
        for format in date_formats:
            try:
                cleaned_date = datetime.strptime(cleaned,format)
                return cleaned_date
            except ValueError:
                continue
            
    def get_news(self,section,section_sel):
        for news, sect in zip(section,section_sel):
            parsed_date = news.find('div',class_='date').text
            parsed_date_obj = self.clean_date(parsed_date)
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj >= self.date_limit:
                link_sel = sect.find_element(By.CLASS_NAME,'title-wrapper')
                link = link_sel.get_attribute('href')
                self.open_new_tab(link_sel)
                # WebDriverWait(self.driver,5).until(lambda e: len(e.window_handles) > 1)
                standard_news = self.get_news_details()
                title = standard_news.get('title')
                summary = standard_news.get('summary')
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                self.latest_news.append(
                    {
                    'PublishDate':publish_date,
                    'Source': 'Contracting Business - Residential',
                    'Type': 'Industry News',
                    'Title': title,
                    'Summary': summary,
                    'Link': link
                    }
                )
        
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
        self.driver.switch_to.window(self.driver.window_handles[1])
        try:
            WebDriverWait(self.driver,10).until(EC.element_to_be_clickable((By.CLASS_NAME,'continue'))).click()
        except:
            pass
        WebDriverWait(self.driver,5).until(EC.presence_of_element_located((By.CLASS_NAME,'above-line')))
        html = self.driver.page_source
        self.soup = BeautifulSoup(html,'html.parser')
        sponsor_tag = self.get_label()
        extracted_title = self.soup.find('h1',class_='title-text').text.strip()
        summary = self.soup.find('div',class_='html').find('p').get_text(strip=True)
        if sponsor_tag == True:
            title = f'--SPONSORED NEWS POST-- {extracted_title}'
        else:
            title = extracted_title
        return ({'title':title,'summary':summary})
        
    def scrape(self):
        self.get_soup()

all_news = []        
def get_contracting_business(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url='https://www.contractingbusiness.com/residential-hvac'
    news=ContractingBusinessNews(driver,coverage_days,url)
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
get_contracting_business(driver,coverage_days=30)

time.sleep(10)
driver.quit()