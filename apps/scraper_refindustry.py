from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from datetime import date, timedelta
import pandas as pd
import time

today = date.today()
yesterday = today-timedelta(days=1)

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920x1080')
options.add_argument('--log-level=3')

def get_ref_industry():
    driver = webdriver.Chrome(service=Service(), options=options)
    driver.get('https://refindustry.com/news/')

    WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'posts_new'))
    )

    news_block = driver.find_element(By.CLASS_NAME, 'posts_new')
    news_title = news_block.find_elements(By.CLASS_NAME, 'post_new')
    publish_date = news_block.find_element(By.CLASS_NAME, 'post_bot_text')

    latest_news = []
    for i in news_title:
        publish_date = i.find_element(By.CLASS_NAME, 'post_bot_text').text
        if publish_date == 'today':
            date_today = today
            publish_date = date_today.strftime("%B %d, %Y")
        elif publish_date == 'yesterday':
            date_yesterday = yesterday
            publish_date = date_yesterday.strftime("%B %d, %Y")
        else:
            publish_date = publish_date.strftime("%B %d, %Y")
            
            
        titles = i.find_element(By.CLASS_NAME, 'post_title')
        short_text = i.find_element(By.CLASS_NAME, 'post_descr')
        news_link = i.get_attribute('href')
        latest_news.append({
            'PublishDate': publish_date,
            'Source': 'Refindustry',
            'Title': titles.text,
            'Summary': short_text.text,
            'Link': news_link
        })
    
    df = pd.DataFrame(latest_news)
    df.to_csv('ref_industry_news.csv', index=False)
        
    time.sleep(10)
