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
    return Option(args.output_dir, args.result_file, int(args.limit) if args.limit is not None else None)


if __name__ == '__main__':
    # 获取命令行参数
    option = get_options_from_command_line()

    if not os.path.exists(option.output_dir):
        os.mkdir(option.output_dir)
    # 设置从url中获取名字的正则表达式
    exp_img = re.compile(r'v/.+?/(.*?)\?')
    exp_video = re.compile(r'v/.+?/(.*?)\?')

    web_options = webdriver.ChromeOptions()
    web_options.add_argument("--enable-javascript")
    # web_options.add_argument('--always-authorize-plugins=true')
    with webdriver.Chrome(options=web_options) as driver:
        # with webdriver.Chrome(chrome_options=options) as driver:
        wait = WebDriverWait(driver, 10)

        # 访问首页
        driver.get(
            "https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=ALL&q=clothing&sort_data[direction]=desc&sort_data[mode]=relevancy_monthly_grouped&start_date[min]=2021-11-25&start_date[max]=2021-11-26&search_type=keyword_unordered&media_type=video")
        # 获取所有视频描述节点
        results = []
        while len(results) < option.limit:
            results = driver.find_elements(By.CSS_SELECTOR,
                                           "div._99s5")
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            time.sleep(5)

        times = 0
        # 准备数据表
        columns = ['title', 'img_name', 'video_name', 'desc']
        df = pd.DataFrame(columns=columns)
        for ele in results:
            ele_item = ele.find_element(By.CSS_SELECTOR, "div.iajz466s div._7jyg")

            # 获取标题节点
            title_item = ele_item.find_element(By.CSS_SELECTOR,
                                               "div._8nsi a.aa8h9o0m>span.a53abz89")
            title = title_item.text
            print(title)

            # 获取描述节点
            desc_item = ele_item.find_element(By.CSS_SELECTOR,
                                              "div._7jyr>span div._4ik4>div")
            desc = desc_item.text

            # 获取视频图片节点
            video_item = ele_item.find_element(By.CSS_SELECTOR,
                                               "div._8o0a>video")
            img_url = video_item.get_attribute('poster')
            # print(img_url)
            img_name = re.search(exp_img, img_url).group(1)
            print(img_name)

            video_url = video_item.get_attribute('src')
            # print(video_url)

            video_name = re.search(exp_video, video_url).group(1) + 'mp4'
            # 网站给出的视频文件没有扩展名，这里随便加一个，应该就可以播放了
            print(video_name)

            if os.path.exists(option.output_dir + video_name):
                # 如果目标路径中，对应的视频文件已经存在，那么跳过该记录
                continue

            # 下载对应的图片和视频文件
            try:
                wget.download(img_url, option.output_dir + img_name)
            except Exception as e:
                print('下载图片"{}"异常：{}'.format(img_url, e))
                continue

            try:
                wget.download(video_url, option.output_dir + video_name)
            except Exception as e:
                print('下载视频"{}"异常：{}'.format(video_url, e))
                continue

            # 新增1条数据记录
            df = df.append({'title': title, 'img_name': img_name, 'video_name': video_name, 'desc': desc},
                           ignore_index=True)
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
