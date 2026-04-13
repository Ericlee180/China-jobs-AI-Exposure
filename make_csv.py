"""
Extract structured data from Markdown files and generate occupations.csv.

Usage:
    uv run python make_csv.py
"""

import csv
import glob
import os
import re
from pathlib import Path

def parse_markdown_file(filepath):
    """
    从单个 Markdown 文件中提取所需字段。
    返回一个字典，包含所有提取到的信息。
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 初始化数据字典，所有字段默认为空字符串
    data = {
        'slug': Path(filepath).stem,  # 文件名作为 slug
        'title': '',
        'career_code': '',
        'education': '',
        'sponsor': '',
        'career_grades': '',
        'type_works': '',
        'posts': '',
        'tasks_count': 0,
    }
    
    # 1. 提取标题 (第一行的 # 标题)
    title_match = re.search(r'^# (.+)', content, re.MULTILINE)
    if title_match:
        data['title'] = title_match.group(1).strip()
    
    # 2. 提取职业代码
    code_match = re.search(r'\*\*职业代码\*\*：(.+)', content)
    if code_match:
        data['career_code'] = code_match.group(1).strip()
    
    # 3. 提取基本信息表格中的内容
    # 匹配从 "## 基本信息" 到下一个 "## " 之间的表格内容
    table_section = re.search(
        r'## 基本信息\n\n(.*?)(?=\n## |\Z)', 
        content, 
        re.DOTALL
    )
    if table_section:
        table_content = table_section.group(1)
        # 使用正则提取每个字段，格式为 | 字段名 | 内容 |
        sponsor_match = re.search(r'\|\s*建设单位\s*\|\s*(.+?)\s*\|', table_content)
        if sponsor_match:
            data['sponsor'] = sponsor_match.group(1).strip()
            
        grades_match = re.search(r'\|\s*职业等级\s*\|\s*(.+?)\s*\|', table_content)
        if grades_match:
            data['career_grades'] = grades_match.group(1).strip()
            
        type_works_match = re.search(r'\|\s*包含工种\s*\|\s*(.+?)\s*\|', table_content)
        if type_works_match:
            data['type_works'] = type_works_match.group(1).strip()
            
        posts_match = re.search(r'\|\s*对应招聘岗位\s*\|\s*(.+?)\s*\|', table_content)
        if posts_match:
            data['posts'] = posts_match.group(1).strip()
            
        edu_match = re.search(r'\|\s*学历要求\s*\|\s*(.+?)\s*\|', table_content)
        if edu_match:
            data['education'] = edu_match.group(1).strip()
    
    # 4. 统计主要工作任务的数量
    # 找到 "## 主要工作任务" 后的列表项 (以 - 开头的行)
    tasks_section = re.search(
        r'## 主要工作任务\n\n.*?\n(.*?)(?=\n## |\Z)', 
        content, 
        re.DOTALL
    )
    if tasks_section:
        tasks_content = tasks_section.group(1)
        # 统计以 "- " 开头的行
        tasks = re.findall(r'^- (.+)', tasks_content, re.MULTILINE)
        data['tasks_count'] = len(tasks)
    
    return data

def main():
    # 确保输出目录存在（通常不需要，因为就在当前目录）
    # os.makedirs("data", exist_ok=True)  # 如果想把 CSV 放在 data/ 下可以取消注释
    
    all_occupations = []
    md_files = glob.glob("pages/*.md")
    
    print(f"找到 {len(md_files)} 个 Markdown 文件，开始解析...")
    
    for filepath in md_files:
        try:
            occ_data = parse_markdown_file(filepath)
            all_occupations.append(occ_data)
            print(f"  ✓ 已解析: {occ_data['title']} ({occ_data['slug']})")
        except Exception as e:
            print(f"  ✗ 解析失败: {filepath} - 错误: {e}")
    
    if not all_occupations:
        print("没有成功解析任何文件，退出。")
        return
    
    # 定义 CSV 的列名（按你希望展示的顺序）
    fieldnames = [
        'slug', 
        'title', 
        'career_code', 
        'education', 
        'sponsor', 
        'career_grades', 
        'type_works', 
        'posts', 
        'tasks_count'
    ]
    
    # 写入 CSV 文件
    csv_path = "occupations.csv"
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_occupations)
    
    print(f"\n✅ 成功生成 CSV 文件: {csv_path}")
    print(f"   共包含 {len(all_occupations)} 个职业的数据。")

if __name__ == "__main__":
    main()