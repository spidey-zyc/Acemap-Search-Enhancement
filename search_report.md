# Acemap Search Agent 测试报告

本报告对比了原始搜索与 Agent 增强搜索在不同场景下的表现。


## 测试场景: Case 1: 拼写错误纠正 (KG Grounding)
**用户查询:** `recent papers about Grnite`

### 🔴 Before: 原始搜索
> **结果:** 6543 篇 (可能包含无关结果)
- 1. Recent papers about molecular markers in PMF
- 2. VIII.—Criticisms on Recent Papers about Faults

### 🟢 After: Agent 增强搜索
- **策略:** **KG校准 (Grounding)** ✨
- **优化关键词:** `recent papers about Grnite` -> `Granite`
- **初步召回:** 10000 篇
- **执行过滤:** 年份 >= 2020
> **✅ 最终推荐:** 5 篇 (Top 5 展示)

| Title       |   Year |   Cited |
|:------------|-------:|--------:|
| Granite...  |   2021 |       0 |
| Granite...  |   2024 |       0 |
| GRANITE:... |   2023 |       0 |
| Granite...  |   2021 |       0 |
| Granite...  |   2022 |       0 |

---


## 测试场景: Case 2: 复杂意图与时间过滤 (Logic & Filtering)
**用户查询:** `Find papers on Basalt from 2023`

### 🔴 Before: 原始搜索
> **结果:** 10000 篇 (可能包含无关结果)
- 1. Selected Papers from EGC 2023
- 2. TCS Special Issue on Selected Papers from AlgoWin 2023

### 🟢 After: Agent 增强搜索
- **策略:** **KG校准 (Grounding)** ✨
- **优化关键词:** `Find papers on Basalt from 2023` -> `basalt`
- **初步召回:** 10000 篇
- **执行过滤:** 年份 >= 2023
> **✅ 最终推荐:** 1 篇 (Top 5 展示)

| Title     |   Year |   Cited |
|:----------|-------:|--------:|
| Basalt... |   2023 |       0 |

---


## 测试场景: Case 3: 跨语言/专业术语映射 (Translation)
**用户查询:** `帮我找关于板块构造的论文`

### 🔴 Before: 原始搜索
> **结果:** 0 篇 (搜索失败)

### 🟢 After: Agent 增强搜索
- **策略:** **KG校准 (Grounding)** ✨
- **优化关键词:** `帮我找关于板块构造的论文` -> `Plate tectonics`
- **初步召回:** 3031 篇
- **执行过滤:** 年份 >= 2020
> **✅ 最终推荐:** 5 篇 (Top 5 展示)

| Title              |   Year |   Cited |
|:-------------------|-------:|--------:|
| Plate Tectonics... |   2021 |       0 |
| Plate Tectonics... |   2020 |       0 |
| Plate Tectonics... |   2021 |       0 |
| Plate Tectonics... |   2024 |       0 |
| Plate Tectonics... |   2022 |       0 |

---


## 测试场景: Case 4: 术语缩写还原 (Normalization)
**用户查询:** `Papers about MORB`

### 🔴 Before: 原始搜索
> **结果:** 10000 篇 (可能包含无关结果)
- 1. Global MORB = N-MORB + E-MORB
- 2. Papers about papers

### 🟢 After: Agent 增强搜索
- **策略:** **KG校准 (Grounding)** ✨
- **优化关键词:** `Papers about MORB` -> `Mid-ocean-ridge basalt`
- **初步召回:** 141 篇
> **✅ 最终推荐:** 20 篇 (Top 5 展示)

| Title                             |   Year |   Cited |
|:----------------------------------|-------:|--------:|
| Mid-Ocean Ridge Basalt...         |   2011 |       0 |
| Mid-Ocean Ridge Basalt...         |   2023 |       0 |
| Mid-Ocean Ridge Basalt...         |   2015 |       0 |
| Mid-ocean-ridge basalt genesis... |   1987 |       2 |
| Mid-ocean ridge basalt (MORB)...  |   2011 |       1 |

---
