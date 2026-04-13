"""
Score occupations using DeepSeek API.
Reads from occupations.csv and pages/*.md, writes to scores.json.

Usage:
    uv run python score.py
"""

import json
import time
import pandas as pd
from pathlib import Path
import requests

# DeepSeek API 配置
DEEPSEEK_API_KEY = "sk-8aaa78be5bbc4d47965a1346840f012b"  # 替换为你的真实密钥
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL_NAME = "deepseek-chat"  # DeepSeek 的模型名称

def load_occupation_description(md_path):
    """读取 Markdown 文件的前几段作为职业描述（控制 token 数）"""
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取标题、职业定义、主要工作任务（约 1500 字以内）
    lines = content.split('\n')
    description_lines = []
    char_count = 0
    for line in lines:
        description_lines.append(line)
        char_count += len(line)
        if char_count > 2000:  # 控制长度，避免 token 过多
            break
    
    return '\n'.join(description_lines)

def score_occupation(title, description):
    """调用 DeepSeek API 对单个职业进行评分"""
    
    prompt = f"""你是一个职业分析专家。请根据以下职业信息，评估该职业的"AI 影响度"（0-10分）。

评分标准：
- 0-2分：几乎不受AI影响，需要高度手工操作、情感交流或现场服务
- 3-4分：AI能提供辅助工具，但核心工作仍需人类
- 5-6分：AI能完成部分核心任务，人类与AI协作
- 7-8分：大部分核心任务可被AI自动化，人类转为监督角色
- 9-10分：整个职业的工作内容可被AI完全或近乎完全替代

职业名称：{title}
职业描述：
{description}

输出格式（仅输出JSON，不要有其他内容）：
{{"score": 分数, "reason": "简短理由"}}
"""
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,  # 降低随机性，让评分更稳定
    }
    
    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=30)
        
        # 检查状态码
        if response.status_code != 200:
            print(f"HTTP {response.status_code}")
            return {"score": None, "reason": f"HTTP {response.status_code}"}
        
        # 解析响应
        result = response.json()
        
        # 提取内容
        try:
            content = result['choices'][0]['message']['content']
        except (KeyError, IndexError) as e:
            print(f"响应结构异常: {e}")
            return {"score": None, "reason": "Invalid response structure"}
        
        # 提取 JSON
        start = content.find('{')
        end = content.rfind('}') + 1
        if start == -1 or end == 0:
            print(f"未找到 JSON: {content[:100]}")
            return {"score": None, "reason": "No JSON found"}
        
        json_str = content[start:end]
        score_data = json.loads(json_str)
        
        return score_data
        
    except requests.exceptions.RequestException as e:
        print(f"网络错误: {e}")
        return {"score": None, "reason": f"Network error: {e}"}
    except Exception as e:
        print(f"未知错误: {e}")
        return {"score": None, "reason": f"Error: {e}"}

def main():
    # 读取 CSV 获取职业列表
    df = pd.read_csv('occupations.csv')
    
    # 如果已有 scores.json，先加载已有的评分（实现断点续传）
    scores = {}
    if Path("scores.json").exists():
        with open("scores.json", "r", encoding="utf-8") as f:
            existing_scores = json.load(f)
            scores.update(existing_scores)
            print(f"✅ 加载已有评分，共 {len(scores)} 个职业")
    
    total = len(df)
    for idx, row in df.iterrows():
        title = row['title']
        slug = row['slug']
        
        # 如果已经评分过，跳过
        if slug in scores and scores[slug].get("score") is not None:
            print(f"📝 跳过 ({idx+1}/{total})：{title} (已有评分: {scores[slug]['score']})")
            continue
        
        md_path = Path(f'pages/{slug}.md')
        if not md_path.exists():
            print(f"⚠️ 跳过 {title}：Markdown 文件不存在")
            continue
        
        print(f"📝 正在评分 ({idx+1}/{total})：{title}...", end=" ", flush=True)
        
        # 读取职业描述
        description = load_occupation_description(md_path)
        
        # 调用 API 评分
        result = score_occupation(title, description)
        
        scores[slug] = {
            "title": title,
            "score": result.get("score"),
            "reason": result.get("reason")
        }
        
        if result.get("score") is not None:
            print(f"得分：{result.get('score')}")
        else:
            print(f"失败：{result.get('reason')}")
        
        # 每评分一个就保存一次，防止中途丢失
        with open('scores.json', 'w', encoding='utf-8') as f:
            json.dump(scores, f, ensure_ascii=False, indent=2)
        
        # 添加延迟，避免请求过快
        time.sleep(1)
    
    # 最终统计
    scored_count = sum(1 for v in scores.values() if v.get("score") is not None)
    print(f"\n✅ 评分完成！共 {scored_count}/{total} 个职业成功评分，结果保存在 scores.json")

if __name__ == "__main__":
    main()