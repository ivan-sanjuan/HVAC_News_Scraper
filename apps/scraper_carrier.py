from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime
import time
import pandas as pd

class CarrierNews:
    def __init__(self,driver,coverage_days,news_url,source):
        self.driver = driver
        self.coverage_days = coverage_days
        self.news_url = news_url
        self.source = source
        self.today = datetime.today()
        self.latest_news = []

    def get_soup(self):
        self.driver.get(self.news_url)
        print(f'Getting {self.source}')
        try:
            list_view = WebDriverWait(self.driver,2).until(
                EC.element_to_be_clickable((By.ID,'btn-listview'))
            )
            list_view.click()
            print('Selecing list view.')
            time.sleep(1)
        except:
            print(f'No list view detected')
            pass
        
        try:
            WebDriverWait(self.driver,10).until(
                EC.presence_of_element_located((By.CLASS_NAME,'newslist'))
            )
            html = self.driver.page_source
            soup = BeautifulSoup(html,'html.parser')
            news_section = soup.find('div',class_='newslist')
            if self.source == 'Carrier-Corporate':
                self.news_list = news_section.find_all('div',class_='card')
            else:
                news_block = news_section.find('div',class_='list-group')
                self.news_list = news_block.find_all('div',class_='pb-4')
            print('Getting news list')
        except:
            self.driver.close()
            print('Connection timed out.')
        
    def get_news(self):
        for news in self.news_list:
            if self.source == 'Carrier-Corporate':
                parsed_date = news.find('p',class_='card-subtitle').find('time',class_='date').text.strip()
                parsed_date_obj = datetime.strptime(parsed_date,'%B %d, %Y')
            else:
                parsed_date = news.find('p').find('time',class_='date').text.strip()
                parsed_date_obj = datetime.strptime(parsed_date,'%b. %d, %Y')

            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj >= self.today-timedelta(days=self.coverage_days):
                if self.source == 'Carrier-Corporate':
                    link_section = news.find('div',class_='card-body').find('a')
                    non_native_title = news.find('p',class_='card-text').text.strip()
                    link = link_section.get('href').strip().split('?')[0].rstrip('/')
                else:
                    link_section = news.find('a')
                    non_native_title = news.find('div',class_='h4').text.strip()
                    root_url = 'https://www.carrier.com'
                    extracted_url = link_section.get('href')
                    link = f'{root_url}{extracted_url}'
                    if link.startswith(('https://www.carrier.com/commercial/', 'https://www.carrier.com/residential/', 'https://www.carrier.com/truck-trailer/')):
                        self.driver.switch_to.new_window('tab')
                        self.driver.get(link)
                        WebDriverWait(self.driver,5).until(
                            EC.presence_of_element_located((By.CLASS_NAME,'card-body'))
                        )
                        html = self.driver.page_source
                        soup = BeautifulSoup(html,'html.parser')
                        title = soup.find('div',class_='card-body').find('h1').text.strip()
                        summary = soup.find('div',class_='card-text').find('p').text.strip()
                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])
                    elif link.startswith('https://www.carrier.com/carrier/en/worldwide/'):
                        self.driver.switch_to.new_window('tab')
                        self.driver.get(link)
                        WebDriverWait(self.driver,5).until(
                            EC.presence_of_element_located((By.CLASS_NAME,'card-text'))
                        )
                        html = self.driver.page_source
                        soup = BeautifulSoup(html,'html.parser')
                        title = soup.find('div',class_='card-title').text.strip()
                        try:
                            summary = soup.find('div',class_='card-text').find('p').get_text()
                        except:
                            summary = 'Failed to get summary, please visit the site instead.'
                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])
                    else:
                        title = non_native_title
                        summary = 'NO SUMMARY - LINK LEADS TO A DIFFERENT SITE; Visit the site for more information.'
                    
                if not any(item['Link'] == link for item in self.latest_news):
                    self.latest_news.append(
                            {
                        'PublishDate': publish_date,
                        'Source': self.source,
                        'Type': 'Company News',
                        'Title': title,
                        'Summary': summary,
                        'Link': link
                        }
                    )
                    
            
    def scrape(self):
        self.get_soup()
        self.get_news()
        
all_news = []
def get_carrier_news(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    sources = [
        {'url':'https://www.corporate.carrier.com/news/?typefilter=Press%20Releases','src':'Carrier-Corporate'},
        {'url':'https://www.carrier.com/residential/en/us/news/','src':'Carrier-Residential'},
        {'url':'https://www.carrier.com/commercial/en/us/news/','src':'Carrier-Commercial'},
        {'url':'https://www.carrier.com/truck-trailer/en/eu/news/','src':'Carrier-Transicold'}
        ]
    for news in sources:
        try:
            run = CarrierNews(driver,coverage_days,news['url'],news['src'])
            run.scrape()
            all_news.extend(run.latest_news)
        except Exception as e:
            print(f'Error scraping {news['src']}: {e}')
    df = pd.DataFrame(all_news)
    df.to_csv('csv/carrier_news.csv',index=False)
    return all_news

# options = Options()
# # options.add_argument('--headless=new')
# options.add_argument('--disable-gpu')
# options.add_argument('--window-size=1920x1080')
# options.add_argument('--log-level=3')
# options.add_argument("--disable-blink-features=AutomationControlled")
# options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115 Safari/537.36")
# driver = webdriver.Chrome(options=options)
# get_carrier_news(driver,coverage_days=16)

# time.sleep(10)
# driver.quit()