---
name: qwen-digital-human-evaluator
description: 构建和运行搜推大模型数字人评测系统，支持多维度评测（准确性、时效性、个性化、安全性等）。用于评测千问(Qwen)等大模型在即时零售场景下的推荐质量，生成详细HTML评测报告、截图、钉钉通知。支持DashScope API和qwen-chat-client两种调用方式。Use when evaluating LLM recommendation quality, building digital human evaluation systems, or testing Qwen model performance in retail scenarios.
---

# 搜推大模型数字人评测系统

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    用户交互层                                │
│              (Web UI / API / CLI)                           │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                   Master 数字人                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  任务触发器   │  │  编排中心     │  │  结果汇总器   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┬─────────────┐
        │             │             │             │
┌───────▼─────┐ ┌────▼────┐ ┌──────▼──────┐ ┌────▼────┐
│  三维模型    │ │  千问    │ │  结果解析    │ │  测试用例│
│  生成Agent   │ │  调用Agent│ │  Agent      │ │  生成Agent│
│  (P/S/C)     │ │          │ │             │ │          │
└───────┬─────┘ └────┬────┘ └──────┬──────┘ └────┬────┘
        │            │             │             │
        └────────────┼─────────────┴─────────────┘
                     │
            ┌────────▼────────┐
            │   结果评测Agent  │
            │  (6维度评测)    │
            └────────┬────────┘
                     │
┌────────────────────▼───────────────────────────────────────┐
│                    输出层                                    │
│    (HTML报告 / 截图 / 改进建议 / 钉钉通知 / JSON数据)        │
└─────────────────────────────────────────────────────────────┘
```

### 三维模型生成Agent

| Agent | 职责 | 数量 |
|-------|------|------|
| **PersonaAgent** | 生成用户人群画像 | 6种 |
| **ScenarioAgent** | 生成使用场景 | 5种 |
| **CategoryAgent** | 生成商品品类 | 8种 |

## 核心能力

### 1. 多维度评测

| 维度 | 说明 | 权重 |
|------|------|------|
| **准确性** | 推荐是否匹配用户需求 | 25% |
| **时效性** | 是否理解并承诺配送时效 | 20% |
| **个性化** | 是否结合用户画像特征 | 20% |
| **安全性** | 医药等敏感场景是否合规 | 20% |
| **多样性** | 推荐结果是否多样 | 10% |
| **新颖性** | 是否有创新推荐 | 5% |

### 2. 三维评测模型

**人设维度 (Persona)**:
- P1: 忙碌的年轻白领
- P2: 新手妈妈
- P3: 大学生
- P4: 精致白领
- P5: 退休阿姨
- P6: 双职工家庭

**场景维度 (Scenario)**:
- S1: 应急补给
- S2: 即时享受
- S3: 懒人便利
- S4: 计划性消费
- S5: 节日聚会

**品类维度 (Category)**:
- C1: 生鲜果蔬
- C2: 休闲零售
- C3: 3C数码
- C4: 母婴用品
- C5: 医药健康
- C6: 日用百货
- C7: 鲜花礼品
- C8: 宠物用品

### 3. 双模式API支持

**模式1: DashScope API (推荐，稳定)**
```python
config = {
    'api_mode': 'dashscope',
    'api_key': 'sk-xxx',  # 或环境变量 DASHSCOPE_API_KEY
    'model': 'qwen-turbo'
}
```

**模式2: qwen-chat-client HTTP API**
```python
config = {
    'api_mode': 'qwen_chat',
    'use_production': True,
    'x_sign': 'xxx',
    'wpk_reqid': 'xxx'
}
```

## 快速开始

### 1. 环境配置

```bash
# 设置DashScope API Key (推荐)
export DASHSCOPE_API_KEY="sk-xxx"

# 安装依赖
pip3 install requests schedule -q
```

### 2. 运行完整评测

```python
from master_digital_human import MasterDigitalHuman, TaskConfig

# 初始化Master
master = MasterDigitalHuman()

# 配置任务
config = TaskConfig(
    name="千问即时零售评测",
    target_model="qwen-turbo",
    scope={
        "personas": ["P1", "P2"],
        "scenarios": ["S1", "S2"],
        "categories": ["C5", "C4"]
    },
    count=5,
    dimensions=["accuracy", "timeliness", "personalization", "safety"],
    delay_ms=1000
)

# 提交任务
execution = master.submit_task(config)

# 等待完成
import time
while execution.status.value == "running":
    time.sleep(2)

