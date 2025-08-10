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

def get_trane_news(driver):
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
        max_date_range = today-timedelta(days=60)
        if parsed_date_obj >= max_date_range:
            title = news.find('a', class_='newspromo__link')
            link = title.get('href')
            publish_date = datetime.strftime(parsed_date_obj, parsed_date_new_format)
            try:
                if title.get('target') == '_self':
                    options = Options()                    
                    options.add_argument('--disable-gpu')
                    options.add_argument('--window-size=1920x1080')
                    options.add_argument('--log-level=3')
                    link_driver = webdriver.Chrome(options=options)
                    link_driver.get(link)
                    WebDriverWait(link_driver, timeout=5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'p'))
                    )
                    html_link = link_driver.page_source
                    summary_soup = BeautifulSoup(html_link, 'html.parser')
                    p_tag = summary_soup.find('div', class_='q4default')
                    p_tag.span.decompose()
                    summary = p_tag.find('p').text.strip()
                    link_driver.close()
                    time.sleep(2)
                else:
                    summary = 'Not Available -- Link leads to another site.'
            
                latest_news.append(
                    {
                        'PublishDate': publish_date.strip(),
                        'Source': 'Trane Technologies',
                        'Title': title.text.strip(),
                        'Summary': summary,
                        'Link': link
                    }
                )
                df = pd.DataFrame(latest_news)
                df.to_csv('csv/trane_technologies_news.csv', index=False)
                
            except Exception as e:
                print(f'An error has occured: {e}')
                
    return latest_news