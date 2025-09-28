def user_agents():
    user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.90 Mobile Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 16_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Mobile/15E148 Safari/604.1"
    ]
    return user_agents

# ------------DESKTOP------------
# options = Options()
# # options.add_argument('--headless=new')
# options.add_argument('--disable-gpu')
# options.add_argument('--window-size=1920x1080')
# options.add_argument('--log-level=3')
# options.add_argument("--disable-blink-features=AutomationControlled")
# options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36")
# options.page_load_strategy = 'eager'
# driver = webdriver.Chrome(options=options)
# get_IEA(driver,coverage_days=25)

# time.sleep(5)
# driver.quit()

# ------------MOBILE------------
# options = Options()
# options.add_argument('--headless=new')
# options.add_argument('--disable-gpu')
# options.add_argument('--window-size=1920x1080')
# options.add_argument('--log-level=3')
# options.add_argument("--disable-blink-features=AutomationControlled")
# options.add_argument("user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H321 Safari/600.1.4")
# options.page_load_strategy = 'eager'
# driver = webdriver.Chrome(options=options)
# get_climate_control_news(driver,coverage_days=15)

# time.sleep(5)
# driver.quit()