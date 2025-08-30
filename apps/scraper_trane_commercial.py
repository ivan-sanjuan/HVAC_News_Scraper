from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime
import pandas as pd
import time
import requests
import json

class TraneCommercial:
    def __init__(self,driver,coverage_days):
        self.driver = driver
        self.coverage_days = coverage_days
        self.latest_news = []

    def fetch_news_from_api(self):
        url = "https://prod-cdn.us.yextapis.com/v2/accounts/me/search/vertical/query"
        params = {
            "experienceKey": "tc-newsroom--en",
            "api_key": "27e22603a683c838c1cb79efe4e5e892",
            "v": "20220511",
            "version": "PRODUCTION",
            "locale": "en",
            "input": "",
            "verticalKey": "newsroom",
            "limit": 21,
            "offset": 0,
            "retrieveFacets": "true",
            "facetFilters": "{}",
            "session_id": "e57dd3b0-9396-464b-b743-91b7753ba094",
            "sessionTrackingEnabled": "true",
            "sortBys": "[]",
            "referrerPageUrl": "",
            "source": "STANDARD",
            "jsLibVersion": "v1.17.9"
        }
        response = requests.get(url,params=params)
        data = response.json()
        print(data)
        
    def scrape(self):
        self.fetch_news_from_api()

def get_trane_commercial(driver,coverage_days):
    news = TraneCommercial(driver,coverage_days)
    news.scrape()

options = Options()
# options.add_argument('--headless=new')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920x1080')
options.add_argument('--log-level=3')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115 Safari/537.36")
driver = webdriver.Chrome(options=options)
get_trane_commercial(driver,coverage_days=120)