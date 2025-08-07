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

driver = webdriver.Chrome()
driver.get('https://naturalrefrigerants.com/news/')

WebDriverWait(driver, timeout=5).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'elementor-post')))

news_section = driver.find_element(By.CLASS_NAME, 'elementor-posts-container')
news_blocks = news_section.find_elements(By.CLASS_NAME, 'elementor-post')

latest_news = []
for news in news_blocks:
    
    title = news.find_element(By.CSS_SELECTOR, "h2.elementor-heading-title.elementor-size-default a")
    summary = news.find_element(By.CLASS_NAME, 'elementor-widget-container')
    link_location = news.find_element(By.CSS_SELECTOR, 'div > a')
    link = link_location.get_attribute('href')
    publish_date = news.find_element(By.CLASS_NAME, 'elementor-post-info')

    latest_news.append(
        {
        'PublishDate': publish_date.text,
        'Source': 'Natural Refrigerants',
        'Title': title.text,
        'Summary': summary.text,
        'Link': link
        }
    )

df = pd.DataFrame(latest_news)
df.to_csv('natural_refrigerants_news.csv', index=False)


time.sleep(10)
