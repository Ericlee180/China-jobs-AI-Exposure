import argparse
import json
import os
import time
import requests

def main():
    parser = argparse.ArgumentParser(description="Scrape chinajob pages")
    parser.add_argument("--start", type=int, default=0, help="Start index (inclusive)")
    parser.add_argument("--end", type=int, default=None, help="End index (exclusive)")
    parser.add_argument("--force", action="store_true", help="Re-scrape even if cached")
    parser.add_argument("--delay", type=float, default=1.0, help="Seconds between requests")
    args = parser.parse_args()

    with open("occupations-cn-full.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        if isinstance(data, dict) and "records" in data:
            occupations = data["records"]
        else:
            occupations = data

    end = args.end if args.end is not None else len(occupations)
    subset = occupations[args.start:end]

    os.makedirs("html", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("pages", exist_ok=True)

    to_scrape = []
    for i, occ in enumerate(subset, start=args.start):
        json_path = f"html/{occ['id']}.json"
        if not args.force and os.path.exists(json_path):
            print(f" [{i}] CACHED {occ['careerName']}")
            continue
        to_scrape.append((i, occ))

    if not to_scrape:
        print("Nothing to scrape - all cached.")
        return
    
    print(f"\nScraping {len(to_scrape)} occupations...\n")

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://chinajob.mohrss.gov.cn",
        "Referer": "https://chinajob.mohrss.gov.cn/zy/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        # 注意：token 头是空的，保持原样
        "token": "",
    }

    success_count = 0
    for idx, (i, occ) in enumerate(to_scrape):
        career_id = str(occ["careerId"])  # 转为字符串
        basecareer_picture_id = str(occ["id"])  # 转为字符串，注意参数名是 basecareerPictureId
        
        api_url = "https://chinajob.mohrss.gov.cn/prod-api/public/occupation/home/selectCareerPicturePreview"
        
        # 正确的参数格式（从 cURL 中复制）
        payload = {
            "careerId": career_id,
            "basecareerPictureId": basecareer_picture_id,
            "isPreview": "0"
        }
        
        json_path = f"html/{occ['id']}.json"
        print(f" [{i}] {occ['careerName']}...", end=" ", flush=True)

        try:
            resp = requests.post(api_url, json=payload, headers=headers, timeout=30)
            
            if resp.status_code != 200:
                print(f"HTTP {resp.status_code} - SKIPPED")
                continue
                
            result = resp.json()
            
            if result.get("code") != 200:
                print(f"API 返回错误: {result.get('msg')}")
                continue
            
            # 保存原始 JSON 数据
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            # 可选：提取并保存基础信息
            if "data" in result and "base" in result["data"]:
                base_info = result["data"]["base"]
                data_path = f"data/{occ['id']}.json"
                with open(data_path, "w", encoding="utf-8") as f:
                    json.dump(base_info, f, ensure_ascii=False, indent=2)
            
            print(f"OK")
            success_count += 1
            
        except Exception as e:
            print(f"ERROR: {e}")

        if idx < len(to_scrape) - 1:
            time.sleep(args.delay)

    print(f"\nDone. Success: {success_count}/{len(to_scrape)} occupations.")
    print(f"Total JSON files cached: {len(os.listdir('html'))}")

if __name__ == "__main__":
    main()