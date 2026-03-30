import os
import random
import time
import json
import requests
import pandas as pd
from lxml import etree
import urllib3

urllib3.disable_warnings()

# 从 JSON 文件加载代理 IP
def load_proxy_from_json():
    try:
        with open('free-ip-json.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        # 提取 IP 和端口
        proxy_list = [f"http://{item['ip']}:{item['port']}" for item in data]
        return proxy_list
    except Exception as e:
        print(f"加载代理 JSON 文件失败：{e}")
        return []

# 初始化代理池
PROXY_POOL = load_proxy_from_json()
proxy_index = 0  # 当前使用的代理索引
used_proxies = set()  # 已使用过的代理

def get_next_proxy():
    """按顺序获取下一个未使用的代理"""
    global proxy_index, used_proxies
    
    # 如果所有代理都用过了，重置
    if len(used_proxies) >= len(PROXY_POOL):
        used_proxies.clear()
        proxy_index = 0
    
    # 找到下一个未使用的代理
    while proxy_index < len(PROXY_POOL):
        proxy = PROXY_POOL[proxy_index]
        proxy_index += 1
        if proxy not in used_proxies:
            used_proxies.add(proxy)
            return proxy
    
    return None

def append_to_excel(data, excel_path, columns):
    df = pd.DataFrame(data, columns=columns)
    if os.path.exists(excel_path):
        existing_df = pd.read_excel(excel_path, engine='openpyxl')
        missing_cols = [col for col in columns if col not in existing_df.columns]
        if missing_cols:
            for col in missing_cols:
                existing_df[col] = ""

        combined_df = pd.concat([existing_df, df], ignore_index=True, sort=False)
        combined_df['序号'] = range(1, len(combined_df) + 1)
        combined_df = combined_df[columns]
        combined_df.to_excel(excel_path, index=False, engine='openpyxl')
        return len(df)
    else:
        # 重新生成序号
        df['序号'] = range(1, len(df) + 1)
        df.to_excel(excel_path, index=False, engine='openpyxl')
        return len(df)

def load_cookies():
    cookie_file = '58city_cookies.json'
    if not os.path.exists(cookie_file):
        print(f"未找到 {cookie_file} 文件，正在自动获取...")
        import subprocess
        import sys
        script_path = os.path.join(os.path.dirname(__file__), '58_cookie_auto.py')
        subprocess.run([sys.executable, script_path], check=True, encoding='utf-8')

    with open(cookie_file, 'r', encoding='utf-8') as f:
        cookies_list = json.load(f)
    cookies_dict = {c.get('name'): c.get('value') for c in cookies_list if c.get('name') and c.get('value')}
    return '; '.join([f"{name}={value}" for name, value in cookies_dict.items()])

# def fetch_proxy_from_api():
#     url = 'https://proxy.scdn.io/api/get_proxy.php?protocol=http&count=20'
#     params = {'protocol': 'http', 'count': 1}
#     response = requests.get(url, params=params, timeout=10)
#     data = response.json()
#     proxies = data.get('data', {}).get('proxies', [])
#
#     proxy_list = [f"http://{p}" for p in proxies ]
#     return proxy_list

def search_url(url, cookies_str, proxy):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0',
        'Cookie': cookies_str
    }
    
    if proxy:
        proxies = {'http': proxy}
        response = requests.get(url, headers=headers, timeout=10, proxies=proxies, verify=False)
        return response.text
    else:
        response = requests.get(url, headers=headers, timeout=10)
        return response.text


def get_proxy_for_retry():
    """重试时获取新代理"""
    # def fetch_proxy_from_api():
    #     url = 'https://proxy.scdn.io/api/get_proxy.php?protocol=http&count=20'
    #     params = {'protocol': 'http', 'count': 1}
    #     response = requests.get(url, params=params, timeout=10)
    #     data = response.json()
    #     proxies = data.get('data', {}).get('proxies', [])
    #     proxy_list = [f"http://{p}" for p in proxies ]
    #     return proxy_list
    
    # 从本地列表获取下一个代理
    return get_next_proxy()


def clean_text(text_list):
    if not text_list:
        return ""
    try:
        text = text_list[0].strip()
        text = text.replace('\xa0', ' ')
        text = text.replace(' ', '')
        return text
    except:
        return ""

