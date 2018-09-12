# coding:utf-8

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from signal import signal, SIGINT
from threading import Thread, current_thread
from time import sleep, time
from copy import deepcopy
from pickle import dump, load
import sys
import os

dirname = os.path.abspath(os.path.dirname(__file__))
good_index = 0


def new_login( browser):
    browser.get( 'https://account.xiaomi.com/')
    sleep(2)
    browser.find_element_by_id("username").send_keys("15754310610")
    browser.find_element_by_id("pwd").send_keys("soleil24555")
    browser.find_element_by_id("login-button").click()
    
    sleep(2)
    print(browser.current_url)
    dump_cookie(browser, "/xiaomicookie.pkl") # dump *.xiaomi.com的cookie
    print(browser.get_cookies())
    browser.get("https://www.mi.com/seckill/")
    order = browser.find_element_by_class_name("link")
    browser.execute_script("arguments[0].target = '';", order)
    order.click() # 跳转到订单页面
    sleep(2)
    print(browser.current_url)
    dump_cookie(browser, "/micookie.pkl") # dump *.mi.com的cookie
    print(browser.get_cookies())

    browser.quit()


def dump_cookie(driver, filename):
    with open(dirname+filename, "wb") as f:
        dump(driver.get_cookies(), f)


def find_good_button(driver):
    global good_index
    div = driver.find_elements_by_xpath("//div[@class='pro-con']")
    if len(div):
        a = div[good_index].find_elements_by_xpath("a")
        if len(a) == 2 :
        # if "登录" not in a[1].text:
            return True
    return False


def seckill():
    with open(dirname+"/micookie.pkl", "rb") as f:
        micookies = load(f)
    with open(dirname+"/xiaomicookie.pkl", "rb") as f:
        xiaomicookies = load(f)
    assert type(micookies) is list, "[!] no cookies"
    driver = webdriver.Chrome(executable_path="/home/beatjean/Documents/chromedriver")
    driver.get("https://account.xiaomi.com/")
    driver.delete_all_cookies()
    for cookie in xiaomicookies:
        driver.add_cookie(cookie)
    driver.get("https://www.mi.com/seckill/")
    for cookie in micookies:
        driver.add_cookie(cookie)
    WebDriverWait(driver, 3).until(find_good_button)
    yinxiang = driver.find_elements_by_class_name("pro-con")[good_index]
    a = yinxiang.find_elements_by_xpath("a")
    # print(a[0].text)
    print("[%s] now select %s" %(current_thread().name, a[0].text))

    input("")

    if "登录" in a[1].text:
        a[1].click()

    WebDriverWait(driver, 3).until(lambda driver:driver.find_elements_by_class_name("pro-con"))
    yinxiang = driver.find_elements_by_class_name("pro-con")[good_index]
    a = yinxiang.find_elements_by_xpath("a")
    print("[%s] now click %s" % (current_thread().name, a[1].text))
    for _ in range(20):
        a[1].click()
    driver.quit()

def rush():
    while True:
        threads = []
        for i in range(10):
            thread = Thread(target=seckill, name="TH-"+str(i))
            thread.setDaemon(True)
            thread.start()
            threads.append(thread)

        for t in threads:
            t.join()


def main():
    global cookies
    desired_capabilities = DesiredCapabilities.CHROME  # 修改页面加载策略
    desired_capabilities["pageLoadStrategy"] = "none"  # 注释这两行会导致最后输出结果的延迟，即等待页面加载完成再输出

    if len(sys.argv) == 2:
        driver = webdriver.Chrome(executable_path="/home/beatjean/Documents/chromedriver")
        driver.implicitly_wait(3)
        new_login(driver)
        return
    seckill()
    # rush()


def shutdown(*args):
    sys.exit(0)


if __name__ == '__main__':
    signal(SIGINT, shutdown)
    main()
