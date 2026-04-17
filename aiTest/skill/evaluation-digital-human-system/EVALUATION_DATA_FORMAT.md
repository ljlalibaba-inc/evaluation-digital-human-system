# 评测数据保存格式说明

## 概述

`eval_agent.py` 在使用大模型进行评测时，会完整保存以下数据：
1. **完整入参** - 包括query、response、dimensions等所有输入参数
2. **LLM调用详情** - 包括prompt、raw_response等
3. **解析结果** - 包括scores、issues、suggestions等

## 文件结构

```json
{
  "execution_id": "评测执行ID",
  "saved_at": "保存时间戳",
  "total_evaluations": 评测总数,
  "evaluations": [
    {
      // 1. 基础评测结果
      "query_id": "查询ID",
      "scores": {
        "accuracy": 4.5,
        "timeliness": 3.0,
        "personalization": 3.0,
        "safety": 5.0
      },
      "overall_score": 4.09,
      "issues": [],
      "suggestions": [],
      "evaluated_dimensions": ["accuracy", "timeliness", "personalization", "safety"],
      "evaluation_mode": "llm",
      "llm_model": "qwen3.6-plus",

      // 2. 完整入参（新增）
      "evaluation_input": {
        "query": {
          "query_id": "...",
          "query_text": "...",
          "persona": "...",
          "scenario": "...",
          "category": "...",
          "tags": [...]
        },
        "response": {
          "content": "...",
          "data": {
            "structured_items": [...],
            "time_commitment": "...",
            "personalization_elements": [...],
            "safety_warnings": [...]
          }
        },
        "dimensions": [...],
        "timestamp": "2026-04-16T19:39:48.819365"
      },

      // 3. LLM评测详情（增强）
      "llm_evaluation": {
        "model": "qwen3.6-plus",

        // LLM输入参数
        "input_params": {
          "query_text": "用户查询文本",
          "response_content": "响应内容",
          "structured_items": [...],
          "dimensions": [...]
        },

        // 完整的Prompt
        "prompt": "你是一位专业的推荐系统评测专家...",

        // 完整的原始返回（raw_response）
        "raw_response": "{\"content\": \"...\", \"data\": {...}}",

        // 重试信息
        "retry_count": 3,
        "fallback_to_rule": true,

        // 解析后的结果
        "parsed_result": {
          "scores": {...},
          "issues": [...],
          "suggestions": [...]
        }
      }
    }
  ]
}
```

## 字段详解

### 1. 基础评测结果

| 字段 | 类型 | 说明 |
|------|------|------|
| `query_id` | string | 查询唯一标识 |
| `scores` | object | 各维度评分（0-5分） |
| `overall_score` | float | 加权总分 |
| `issues` | array | 发现的问题列表 |
| `suggestions` | array | 改进建议列表 |
| `evaluation_mode` | string | 评测模式：`llm` 或 `rule` |
| `llm_model` | string | 使用的大模型名称 |

### 2. 完整入参 (evaluation_input)

保存了 `evaluate()` 方法的所有入参：

| 字段 | 类型 | 说明 |
|------|------|------|
| `query` | object | 完整的query对象，包括query_id、query_text、persona、scenario、category、tags |
| `response` | object | 完整的response对象，包括content和data |
| `dimensions` | array | 评测维度列表 |
| `timestamp` | string | 评测开始时间戳 |

### 3. LLM评测详情 (llm_evaluation)

#### input_params
传递给大模型的输入参数：
- `query_text`: 用户查询文本
- `response_content`: 响应内容
- `structured_items`: 结构化商品数据
- `dimensions`: 评测维度

#### prompt
完整的评测提示词，包含：
- 用户查询
- 推荐系统返回内容
- 结构化商品数据
- 评测维度说明
- 输出格式要求

#### raw_response
大模型的原始返回数据（未解析的完整响应），可用于：
- 调试评测逻辑
- 验证解析正确性
- 分析大模型行为

#### retry_count
重试次数，记录LLM调用失败后的重试情况。

#### fallback_to_rule
是否回退到规则评测。当LLM评测多次失败后，会自动回退到规则引擎。

#### parsed_result
从raw_response解析后的结果，包含：
- `scores`: 各维度分数
- `issues`: 问题列表
- `suggestions`: 建议列表

## 使用场景

### 1. 调试评测逻辑

通过查看 `llm_evaluation.prompt` 和 `llm_evaluation.raw_response`，可以：
- 验证prompt是否正确构建
- 检查大模型返回格式
- 分析解析失败原因

### 2. 验证评分准确性

对比 `input_params` 和 `parsed_result.scores`，可以：
- 验证评分是否合理
- 检查各维度权重分配
- 分析评分偏差原因

### 3. 追踪评测流程

通过 `retry_count` 和 `fallback_to_rule`，可以：
- 了解LLM调用稳定性
- 分析评测失败原因
- 优化重试策略

### 4. 数据分析和报告

完整的入参和返回数据支持：
- 生成详细的评测报告
- 进行数据统计分析
- 可视化展示评测结果

## 示例代码

### 读取评测结果

```python
import json

with open('evaluation_results_xxx.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for eval_item in data['evaluations']:
    # 基础信息
    query_id = eval_item['query_id']
    overall_score = eval_item['overall_score']

    # 完整入参
    query = eval_item['evaluation_input']['query']
    response = eval_item['evaluation_input']['response']

    # LLM详情
    llm_eval = eval_item.get('llm_evaluation', {})
    prompt = llm_eval.get('prompt')
    raw_response = llm_eval.get('raw_response')
    retry_count = llm_eval.get('retry_count', 0)

    print(f"Query: {query['query_text']}")
    print(f"Score: {overall_score}")
    print(f"Retries: {retry_count}")
```

### 分析重试情况

```python
# 统计有多少评测发生了重试
retry_count = sum(
    e.get('llm_evaluation', {}).get('retry_count', 0)
    for e in data['evaluations']
)
print(f"总重试次数: {retry_count}")

# 统计回退到规则评测的数量
fallback_count = sum(
    1 for e in data['evaluations']
    if e.get('llm_evaluation', {}).get('fallback_to_rule', False)
)
print(f"回退到规则评测: {fallback_count}")
```

## 注意事项

1. **raw_response可能很大** - 包含完整的LLM返回，文件可能较大
2. **敏感信息** - prompt和raw_response可能包含敏感信息，注意数据安全
3. **存储空间** - 完整保存会占用更多存储空间，定期清理旧数据