if __name__ == "__main__":
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    excel_path = os.path.join(desktop_path, "租房信息表.xlsx")
    all_houses = []
    # 定义列顺序
    columns = ["序号", "标题", "价格 (元/月)","房屋类型和面积", "详细地址", "来源链接"]
    start_page = 1
    end_page = 70
    
    # 获取初始代理
    proxy = get_next_proxy()
    if proxy:
        print(f"✓ 已加载 {len(PROXY_POOL)} 个代理 IP，当前使用：{proxy}")
    else:
        print("⚠ 未找到可用代理 IP")

    # 加载 cookie
    print("正在加载 cookie...")
    cookies_str = load_cookies()
    if not cookies_str:
        print("无法继续执行，程序退出。")
        exit()
    print("✓ Cookie 加载成功！")

    for page in range(start_page, end_page + 1):
        print(f"\n正在爬取第 {page} 页...")
        urls = [f'https://sh.58.com/chuzu/pn{page}/']
        for url in urls:
            success = False
            house_elements = ""
            # 最多重试 20 次
            for retry in range(20):
                html_text = search_url(url, cookies_str, proxy)
                tree = etree.HTML(html_text)
                # 获取所有房源链接
                house_elements = tree.xpath('/html/body/div[6]/div[2]/ul/li')
                # 如果能获取到房源，说明成功
                if house_elements:
                    success = True
                    break
                else:
                    print(f"  未获取到房源数据，尝试切换 IP 重试... ({retry + 1}/20)")
                # 获取下一个 IP
                new_proxy = get_proxy_for_retry()
                if new_proxy:
                    proxy = new_proxy
                    print(f"  已切换 IP: {proxy}")
                else:
                    print("  ⚠ 所有 IP 都已使用，将重新循环使用")
            
            # 8 次重试都失败，跳过
            if not success:
                print(f"第 {page} 页重试 20 次后仍然失败，跳过")
                # 更新代理供下一页使用
                new_proxy = get_proxy_for_retry()
                if new_proxy:
                    proxy = new_proxy
                continue
            
            house_links = house_elements[:-1]
            print(f"共识别到 {len(house_elements)} 条房源")
            for i, li in enumerate(house_elements, 1):
                # 标题
                title_elements = li.xpath('.//div[2]/h2/a/text()')
                title = clean_text(title_elements) if title_elements else "未知"
                # 价格
                price_elements = li.xpath('.//div[2]/b/text()')
                price = clean_text(price_elements) if price_elements else ""
                # 房屋类型与面积
                house_type_elements = li.xpath('.//div[2]/p[1]/text()')
                house_type_and_area = clean_text(house_type_elements) if house_type_elements else ""

                # 所在地点
                address_elements = li.xpath('.//div[2]/p[2]/a[2]/text()')
                address = clean_text(address_elements) if address_elements else ""
                # 链接
                linke_elements = li.xpath('.//div[2]/h2/a/@href')
                link = clean_text(linke_elements) if linke_elements else ""

                # 检查是否有有效数据，如果缺少关键信息就跳过
                if not title or title == "未知" or not house_type_and_area or not address or not link:
                    continue

                # 将数据存储到字典
                house_info = {
                    "标题": title,
                    "价格 (元/月)": price,
                    "房屋类型和面积": house_type_and_area,
                    "详细地址": address,
                    "来源链接": link
                }
                all_houses.append(house_info)
                print(f"    #{i} 爬取成功：{title}")

            if all_houses:
                print(f"\n共爬取到 {len(all_houses)} 条房源信息")
                print("正在保存到 Excel 文件...")
                # 追加到 Excel
                added_count = append_to_excel(all_houses, excel_path, columns)
                all_houses = []
                print(f"\n✓ 数据已成功保存到桌面：{excel_path}")
                print(f"  本次新增 {added_count} 条数据")

                # 显示总数据量
                if os.path.exists(excel_path):
                    try:
                        existing_df = pd.read_excel(excel_path, engine='openpyxl')
                        print(f"  文件现有总数据：{len(existing_df)} 条")
                    except Exception as e:
                        print(f"  无法读取文件统计总数据：{e}")
            else:
                print("\n⚠ 没有爬取到任何房源信息")
