from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import dateutil.parser
from datetime import datetime
import pandas as pd
import time


def get_natural_refrigerants_news(driver):
    driver.get('https://naturalrefrigerants.com/news/')
    WebDriverWait(driver, timeout=5).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'elementor-post')))

    html_data = driver.page_source
    soup = BeautifulSoup(html_data,'html.parser')
    news_section = soup.find('div', class_='elementor-posts-container')
    news_blocks = news_section.find_all('article', class_='elementor-post')

    latest_news = []
    for news in news_blocks:
        publish_date = news.find('time').text.strip()
        title = news.find('h2', class_='elementor-heading-title')
        link = title.find('a').get('href')
        summary = news.find('div', class_='elementor-widget-theme-post-excerpt')
        time_original_format = '%B %d, %Y'
        publish_date_obj = datetime.strptime(publish_date,time_original_format)
        time_new_format = '%Y-%m-%d'
        publish_date_formatted = datetime.strftime(publish_date_obj, time_new_format)
        
        latest_news.append(
            {
                'PublishDate': publish_date_formatted,
                'Source': 'Natural Refrigerants',
                'Title': title.text.strip(),
                'Summary': summary.text.strip(),
                'Link': link
            }
        )

    df = pd.DataFrame(latest_news)
    df.to_csv('csv/natural_refrigerants_news.csv', index=False)
    
    return latest_news

