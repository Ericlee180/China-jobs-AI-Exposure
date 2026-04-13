"""
Process scraped JSON files into Markdown.

Reads from html/<id>.json, writes to pages/<slug>.md.
Extracts career information from the JSON structure.

Usage:
    uv run python process.py              # process all JSON files
    uv run python process.py --force      # re-process even if .md exists
"""

import argparse
import json
import os
import re

def extract_markdown_from_json(json_path):
    """从职业JSON文件中提取信息并生成Markdown内容"""
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # 检查数据有效性
    if data.get("code") != 200:
        print(f"  警告: {json_path} 返回码异常")
        return None
    
    career_data = data.get("data", {})
    base_info = career_data.get("base", {})
    dimension_info = career_data.get("dimension", {})
    
    # 开始构建Markdown内容
    md_lines = []
    
    # 1. 标题和基本信息
    career_name = base_info.get("careerName", "未知职业")
    md_lines.append(f"# {career_name}\n")
    
    # 职业口号
    poster = base_info.get("careerPoster")
    if poster:
        md_lines.append(f"> {poster}\n")
    
    # 职业代码
    career_code = base_info.get("careerCode")
    if career_code:
        md_lines.append(f"**职业代码**：{career_code}\n")
    
    # 2. 职业定义
    career_define = base_info.get("careerDefine")
    if career_define:
        md_lines.append("## 职业定义\n")
        md_lines.append(f"{career_define}\n")
    
    # 3. 基本信息表格
    md_lines.append("## 基本信息\n")
    md_lines.append("| 项目 | 内容 |")
    md_lines.append("|------|------|")
    
    # 建设单位
    sponsor = base_info.get("sponsorName")
    if sponsor:
        md_lines.append(f"| 建设单位 | {sponsor} |")
    
    # 职业等级
    career_grade = base_info.get("careerGrade")
    if career_grade:
        md_lines.append(f"| 职业等级 | {career_grade} |")
    
    # 包含工种
    type_works = base_info.get("typeWorks")
    if type_works:
        md_lines.append(f"| 包含工种 | {type_works} |")
    
    # 对应招聘岗位
    posts = base_info.get("posts")
    if posts:
        md_lines.append(f"| 对应招聘岗位 | {posts} |")
    
    # 学历要求
    education = base_info.get("education")
    if education:
        md_lines.append(f"| 学历要求 | {education} |")
    
    md_lines.append("")  # 空行
    
    # 4. 技能要求部分（从 dimension.childrenList 中提取）
    if dimension_info:
        children = dimension_info.get("childrenList", [])
        
        # 按 sort 排序，保持页面顺序
        children.sort(key=lambda x: x.get("sort", 0))
        
        for section in children:
            section_name = section.get("name")
            if not section_name:
                continue
                
            md_lines.append(f"## {section_name}\n")
            
            # 副标题（英文）
            e_name = section.get("eName")
            if e_name:
                md_lines.append(f"*{e_name}*\n")
            
            # 数据来源
            source = section.get("source")
            if source:
                md_lines.append(f"> {source}\n")
            
            # 处理列表数据
            items = section.get("list", [])
            if items:
                for item in items:
                    # 根据不同的 section 类型，提取不同的字段
                    if "work_task" in item:
                        # 主要工作任务
                        md_lines.append(f"- {item['work_task']}")
                    elif "evaluate" in item:
                        # 评价申报条件
                        grade = item.get("grade", "")
                        grade_name = {
                            "2": "四级/中级工",
                            "3": "三级/高级工", 
                            "4": "二级/技师",
                            "5": "一级/高级技师"
                        }.get(str(grade), f"{grade}级")
                        md_lines.append(f"### {grade_name}\n")
                        md_lines.append(f"{item['evaluate']}\n")
                    elif "name" in item and "base_career_picture_id" in item:
                        # 职业能力特征、评价方式等
                        md_lines.append(f"- {item['name']}")
                    else:
                        # 其他情况，尝试提取常见字段
                        content = item.get("work_task") or item.get("name") or item.get("evaluate")
                        if content:
                            md_lines.append(f"- {content}")
                md_lines.append("")  # 列表后空行
    
    # 5. 绿色职业标识
    is_green = base_info.get("isGreen")
    if is_green == "1":
        md_lines.append("---\n")
        md_lines.append("✅ **此职业为绿色职业**（指工作环境友好、可持续发展、符合环保要求的职业）\n")
    
    # 6. 数字化职业标识
    is_number = base_info.get("isNumber")
    if is_number == "1":
        md_lines.append("---\n")
        md_lines.append("💻 **此职业为数字职业**（指需要数字技能、与数字经济相关的职业）\n")
    
    return "\n".join(md_lines)


def slugify(name):
    """将职业名称转换为文件名友好的slug"""
    # 移除特殊字符，替换空格为短横线
    slug = re.sub(r'[^\w\s-]', '', name)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-').lower()


def main():
    parser = argparse.ArgumentParser(description="Convert JSON to Markdown")
    parser.add_argument("--force", action="store_true", help="Re-process even if .md exists")
    args = parser.parse_args()

    # 创建输出目录
    os.makedirs("pages", exist_ok=True)
    
    # 读取职业列表（用于获取名称和slug映射）
    with open("occupations-cn-full.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        if isinstance(data, dict) and "records" in data:
            occupations = data["records"]
        else:
            occupations = data

    processed = 0
    skipped = 0
    missing = 0

    for occ in occupations:
        career_id = occ["id"]
        career_name = occ["careerName"]
        
        # 使用id作为文件名，也可以使用slugified名称
        json_path = f"html/{career_id}.json"
        # 使用拼音或英文slug会更好，这里先用id
        md_filename = slugify(career_name) + ".md"
        md_path = f"pages/{md_filename}"
        
        # 也可以保留id作为文件名，更简单：
        # md_path = f"pages/{career_id}.md"
        
        if not os.path.exists(json_path):
            missing += 1
            print(f"  MISSING JSON: {career_name} (id: {career_id})")
            continue

        if not args.force and os.path.exists(md_path):
            skipped += 1
            continue

        print(f"  Processing: {career_name}...", end=" ", flush=True)
        
        try:
            md_content = extract_markdown_from_json(json_path)
            if md_content:
                with open(md_path, "w", encoding="utf-8") as f:
                    f.write(md_content)
                print("OK")
                processed += 1
            else:
                print("FAILED (no content)")
                
        except Exception as e:
            print(f"ERROR: {e}")

    total_json = len([f for f in os.listdir("html") if f.endswith(".json")])
    total_md = len([f for f in os.listdir("pages") if f.endswith(".md")])
    
    print(f"\n{'='*50}")
    print(f"处理统计:")
    print(f"  - 新生成 Markdown: {processed}")
    print(f"  - 跳过（已存在）: {skipped}")
    print(f"  - 缺失 JSON 文件: {missing}")
    print(f"  - 总计 JSON 文件: {total_json}")
    print(f"  - 总计 Markdown 文件: {total_md}")

if __name__ == "__main__":
    main()