from selenium import webdriver
import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import dateutil.parser
from datetime import datetime, timedelta
import pandas as pd
import time

options = Options()
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920x1080')
options.add_argument('--log-level=3')
driver = webdriver.Chrome(options=options)
driver.get('https://www.tranetechnologies.com/en/index/news/news-archive.html')
WebDriverWait(driver, timeout=5).until(
    EC.presence_of_element_located((By.CLASS_NAME, 'newspromo__promos'))
)
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
news_block = soup.find('div', class_='newspromo__promos')
news_section = news_block.find_all('div', class_='newspromo__text')

latest_news = []
for news in news_section:
    parsed_date = news.find('p', class_='newspromo__date').text
    parsed_date_original_format = '%B %d, %Y'
    parsed_date_obj = datetime.strptime(parsed_date, parsed_date_original_format)
    today = datetime.today()
    parsed_date_new_format = '%Y-%m-%d'
    max_date_range = today-timedelta(days=30)
    if parsed_date_obj >= max_date_range:
        title = news.find('a', class_='newspromo__link')
        link = title.get('href')
        publish_date = datetime.strftime(parsed_date_obj, parsed_date_new_format)
        if title.get('target') == '_self':
            response = requests.get(link)
            html = response.text
            summary_soup = BeautifulSoup(html, 'html.parser')
            summary = summary_soup.find('p').text
        else:
            summary = 'Not Available'
            
            latest_news.append(
                {
                    'PublishDate': publish_date.strip(),
                    'Source': 'Trane Technologies',
                    'Title': title.text.strip(),
                    'Summary': summary[:100],
                    'Link': link
                }
            )
    
print(latest_news)

time.sleep(10)
driver.close()