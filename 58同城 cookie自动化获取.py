import json
import os
import time
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service

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
        a1.quit()
if __name__ == '__main__':
    a1 = start()
    a1.get('https://passport.58.com/login/')
    get_Cookie()