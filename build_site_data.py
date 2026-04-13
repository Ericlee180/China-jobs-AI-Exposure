"""
Build site data from CSV and scores.json for Karpathy-style frontend.
Reads from occupations.csv and scores.json, writes to site/data.json.

Usage:
    uv run python build_site_data.py
"""

import json
import csv
from pathlib import Path

def categorize_occupation(title):
    """根据职业名称判断行业大类"""
    categories = {
        "信息技术": ["人工智能", "软件", "开发", "工程师", "技术", "数据", "网络", "计算机"],
        "生产制造": ["制造", "生产", "维修", "装配", "车工", "钳工", "电工", "焊工", "机械", "设备", "制冷", "玻璃", "缝纫"],
        "生活服务": ["厨师", "面点", "服务员", "美容", "美发", "保健", "养老", "家政", "调解", "导游", "咖啡", "调酒", "宠物"],
        "医疗健康": ["医疗", "护理", "药师", "康复", "口腔", "兽医", "动物", "健康", "保健按摩", "医疗护理"],
        "商业管理": ["管理", "销售", "市场", "人力", "财务", "会计", "行政", "经济", "金融", "信用", "电子商务"],
        "交通运输": ["驾驶", "物流", "仓储", "运输", "快递", "配送", "公路"],
        "建筑装修": ["建筑", "装修", "设计", "施工", "电工", "水暖", "制冷", "安装"],
        "农林牧渔": ["农业", "林业", "畜牧业", "养殖", "植保", "农作物", "检疫", "动物检疫"],
        "文化艺术": ["设计", "摄影", "表演", "艺术", "创作", "编辑", "记者", "编剧", "制图"],
        "其他": []
    }
    
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in title:
                return category
    return "其他"

def main():
    # 1. 读取评分数据
    scores = {}
    scores_path = Path("scores.json")
    if scores_path.exists():
        with open(scores_path, "r", encoding="utf-8") as f:
            scores_data = json.load(f)
            if isinstance(scores_data, dict) and "records" in scores_data:
                scores_data = scores_data["records"]
            scores = scores_data
        print(f"✅ 读取 scores.json，共 {len(scores)} 个职业")
    else:
        print("⚠️ 未找到 scores.json，将使用默认分数 0")
    
    # 2. 读取 CSV 数据
    csv_path = Path("occupations.csv")
    if not csv_path.exists():
        print(f"❌ 未找到 {csv_path}，请先运行 make_csv.py")
        return
    
    occupations = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        print(f"CSV 列名: {fieldnames}")
        
        id_field = 'slug' if 'slug' in fieldnames else 'title'
        
        for row in reader:
            title = row.get('title', '')
            if not title:
                continue
            
            identifier = row.get(id_field, title)
            
            # 获取评分
            score_info = scores.get(identifier, {})
            if isinstance(score_info, dict):
                ai_score = score_info.get("score", 0)
                rationale = score_info.get("reason", "")
            else:
                ai_score = 0
                rationale = ""
            
            if ai_score is None:
                ai_score = 0
            
            category = categorize_occupation(title)
            
            # 根据行业类别估算就业人数和薪资
            industry_defaults = {
                "信息技术": {"jobs": 30000, "pay": 120000},
                "生产制造": {"jobs": 50000, "pay": 70000},
                "生活服务": {"jobs": 80000, "pay": 45000},
                "医疗健康": {"jobs": 40000, "pay": 80000},
                "商业管理": {"jobs": 45000, "pay": 90000},
                "交通运输": {"jobs": 35000, "pay": 60000},
                "建筑装修": {"jobs": 38000, "pay": 65000},
                "农林牧渔": {"jobs": 25000, "pay": 50000},
                "文化艺术": {"jobs": 20000, "pay": 55000},
            }
            defaults = industry_defaults.get(category, {"jobs": 15000, "pay": 50000})
            
            education = row.get('education', '')
            if not education:
                education = "未知"
            
            occupations.append({
                "title": title,
                "jobs": defaults["jobs"],
                "pay": defaults["pay"],
                "outlook": 5,  # 默认前景增长率 5%
                "education": education,
                "exposure": ai_score,
                "exposure_rationale": rationale,
                "category": category,
                "url": f"pages/{identifier}.md" if identifier else None
            })
    
    # 3. 创建输出目录并保存
    Path("site").mkdir(exist_ok=True)
    output_path = Path("site/data.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(occupations, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 生成 {output_path}，共 {len(occupations)} 个职业")
    
    # 统计各类别数量
    category_counts = {}
    for occ in occupations:
        cat = occ['category']
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    print(f"\n📊 行业分类统计:")
    for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   - {cat}: {count} 个职业")
    
    # 显示第一条数据作为示例
    if occupations:
        print(f"\n📋 数据示例（第一条）:")
        print(json.dumps(occupations[0], ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()