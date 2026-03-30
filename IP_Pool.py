import requests

url = 'https://proxy.scdn.io/api/get_proxy.php?protocol=http&count=20'
params = {
    'protocol': 'http',
    'count': 20
}
response = requests.get(url, params=params)
data = response.json()
proxies = data["data"]['proxies']

# 生成 PROXY_POOL 列表格式
print("PROXY_POOL = [")
for proxy in proxies:
    # 确保格式为 'http://ip:port'
    proxy_address = f"http://{proxy['ip']}:{proxy['port']}"
    print(f"    '{proxy_address}',")
print("]")