from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import re
import dateutil.parser
from datetime import datetime, date, timedelta
import pandas as pd
import time

today = date.today()
yesterday = today-timedelta(days=-1)

def get_cooling_post_news(driver):
    driver.get('https://www.coolingpost.com/')

    WebDriverWait(driver, timeout=5).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'cl-element-title__anchor'))
    )

    html_data = driver.page_source
    soup = BeautifulSoup(html_data, 'html.parser')
    news_section = soup.find('div', id='main-content')
    news_block = news_section.find_all('div', class_='cl-template--image-top')

    latest_news = []
    for news in news_block:
        title = news.find('a', class_='cl-element-title__anchor')
        summary = news.find('div', class_='cl-element-excerpt')
        link = title.get('href')
        parsed_date = news.find('div', 'cl-element-published_date').text
        parsed_date_cleaned = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', parsed_date)
        old_format = '%d %B %Y'
        new_format = '%Y-%m-%d'
        parsed_date_formatted = datetime.strptime(parsed_date_cleaned, old_format)
        publish_date = datetime.strftime(parsed_date_formatted, new_format)
        
        latest_news.append(
            {
                'PublishDate': publish_date,
                'Source': 'Cooling Post',
                'Title': title.text.strip(),
                'Summary': summary.text.strip(),
                'Link': link
            }
        )
        
    df = pd.DataFrame(latest_news)
    df.to_csv('csv/cooling_post_news.csv', index=False)

    return latest_news