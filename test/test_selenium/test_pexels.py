import re
import time

import wget as wget
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
import urllib

# This example requires Selenium WebDriver 3.13 or newer
# options = webdriver.ChromeOptions()
# prefs = {"download.default_directory": "d:\\temp"}
# example: prefs = {"download.default_directory" : "C:\Tutorial\down"};
# options.add_experimental_option("prefs", prefs)

exp = re.compile(r'external/(.*?)\?')
with webdriver.Chrome() as driver:
    # with webdriver.Chrome(chrome_options=options) as driver:
    wait = WebDriverWait(driver, 10)

    driver.get("https://www.pexels.com/videos/")
    results = driver.find_elements(By.CSS_SELECTOR,
                                   "div.photos>div.photos__column>div>article")
    times = 0
    for ele in results:
        source_ele = ele.find_element(By.CSS_SELECTOR,
                                       "a.js-photo-link>video.photo-item__video>source")

        url = source_ele.get_attribute('src')
        print(url)
        name = re.search(exp, url).group(1)
        print(name)
        wget.download(url, name)
        if times >= 0:
            break
        times += 1
        # # driver.get(ele.get_attribute('src'))
        time.sleep(1)
