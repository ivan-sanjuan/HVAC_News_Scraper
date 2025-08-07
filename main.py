from apps.scraper_coolingpost import get_cooling_post_news
from apps.scraper_refindustry import get_refindustry_news
from apps.scraper_natural_refrigerants import get_natural_refrigerants_news
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import pandas as pd

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920x1080')
options.add_argument('--log-level=3')

driver = webdriver.Chrome(options=options)

scrapers = [
    get_cooling_post_news,
    get_refindustry_news
]

try:
    for scraper in scrapers:
        scraper(driver)
        time.sleep(2)
finally:
    driver.quit()

df1 = pd.read_csv('csv/ref_industry_news.csv')
df2 = pd.read_csv('csv/cooling_post_news.csv')

combined_df = pd.concat([df1, df2], ignore_index=True)

combined_df.to_csv('combined_news.csv', index=False)