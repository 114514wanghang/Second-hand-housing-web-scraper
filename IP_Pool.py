import requests
# 获取代理 IP
url = 'https://proxy.scdn.io/api/get_proxy.php?protocol=http&count=20'
response = requests.get(url)
data = response.json()
proxies = data["data"]['proxies']
output_file = 'free-ip.txt'
with open(output_file, 'w', encoding='utf-8') as f:
    for proxy in proxies:
        f.write(f"{proxy}\n")
print(f"✓ 成功保存 {len(proxies)} 个代理 IP 到 {output_file}")
