# Prompt增强总结

## 概述

已将您提供的专业电商搜索算法评估标准整合到 `eval_agent.py` 的大模型评测prompt中。

## 核心增强内容

### 1. 角色定位
**原角色**: 即时零售推荐系统评测专家  
**新角色**: 资深的电商搜索算法专家和数据标注员

### 2. 核心评估标准（新增）

#### 2.1 核心意图匹配
评估商品是否解决了用户的核心需求。

**示例说明**:
- 搜"退烧药"，退热贴只能算部分匹配（物理降温而非药物）
- 搜"iPhone 15"，iPhone 14 算不相关或弱相关
- 搜"布洛芬"，推荐了对乙酰氨基酚属于替代方案
- 搜"苹果"，推荐了苹果手机壳而不是水果属于弱相关
- 搜"婴儿退烧药"，推荐了成人退烧药属于弱相关

#### 2.2 属性一致性
评估品牌、型号、规格、适用人群等关键属性是否一致。

**考察要点**:
- 品牌是否匹配（如搜"耐克"，推荐阿迪达斯属于品牌不符）
- 型号是否匹配（如搜"iPhone 15 Pro"，推荐iPhone 15属于型号不符）
- 规格是否匹配（如搜"500ml"，推荐"300ml"属于规格偏差）
- 适用人群是否匹配（如搜"婴儿"，推荐成人用品属于人群不符）

#### 2.3 时效性与可用性
评估商品是否在售，是否符合当前的季节或紧急程度。

**考察要点**:
- 商品是否在售（非下架或缺货状态）
- 配送时效是否符合紧急程度
- 是否符合季节性需求

### 3. 评分等级定义（更新）

| 分数 | 等级 | 定义 |
|------|------|------|
| 5分 | 完美匹配 | 商品完全符合用户意图，属性精准，无歧义 |
| 4分 | 高度相关 | 商品符合核心意图，但次要属性略有偏差 |
| 3分 | 一般相关/替代方案 | 商品能解决部分问题，或者是次优替代品 |
| 2分 | 弱相关 | 商品仅包含关键词，但核心意图不符 |
| 1分 | 不相关 | 商品与查询完全无关，或错误类别 |

### 4. 输出格式增强

新增以下字段：

```json
{
    "scores": {
        "accuracy": "1-5的整数",
        "timeliness": "1-5的整数",
        "personalization": "1-5的整数",
        "safety": "0-5的整数",
        "diversity": "1-5的整数",
        "novelty": "1-5的整数"
    },
    "item_evaluations": [
        {
            "item_name": "商品名称",
            "score": "1-5的整数",
            "reasoning": "简短的分析理由",
            "category_match": "布尔值, 品类是否匹配",
            "attribute_match": "布尔值, 关键属性是否匹配"
        }
    ],
    "issues": ["问题列表"],
    "suggestions": ["建议列表"],
    "evaluation_summary": "整体评价（50-100字）",
    "overall_assessment": {
        "core_intent_match": "核心意图匹配情况说明",
        "attribute_consistency": "属性一致性说明",
        "timeliness_availability": "时效性与可用性说明"
    }
}
```

## Prompt结构

```markdown
# 评测任务
## 1. 用户查询分析
## 2. 推荐系统响应
## 3. 商品结构化数据

---

# 核心评估标准
## 1. 核心意图匹配
## 2. 属性一致性
## 3. 时效性与可用性

---

# 评分等级定义（1-5分）
## 5分 (完美匹配)
## 4分 (高度相关)
## 3分 (一般相关/替代方案)
## 2分 (弱相关)
## 1分 (不相关)

---

# 多维度综合评测
## accuracy（需求匹配度）- 权重25%
## timeliness（时效可信度）- 权重20%
## personalization（个性化程度）- 权重20%
## safety（安全引导）- 权重20%
## diversity（商品多样性）- 权重10%
## novelty（推荐新颖性）- 权重5%

---

# 输出格式要求
```

## 使用示例

### 查看完整Prompt

```python
import json

with open('evaluation_results_xxx.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 获取第一个评测的prompt
prompt = data['evaluations'][0]['llm_evaluation']['prompt']
print(prompt)
```

### 分析商品级别评估

```python
# 查看每个商品的详细评估
for eval_item in data['evaluations']:
    query_id = eval_item['query_id']
    item_evals = eval_item.get('item_evaluations', [])
    
    print(f"\nQuery: {query_id}")
    for item_eval in item_evals:
        print(f"  - {item_eval['item_name']}: {item_eval['score']}分")
        print(f"    理由: {item_eval['reasoning']}")
        print(f"    品类匹配: {item_eval['category_match']}")
        print(f"    属性匹配: {item_eval['attribute_match']}")
```

### 统计核心意图匹配情况

```python
from collections import Counter

intent_matches = []
for eval_item in data['evaluations']:
    assessment = eval_item.get('overall_assessment', {})
    intent_match = assessment.get('core_intent_match', '')
    intent_matches.append(intent_match)

# 统计匹配情况
print("核心意图匹配分析:")
for match_desc, count in Counter(intent_matches).items():
    print(f"  {match_desc}: {count}次")
```

## 优势

1. **专业评估标准** - 基于电商搜索算法的专业评估体系
2. **明确的评分等级** - 1-5分每个等级都有清晰的定义和示例
3. **商品级别评估** - 支持对每个商品进行单独评估
4. **多维度分析** - 核心意图、属性一致性、时效性三个核心维度
5. **详细的输出要求** - 包含reasoning、category_match、attribute_match等字段
6. **完整保存** - prompt和评估结果都被完整保存，便于审计和调试
