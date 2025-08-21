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

class LGNews:
    def __init__(self,driver,coverage_days,news_url,source):
        self.driver = driver
        self.coverage_days = coverage_days
        self.news_url = news_url
        self.latest_news = []
        self.today = datetime.today()
        self.source = source

    def get_highlight_soup(self):
        WebDriverWait(self.driver,5).until(
            EC.presence_of_element_located((By.CLASS_NAME,'page_content'))
        )
        html = self.driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        article = soup.find('div',class_='page_content')
        parsed_date = article.find('div',class_='date').text
        parsed_date_obj = datetime.strptime(parsed_date,'%B %d, %Y')
        publish_date = parsed_date_obj.strftime('%Y-%m-%d')
        if parsed_date_obj >= self.today-timedelta(days=self.coverage_days):
            title = article.find('h2',class_='st_title').text.strip()
            summary_block = article.find('p',style='text-align: justify;')
            summary_block.strong.decompose()
            summary = summary_block.text.strip()
            self.latest_news.append(
                {
                'PublishDate': publish_date,
                'Source': self.source,
                'Title': title,
                'Summary': summary,
                'Link': self.hlink
                }
            )
        self.driver.back()
        
    def get_blocks_soup(self):
        home_html=self.driver.page_source
        home_soup=BeautifulSoup(home_html,'html.parser')
        news_section = home_soup.find('div', class_='bs_psbx')
        news_blocks = news_section.find_all('a', class_='post')
        for news in news_blocks:
            self.link = news.get('href')
            self.driver.switch_to.new_window('tab')
            self.driver.get(self.link)
            WebDriverWait(self.driver,5).until(
                EC.presence_of_element_located((By.CLASS_NAME,'page_content'))
            )
            html = self.driver.page_source
            soup = BeautifulSoup(html,'html.parser')
            article = soup.find('div',class_='page_content')
            parsed_date = article.find('div',class_='date').text.strip()
            parsed_date_obj = datetime.strptime(parsed_date,'%B %d, %Y')
            publish_date = parsed_date_obj.strftime('%Y-%m-%d')
            if parsed_date_obj >= self.today-timedelta(days=self.coverage_days):
                title = article.find('h2',class_='st_title').text.strip()
                summary_block = article.find('p',style='text-align: justify;')
                summary_block.strong.decompose()
                summary = summary_block.text.strip()
                self.latest_news.append(
                    {
                    'PublishDate': publish_date,
                    'Source': self.source,
                    'Title': title,
                    'Summary': summary,
                    'Link': self.link
                    }
                )
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            
    def get_news(self):
        self.driver.get(self.news_url)
        highlighted_news = WebDriverWait(self.driver,5).until(
            EC.presence_of_element_located((By.CLASS_NAME,'itembx'))
        )
        self.hlink = highlighted_news.get_attribute('href')
        highlighted_news.click()
        self.get_highlight_soup()
        self.get_blocks_soup()
        
    def scrape(self):
        self.get_news()

all_news = []
def get_LG_B2B_news(driver,coverage_days):
    corporate_url = 'https://www.lgnewsroom.com/category/news/corporate/'
    appliance_solution_url = 'https://www.lgnewsroom.com/category/news/home-appliances-solution/'
    entertainment_url = 'https://www.lgnewsroom.com/category/news/media-entertainment-solution/'
    vehicle_solutions_url = 'https://www.lgnewsroom.com/category/news/vehicle-solution/'
    eco_solutions_url = 'https://www.lgnewsroom.com/category/news/eco-solution/'
    statements_url = 'https://www.lgnewsroom.com/category/news/statements/'
    corporate_source = 'LG-Corporate'
    appliance_solution_source = 'LG-ApplianceSolution'
    entertainment_source = 'LG-Entertainment'
    vehicle_solutions_source = 'LG-VehicleSolutions'
    eco_solutions_source = 'LG-EcoSolutions'
    statements_source = 'LG-Statements'
    corporate = LGNews(driver,coverage_days,corporate_url,corporate_source)
    appliance = LGNews(driver,coverage_days,appliance_solution_url,appliance_solution_source)
    entertainment = LGNews(driver,coverage_days,entertainment_url,entertainment_source)
    vehicle_solutions = LGNews(driver,coverage_days,vehicle_solutions_url,vehicle_solutions_source)
    eco_solutions = LGNews(driver,coverage_days,eco_solutions_url,eco_solutions_source)
    statements = LGNews(driver,coverage_days,statements_url,statements_source)
    corporate.scrape()
    appliance.scrape()
    entertainment.scrape()
    vehicle_solutions.scrape()
    eco_solutions.scrape()
    statements.scrape()
    latest_news_list = [
        corporate.latest_news,
        appliance.latest_news,
        entertainment.latest_news,
        vehicle_solutions.latest_news,
        eco_solutions.latest_news,
        statements.latest_news,
    ]
    for category in latest_news_list:
        all_news.extend(category)
    df = pd.DataFrame(all_news)
    df.to_csv('csv/LG_News.csv', index=False)

    return all_news