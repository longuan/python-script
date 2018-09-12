# coding:utf-8

import time
import re
from config import username, password, thread_num
from hashlib import md5
import json
from threading import Thread, current_thread
from signal import signal, SIGINT
from random import randint
from pickle import load
import os
import requests


dirname = os.path.abspath(os.path.dirname(__file__))
s = requests.session()
headers = {
"Connection": "close",
"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36",
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
"Accept-Encoding": "gzip, deflate",
}
s.headers.update(headers)
start_time = 0
end_time   = 0
rand_num = randint(100, 300)
salt = ""
token = ""


def now():
    return str(int(time.time()))


def time2str(timestamp):
    now = time.localtime(timestamp)
    return time.strftime("%m.%d %H:%M", now)


def rand_number():
    global rand_num
    rand_num += 1
    return str(rand_num)


def load_cookie(filename):
    with open(dirname+filename, "rb") as f:
        cookie = load(f)
    result = dict()
    for i in cookie:
        result[i['name']] = i['value']
    return result


xiaomicookies = load_cookie("/xiaomicookie.pkl")
micookies = load_cookie("/micookie.pkl")

# 此函数已弃用
def xiaomi_login():
    global s
    headers = {
    "Connection": "close",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    }
    s.headers.update(headers)

    login_url = "https://account.xiaomi.com/pass/serviceLogin"
    # login_url = "https://order.mi.com//site/login"
    res = s.get(login_url,cookies=cookies)
    callback = re.findall('callback:"(.*?)"', res.text)[0]
    sid      = re.findall("sid:'(.*?)'", res.text)[0]
    qs       = re.findall('qs:"(.*?)"', res.text)[0]
    _sign    = re.findall('_sign":"(.*?)"', res.text)[0]
    service_param = re.findall("serviceParam :'(.*?)'", res.text)[0]

    auth_url = "https://account.xiaomi.com/pass/serviceLoginAuth2?_dc="+now()
    s.headers["Referer"] = "https://account.xiaomi.com/pass/serviceLogin"
    s.headers["Content-type"] = "application/x-www-form-urlencoded"

    post_data = {"_json":"true", "callback":callback, "sid":sid, "qs":qs, "_sign":_sign,
                 "serviceParam":service_param, "user":username, "hash":md5(password.encode("utf-8")).hexdigest().upper()}
    res = s.post(auth_url, data=post_data, proxies=proxies, verify=False)
    print(res.text)
    login_data = res.text
    assert "成功" in login_data, "[!] login failed"

    s.headers.pop("Referer")
    s.headers.pop("Content-type")

    s.headers['Referer'] = login_url
    location = re.findall('location":"(.*?)"', login_data)[0]
    res = s.get(location, proxies=proxies, verify=False)

    s.headers['Referer'] = "https://www.mi.com/seckill/"
    r = s.get("https://account.xiaomi.com/pass/userInfoJsonP?userId=0&callback=setLoginInfo_getAccountInfo", proxies=proxies, verify=False)


def get_seckill_goods():
    global s, start_time, end_time, cookies
    url = "https://a.huodong.mi.com/flashsale/getslideshow"
    res = s.get(url,cookies=micookies)
    current_seckill = json.loads(res.text.strip().strip(";").strip(')').strip('('))

    start_time = int(current_seckill['data']['list']['start_time'])
    end_time   = int(current_seckill['data']['list']['end_time'])
    goods_list = current_seckill['data']['list']['list']
    print("[*] this turn seckill from %s to %s" %(time2str(start_time), time2str(end_time) ) )
    assert len(goods_list)>0, "[!] good_list is empty"
    print("[*] get %d good info" % (len(goods_list)))
    return goods_list


def get_salt(goods):
    global salt

    jsonpcallback = "jQuery111306643493297083507_%s%s" % (now(), rand_number())
    s.headers["Referer"] = "https://www.mi.com/seckill/"
    s.headers["Accept"]  = "*/*"
    params = {"jsonpcallback": "hdinfo", "sitename": "cn", "start": str(start_time),
              "source": "flashsale", "m": "1", "_": now()+rand_number()}
    while salt is "" and (int(time.time()) - start_time ) < 60:
        r = s.get("https://tp.hd.mi.com/hdinfo/cn", cookies=micookies,params=params)
        print("[%s] now request url: %s" % (current_thread().name, r.request.url))
        hdinfo = json.loads(r.text.strip("hdinfo").strip("(").strip(")"))
        ss = hdinfo['status'][goods['goods_id']]['salt']
        if ss is not "" and salt is "":
            salt = ss
            print("[%s] get salt: %s" % (current_thread().name, salt))
            return
        print("hdinfo: %s" % hdinfo['status'][goods['goods_id']] )


def add_good_cart(goods):
    global salt, token
    while salt is "":
        time.sleep(0.01)
    params = {"jsonpcallback":"cn"+goods['goods_id'], "source":"flashsale", "product":goods['goods_id'],
              "salt":salt, "m":"1", "addcart":"1",
              "cstr1":"0",
              "cstr2":"0",
              "_":now()+rand_number() }
    while token is "" and (int(time.time()) - start_time ) < 60:
        r = s.get("https://tp.hd.mi.com/hdget/cn",cookies=micookies, params=params)
        print("[%s] now request url: %s" % (current_thread().name, r.request.url))
        try:
            hdget = json.loads(r.text.strip(params['jsonpcallback']).strip("(").strip(")"))
        except Exception as e:
            continue
        hdurl = hdget['status'][goods['goods_id']]['hdurl']
        if hdurl is not "" and token is "":
            token = hdurl
            print("[%s] get token: %s" % (current_thread().name, token))
        print("hdget: %s" % hdget)

    for _ in range(5):
        addcart_url = "https://cart.mi.com/cart/add/%s" % (goods['goods_id'])
        jsonpcallback = "jQuery111306643493297083507_%s%s" % (now(), rand_number())
        params = {"jsonpcallback":jsonpcallback, "product_id":goods['goods_id'], "source":"bigtap_flash",
                  "extend_field[end_time]":str(end_time), "extend_field[start_time]":str(start_time), "token":token, "_":now()}
        r = s.get(addcart_url, params=params,cookies=micookies)
        print("[%s] now request url: %s" % (current_thread().name, r.request.url))
        print("[%s] add cart result is: %s" %(current_thread().name, r.text))


def rush_with_threads(goods):
    threads = list()
    while (int(time.time())-start_time) < 60:
        for i in range(thread_num):
            if salt is "":
                thread = Thread(target=get_salt, args=(goods, ), name="S-"+str(i))
                threads.append(thread)
                thread.start()
            thread = Thread(target=add_good_cart, args=(goods, ), name="T-"+str(i))
            threads.append(thread)
            thread.start()

        for t in threads:
            t.join()


def main():
    goods_list = get_seckill_goods()
    keyword = "积木"
    goods = None

    for good in goods_list:
        if keyword in good['goods_name']:
            goods = good
            break

    if goods:
        time.sleep(50)
        print("now select good is: %s" %(goods['goods_name']))

        rush_with_threads(goods)
    else:
        print("[!] no found %s" % keyword)


def shutdown(*args):
    import sys
    sys.exit(1)

if __name__ == '__main__':
    signal(SIGINT, shutdown)
    main()
