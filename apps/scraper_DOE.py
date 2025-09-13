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

class DOENews:
    def __init__(self,driver,coverage_days,url,source):
        self.driver = driver
        self.coverage = coverage_days
        self.url = url
        self.latest_news = []
        self.date_limit = datetime.today()-timedelta(days=self.coverage)
        self.source = source
        self.page_num = 1
    
    def get_soup(self):
        print(f'Opening: {self.source}')
        self.driver.get(self.url)
        while True:
            try:
                self.driver_wait(EC.presence_of_element_located((By.CLASS_NAME,'MuiList-root')))
                news_section = self.driver.find_element(By.CLASS_NAME,'MuiList-root')
                news_blocks = news_section.find_elements(By.CSS_SELECTOR,'li')
                for news in news_blocks:
                    self.driver_wait(lambda e: len(e.window_handles) == 1)
                    self.driver.execute_script("arguments[0].scrollIntoView();",news)
                    button = news.find_element(By.CSS_SELECTOR,'a')
                    link = button.get_attribute('href')
                    self.open_in_new_tab(button)
                    self.driver_wait(lambda e: len(e.window_handles) > 1)
                    self.driver.switch_to.window(self.driver.window_handles[1])
                    self.driver_wait(EC.presence_of_element_located((By.ID,'block-main-page-content')))
                    html = self.driver.page_source
                    soup = BeautifulSoup(html,'html.parser')
                    parsed_date = soup.find('span',class_='display-date').get_text(strip=True)
                    parsed_date_obj = datetime.strptime(parsed_date,'%B %d, %Y')
                    publish_date = parsed_date_obj.strftime('%Y-%m-%d')
                    if parsed_date_obj < self.date_limit:
                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])
                        return False
                    title = soup.find('div',class_='page-title-outside-hero').get_text(strip=True)
                    print(f'Fetching: {title}')
                    summary_block = soup.find('div',class_='field--type-text-long')
                    paragraphs = summary_block.find_all('p')
                    try:
                        for sum in paragraphs:
                            para = sum.get_text(strip=True)
                            if len(para) > 150:
                                summary = para
                                break
                            else:
                                continue
                        else:
                            summary = paragraphs[0].get_text(strip=True)
                    except IndexError:
                        summary = 'Unable to parse summary, please visit the news page instead.'
                    self.append(publish_date,title,summary,link)
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
                self.page_num += 1
                pagination = self.driver.find_element(By.CLASS_NAME,'MuiPagination-root')
                button = pagination.find_element(By.XPATH,f"//button[@aria-label='Go to page {self.page_num}']")
                button.click()
            except StaleElementReferenceException:
                pass
            
    def append(self,publish_date,title,summary,link):
        self.latest_news.append(
            {
            'PublishDate':publish_date,
            'Source': self.source,
            'Type': 'Industry News',
            'Title': title,
            'Summary': summary,
            'Link': link
            }
        )

    def open_in_new_tab(self,button):
        ActionChains(self.driver)\
            .key_down(Keys.CONTROL)\
                .click(button)\
                    .key_up(Keys.CONTROL)\
                        .perform()
    
    def scrape(self):
        self.get_soup()

    def driver_wait(self,condition):
        try:
            WebDriverWait(self.driver,10).until(condition)
        except:
            pass

sites = [
    {'url':'https://www.energy.gov/search?page=0&sort_by=date&f%5B0%5D=article_type%3A1&f%5B1%5D=content_type_rest%3Aarticle', 'source':'DOE - Press Release'},
    {'url':'https://www.energy.gov/search?page=0&f%5B0%5D=article_type%3A430939', 'source':'DOE - Testimony'},
    {'url':'https://www.energy.gov/search?page=0&f%5B0%5D=article_type%3A1380643', 'source':'DOE - Latest OpEds'}
]

all_news = []
def get_DOE(driver,coverage_days):
    driver.set_window_size(1920, 1080)
    for site in sites:
        url = site.get('url')
        src = site.get('source')
        news = DOENews(driver,coverage_days,url,src)
        news.scrape()
        all_news.extend(news.latest_news)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/DOE_news.csv',index=False)

