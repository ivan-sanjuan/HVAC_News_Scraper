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

options = Options()
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920x1080')
options.add_argument('--log-level=3')

driver = webdriver.Chrome(options=options)
driver.get('https://naturalrefrigerants.com/news/')
WebDriverWait(driver, timeout=5).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'elementor-post')))

html_data = driver.page_source
soup = BeautifulSoup(html_data,'html.parser')
news_section = soup.find('div', class_='elementor-posts-container')
news_blocks = news_section.find_all('article', class_='elementor-post')
news_block_selenium = driver.find_elements(By.CLASS_NAME, 'ecs-posts')

latest_news = []
for news in news_blocks:
    title = news.find('a').text.strip()
    for sel_news in news_block_selenium:
        summary_element = sel_news.find_element(By.CSS_SELECTOR, 'a')
        summary = driver.execute_script('return arguments[0].textContent;', summary_element)
    
    latest_news.append(
        {
            'Title': title,
            'Summary': summary,
        }
    )

print(latest_news)

time.sleep(10)
driver.close()



