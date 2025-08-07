from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import dateutil.parser
from datetime import datetime
import pandas as pd
import time

options = Options()
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920x1080')
options.add_argument('--log-level=3')

def get_coolingpost():
    driver = webdriver.Chrome(options=options)
    driver.get('https://www.coolingpost.com/')

    WebDriverWait(driver, timeout=5).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'cl-element-title__anchor'))
    )

    main_content = driver.find_element(By.ID, 'main-content')
    news_blocks = main_content.find_elements(By. CLASS_NAME, 'cl-layout-container')

    latest_news = []
    for news in news_blocks:
        title = news.find_element(By.CLASS_NAME,'cl-element-title__anchor')
        summary = news.find_element(By.CLASS_NAME, 'cl-element-excerpt')
        publish_date = news.find_element(By.CLASS_NAME, 'cl-element-published_date').text
        formatted_date = dateutil.parser.parse(publish_date)
        formatted_date_output = formatted_date.strftime("%B %d, %Y")
        link = title.get_attribute('href')
        
        latest_news.append({
            'PublishDate': formatted_date_output,
            'Source': 'Cooling Post',
            'Title': title.text,
            'Summary': summary.text,
            'Link': link
        })
        
        df = pd.DataFrame(latest_news)
        df.to_csv('cooling_post_news.csv', index=False)
        
    time.sleep(10)