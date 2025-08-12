from selenium import webdriver
import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver.common.window import WindowTypes
from datetime import datetime, timedelta
import pandas as pd
import time

def get_LG_B2B_news(driver):
    url = 'https://www.lgnewsroom.com/category/b2b/product-and-solutions/'
    driver.get(url)
    WebDriverWait(driver, timeout=5).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'page_content'))
    )
    news_section = driver.find_element(By.CLASS_NAME, 'page_content')
    highlighted_post = news_section.find_element(By.CLASS_NAME, 'sticky_post')
    window_handles = driver.window_handles
    hlight_link = highlighted_post.find_element(By.CLASS_NAME, 'itembx').get_attribute('href')
    home_html = driver.page_source
    home_soup = BeautifulSoup(home_html, 'html.parser')
    news_blocks = home_soup.find_all('div', class_='bs_ps_item')
    
    latest_news = []
    def get_news_details(link):
        driver.switch_to.new_window(WindowTypes.TAB)
        driver.get(link)
        WebDriverWait(driver, timeout=5).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'page_content'))
        )
        html = driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        page_content = soup.find('div', class_='page_content')
        try:
            title = page_content.find('h2', class_='st_title')
            summary_group = page_content.find('div', class_='single_cont')
            p_tag_summary = summary_group.find('p', style='text-align: justify;')
            if p_tag_summary.strong:
                p_tag_summary.strong.decompose()
            summary = p_tag_summary.text
            parsed_date = page_content.find('div', class_='date').text
            original_format = '%B %d, %Y'
            parsed_date_obj = datetime.strptime(parsed_date,original_format)
            new_date_format = '%Y-%m-%d'
            publish_date = datetime.strftime(parsed_date_obj,new_date_format)
            driver.close()
            driver.switch_to.window(window_handles[0])
            
        except Exception as e:
            print(f'An error has occured: {e}')
            
        latest_news.append(
                {
                'Title': title.text.strip(),
                'Source': 'LG B2B',
                'Link': link,
                'Summary': summary.strip(),
                'PublishDate': publish_date
                }
            )
        
    get_news_details(hlight_link)
    
    for news_links in news_blocks:
        link = news_links.find('a', class_='itembx').get('href')
        get_news_details(link)
     
    df = pd.DataFrame(latest_news)
    df.to_csv('csv/LG_B2B_news.csv', index=False)
    
    return latest_news