# src/kg_linker.py
import pandas as pd
from fuzzywuzzy import process
from .config import Config

class KGLinker:
    def __init__(self):
        print(f"Loading Knowledge Graph from {Config.DATA_PATH}...")
        self.vocab = []
        try:
            # 优化：只读取 subject 和 object 列，节省内存
            # 确保安装了 pyarrow: pip install pyarrow
            df = pd.read_parquet(Config.DATA_PATH, engine='pyarrow', columns=['subject', 'object'])
            
            # 构建词表：合并两列并去重
            vocab_set = set(df['subject'].dropna().unique()) | set(df['object'].dropna().unique())
            self.vocab = list(vocab_set)
            
            print(f"KG Loaded. Vocab size: {len(self.vocab)}")
            
        except Exception as e:
            print(f"⚠️ Error loading KG: {e}")
            print("Running in offline mode (No Grounding).")
            self.vocab = []

    def ground_keyword(self, keyword, threshold=85):
        """
        输入一个词，返回图谱中最相似的标准词。
        如果相似度不够高，就返回原词。
        """
        if not self.vocab or not keyword:
            return keyword
            
        # 使用 fuzzywuzzy 进行模糊匹配
        # extractOne 返回格式: ('匹配词', 分数)
        best_match, score = process.extractOne(keyword, self.vocab)
        
        if score >= threshold:
            # 只有当相似度很高时（比如 > 85），才认为是拼写错误并修正
            # print(f"[KG Grounding] '{keyword}' -> '{best_match}' (Score: {score})") # 调试用
            return best_match
        
        return keyword