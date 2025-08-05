from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

driver = webdriver.Chrome()
# driver.get('https://refindustry.com/news/')
driver.get('https://www.selenium.dev/selenium/web/web-form.html')
title = driver.title

print(title)