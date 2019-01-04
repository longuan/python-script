# coding:utf-8

import requests
import os
import re

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

def get_html_filename(url, dst_name=None):
    log_txt = ROOT_DIR+"/log.txt"
    if os.path.exists(log_txt):
        with open(log_txt, "r") as f:
            a = re.findall("%s\n(.*?)\n\n" % url, f.read())
            if a:
                # print("find it in cache")
                return ROOT_DIR+"/html/"+a[0]

    # print("not in cache")
    if not dst_name:
        dst_name = requests.utils.quote(url).replace("/", "_") + ".html"

    page = requests.get(url)
    if page.status_code != 200:
        print("could not get page source html: %s" % str(page.status_code))
        exit(1)

    print("download HTML page source : %s" % url)
    with open(ROOT_DIR+"/html/%s" % dst_name, "w") as f:
        f.write(page.content.decode("utf-8"))
    with open(ROOT_DIR+"/log.txt", "a") as f:
        f.write("%s\n%s\n\n" % (url, dst_name))

    # print("now, it is in cache")
    return ROOT_DIR+"/html/"+dst_name

if __name__ == '__main__':
    get_html_filename("https://www.baidu.com")
    get_html_filename("https://www.baidu.com")
    get_html_filename("https://www.baidu.com")
