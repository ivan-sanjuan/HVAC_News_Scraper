from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
import threading
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
import pandas as pd
import time

class ACRJournal:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)

    def get_soup(self):
        self.driver.get(self.url)
        try:
            WebDriverWait(self.driver,5).until(EC.element_to_be_clickable((By.ID,'accept-btn'))).click()
        except:
            pass
        popup_thread = threading.Thread(
            target=self.popup_watcher,
            args=((By.CLASS_NAME,'modal-content'),),
            daemon=True
        )
        popup_thread.start()
        
    def popup_watcher(self,selector):
        start_time = time.time()
        timeout = 30
        interval = 1
        while time.time()-start_time < timeout:
            try:
                popup = self.driver.find_element(*selector)
                if popup.is_displayed():
                    print('Pop-up detected.')
                    close_btn = popup.find_element(By.LINK_TEXT,'Dismiss')
                    close_btn.click()
                    print('Pop-up closed.')
                    return True
            except (NoSuchElementException, StaleElementReferenceException):
                pass
            time.sleep(interval)
        print('No pop-up detected within timeout.')
        return False
        
    def scrape(self):
        self.get_soup()
        # self.get_news()

def get_acr_journal(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url='https://www.acrjournal.uk/news'
    news = ACRJournal(driver,coverage_days,url)
    news.scrape()

options = Options()
# options.add_argument('--headless=new')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920x1080')
options.add_argument('--log-level=3')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115 Safari/537.36")
driver = webdriver.Chrome(options=options)
get_acr_journal(driver,coverage_days=10)

time.sleep(10)
driver.quit()