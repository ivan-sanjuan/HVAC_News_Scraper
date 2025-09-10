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

class RefrigeratedFrozenFood:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)

    def get_soup(self):
        self.driver.get(self.url)
        try:
            WebDriverWait(self.driver,10).until(EC.element_to_be_clickable((By.CLASS_NAME,'close-olytics-image-bottom-mid'))).click()
        except:
            pass
        
    def scrape(self):
        self.get_soup()

def get_refrigerated_frozen_food(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://www.refrigeratedfrozenfood.com/'
    news = RefrigeratedFrozenFood(driver,coverage_days,url)
    news.scrape()

