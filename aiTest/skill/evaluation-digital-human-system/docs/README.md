# 搜推大模型测评数字人系统

## 系统概述

一个多Agent协同的搜推大模型测评系统，采用数字人架构设计，包含1个Master数字人和4个原子能力Agent。

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Master 数字人                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  任务触发器   │  │  编排中心     │  │  结果汇总器   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
┌───────▼─────┐ ┌────▼────┐ ┌──────▼──────┐
│  测试用例    │ │  千问    │ │  结果解析    │
│  生成Agent   │ │  调用Agent│ │   Agent     │
└───────┬─────┘ └────┬────┘ └──────┬──────┘
        │            │             │
        └────────────┼─────────────┘
                     │
            ┌────────▼────────┐
            │   结果评测Agent  │
            └─────────────────┘
```

## 核心组件

### 1. Master 数字人 (`master_digital_human.py`)

**职责**: 系统中枢，负责任务调度与结果汇总

**核心模块**:
- **任务触发器**: 接收用户测评需求，解析意图
- **编排中心**: 协调各Agent执行顺序，管理依赖关系
- **结果汇总器**: 聚合各Agent输出，生成最终报告

**关键方法**:
```python
master = MasterDigitalHuman()
execution = master.submit_task(task_config)  # 提交任务
report = master.generate_report(execution_id)  # 生成报告
```

### 2. 原子能力 Agent

#### 2.1 测试用例生成 Agent (`agents/testcase_agent.py`)

**集成Skill**: `instant-retail-query-gen`

**职责**: 基于人群×场景×品类三维模型生成测评Query

**使用**:
```python
from agents.testcase_agent import TestCaseAgent

agent = TestCaseAgent()
queries = agent.generate(
    personas=["P1", "P2"],
    scenarios=["S1", "S2"],
    categories=["C5", "C4"],
    count=50
)
```

#### 2.2 千问调用 Agent (`agents/qwen_agent.py`)

**集成Skill**: `qwen-chat-client`

**职责**: 调用千问大模型获取响应

**使用**:
```python
from agents.qwen_agent import QwenAgent

agent = QwenAgent(api_key="your-key")
response = agent.call(
    query_text="我是加班族，现在头痛需要止痛药...",
    system_prompt="你是即时零售助手..."
)
```

#### 2.3 结果解析 Agent (`agents/parser_agent.py`)

**集成Skill**: `result_parse`

**职责**: 解析千问响应，提取结构化信息

**解析维度**:
- 推荐商品列表
- 时效承诺
- 个性化元素
- 安全提示
- 意图识别情况

#### 2.4 结果评测 Agent (`agents/eval_agent.py`)

**集成Skill**: `search_eval`

**职责**: 基于多维度评估模型输出质量

**评测维度**:
- **准确性** (25%): 推荐是否匹配用户需求
- **时效性** (15%): 是否理解并承诺时效
- **个性化** (15%): 是否结合用户特征
- **安全性** (25%): 医药等敏感场景是否合规
- **多样性** (10%): 推荐结果是否多样
- **新颖性** (10%): 是否有创新推荐

## 文件清单

| 文件 | 大小 | 说明 |
|------|------|------|
| `SKILL.md` | 14K | Skill定义文档 |
| `master_digital_human.py` | 12K | Master数字人实现 |
| `demo_system.py` | 11K | 系统演示脚本 |
| `agents/__init__.py` | 1K | Agent包初始化 |
| `agents/base_agent.py` | 1K | Agent基类 |
| `agents/testcase_agent.py` | 3K | 测试用例生成Agent |
| `agents/qwen_agent.py` | 4K | 千问调用Agent |
| `agents/parser_agent.py` | 6K | 结果解析Agent |
| `agents/eval_agent.py` | 8K | 结果评测Agent |

## 快速开始

### 1. 运行完整演示

```bash
cd evaluation-digital-human-system
python3 demo_system.py
```

### 2. 使用Master数字人

```python
from master_digital_human import MasterDigitalHuman, TaskConfig

# 初始化
master = MasterDigitalHuman()