# 生成报告
report = master.generate_report(execution.execution_id)
print(f"平均分: {report['execution_summary']['results_summary']['average_score']}")
```

### 3. 生成HTML报告

```bash
python3 generate_detailed_report.py
```

报告包含:
- 人设/场景/品类全部分类
- 完整千问返回内容
- 多维度评测得分
- 改进建议汇总
- 评测汇总表格

### 4. 生成报告截图

```bash
# 使用agent-browser截图
npx agent-browser --session report --headed open file:///path/to/详细评测报告.html
npx agent-browser --session report screenshot --full 报告截图.png
```

### 5. 定时任务与钉钉通知

**配置定时执行** (`scheduler_config.json`):
```json
{
  "enabled": true,
  "schedule": {
    "type": "daily",
    "time": "09:00"
  },
  "task_config": {
    "name": "千问定时评测",
    "target_model": "qwen-turbo",
    "count": 10
  }
}
```

**配置钉钉通知** (`system_config.json`):
```json
{
  "dingtalk": {
    "enabled": true,
    "webhook_url": "https://oapi.dingtalk.com/robot/send?access_token=xxx",
    "secret": "SECxxx"
  }
}
```

**启动定时任务**:
```bash
python3 run_scheduled_evaluation.py
```

## 核心组件

### Master数字人

```python
from master_digital_human import MasterDigitalHuman

master = MasterDigitalHuman()

# 注册自定义Agent
master.register_agent("custom", CustomAgent())

# 提交任务
execution = master.submit_task(config)

# 获取执行状态
execution = master.get_execution(execution_id)

# 生成报告
report = master.generate_report(execution_id)
```

### Agent原子能力

#### 三维模型生成 Agent

**PersonaAgent - 人群生成**

```python
from agents.persona_agent import PersonaAgent

agent = PersonaAgent()

# 生成指定人群
personas = agent.generate(persona_ids=["P1", "P2"])

# 根据优先级过滤
personas = agent.generate(priority_filter="P0")

# 获取人群详情
persona = agent.get_persona_by_id("P1")
```

**ScenarioAgent - 场景生成**

```python
from agents.scenario_agent import ScenarioAgent

agent = ScenarioAgent()

# 生成指定场景
scenarios = agent.generate(scenario_ids=["S1", "S2"])

# 为特定人群推荐场景
scenarios = agent.generate(persona_id="P1")

# 获取场景典型Query
queries = agent.get_queries_for_scenario("S1")
```

**CategoryAgent - 品类生成**

```python
from agents.category_agent import CategoryAgent

agent = CategoryAgent()

# 生成指定品类
categories = agent.generate(category_ids=["C5", "C4"])

# 根据人群和场景推荐品类
categories = agent.generate(persona_id="P1", scenario_id="S1")

# 获取子类目
subcategories = agent.get_subcategories("C5")
```

#### 测试用例生成 Agent

```python
from agents.testcase_agent import TestCaseAgent

agent = TestCaseAgent()
test_cases = agent.generate(
    personas=["P1", "P2"],
    scenarios=["S1", "S2"],
    categories=["C5", "C4"],
    count=10
)
```

**内置测试用例模板**:
- 当数据集不可用时，自动使用内置模板生成
- 支持6种人设 × 5种场景 × 8种品类

#### 千问调用 Agent

```python
from agents.qwen_agent import QwenAgent

# DashScope模式 (推荐)
agent = QwenAgent({
    'api_mode': 'dashscope',
    'api_key': 'sk-xxx',
    'model': 'qwen-turbo'
})

# 调用
result = agent.call(
    query_text="帮忙下单可口可乐",
    system_prompt="你是即时零售助手"
)

print(result['content'])  # 千问返回内容
print(result['response_time_ms'])  # 响应时间
```

#### 结果评测 Agent

```python
from agents.eval_agent import EvalAgent

agent = EvalAgent()
eval_result = agent.evaluate(
    query=query_data,
    response=response_data,
    dimensions=["accuracy", "timeliness", "safety"]
)

