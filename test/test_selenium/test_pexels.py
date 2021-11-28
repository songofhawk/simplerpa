import re
import time

import wget as wget
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
import urllib
import pandas as pd

# This example requires Selenium WebDriver 3.13 or newer
# options = webdriver.ChromeOptions()
# prefs = {"download.default_directory": "d:\\temp"}
# example: prefs = {"download.default_directory" : "C:\Tutorial\down"};
# options.add_experimental_option("prefs", prefs)

exp_img = re.compile(r'videos/\d+/(.*?)\?')
exp_video = re.compile(r'external/(.*?)\?')
with webdriver.Chrome() as driver:
    # with webdriver.Chrome(chrome_options=options) as driver:
    wait = WebDriverWait(driver, 10)

    driver.get("https://www.pexels.com/videos/")
    results = driver.find_elements(By.CSS_SELECTOR,
                                   "div.photos>div.photos__column>div>article")
    times = 0
    df = pd.DataFrame(columns=['title', 'img_name', 'video_name'])
    for ele in results:
        title = ele.get_attribute('data-meta-title')
        print(title)
        img_ele = ele.find_element(By.CSS_SELECTOR,
                                   "a.js-photo-link>img.photo-item__img")
        img_url = img_ele.get_attribute('src')
        print(img_url)
        img_name = re.search(exp_img, img_url).group(1)
        print(img_name)
        wget.download(img_url, img_name)

        source_ele = ele.find_element(By.CSS_SELECTOR,
                                      "a.js-photo-link>video.photo-item__video>source")

        video_url = source_ele.get_attribute('src')
        # print(video_url)

        video_name = re.search(exp_video, video_url).group(1)
        print(video_name)
        wget.download(video_url, video_name)

        df = df.append({title, img_name, video_name}, ignore_index=True)
        if times >= 0:
            break
        times += 1
        # # driver.get(ele.get_attribute('src'))
        time.sleep(1)

    with open('result.csv', 'a', encoding="utf-8", newline='') as f:
        df.to_csv(f, header=f.tell() == 0)
