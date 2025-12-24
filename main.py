# main.py
from src.agent import SearchAgent

def main():
    # 实例化 Agent (会加载一次数据)
    agent = SearchAgent()
    
    # 模拟输入
    queries = [
        "找一下MIT关于Grnite的论文", # 拼写错误 + 机构
        "最近三年的板块构造研究"    # 时间 + 关键词
    ]
    
    for q in queries:
        print(f"\nUser: {q}")
        result = agent.parse(q)
        print(f"Agent Output: {result}")

if __name__ == "__main__":
    main()