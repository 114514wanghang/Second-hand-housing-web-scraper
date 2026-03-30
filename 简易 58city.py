import os
import time

import pandas as pd
from lxml import etree
import requests

def append_to_excel(data, excel_path, columns):
    df = pd.DataFrame(data, columns=columns)
    if os.path.exists(excel_path):
        try:
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

        except Exception as e:
            print(f"读取现有文件出错，将创建新文件：{e}")
            # 重新生成序号
            df['序号'] = range(1, len(df) + 1)
            df.to_excel(excel_path, index=False, engine='openpyxl')
            return len(df)
    else:
        # 重新生成序号
        df['序号'] = range(1, len(df) + 1)
        df.to_excel(excel_path, index=False, engine='openpyxl')
        return len(df)

def search_url(url):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0',
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        time.sleep(1)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"请求 URL 失败：{url}, 错误：{e}")
        return ""

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
    excel_path = os.path.join(desktop_path, "上海租房信息表.xlsx")
    all_houses = []
    # 定义列顺序
    columns = ["序号", "标题", "价格 (元/月)","房屋类型和面积", "详细地址", "来源链接"]
    start_page = 1
    end_page = 70
    for page in range(start_page, end_page + 1):
        print(f"\n正在爬取第 {page} 页...")
        urls = [f'https://sh.58.com/chuzu/pn{page}/']
        for url in urls:
            html_text = search_url(url)
            tree = etree.HTML(html_text)
            # 获取所有房源链接
            house_elements = tree.xpath('/html/body/div[6]/div[2]/ul/li')
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
