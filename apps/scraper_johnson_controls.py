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

class JohnsonControlsNews:
    def __init__(self,driver,coverage_days,url):
        self.driver = driver
        self.coverage_days = coverage_days
        self.url = url
        self.latest_news = []
    
    def click_accept_all(self, timeout=30):
        try:
            # Step 1: Detect and switch to iframe (if present)
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            for iframe in iframes:
                self.driver.switch_to.frame(iframe)
                try:
                    # Step 2: Wait for footer to appear inside iframe
                    footer = WebDriverWait(self.driver, timeout).until(
                        EC.visibility_of_element_located((By.ID, 'ta-overlay-footer'))
                    )

                    # Step 3: Locate Accept All button
                    accept_btn = footer.find_element(By.XPATH, "//button[contains(@class, 'trustarc-acceptall-btn') and contains(text(), 'Accept All')]")
                    print("✅ Found Accept button:", accept_btn.text)

                    # Step 4: Scroll into view
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", accept_btn)

                    # Step 5: Wait for clickability
                    WebDriverWait(self.driver, timeout).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'trustarc-acceptall-btn') and contains(text(), 'Accept All')]"))
                    )

                    # Step 6: Force-click using JavaScript
                    self.driver.execute_script("""
                        const btn = arguments[0];
                        btn.style.display = 'block';
                        btn.style.visibility = 'visible';
                        btn.style.opacity = 1;
                        btn.click();
                    """, accept_btn)

                    print("🎯 Cookie overlay accepted.")
                    return  # Exit after successful click

                except Exception:
                    self.driver.switch_to.default_content()  # Try next iframe
                    continue

            print("❌ Accept All button not found in any iframe.")

        except Exception as e:
            print(f"❌ Failed to click Accept All: {e}")
        
    def get_soup(self):
        print(f'📰Opening: Johnson Controls')
        self.driver.get(self.url)
        self.click_accept_all()
        time.sleep(5)
        WebDriverWait(self.driver,30).until(
            EC.presence_of_element_located((By.CLASS_NAME,'search-wrap-text'))
        )
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        self.news_blocks = soup.find_all('div',class_='search-wrap-text')

    def get_news(self):
        for news in self.news_blocks:
            parsed_date = news.find('div',class_='mediacenter__date').text.strip()
        print(parsed_date)
        
    def scrape(self):
        self.get_soup()
        

def get_johnsonControls_news(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    url = 'https://www.johnsoncontrols.com/media-center/news#sort=%40insightdate%20descending'
    news = JohnsonControlsNews(driver,coverage_days,url)
    news.scrape()

options = Options()
# options.add_argument('--headless=new')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920x1080')
options.add_argument('--log-level=3')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115 Safari/537.36")
driver = webdriver.Chrome(options=options)
get_johnsonControls_news(driver,coverage_days=30)

driver.quit()
time.sleep(10)