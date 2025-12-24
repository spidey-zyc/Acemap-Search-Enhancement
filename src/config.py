import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

class Config:
    # 自动获取当前项目的根目录
    BASE_DIR = Path(__file__).parent.parent
    
    # 获取 API 设置
    API_KEY = os.getenv("OPENAI_API_KEY")
    BASE_URL = os.getenv("OPENAI_BASE_URL")
    
    # 构建数据文件的绝对路径 (兼容 Windows/Mac/Linux)
    DATA_PATH = BASE_DIR / os.getenv("GAKG_PATH", "data/gakg_subset.parquet")

    # 模型选择
    MODEL_NAME = "qwen-plus" 