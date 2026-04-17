# 评测结果保存指南

## 概述

从最新版本开始，`master_digital_human.py` 会在评测阶段自动保存评测结果到文件。这样可以确保 `eval_agent.py` 的评测数据不会丢失。

## 保存的文件

评测结果会保存在 `results/` 目录下，文件名为：
```
evaluation_results_{execution_id}.json
```

例如：
```
evaluation_results_exec_20260416_185444_ab5ca1.json
```

## 文件结构

```json
{
  "execution_id": "exec_20260416_185444_ab5ca1",
  "saved_at": "2026-04-16T19:10:26.090564",
  "total_evaluations": 16,
  "evaluations": [
    {
      "query_id": "P1_S1_C5_001",
      "scores": {
        "accuracy": 4.5,
        "timeliness": 4.0,
        "personalization": 3.5,
        "safety": 5.0
      },
      "overall_score": 4.25,
      "issues": [],
      "suggestions": ["加强个性化推荐"],
      "evaluated_dimensions": ["accuracy", "timeliness", "personalization", "safety"],
      "evaluation_mode": "llm",
      "llm_model": "qwen3.6-plus",
      "llm_evaluation": {
        "model": "qwen3.6-plus",
        "prompt": "评测提示词...",
        "raw_response": "{\"scores\": {...}}"
      }
    }
  ]
}
```

## 评测结果字段说明

| 字段 | 说明 |
|------|------|
| `query_id` | 对应的查询ID |
| `scores` | 各维度评分（0-5分） |
| `overall_score` | 加权总分 |
| `issues` | 发现的问题列表 |
| `suggestions` | 改进建议列表 |
| `evaluated_dimensions` | 评测的维度列表 |
| `evaluation_mode` | 评测模式：`llm` 或 `rule` |
| `llm_model` | 使用的大模型名称（LLM模式） |
| `llm_evaluation` | LLM评测的详细信息（可选） |

## 如何使用

### 1. 运行评测

```bash
python3 master_digital_human.py
```

评测完成后，会自动保存结果到 `results/evaluation_results_{execution_id}.json`

### 2. 生成报告

```bash
python3 generate_report_from_results.py
```

该脚本会自动读取评测结果文件并生成完整的报告。

### 3. 生成HTML报告

```bash
python3 scripts/generate_detailed_report.py ./report_{execution_id}.json
```

## 历史评测数据

对于之前已经运行过的评测（没有保存eval_agent结果），可以使用以下方式处理：

1. **重新运行评测**：使用更新后的代码重新执行评测
2. **手动补充评测数据**：如果需要保留历史数据，可以手动创建评测结果文件

## 注意事项

1. **评测模式**：
   - `llm` 模式：使用大模型（如 qwen3.6-plus）进行自动评测
   - `rule` 模式：使用规则引擎进行评测

2. **LLM评测详情**：
   - 当使用LLM模式时，会保存完整的prompt和raw_response
   - 这有助于调试和验证评测结果

3. **评分标准**：
   - 优秀 (4.5-5.0)：绿色
   - 良好 (4.0-4.5)：蓝色
   - 一般 (3.5-4.0)：黄色
   - 较差 (<3.5)：红色

## 故障排查

### 评测结果文件未生成

检查日志中是否有以下输出：
```
[Master] 评测结果已保存: ./results/evaluation_results_{execution_id}.json
```

如果没有，可能是：
1. 评测阶段发生错误
2. 代码版本较旧，需要更新

### 评测结果为空

检查 `eval_agent.py` 是否正确返回了结果。可以在 `eval_agent.py` 中添加调试日志：

```python
print(f"[EvalAgent] 评测完成: {eval_result}")
```
