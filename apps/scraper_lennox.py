from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime
import pandas as pd
import time

class LennoxNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        self.root = 'https://investor.lennox.com/'
    
    def get_soup(self):
        print(f'📰Opening: Lennox')
        self.driver.get(self.url)
        self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'nir-widget--list')))
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        news_section = soup.find('div',class_='nir-widget--list')
        self.news_blocks = news_section.find_all('article')
        self.toggle_buttons = self.driver.find_elements(By.TAG_NAME,'article')
        
    def get_news(self):
        for news, toggle in zip(self.news_blocks, self.toggle_buttons):
            parsed_date = news.find('div',class_='nir-widget--news--date-time').text.strip()
            parsed_date_obj = datetime.strptime(parsed_date,'%B %d, %Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj >= self.date_limit:
                button = toggle.find_element(By.CLASS_NAME,'nir-widget--news--accordion-toggle')
                if button:
                    self.driver.execute_script("arguments[0].scrollIntoView();", button)
                button_clicked = False
                if not button_clicked:
                    button.click()
                    button_clicked = True
                    title = news.find('a',class_='nir-widget--news--accordion-toggle').text.strip()
                    print(title)
                    summary_section = news.find('div','nir-widget--news--teaser')
                    p_tag = summary_section.find('p')
                    if p_tag:
                        summary = news.find('div','nir-widget--news--teaser').find('p').text.strip()
                    else:
                        summary = news.find('div','nir-widget--news--teaser').text.strip()
                    link = news.find('div',class_='nir-widget--news--read-more')
                    if link:
                        link = link.find('a').get('href')
                    self.append(publish_date,title,summary,link)
    
    def append(self,publish_date,title,summary,link):
        print(f'Fetching: {title}')
        self.latest_news.append(
                        {
                        'PublishDate': publish_date,
                        'Source': 'Lennox',
                        'Type': 'Company News',
                        'Title': title,
                        'Summary': summary,
                        'Link': link
                        }
                    )
    
    def driver_wait(self,condition):
        try:
            WebDriverWait(self.driver,5).until(condition)
        except:
            pass
                
    def scrape(self):
        self.get_soup()
        self.get_news()

all_news = []
def get_lennox_news(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://investor.lennox.com/news-events/news-releases'
    news = LennoxNews(driver,coverage_days,url)
    news.scrape()
    all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df = df.drop_duplicates(subset=['Link'])
    df.to_csv('csv/lennox_news.csv', index=False)
    
options = Options()
# options.add_argument('--headless=new')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920x1080')
options.add_argument('--log-level=3')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H321 Safari/600.1.4")
options.page_load_strategy = 'eager'
driver = webdriver.Chrome(options=options)
get_lennox_news(driver,coverage_days=15)

time.sleep(5)
driver.quit()