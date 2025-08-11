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
        link_src = news.find('a', class_='tile__link').get('href')
        link = f'https://www.danfoss.com{link_src}'
        summary = news.find('div', class_='tile__text-description').find('span').text
        parsed_date = news.find('div', class_='tile__text-details_item').text.strip().split(maxsplit=1)[1]
        original_date_format = '%B %d, %Y'
        parsed_date_obj = datetime.strptime(parsed_date, original_date_format)
        new_date_format = '%Y-%m-%d'
        publish_date = datetime.strftime(parsed_date_obj, new_date_format)
        
        latest_news.append(
            {
                'Title': title.text.strip(),
                'Source': 'Danfoss',
                'Link': link,
                'Summary': summary.strip(),
                'PublishDate': publish_date
            }
        )
    
    df = pd.DataFrame(latest_news)
    df.to_csv('csv/danfoss_news.csv', index=False)