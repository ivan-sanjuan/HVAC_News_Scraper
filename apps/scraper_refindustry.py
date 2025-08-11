from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime
import pandas as pd
import time

today = date.today()
yesterday = today-timedelta(days=1)

def get_refindustry_news(driver):
    driver.get('https://refindustry.com/news/')

    WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'posts_new'))
        )

    html_data = driver.page_source
    soup = BeautifulSoup(html_data, 'html.parser')
    news_section = soup.find('div', class_='posts_new')
    news_blocks = news_section.find_all('a', class_='post_new _post_news_status')

    latest_news = []
    for news in news_blocks:
        title = news.find('div', class_='post_title').text
        summary = news.find('div', class_='post_descr')
        link = news.get('href')
        parsed_date = news.find('div', class_='post_bot_text').text
        if parsed_date == 'today':
            publish_date = today
        elif parsed_date == 'yesterday':
            publish_date = yesterday
        else:
            original_format = '%d %b %Y'
            original_format_date_obj = datetime.strptime(parsed_date, original_format)
            new_format = '%Y-%m-%d'
            publish_date = original_format_date_obj.strftime(new_format)
        
        latest_news.append(
            {
                'PublishDate': publish_date,
                'Source': 'RefIndustry',
                'Title': title.strip(),
                'Summary': summary.text.strip(),
                'Link': link
            }
        )

    df = pd.DataFrame(latest_news)
    df.to_csv('csv/ref_industry_news.csv', index=False)
    
    return latest_news
