import os
import re
import time
from option import Option

import pandas as pd
import wget as wget
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import download

__author__ = 'Song Hui'  # 作者名


def get_options_from_command_line():
    import argparse
    # Initialize parser
    parser = argparse.ArgumentParser()

    # Adding optional argument
    parser.add_argument("-o", "--output_dir", help="to set directory of all output files")
    parser.add_argument("-r", "--result_file", help="to set result CSV file name")
    parser.add_argument("-l", "--limit", help="to set max file count")

    # Read arguments from command line
    args = parser.parse_args()

    if args:
        print("parsing arguments: {}".format(args))
    return Option(args.output_dir, args.result_file, int(args.limit))


if __name__ == '__main__':
    # 获取命令行参数
    option = get_options_from_command_line()

    if not os.path.exists(option.output_dir):
        os.mkdir(option.output_dir)
    # 设置从url中获取名字的正则表达式
    exp_img = re.compile(r'videos/\d+/(.*?)\?')
    exp_video = re.compile(r'external/(.*?)\?')

    web_options = webdriver.ChromeOptions()
    web_options.add_argument("--enable-javascript")
    # web_options.add_argument('--always-authorize-plugins=true')
    with webdriver.Chrome(options=web_options) as driver:
        # with webdriver.Chrome(chrome_options=options) as driver:
        wait = WebDriverWait(driver, 10)

        # 访问首页
        driver.get("https://www.pexels.com/videos/")
        # 获取所有视频描述节点
        results = []
        while len(results) < option.limit:
            results = driver.find_elements(By.CSS_SELECTOR,
                                           "div.photos>div.photos__column>div>article")
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            time.sleep(5)

        times = 0
        # 准备数据表
        df = pd.DataFrame(columns=['title', 'img_name', 'video_name'])
        for ele in results:
            title = ele.get_attribute('data-meta-title')
            print(title)

            # 获取图片节点
            img_ele = ele.find_element(By.CSS_SELECTOR,
                                       "a.js-photo-link>img.photo-item__img")
            img_url = img_ele.get_attribute('src')
            # print(img_url)
            img_name = re.search(exp_img, img_url).group(1)
            print(img_name)

            # 这里是最终是视频节点
            source_ele = ele.find_element(By.CSS_SELECTOR,
                                          "a.js-photo-link>video.photo-item__video>source")

            video_url = source_ele.get_attribute('src')
            # print(video_url)

            video_name = re.search(exp_video, video_url).group(1)
            print(video_name)

            if os.path.exists(option.output_dir + video_name):
                # 如果目标路径中，对应的视频文件已经存在，那么跳过该记录
                continue

            # 下载对应的图片和视频文件
            # 这里之所以用不同方式下载，是因为wget是最简洁稳定的方式，还能显示进度，但它不支持伪装user-agent
            # 而图片的目标网站拒绝自动机器人下载
            try:
                download.urlretrieve(img_url, option.output_dir + img_name)
            except Exception as e:
                print('下载图片"{}"异常：{}'.format(img_url, e))
                continue

            try:
                wget.download(video_url, option.output_dir + video_name)
            except Exception as e:
                print('下载视频"{}"异常：{}'.format(video_url, e))
                continue

            # 新增1条数据记录
            df = df.append({'title': title, 'img_name': img_name, 'video_name': video_name}, ignore_index=True)
            # 检查数据上限
            times += 1
            if times >= option.limit:
                break
            # # driver.get(ele.get_attribute('src'))
            time.sleep(0.5)
        # 保存数据文件
        with open(option.output_result, 'a', encoding="utf-8", newline='') as f:
            # 如果文件存在，则添加数据
            df.to_csv(f, header=f.tell() == 0)
