#coding:utf-8
import requests
from hashlib import md5
import json
import re


username = "username"   #修改为自己的教学号
passwd_plain = "password"   #修改为自己的密码





login_url = "http://uims.jlu.edu.cn/ntms/j_spring_security_check"
header = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0',
    # 'Content-Type': 'application/json',
}

passwd_md5 = md5()
passwd_md5.update("UIMS"+username+passwd_plain)
password = passwd_md5.hexdigest()

login_data = {
    'j_username': username,
    'j_password': str(password),
    'save_cookie': 'none'
}

res_data = {
    "tag":"student@evalItem",
    "branch":"self",
    "params":{"blank":"Y"}
}

course_rank = {
    "evalItemId":"3282600",
    "answers":{"prob11":"A","prob12":"A","prob13":"D","prob14":"A","prob15":"D","prob21":"A","prob22":"A","prob23":"A","prob31":"A","prob32":"A","prob41":"A","prob42":"A","prob43":"D","prob51":"A","prob52":"B","sat6":"A","mulsel71":"L","advice8":""}
}

s = requests.Session()
s.post(url=login_url,data=login_data, headers=header)
header['Content-Type'] = 'application/json'
page = s.post(url='http://uims.jlu.edu.cn/ntms/service/res.do', headers=header, data=json.dumps(res_data))
jj = page.text

pattern = re.compile("evalItemId\":\"(.*?)\",\"notes")
course_list = pattern.findall(jj)
for i in course_list:
    course_rank['evalItemId'] = str(int(i))
    s.post(url = 'http://uims.jlu.edu.cn/ntms/eduEvaluate/eval-with-answer.do', headers=header, data=json.dumps(course_rank))