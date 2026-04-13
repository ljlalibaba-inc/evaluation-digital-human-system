# 使用示例

## 示例1: 基础评测任务

```python
from master_digital_human import MasterDigitalHuman, TaskConfig

# 初始化
master = MasterDigitalHuman()

# 配置评测任务
config = TaskConfig(
    name="千问医药健康品类评测",
    target_model="qwen-turbo",
    scope={
        "personas": ["P1", "P2", "P5"],  # 白领、新手妈妈、退休阿姨
        "scenarios": ["S1"],              # 应急补给
        "categories": ["C5"]              # 医药健康
    },
    count=10,
    dimensions=["accuracy", "timeliness", "safety"],
    delay_ms=200
)

# 执行
execution = master.submit_task(config)

# 等待完成（实际使用时可异步处理）
import time
while execution.status.value == "running":
    time.sleep(1)

# 生成报告
report = master.generate_report(execution.execution_id)
print(f"平均分: {report['execution_summary']['results_summary']['average_score']}")
```

## 示例2: 全品类覆盖评测

```python
config = TaskConfig(
    name="全品类综合评测",
    target_model="qwen-turbo",
    scope={
        "personas": ["P1", "P2", "P3", "P4", "P5", "P6"],
        "scenarios": ["S1", "S2", "S3", "S4", "S5"],
        "categories": ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"]
    },
    count=100,  # 大规模评测
    dimensions=["accuracy", "timeliness", "personalization", "safety", "diversity"],
    parallel=True,
    batch_size=10
)
```

## 示例3: 生成详细HTML报告

```bash
# 运行评测后生成报告
cd /Users/linjie/.qoderwork/skills/qwen-digital-human-evaluator
python3 generate_detailed_report.py

# 打开报告
open 详细评测报告.html
```

## 示例4: 定时任务配置

编辑 `scheduler_config.json`:

```json
{
  "enabled": true,
  "schedule": {
    "type": "weekly",
    "day": "monday",
    "time": "09:00"
  },
  "task_config": {
    "name": "周一例行评测",
    "target_model": "qwen-turbo",
    "scope": {
      "personas": ["P1", "P2"],
      "scenarios": ["S1", "S2"],
      "categories": ["C4", "C5"]
    },
    "count": 20,
    "dimensions": ["accuracy", "timeliness", "personalization", "safety"]
  }
}
```

启动定时任务：
```bash
python3 run_scheduled_evaluation.py
```

## 示例5: 钉钉通知配置

编辑 `system_config.json`:

```json
{
  "dingtalk": {
    "enabled": true,
    "webhook_url": "https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN",
    "secret": "SECYOUR_SECRET"
  }
}
```

**钉钉机器人设置要点**:
1. 创建机器人时选择"自定义"类型
2. 安全设置中选择"加签"并复制密钥
3. 设置关键词为"【评测报告】"

## 示例6: 评测结果分析

```python
import json

# 加载报告
with open('report_exec_xxx.json') as f:
    report = json.load(f)

# 分析问题分布
detailed = report['detailed_results']
safety_issues = [r for r in detailed if '安全' in str(r.get('issues', []))]
print(f"安全问题数量: {len(safety_issues)}")

# 按品类统计平均分
from collections import defaultdict
category_scores = defaultdict(list)
for r in detailed:
    query_id = r['query_id']
    # 根据query_id映射到品类
    category = get_category_by_query_id(query_id)
    category_scores[category].append(r['overall_score'])

for cat, scores in category_scores.items():
    print(f"{cat}: 平均分 {sum(scores)/len(scores):.2f}")
```

## 示例7: 自定义评测维度

```python
# 在 agents/eval_agent.py 中添加新维度

def _eval_price_competitiveness(self, query, response):
    """评估价格竞争力"""
    score = 5.0
    response_text = str(response).lower()
    
    # 检查是否提及价格信息
    if '价格' in response_text or '元' in response_text:
        score -= 0
    else:
        score -= 2  # 缺少价格信息扣分
    
    # 检查是否有优惠信息
    if any(word in response_text for word in ['优惠', '折扣', '满减']):
        score += 0.5
    
    return min(5.0, max(1.0, score))
```

然后在配置中使用：
```python
config = TaskConfig(
    dimensions=["accuracy", "timeliness", "price_competitiveness"]
)
```
