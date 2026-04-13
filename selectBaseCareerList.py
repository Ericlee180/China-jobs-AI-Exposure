import requests
import json

api_url = "https://chinajob.mohrss.gov.cn/prod-api/public/occupation/home/selectBaseCareerList"
all_data = []

for page in range(1, 6):
    payload = {
        "pageNo": page,
        "pageSize": 24,
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0",
        "Content-Type": "application/json;charset=UTF-8",
        "Referer": "https://chinajob.mohrss.gov.cn/zy/",
        "Origin": "https://chinajob.mohrss.gov.cn"
    }
    resp = requests.post(api_url, json=payload, headers=headers)
    if resp.status_code == 200:
        page_data = resp.json()
        if page == 1:
            print(f"第一页返回数据示例：{page_data.keys()}")
        records = page_data.get("data", {}).get("records", [])
        if not records and "records" in page_data:
            records = page_data.get("records", [])
        all_data.extend(records)
        print(f"第 {page} 页抓取成功，获取 {len(records)} 条")
    else:
        print(f"第 {page} 页抓取失败，状态码：{resp.status_code}")
        print(f"返回内容： {resp.text}")


with open("occupations-cn-full.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print(f"总共获取 {len(all_data)} 条职业数据")

with open("occupations-cn-full.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    print(f"数据类型： {type(data)}")
    if isinstance(data, dict):
        print(f"字典的健： {list(data.keys())}")
    else:
        print(f"列表长度： {len(data)}")