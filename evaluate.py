import pandas as pd
import time
from src.agent import SearchAgent
from src.config import Config

# 为了让表格显示好看，调整 Pandas 显示设置
pd.set_option('display.max_colwidth', 40)
pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.expand_frame_repr', False)

def create_mock_kg_if_needed():
    """
    如果还没下载 Parquet 文件，临时创建一个假的 KG 用于测试代码逻辑
    """
    import os
    if not os.path.exists(Config.DATA_PATH):
        print("⚠️ 未检测到 Parquet 文件，正在创建临时测试数据...")
        mock_data = {
            'subject': ['Igneous rock', 'Granite', 'Basalt', 'Plate tectonics', 'Sedimentary basin'],
            'object': ['Quartz', 'Feldspar', 'Lava', 'Continental drift', 'Oil reservoir']
        }
        df = pd.read_parquet(Config.DATA_PATH) if os.path.exists(Config.DATA_PATH) else pd.DataFrame(mock_data)
        # 这里的逻辑主要依赖 src/kg_linker.py 的读取，
        # 如果你已有真实文件，这个函数会自动被跳过，或者你可以手动在 kg_linker 里把路径指过去
        pass

def highlight_diff(row):
    """
    辅助函数：比较原始词和校准后的词，如果有变化，返回标记
    """
    raw = set(row['Raw_Keywords'])
    final = set(row['Final_Keywords'])
    if raw != final:
        return "✅ 已修正"
    return "-"

def run_test_suite():
    print(f"🚀 正在初始化 Agent (模型: {Config.MODEL_NAME})...")
    agent = SearchAgent()
    
    # === 定义你的测试集 ===
    test_cases = [
        # 1. 基础正常 Case
        "Find papers about Granite from MIT",
        
        # 2. 拼写错误 Case (这是你的得分亮点！)
        "Research on Grnite and Bsallt",  # Granite, Basalt
        "Sdimetary basin analysis",       # Sedimentary basin
        
        # 3. 复杂意图 Case
        "Recent articles by author John Smith on Plate Tctnics",
        
        # 4. 中文输入 Case (测试 LLM 翻译 + KG 映射)
        "帮我找关于 火成岩 的论文", 
        
        # 5. 干扰项 Case (测试是否胡乱匹配)
        "Papers about UnknowxxxxThing", # 图谱里肯定没有这个词
    ]
    
    results = []

    print(f"📋 开始执行测试，共 {len(test_cases)} 条...\n")
    
    for i, query in enumerate(test_cases):
        print(f"Testing [{i+1}/{len(test_cases)}]: {query} ...")
        start_time = time.time()
        
        # --- 核心调用 ---
        # 注意：为了对比，我们需要修改一下 src/agent.py 
        # 让它把 raw_intent 也返回出来，或者我们在测试里分步调用
        # 这里演示分步调用以获取中间结果：
        
        # 1. LLM 原始提取
        raw_intent = agent.llm.extract_intent(query)
        raw_kws = raw_intent.get('keywords', [])
        
        # 2. KG 校准
        final_keywords = []
        for kw in raw_kws:
            # 这里调用 agent 内部的 kg 模块
            final_keywords.append(agent.kg.ground_keyword(kw))
            
        final_intent = raw_intent.copy()
        final_intent['keywords'] = final_keywords
        # ----------------
        
        duration = time.time() - start_time
        
        results.append({
            "Query": query,
            "Raw_Keywords": raw_kws,
            "Final_Keywords": final_keywords,
            "Other_Info": f"Inst: {final_intent.get('institution')}, Time: {final_intent.get('year_start')}",
            "Time(s)": round(duration, 2)
        })

    # 生成报告
    df_result = pd.DataFrame(results)
    
    # 添加一列状态，看是否触发了校准
    df_result['Status'] = df_result.apply(highlight_diff, axis=1)
    
    # 调整列顺序
    cols = ['Status', 'Query', 'Raw_Keywords', 'Final_Keywords', 'Other_Info', 'Time(s)']
    df_result = df_result[cols]
    
    print("\n" + "="*50)
    print("📊 测试结果报告")
    print("="*50)
    print(df_result)
    
    # 导出为 CSV 方便放入报告
    df_result.to_csv("test_report.csv", index=False, encoding='utf-8-sig')
    print("\n✅ 结果已保存至 test_report.csv")

if __name__ == "__main__":
    # create_mock_kg_if_needed() # 如果你还没有真实数据，取消这行注释
    run_test_suite()