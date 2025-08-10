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

def get_danfoss_news(driver):
    driver.get('https://www.danfoss.com/en/about-danfoss/news/?pageSize=10&sort=startDate_desc')
    
    def handle_cookie_popup(driver):
        try:
            consent_button = WebDriverWait(driver, timeout=5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Decline all')]"))
            )
            consent_button.click()
            print('COOKIE POP-UP DETECTED, Declined all.')
        except:
            print('no cookie popup detected.')

    handle_cookie_popup(driver)
    
    WebDriverWait(driver, timeout=5).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'news-list-items'))
    )
    
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    news_block = soup.find('ul', class_='tile-group')
    news_sections = news_block.find_all('li', class_='tile')

    latest_news = []
    for news in news_sections:
        title = news.find('div', class_='tile__text-title')
        
        latest_news.append(
            {
                'Title': title.text.strip()
            }
        )
    
    print(latest_news)

options = Options()
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920x1080')
options.add_argument('--log-level=3')
driver = webdriver.Chrome(options=options)
get_danfoss_news(driver)


driver.quit()
time.sleep(10)