# 配置任务
config = TaskConfig(
    name="千问测评",
    target_model="qwen-turbo",
    scope={
        "personas": ["P1", "P2"],
        "scenarios": ["S1", "S2"],
        "categories": ["C5", "C4"]
    },
    count=10,
    dimensions=["accuracy", "timeliness", "safety"]
)

# 提交任务
execution = master.submit_task(config)

# 等待完成
while execution.status.value == "running":
    time.sleep(1)

# 生成报告
report = master.generate_report(execution.execution_id)
```

### 3. 单独使用Agent

```python
from agents import TestCaseAgent, QwenAgent, SearchEvalAgent

# 生成测试用例
testcase_agent = TestCaseAgent()
queries = testcase_agent.generate(
    personas=["P1"], scenarios=["S1"], categories=["C5"], count=5
)

# 调用千问
qwen_agent = QwenAgent()
response = qwen_agent.call(queries[0]['query_text'])

# 评测结果
eval_agent = SearchEvalAgent()
result = eval_agent.evaluate(
    query=queries[0],
    response=response,
    dimensions=["accuracy", "safety"]
)
```

## 工作流程

```
1. 用户提交测评需求
   ↓
2. Master解析需求，生成执行计划
   ↓
3. 测试用例生成Agent生成Query
   ↓
4. 千问调用Agent批量调用模型
   ↓
5. 结果解析Agent解析响应
   ↓
6. 结果评测Agent多维度评估
   ↓
7. Master汇总结果，生成报告
   ↓
8. 输出测评报告与改进建议
```

## 输出报告格式

```json
{
  "report_id": "rpt_exec_20260409_xxx",
  "execution_summary": {
    "execution_id": "exec_20260409_xxx",
    "task_config": {...},
    "status": "completed",
    "duration_seconds": 14.36,
    "stages": [
      {"name": "testcase_generation", "status": "completed", "duration_seconds": 0.00},
      {"name": "model_calling", "status": "completed", "duration_seconds": 14.35},
      {"name": "result_parsing", "status": "completed", "duration_seconds": 0.01},
      {"name": "evaluation", "status": "completed", "duration_seconds": 0.00}
    ],
    "results_summary": {
      "total_evaluated": 10,
      "average_score": 4.25,
      "pass_count": 8
    }
  },
  "detailed_results": [...]
}
```

## 演示结果

运行演示后，系统会输出：

```
✓ 任务执行成功!

各阶段执行情况:
  ✓ testcase_generation: 0.00s
  ✓ model_calling: 14.35s
  ✓ result_parsing: 0.01s
  ✓ evaluation: 0.00s

测评报告摘要:
  - 报告ID: rpt_exec_20260409_xxx
  - 执行时长: 14.36秒
  - 评测Query数: 3
  - 平均得分: 4.06/5.0
  - 通过数(≥4.0): 2
```

## 扩展开发

### 添加新Agent

```python
from agents.base_agent import BaseAgent

class CustomAgent(BaseAgent):
    def execute(self, input_data):
        # 实现逻辑
        return output_data

# 注册到Master
master.register_agent("custom", CustomAgent())
```

### 自定义评测维度

```python
# 在eval_agent.py中添加新维度
def _eval_custom(self, query, response):
    score = 3.0
    # 实现评分逻辑
    return score
```

## 依赖关系

本系统依赖以下Skill：
- `instant-retail-query-gen`: 测试用例生成
- `qwen-chat-client`: 千问API调用
- `result_parse`: 结果解析
- `search_eval`: 结果评测

## 注意事项

1. **API密钥**: 使用真实测评时需要设置 `QWEN_API_KEY` 环境变量
2. **调用频率**: 建议设置适当的delay_ms避免API限流
3. **安全合规**: 医药品类的安全评测需要特别关注
4. **结果复核**: 自动评分结果建议人工复核

## 系统特点

- ✅ 数字人架构，Master+Agent协同
- ✅ 三维测评模型（人群×场景×品类）
- ✅ 多维度评估（准确性/时效性/安全性等）
- ✅ 可视化执行流程
- ✅ 详细测评报告
- ✅ 易于扩展的插件化设计
