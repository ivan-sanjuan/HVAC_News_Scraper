from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.window import WindowTypes
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime
import pandas as pd
import re
import time

today = date.today()
yesterday = today-timedelta(days=-1)
def get_cooling_post_news(driver, coverage_date):
    driver.get('https://www.coolingpost.com/')
    
    latest_news = []
    WebDriverWait(driver, timeout=5).until(
        EC.presence_of_element_located((By.ID, 'main-content'))
    )
    href_world_news = driver.find_element(By.XPATH, '//*[@id="main-content"]/div/div[3]/div/div/h2/a').get_attribute('href')
    driver.switch_to.new_window(WindowTypes.TAB)
    driver.get(href_world_news)
    worldnews_html = driver.page_source
    worldnews_soup = BeautifulSoup(worldnews_html,'html.parser')
    WebDriverWait(driver, timeout=5).until(
        EC.presence_of_element_located((By.ID,'main-content'))
    )
    worldnews_block = worldnews_soup.find('div', id='main-content')
    worldnews_section = worldnews_block.find_all('div', class_='cl-element-section')
    for news in worldnews_section:
        parsed_date = news.find('div', class_='cl-element-published_date').text
        parsed_date_obj = datetime.strptime(re.sub(r'(\d+)(st|nd|rd|th)', r'\1', parsed_date), '%d %B %Y')
        worldnews_publish_date = parsed_date_obj.strftime('%Y-%m-%d')
        if parsed_date_obj.date() >= today-timedelta(days=coverage_date):
            worldnews_title=news.find('a', class_='cl-element-title__anchor')
            worldnews_link=worldnews_title.get('href')
            worldnews_summary=news.find('div', class_='cl-element-excerpt')
            latest_news.append(
                {
                    'PublishDate': worldnews_publish_date,
                    'Title': worldnews_title.text.strip(),
                    'Source': 'CoolingPost-World',
                    'Link': worldnews_link,
                    'Summary': worldnews_summary.text.strip()
                }
            )
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
            
    href_uknews = driver.find_element(By.XPATH, '//*[@id="main-content"]/div/div[5]/div/div/h2/a').get_attribute('href')
    driver.switch_to.new_window(WindowTypes.TAB)
    driver.get(href_uknews)
    uknews_html = driver.page_source
    uknews_soup = BeautifulSoup(uknews_html,'html.parser')
    WebDriverWait(driver, timeout=5).until(
        EC.presence_of_element_located((By.ID, 'main-content'))
    )
    uknews_block = uknews_soup.find('div', class_='cl-layout-container')
    uknews_section = uknews_block.find_all('div', class_='cl-element-section')
    for news in uknews_section:
        parsed_date = news.find('div', class_='cl-element-published_date').text
        parsed_date_obj = datetime.strptime(re.sub(r'(\d+)(st|nd|rd|th)', r'\1', parsed_date), '%d %B %Y')
        uknews_publish_date = parsed_date_obj.strftime('%Y-%m-%d')
        if parsed_date_obj.date() >= today-timedelta(days=coverage_date):
            uknews_title = news.find('a', class_='cl-element-title__anchor')
            uknews_link = uknews_title.get('href')
            uknews_summary = news.find('div', class_='cl-element-excerpt')
            latest_news.append(
                {
                    'PublishDate': uknews_publish_date,
                    'Title': uknews_title.text.strip(),
                    'Source': 'CoolingPost-UK',
                    'Link': uknews_link,
                    'Summary': uknews_summary.text.strip()
                }
            )
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    df = pd.DataFrame(latest_news)
    df.to_csv('csv/cooling_post_news.csv', index=False)
    
    return latest_news
            
options = Options()
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920x1080')
options.add_argument('--log-level=3')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115 Safari/537.36")

driver = webdriver.Chrome(options=options)
get_cooling_post_news(driver, coverage_date=15)

time.sleep(10)
driver.quit()
    