from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
import re
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
import pandas as pd
import time

class BSRIANews:

def get_BSRIA(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://www.bsria.com/uk/news/'
    news = BSRIANews(driver,coverage_days,url)
    news.scrape()

options = Options()
# options.add_argument('--headless=new')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920x1080')
options.add_argument('--log-level=3')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115 Safari/537.36")
driver = webdriver.Chrome(options=options)
get_BSRIA(driver,coverage_days=30)

driver.quit()