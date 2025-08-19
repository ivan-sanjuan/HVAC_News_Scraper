from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.window import WindowTypes
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime
import pandas as pd
import time

def get_refindustry_news(driver, coverage_days):
    page_num = 1
    conditions_met = False
    latest_news = []
    today = date.today()
    yesterday = today-timedelta(days=1)
    while True:
        if page_num == 1:
            driver.get('https://refindustry.com/news/')
        else:
            driver.execute_script(f'goToPage({page_num})')
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'posts_new'))
                )
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            news_section = soup.find('div', class_='posts_new')
            news_blocks = news_section.find_all('a', class_='post_new')
            for news in news_blocks:
                parsed_date = news.find('div', class_='post_bot_text').text
                if parsed_date == 'today':
                    publish_date = today
                elif parsed_date == 'yesterday':
                    publish_date = yesterday
                else:
                    old_format = '%d %b %Y'
                    parsed_date_obj = datetime.strptime(parsed_date, old_format)
                    publish_date = parsed_date_obj.strftime('%Y-%m-%d')
                    max_date_range = today-timedelta(days=coverage_days)
                    if parsed_date_obj.date() >= max_date_range:
                        link = news.get('href')
                        driver.switch_to.new_window(WindowTypes.TAB)
                        driver.get(link)
                        news_soup = BeautifulSoup(driver.page_source, 'html.parser')
                        title = news_soup.find('h1', class_='page-title_new')
                        WebDriverWait(driver, timeout=5).until(
                            EC.presence_of_element_located((By.CLASS_NAME, 'news-detail-full-text-block_new'))
                        )
                        summary_div = news_soup.find('div', class_='news-detail-full-text-block_new')
                        if summary_div:
                            summary_p = summary_div.find('p')
                            if summary_p:
                                summary = summary_p.get_text(strip=True)
                            else:
                                summary = summary_div.get_text(strip=True)
                        else:
                            summary = None
                        
                        latest_news.append(
                            {
                            'PublishDate': publish_date,
                            'Title': title.text.strip(),
                            'Source': 'Ref Industry',
                            'Link': link,
                            'Summary': summary
                            }
                        )
                        
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                    else:
                        conditions_met = True
                        break

            if conditions_met == True:
                break
        
        page_num += 1
            
    print(latest_news)
    
    df = pd.DataFrame(latest_news)
    df.to_csv('csv/ref_industry_news.csv', index=False)
    return latest_news