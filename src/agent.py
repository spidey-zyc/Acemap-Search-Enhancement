from typing import Dict, Any, List
from .llm_client import LLMClient
from .kg_linker import KGLinker

class SearchAgent:
    def __init__(self):
        self.llm = LLMClient()
        self.kg = KGLinker()

    def parse(self, user_query: str) -> Dict[str, Any]:
        """
        全流程：Query -> LLM提取 -> KG校准 -> 标准化参数
        """
        # 1. LLM 提取粗糙意图
        # 预期格式: {'keywords': ['Grnite'], 'institution': ..., 'year_start': ...}
        raw_intent = self.llm.extract_intent(user_query)
        
        # 打印调试信息，确认 LLM 是否工作
        print(f"[Debug] LLM Raw Extract: {raw_intent}")

        # 获取原始关键词 (增加容错：万一 LLM 返回了字符串而不是列表)
        raw_keywords = raw_intent.get('keywords', [])
        if isinstance(raw_keywords, str):
            raw_keywords = [raw_keywords]
        
        # 2. KG 校准关键词 (生成新列表，不要覆盖旧的)
        grounded_keywords = []
        for kw in raw_keywords:
            # 拿着原始词去图谱里查标准词
            standard_kw = self.kg.ground_keyword(kw)
            grounded_keywords.append(standard_kw)
            
        # 3. 构造符合 compare_search.py 标准的输出结构
        # === 关键修改点 ===
        output = {
            "search_params": {
                "keywords_raw": raw_keywords,          # 保留原始词，供对比
                "keywords_grounded": grounded_keywords # 校准后的词，供搜索
            },
            "filters": {
                # 把过滤条件单独摘出来
                "institution": raw_intent.get('institution'),
                "author": raw_intent.get('author'),
                "year_start": raw_intent.get('year_start'),
                "year_end": raw_intent.get('year_end')
            }
        }
        
        return output