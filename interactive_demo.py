import requests
import pandas as pd
import json
import sys
import os
import time

# === 1. 环境设置 ===
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.agent import SearchAgent

# === 2. 配置 ===
ACEMAP_API_URL = "https://acemap.info/api/v1/work/search"

# ==========================================
# 3. API 调用函数 (复用之前的稳定版本)
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
        if "results" in data:
            papers = data["results"]
            total = data.get("meta", {}).get("count", len(papers))
            return total, papers
        return 0, []
    except Exception:
        return 0, []

# ==========================================
# 4. 交互式主逻辑
# ==========================================
def start_interactive_session():
    print("\n" + "="*60)
    print("🤖 Acemap 智能搜索增强助手 (Interactive Demo)")
    print("="*60)
    print("正在初始化 Agent (加载知识图谱)... 请稍候...")
    
    # 初始化 Agent (耗时操作只做一次)
    start_time = time.time()
    try:
        agent = SearchAgent()
        print(f"✅ 初始化完成! (耗时: {time.time() - start_time:.2f}s)")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return

    print("\n💡 提示: 输入 'q', 'exit', 'quit' 可退出程序")
    print("-" * 60)

    while True:
        # 1. 获取用户输入
        try:
            user_query = input("\n👉 请输入您的查询 (例如: 'Find papers on Grnite'): ").strip()
        except KeyboardInterrupt:
            print("\n程序已终止。")
            break

        if user_query.lower() in ['q', 'exit', 'quit']:
            print("👋 再见！")
            break
        
        if not user_query:
            continue

        print(f"\n🔄 正在分析意图...")
        
        # 2. Agent 解析
        try:
            agent_output = agent.parse(user_query)
        except Exception as e:
            print(f"❌ Agent 解析出错: {e}")
            continue

        # 3. 提取分析结果
        params = agent_output.get('search_params', {})
        filters = agent_output.get('filters', {})
        
        grounded_kws = params.get('keywords_grounded', [])
        raw_kws = params.get('keywords_raw', [])
        
        # 4. 确定搜索策略
        best_keyword = user_query
        strategy = "原句兜底"
        
        if grounded_kws:
            best_keyword = grounded_kws[0]
            strategy = "✨ KG 知识校准 (Grounding)"
        elif raw_kws:
            best_keyword = raw_kws[0]
            strategy = "🧠 LLM 意图提取"
        
        # 5. 展示 Agent 的思考过程 (这是得分点！)
        print(f"   [策略]: {strategy}")
        if best_keyword != user_query:
            print(f"   [优化]: '{user_query}' ==> '{best_keyword}'")
        
        if filters.get('year_start') or filters.get('institution'):
            print(f"   [过滤]: {json.dumps(filters, ensure_ascii=False)}")

        # 6. 执行搜索
        print(f"🔍 正在检索 Acemap 数据库...")
        total, papers = call_acemap_api(best_keyword, limit=20) # 多取一点用于过滤
        
        # 7. 执行客户端过滤
        year_start = filters.get('year_start')
        final_papers = []
        
        for p in papers:
            keep = True
            # 年份过滤
            if year_start:
                p_year = p.get('publication_year')
                if not (p_year and int(p_year) >= int(year_start)):
                    keep = False
            
            if keep:
                final_papers.append(p)
        
        # 8. 展示结果
        print("-" * 60)
        if not final_papers:
            print("⚠️ 未找到符合条件的论文 (可能条件过于严格)。")
        else:
            print(f"✅ 找到 {len(final_papers)} 篇相关论文 (展示 Top 5):")
            
            table_data = []
            for p in final_papers[:5]:
                title = p.get('display_name') or p.get('title') or "No Title"
                table_data.append({
                    "Year": p.get('publication_year', '-'),
                    "Cited": p.get('cited_by_count', 0),
                    "Title": title
                })
            
            # 打印表格
            df = pd.DataFrame(table_data)
            print(df.to_markdown(index=False))
        print("-" * 60)

if __name__ == "__main__":
    start_interactive_session()