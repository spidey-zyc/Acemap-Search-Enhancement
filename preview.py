import pandas as pd
from difflib import get_close_matches

# ---------------------------------------------------------
# 配置：你的 Parquet 文件路径
PARQUET_PATH = "data/gakg_subset.parquet" 
# ---------------------------------------------------------

def inspect_parquet():
    """
    功能 1: 查看 Parquet 文件内部结构
    """
    print("\n" + "="*50)
    print(f"📂 正在读取文件: {PARQUET_PATH}")
    print("="*50)
    
    try:
        # engine='pyarrow' 是读取 parquet 的关键
        df = pd.read_parquet(PARQUET_PATH, engine='pyarrow')
        
        print(f"✅ 读取成功！数据集共有 {len(df)} 行数据。")
        print("\n[ 数据预览 (前 5 行) ]")
        print(df.head().to_markdown(index=False)) # 打印漂亮的表格
        
        print("\n[ 列信息 ]")
        print(df.info())
        
        return df
    except Exception as e:
        print(f"❌ 读取失败: {e}")
        print("💡 提示: 请确保你安装了 pyarrow (pip install pyarrow)")
        # 如果没有真实文件，返回一个模拟的 DataFrame 用于演示
        return create_mock_dataframe()

def create_mock_dataframe():
    """创建一个模拟数据，防止报错，方便演示"""
    print("\n⚠️ 使用模拟数据进行演示...")
    data = {
        'subject': ['Igneous rock', 'Granite', 'Basalt', 'Sedimentary basin', 'Plate tectonics'],
        'relation': ['is_a', 'is_a', 'is_a', 'related_to', 'related_to'],
        'object': ['Rock', 'Igneous rock', 'Igneous rock', 'Geology', 'Geophysics'],
        'paperid': [1001, 1002, 1003, 1004, 1005]
    }
    return pd.DataFrame(data)

def visualize_impact(df_kg):
    """
    功能 2: 直观展示意图分析前后的区别
    """
    print("\n" + "="*50)
    print("🧠 意图分析效果模拟 (Before vs After)")
    print("="*50)

    # 1. 准备知识库词表
    vocab = set(df_kg['subject'].unique()) | set(df_kg['object'].unique())
    
    # 2. 模拟几个用户的查询场景 (包含拼写错误)
    test_cases = [
        # (Case 1) 拼写错误: Grnite -> Granite
        {"query": "找一下 MIT 关于 Grnite 的论文", "llm_raw": ["Grnite", "MIT"]},
        # (Case 2) 模糊输入: Basalt -> Basalt (无需修改)
        {"query": "帮我找 Basalt 相关的研究", "llm_raw": ["Basalt"]},
        # (Case 3) 严重拼写错误: Sedimentary bsin -> Sedimentary basin
        {"query": "关于 Sedimentary bsin 的文章", "llm_raw": ["Sedimentary bsin"]}
    ]
    
    results = []
    
    # 3. 运行 "KG 校准" 逻辑
    for case in test_cases:
        raw_kws = case['llm_raw']
        grounded_kws = []
        status_log = []
        
        for kw in raw_kws:
            # 模拟 KG 查找 (简单模糊匹配)
            matches = get_close_matches(kw, vocab, n=1, cutoff=0.7)
            
            if kw == "MIT": # 假设这是机构，不在地质图谱里
                grounded_kws.append(kw)
                continue
                
            if matches:
                fixed_word = matches[0]
                grounded_kws.append(fixed_word)
                if fixed_word != kw:
                    status_log.append(f"🛠️ 修正: {kw} -> {fixed_word}")
            else:
                grounded_kws.append(kw) # 没找到，保持原样
        
        results.append({
            "User Query (用户输入)": case['query'],
            "🔴 Before (LLM直出)": str(raw_kws),
            "🟢 After (KG增强)": str(grounded_kws),
            "✨ 效果": ", ".join(status_log) if status_log else "-"
        })

    # 4. 打印对比表格
    df_res = pd.DataFrame(results)
    print(df_res.to_markdown(index=False))

if __name__ == "__main__":
    # 1. 看数据
    df = inspect_parquet()
    
    # 2. 看效果
    if df is not None:
        visualize_impact(df)