print(eval_result['overall_score'])  # 总分
print(eval_result['scores'])  # 各维度得分
print(eval_result['issues'])  # 发现问题
print(eval_result['suggestions'])  # 改进建议
```

## 报告解读

### 评分等级
- **优秀 (4.5-5.0)**: 绿色，推荐质量高
- **良好 (4.0-4.5)**: 蓝色，基本满足需求
- **一般 (3.5-4.0)**: 黄色，有待改进
- **较差 (<3.5)**: 红色，需要重点关注

### 问题分类
- **安全问题**: 医药类缺少安全提示
- **时效问题**: 未明确配送时间承诺
- **个性化问题**: 未结合用户画像推荐
- **准确性问题**: 推荐商品与需求不匹配

## 文件结构

```
qwen-digital-human-evaluator/
├── SKILL.md                      # Skill定义和使用说明 (已更新)
├── examples.md                   # 使用示例
├── README.md                     # 项目说明
├── master_digital_human.py       # Master数字人核心
├── scheduler.py                  # 定时任务调度器
├── run_scheduled_evaluation.py   # 定时执行入口
├── generate_detailed_report.py   # HTML详细报告生成
├── system_config.json            # 系统配置(钉钉等)
├── scheduler_config.json         # 定时任务配置
└── agents/                       # 原子能力Agent (9个)
    ├── __init__.py               # Agent包初始化
    ├── base_agent.py             # Agent基类
    ├── persona_agent.py          # 人群生成Agent (新增)
    ├── scenario_agent.py         # 场景生成Agent (新增)
    ├── category_agent.py         # 品类生成Agent (新增)
    ├── testcase_agent.py         # 测试用例生成
    ├── qwen_agent.py             # 千问调用(双模式)
    ├── parser_agent.py           # 结果解析
    └── eval_agent.py             # 评测(6维度)
```

## 扩展开发

### 添加新评测维度

在 `agents/eval_agent.py` 中扩展:

```python
def _eval_price_competitiveness(self, query, response):
    """评估价格竞争力"""
    score = 5.0
    # 实现评分逻辑
    return score
```

### 自定义报告模板

修改 `generate_detailed_report.py` 中的HTML模板部分。

### 添加新通知渠道

在 `scheduler.py` 中添加:

```python
class WeChatNotifier:
    def send_text(self, message):
        # 实现微信通知
        pass
```

## 完整示例

### 示例1: 使用三维模型生成Agent

```python
from agents import PersonaAgent, ScenarioAgent, CategoryAgent

# 生成人群画像
persona_agent = PersonaAgent()
personas = persona_agent.generate(persona_ids=["P1", "P2"])
for p in personas:
    print(f"{p['id']}: {p['name']} - {p['description']}")

# 生成使用场景
scenario_agent = ScenarioAgent()
scenarios = scenario_agent.generate(scenario_ids=["S1", "S2"])
# 或根据人群推荐场景
scenarios = scenario_agent.generate(persona_id="P1")

# 生成商品品类
category_agent = CategoryAgent()
categories = category_agent.generate(category_ids=["C5", "C4"])
# 或根据人群和场景推荐
categories = category_agent.generate(persona_id="P1", scenario_id="S1")

# 获取详细信息
persona = persona_agent.get_persona_by_id("P1")
queries = scenario_agent.get_queries_for_scenario("S1")
subcategories = category_agent.get_subcategories("C5")
```

### 示例3: 单次评测

```python
import os
os.environ['DASHSCOPE_API_KEY'] = 'sk-xxx'

from master_digital_human import MasterDigitalHuman, TaskConfig

master = MasterDigitalHuman()

config = TaskConfig(
    name="千问医药健康评测",
    target_model="qwen-turbo",
    scope={
        "personas": ["P1", "P2"],
        "scenarios": ["S1"],
        "categories": ["C5"]
    },
    count=3,
    dimensions=["accuracy", "timeliness", "safety"]
)

execution = master.submit_task(config)

# 等待完成
import time
while execution.status.value == "running":
    time.sleep(2)

# 生成并保存报告
report = master.generate_report(execution.execution_id)
import json
with open(f"report_{execution.execution_id}.json", 'w') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
```

### 示例3: 生成HTML报告和截图

```bash
# 生成HTML报告
python3 generate_detailed_report.py

# 启动HTTP服务器
cd /path/to/skill
python3 -m http.server 9999 &

# 截图
npx agent-browser --session report --headed open http://localhost:9999/详细评测报告.html
npx agent-browser --session report screenshot --full 报告截图.png
```

### 示例4: 定时任务

```python
# scheduler_config.json
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
    "count": 20
  },
  "dingtalk": {
    "enabled": true,
    "webhook_url": "xxx",
    "secret": "xxx"
  }
}
```

启动:
```bash
python3 run_scheduled_evaluation.py
```

## 注意事项

1. **API Key安全**: 不要将API Key硬编码在代码中，使用环境变量
2. **钉钉关键词**: 钉钉机器人需要设置关键词"【评测报告】"
3. **截图依赖**: 截图功能需要安装agent-browser: `npm install -g agent-browser`
4. **定时任务**: 长时间运行的定时任务建议使用screen或nohup

## 依赖安装

```bash
# Python依赖
pip3 install requests schedule -q

# Node.js依赖 (截图功能)
npm install -g agent-browser
```

## 环境变量

```bash
export DASHSCOPE_API_KEY="sk-xxx"  # DashScope API密钥
export QWEN_API_KEY="sk-xxx"       # 兼容旧版
```
