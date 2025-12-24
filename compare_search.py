import requests
import pandas as pd
import json
import sys
import os
import io

# === 1. 环境与路径设置 ===
# 确保能导入 src 目录下的模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.agent import SearchAgent

# === 2. 配置 ===
ACEMAP_API_URL = "https://acemap.info/api/v1/work/search"
REPORT_FILE = "search_report.md"  # 结果将保存到这个文件

# 用于缓存输出日志，最后统一写入文件
log_buffer = []

def log(text=""):
    """同时打印到终端和缓存到文件"""
    print(text)
    log_buffer.append(text)

# ==========================================
# 3. API 调用 (保持之前修复后的版本)
# ==========================================
def call_acemap_api(keyword, limit=10):
    if not keyword:
        return 0, []

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    params = {
        "keyword": keyword,
        "page": 1,
        "size": limit,
        "order": "desc"
    }
    
    try:
        response = requests.get(ACEMAP_API_URL, params=params, headers=headers, timeout=10)
        if response.status_code != 200:
            return 0, []

        data = response.json()
        
        # 适配 Acemap 新版 JSON 结构 {"results": [...]}
        if "results" in data:
            papers = data["results"]
            total = data.get("meta", {}).get("count", len(papers))
            return total, papers
        else:
            return 0, []
    except Exception:
        return 0, []

# ==========================================
# 4. 核心对比逻辑 (增强版)
# ==========================================
def run_comparison(case_name, user_query, agent):
    log(f"\n## 测试场景: {case_name}")
    log(f"**用户查询:** `{user_query}`\n")

    # --- 场景 A: Before (直接搜原句) ---
    log("### 🔴 Before: 原始搜索")
    total_raw, papers_raw = call_acemap_api(user_query, limit=5)
    
    if total_raw == 0:
        log(f"> **结果:** 0 篇 (搜索失败)")
    else:
        log(f"> **结果:** {total_raw} 篇 (可能包含无关结果)")
        # 简单展示前2篇标题
        for i, p in enumerate(papers_raw[:2]):
            title = p.get('display_name') or p.get('title')
            log(f"- {i+1}. {title}")

    # --- 场景 B: After (Agent 增强) ---
    log("\n### 🟢 After: Agent 增强搜索")
    
    # 1. Agent 解析意图
    try:
        agent_output = agent.parse(user_query)
    except Exception as e:
        log(f"❌ Agent Error: {e}")
        return

    # 获取参数
    params = agent_output.get('search_params', {})
    filters = agent_output.get('filters', {})
    
    grounded_kws = params.get('keywords_grounded', [])
    raw_kws = params.get('keywords_raw', [])
    
    # 2. 选词策略
    best_keyword = user_query
    strategy = "原句兜底"
    
    if grounded_kws:
        best_keyword = grounded_kws[0]
        strategy = "**KG校准 (Grounding)** ✨"
    elif raw_kws:
        best_keyword = raw_kws[0]
        strategy = "**LLM提取 (Extraction)**"
        
    log(f"- **策略:** {strategy}")
    log(f"- **优化关键词:** `{user_query}` -> `{best_keyword}`")
    
    # 3. API 召回
    # 为了演示过滤效果，我们多召回一些数据 (limit=20)
    total_opt, papers_opt = call_acemap_api(best_keyword, limit=20)
    log(f"- **初步召回:** {total_opt} 篇")

    # 4. 客户端智能过滤 (Client-side Filtering)
    year_start = filters.get('year_start')
    institution = filters.get('institution')
    
    final_papers = []
    
    if year_start:
        log(f"- **执行过滤:** 年份 >= {year_start}")
        for p in papers_opt:
            p_year = p.get('publication_year')
            # 只有年份存在且符合要求才保留
            if p_year and int(p_year) >= int(year_start):
                final_papers.append(p)
    else:
        final_papers = papers_opt
        
    # (可选) 机构过滤逻辑
    # 注意：Acemap API 返回列表通常不含机构信息，这里仅做逻辑演示
    if institution:
         log(f"- **意图识别到的机构:** {institution} (注: 因API限制，本步骤仅做展示，暂未执行严格过滤)")

    # 5. 生成结果表格
    if not final_papers:
        log("> **最终推荐:** 无符合条件的论文")
    else:
        log(f"> **✅ 最终推荐:** {len(final_papers)} 篇 (Top 5 展示)")
        
        table_data = []
        for p in final_papers[:5]:
            title = p.get('display_name') or p.get('title') or "No Title"
            table_data.append({
                "Title": title[:50] + "...", # 截断标题
                "Year": p.get('publication_year', 'N/A'),
                "Cited": p.get('cited_by_count', 0)
            })
            
        # 使用 Pandas 生成 Markdown 表格
        df = pd.DataFrame(table_data)
        log("\n" + df.to_markdown(index=False))

    log("\n---\n")

# ==========================================
# 5. 主程序入口
# ==========================================
if __name__ == "__main__":
    # 初始化 Agent (只加载一次 KG)
    print("🚀 初始化 Agent 中... (加载 Parquet 可能需要几秒)")
    agent = SearchAgent()
    
    # 准备报告头
    log("# Acemap Search Agent 测试报告\n")
    log("本报告对比了原始搜索与 Agent 增强搜索在不同场景下的表现。\n")

    # === 测试用例 1: 拼写错误与术语校准 ===
    # 目的: 展示 GAKG 的 Grounding 能力
    run_comparison(
        case_name="Case 1: 拼写错误纠正 (KG Grounding)",
        user_query="recent papers about Grnite",
        agent=agent
    )
    
    # === 测试用例 2: 多条件复杂逻辑 ===
    # 目的: 展示 LLM 的意图提取 + 客户端年份过滤
    run_comparison(
        case_name="Case 2: 复杂意图与时间过滤 (Logic & Filtering)",
        user_query="Find papers on Basalt from 2023",
        agent=agent
    )

    # === 测试用例 3: 跨语言检索 ===
    # 目的: 展示 LLM 将中文口语转化为英文学术术语的能力
    run_comparison(
        case_name="Case 3: 跨语言/专业术语映射 (Translation)",
        user_query="帮我找关于板块构造的论文", 
        # Agent 会将其翻译为 "Plate tectonics"
        agent=agent
    )

    # === 测试用例 4: 术语消歧/缩写还原 (可选) ===
    # 如果你的图谱里有 MORB -> Mid-Ocean Ridge Basalt 的关系
    run_comparison(
        case_name="Case 4: 术语缩写还原 (Normalization)",
        user_query="Papers about MORB", 
        agent=agent
    )

    # 保存报告
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(log_buffer))
    
    print(f"✅ 测试完成！完整报告已保存至: {os.path.abspath(REPORT_FILE)}")