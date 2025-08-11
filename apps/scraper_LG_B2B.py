from selenium import webdriver
import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd
import time

# def get_LG_B2B_news(driver):

options = Options()
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920x1080')
options.add_argument('--log-level=3')
driver = webdriver.Chrome(options=options)

driver.get('https://www.lgnewsroom.com/category/b2b/product-and-solutions/')
WebDriverWait(driver, timeout=5).until(
    EC.presence_of_element_located((By.CLASS_NAME, 'page_content'))
)

latest_news = []
try:
    highlighted_post = driver.find_element(By.CLASS_NAME, 'itembx')
    highlighted_post_link = highlighted_post.get_attribute('href')
    highlighted_post_driver = webdriver.Chrome(options=options)
    highlighted_post_driver.get(highlighted_post_link)
    html_highlighted_post = highlighted_post_driver.page_source
    highlighted_post_soup = BeautifulSoup(html_highlighted_post, 'html.parser')
    WebDriverWait(highlighted_post_driver, timeout=5).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'page_content'))
    )
    highlighted_post_content_block = highlighted_post_soup.find('div', class_='page_content')
    highlighted_post_title = highlighted_post_content_block.find('h2', class_='st_title')
    highlighted_post_p_tag = highlighted_post_content_block.find('p', style='text-align: justify;')
    highlighted_post_p_tag.strong.decompose()
    highlighted_post_summary = highlighted_post_content_block.find('p', style='text-align: justify;').text
    highlighted_post_parsed_date = highlighted_post_content_block.find('div', class_='date').text
    original_date_format = '%B %d, %Y'
    highlighted_post_parsed_date_obj = datetime.strptime(highlighted_post_parsed_date, original_date_format)
    new_date_format = '%Y-%m-%d'
    highlighted_post_publish_date = datetime.strftime(highlighted_post_parsed_date_obj, new_date_format)

    latest_news.append(
        {
        'Title': highlighted_post_title.text.strip(),
        'Source': 'LG B2B News',
        'Link': highlighted_post_link,
        'Summary': highlighted_post_summary.strip(),
        'PublishDate': highlighted_post_publish_date
        }
    )
    highlighted_post_driver.get('https://www.lgnewsroom.com/category/b2b/product-and-solutions/')
    
except Exception as e:
    print(f'An error has occured: {e}')
    


print(latest_news)


# get_LG_B2B_news(driver)

driver.quit()
time.sleep(10)