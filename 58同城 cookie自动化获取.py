import json
import os
import time
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By

def start():
    q1 = Options()
    q1.add_experimental_option('detach', True)  # 保持浏览器开启状态
    a1 = webdriver.Edge(service=Service('msedgedriver.exe'),options=q1)
    return a1
def get_Cookie():
    if not os.path.exists('58city_cookies.json'):
        time.sleep(20)
        cookies = a1.get_cookies() #给你登入时间获取到 我们的cookie
        with open('58city_cookies.json', 'w') as f:
            f.write(json.dumps(cookies))  # 将cookies保存到本地cookies.json文件中 使用json.dumps 获取
    with open('58city_cookies.json', 'r') as f:
        cookies = json.loads(f.read()) #转化成字典
        for cookie in cookies:
            cookie_dict = {
                'domain': cookie.get('domain'),
                'name': cookie.get('name'),
                'value': cookie.get('value'),
                "expires": cookie.get('expires'),
                'path': '/',
                'httpOnly': False,
                'HostOnly': False,
                'Secure': False
            }
            a1.add_cookie(cookie_dict)
        a1.refresh()
if __name__ == '__main__':
    a1 = start()
    a1.get('https://xm.58.com/')
    get_Cookie()