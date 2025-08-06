from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import pandas as pd
import csv
import time

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920x1080')
options.add_argument('--log-level=3')

driver = webdriver.Chrome(service=Service(), options=options)
driver.get('https://refindustry.com/news/')
title = driver.title
driver.implicitly_wait(0.5)

WebDriverWait(driver, 5).until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, 'posts_new'))
)

news_block = driver.find_element(By.CLASS_NAME, 'posts_new')
news_title = news_block.find_elements(By.CLASS_NAME, 'post_new')

latest_news = []
for i in news_title:
    titles = i.find_element(By.CLASS_NAME, 'post_title')
    short_text = i.find_element(By.CLASS_NAME, 'post_descr')
    news_link = i.get_attribute('href')
    latest_news.append({
        'Titles': titles.text,
        'Short Description': short_text.text,
        'Links': news_link
    })
    
    df = pd.DataFrame(latest_news)
    df.to_csv('latest_news.csv', index=False)
    
time.sleep(10)
