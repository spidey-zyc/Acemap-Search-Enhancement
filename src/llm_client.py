# src/llm_client.py
from openai import OpenAI
import json
from .config import Config

class LLMClient:
    def __init__(self):
        # 初始化客户端
        self.client = OpenAI(api_key=Config.API_KEY, base_url=Config.BASE_URL)

    def extract_intent(self, user_query):
        """
        发送 Prompt 并解析 JSON，提取结构化意图
        """
        # --- 关键修改：Prompt 必须明确要求返回哪些字段 ---
        prompt = f"""
        You are an expert academic search assistant, a professional Geology Librarian and Search Query Optimizer.
        Analyze the user query: "{user_query}".
        Your task is to convert the user's natural language query into a structured JSON for an academic search engine.

        ### Guidelines:
        1. **Keywords (Critical)**: 
           - Extract the main geological/scientific terms.
           - **Normalize to Singular form**: e.g., "rocks" -> "rock", "volcanoes" -> "volcano".
           - **Translate to English**: If the query is in Chinese, translate keywords to standard English geological terms.
           - **Specific Terms**: Prefer specific terms over general ones (e.g., use "Granite" instead of just "Rock" if mentioned).

        2. **Institution**: 
           - Extract the university or organization name.
           - **Expand Abbreviations**: Convert "MIT" to "Massachusetts Institute of Technology", "CAS" to "Chinese Academy of Sciences". Use the official full name.

        3. **Time**:
           - If the user says "recent" or "latest", set 'year_start' to 2020.
           - If a specific year is mentioned (e.g., "since 2015"), use that.

        Output JSON format:
        {{
            "keywords": ["English Term 1", "English Term 2"], 
            "institution": "English Name or null",
            "author": "Name or null",
            "year_start": 2020 (int or null),
            "year_end": null
        }}

        Rules:
        - Only return the JSON object.

        ### Examples:
        - Input: "find papers on rocks"
          Output: {{"keywords": ["rock"], "institution": null, ...}}  <-- Note: "rock" (singular)
        
        - Input: "Granite research from MIT"
          Output: {{"keywords": ["granite"], "institution": "Massachusetts Institute of Technology", ...}} <-- Note: Full Name
        
        - Input: "帮我找关于板块构造的论文"
          Output: {{"keywords": ["plate tectonics"], ...}} <-- Note: Translated

        ### Output Format (Strict JSON only):
        {{
            "keywords": ["Term 1", "Term 2"], 
            "institution": "Full Name or null",
            "author": "Name or null",
            "year_start": 2020 (int or null),
            "year_end": null
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=Config.MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0 # 温度设为0，让输出更稳定
            )
            content = response.choices[0].message.content
            
            # 清洗一下返回内容，防止包含 ```json ``` 标记
            content = content.replace("```json", "").replace("```", "").strip()
            
            return json.loads(content)
            
        except json.JSONDecodeError:
            print(f"[LLM Error] Failed to parse JSON. Raw content: {content}")
            # 降级处理：提取失败时，把整个查询当做关键词
            return {"keywords": [user_query]}
            
        except Exception as e:
            print(f"[LLM Error] API Call failed: {e}")
            return {"keywords": [user_query]}