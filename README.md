# Acemap Search Agent - 先导项目

> **项目选题**: 选题三 - 基于知识图谱的 Acemap 搜索增强  
> **负责模块**: Member A (意图识别与代理模块)  
> **核心功能**: LLM 意图提取 + GAKG 知识校准 + 客户端逻辑过滤

## 📖 项目简介
本项目构建了一个智能搜索代理 (Search Agent)，旨在解决 Acemap 现有搜索接口在处理**自然语言长句**、**拼写错误**及**跨语言检索**时的局限性。

系统通过 **大语言模型 (LLM)** 提取用户意图，结合 **GAKG 知识图谱** 进行术语校准 (Grounding)，并调用 Acemap API 进行检索与二次过滤，显著提升了搜索结果的精准度与召回率。

---

## ⚙️ 环境配置 (Configuration)

为了复现本项目，请按照以下步骤配置环境与 API 密钥。

### 1. 安装依赖
本项目基于 Python 开发，请确保已安装 Python 3.8+。
```bash
pip install -r requirements.txt
```

### 2. 配置 .env 文件 (关键步骤)

由于涉及 API 密钥安全，请在项目根目录下创建一个`.env` 文件（或复制提供的 .env.example），并填入您的配置信息。

`.env` 文件内容模板：
```toml
# ================= LLM 设置 =================
# 您的 OpenAI API Key (必填)
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# LLM 模型名称 (推荐 qwen-plus, gpt-4o, gpt-3.5-turbo)
LLM_MODEL_NAME=qwen-plus

# API Base URL (如果您使用的不是阿里云，请修改此项)
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# ================= 数据路径 =================
# GAKG 知识图谱数据路径 (请确保该文件在 data 目录下)
DATA_PATH=data/gakg-subset.parquet
```
    

## 🚀 快速开始 (Quick Start)
本项目提供了两个脚本，分别用于交互式体验和批量效果评估。

### 1. 启动交互式搜索 (推荐)

这是一个模拟用户查询的命令行工具。您可以输入任意自然语言，观察 Agent 如何分析意图、校准术语并过滤结果。
```bash
python interactive_demo.py
```

推荐测试查询 (Test Cases)：

* 拼写纠错: `find papers on Grnite `(Grnite -> Granite)
* 跨语言: `帮我找关于板块构造的论文 `(中文 -> Plate tectonics)
* 复杂逻辑: `Basalt papers from 2023 `(年份过滤)

### 2. 生成对比测试报告

该脚本会自动运行预设的测试集，对比“原始搜索”与“Agent 增强搜索”的效果，并生成 `search_report.md`报告。
```bash
python compare_search.py
```

## 📂 文件结构说明
```
Project_Root/
├── src/
│   ├── agent.py          # [核心] SearchAgent 类，统筹 LLM 和 KG
│   ├── llm_client.py     # LLM 接口，包含 Prompt Engineering (翻译/单数化)
│   ├── kg_linker.py      # 知识图谱模块，负责模糊匹配与术语校准
│   └── config.py         # 配置加载模块
├── data/
│   └── gakg-subset.parquet  # 知识图谱子集数据
├── interactive_demo.py   # [入口] 交互式查询脚本
├── compare_search.py     # [入口] 自动化评估脚本
├── requirements.txt      # 依赖库列表
├── .env                  # 配置文件 (需手动创建)
└── README.md             # 项目说明文档
```
## 📊 评估指标与效果
本系统引入了以下增强设计：

* Recall (召回率) 提升: 通过 KG 拼写纠错，将因拼写错误导致的 0 结果查询成功召回。
* Quality (质量) 提升: 通过跨语言映射，将中文查询转化为英文学术术语，大幅提升了检索文献的引用率与国际影响力。
* Precision (准确率) 提升: 通过客户端后处理 (Post-processing)，实现了 API 不支持的年份与机构精确过滤。

注意:本项目中的数据过滤逻辑目前在客户端运行，用于验证 Agent 解析参数的准确性。在后续的小组大作业中，该部分将迁移至后端系统模块。