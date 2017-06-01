# coding:utf-8

"""
整个程序流程:

1. read_config()返回一个字典{url:pattern}
2. get_proxy_raw_data() 多线程爬取网站获取原生结果,未验证的代理信息都存入proxy_queue   √
3. check_available() 多线程验证代理可用性, 验证成功的代理信息存入OutputQueue
4. save_data() 结果存入本地文件或者数据库
"""
import os
import re
import configparser
import queue
import threading
import requests
import time
import src.utils as utils

ROOT_PATH = os.path.dirname(__file__)
PAGE = 2                                           # 爬取每个网站的页面数
CONFIG_FILE_PATH = ROOT_PATH + "/config"           # 配置文件路径
THREAD_NUM = 10                                    # 进行验证的线程数
URL_PATTERN = None                                 # 储存url与pattern的对应,在read_config函数重写

proxy_queue = queue.Queue()                        # 从网页提取的未验证的数据
save_lock = threading.Lock()                       # 将经过验证的代理数据保存时加锁
proxy_queue_lock = threading.Lock()                # 改动proxy_queue需要加锁


def get_raw_proxy_data(raw_url, pattern):
    """
    从网页获取的未加验证的原生数据, 并存入proxy_queue队列, 被函数task_get_raw_proxy()调用
    :return:
    """
    if "{page_num}" not in raw_url:
        page_count = 1
    else:
        page_count = PAGE
    for num in range(1, page_count+1):
        try:
            url = raw_url.format(page_num=num)
        except KeyError as e:
            url = raw_url
        page_get = utils.get(url)
        if not page_get:
            print("[!]: 此页(" + url + ")页面源码获取失败")
            continue
        print("[*]: 此页(" + url + ")页面源码获取成功")
        proxy_raw_data = re.findall(pattern, page_get.text)
        if not proxy_raw_data:
            print("[!]: 此页(" + url + ")提取结果为空, 请检查pattern")
            continue
        if not utils.check_ip_port(proxy_raw_data):
            print("[!]: 此页(" + url + ")提取结果ip_port检查不通过")
            continue
        # 将结果存入proxy_queue, 加锁解锁
        print("[*]: 将提取结果存入队列中")
        proxy_queue_lock.acquire()
        for item in proxy_raw_data:
            proxy_queue.put(item)
        proxy_queue_lock.release()
        print("[*]: 提取结果存入队列完成")


def check_available():
    """
    检测代理的可用性
    :return:
    """
    while not proxy_queue.empty():
        item = proxy_queue.get()
        if len(item) == 2:
            ip, port = item
            protocol = "http"
        elif len(item) == 3:
            ip, port, protocol = item
            protocol = protocol.lower()
            if re.search("HTTP", protocol, re.IGNORECASE) and re.search("HTTPS", protocol, re.IGNORECASE):
                protocol = "http"
        else:
            print("[!]: 代理数据格式不正确")
            continue
        url = protocol+"://"+ip+":"+port
        proxy = {protocol: url}
        print(url)
        try:
            test_proxy = requests.get("http://httpbin.org/ip", proxies=proxy, timeout=10)
        except Exception as e:
            # print("[!]: ", e)
            continue
        else:
            if ip in test_proxy.text:
                save_lock.acquire()
                save_data(url)
                save_lock.release()


def run_task():
    get_raw_proxy_threads = []
    check_available_threads = []
    for url, pattern in URL_PATTERN.items():
        t = threading.Thread(target=get_raw_proxy_data, args=(url, pattern))
        get_raw_proxy_threads.append(t)
    for _ in range(THREAD_NUM):
        t = threading.Thread(target=check_available)
        check_available_threads.append(t)
    for thread in get_raw_proxy_threads:
        thread.start()
    for thread in get_raw_proxy_threads:
        thread.join()

    for thread in check_available_threads:
        thread.start()
    for thread in check_available_threads:
        thread.join()


def save_data(proxy):
    """
    保存结果到文件或者数据库
    :return:
    """
    result_file_path = ROOT_PATH + "/result.txt"
    with open(result_file_path, "a+") as fo:
        fo.write(proxy+"\n")


def read_config(config_file_path):
    """
    从配置文件读入相关设置, 并过滤未设置pattern的section
    :return:
    """
    global URL_PATTERN
    URL_PATTERN = dict()
    cf = configparser.ConfigParser()
    cf.read(config_file_path)
    for i in cf.sections():
        url = cf.get(i, "url")
        try:
            pattern = cf.get(i, "pattern")
        except configparser.NoOptionError as e:
            print("[!]: ",e)
            continue
        URL_PATTERN[url] = pattern


def main():
    read_config(CONFIG_FILE_PATH)
    run_task()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        print("ctrl+c by user")
        exit(1)


# TODO : 生成api
# TODO : 代理ip去重
# TODO : 对代理ip可用性划分权值
# TODO : config代理网站完善
# TODO : utils.check_ip_port函数完善

# 验证可用性网站:http://ip.chinaz.com/getip.aspx
# 验证可用性网站:http://httpbin.org/ip
