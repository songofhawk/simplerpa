from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located

#This example requires Selenium WebDriver 3.13 or newer
with webdriver.Chrome() as driver:
    wait = WebDriverWait(driver, 10)
    driver.get("https://www.pexels.com/videos/")
    results = driver.find_elements(By.CSS_SELECTOR, "div.photos>div.photos__column>div>article>a.js-photo-link>video.photo-item__video>source")
    for ele in results:
        print(ele.get_attribute('src'))
