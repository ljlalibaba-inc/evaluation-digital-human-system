# 搜推大模型数字人评测系统

## 目录结构

```
evaluation-digital-human-system/
├── SKILL.md                      # Skill 定义和使用说明
├── README.md                     # 本文件
├── master_digital_human.py       # Master 数字人核心模块
├── system_config.json            # 系统配置（API密钥、钉钉等）
├── scheduler_config.json         # 定时任务配置
│
├── agents/                       # 原子能力 Agent 模块
│   ├── __init__.py
│   ├── base_agent.py             # Agent 基类
│   ├── persona_agent.py          # 人群生成 Agent
│   ├── scenario_agent.py         # 场景生成 Agent
│   ├── category_agent.py         # 品类生成 Agent
│   ├── testcase_agent.py         # 测试用例生成 Agent
│   ├── qwen_agent.py             # 千问调用 Agent（支持 DashScope 和 qwen_chat 双模式）
│   ├── parser_agent.py           # 结果解析 Agent
│   └── eval_agent.py             # 评测 Agent（6维度）
│
├── scripts/                      # 执行脚本
│   ├── run_once.py               # 单次评测执行
│   ├── run_qwen_chat_eval.py     # 使用 qwen_chat API 模式执行评测
│   ├── run_custom_query.py       # 自定义查询评测
│   ├── run_scheduled_evaluation.py # 定时任务执行
│   ├── scheduler.py              # 定时任务调度器
│   ├── demo_system.py            # 演示系统
│   ├── test_dashscope.py         # DashScope API 测试
│   ├── test_qwen_chat_api.py     # qwen_chat API 测试
│   ├── test_coke_order.py        # 可乐下单测试
│   ├── generate_detailed_report.py # 生成详细 HTML 报告
│   ├── generate_html_report.py   # 生成 HTML 报告
│   ├── generate_report.py        # 生成报告
│   └── qwen_streaming_example.py # 流式调用示例
│
├── reports/                      # 评测报告输出
│   ├── report_exec_*.json        # JSON 格式报告
│   ├── report_exec_*.html        # HTML 格式报告
│   └── 报告截图_*.png            # 报告截图
│
├── tests/                        # 测试数据和结果
│   ├── sample.txt                # 样例数据
│   └── test_*_result.json        # 测试结果
│
├── docs/                         # 文档
│   ├── README.md                 # 项目说明
│   ├── SCHEDULER_README.md       # 定时任务说明
│   ├── examples.md               # 使用示例
│   ├── BROWSER_AUTH_EXTRACTION.md # 浏览器认证提取说明
│   └── assets/                   # 文档资源
│
├── utils/                        # 工具函数
│   ├── browser_auth_extractor.py # 浏览器认证提取器
│   ├── qwen_auth_sniffer.js      # 认证嗅探脚本
│   └── qwen_auth_bookmarklet.js  # 书签工具
│
└── results/                      # 运行时结果（自动清理）
```

## 快速开始

### 1. 环境配置

```bash
# 设置 DashScope API Key
export DASHSCOPE_API_KEY="sk-xxx"

# 安装依赖
pip3 install requests schedule -q
```

### 2. 运行单次评测

```bash
cd scripts
python3 run_once.py
```

### 3. 使用 qwen_chat API 模式

```bash
cd scripts
python3 run_qwen_chat_eval.py
```

### 4. 生成 HTML 报告

```bash
cd scripts
python3 generate_detailed_report.py
```

## 核心组件

### Master 数字人

```python
from master_digital_human import MasterDigitalHuman, TaskConfig

master = MasterDigitalHuman()
config = TaskConfig(
    name="评测任务",
    target_model="qwen-turbo",
    scope={
        "personas": ["P1", "P2"],
        "scenarios": ["S1", "S2"],
        "categories": ["C5", "C4"]
    },
    cases_per_combination=2,
    dimensions=["accuracy", "timeliness", "personalization", "safety"]
)
execution = master.submit_task(config)
```

### 评测维度

- **准确性**: 推荐是否匹配用户需求 (25%)
- **时效性**: 是否理解并承诺配送时效 (20%)
- **个性化**: 是否结合用户画像特征 (20%)
- **安全性**: 医药等敏感场景是否合规 (20%)
- **多样性**: 推荐结果是否多样 (10%)
- **新颖性**: 是否有创新推荐 (5%)

## 配置文件

### system_config.json

```json
{
  "evaluation": {
    "name": "千问大模型定时评测",
    "target_model": "qwen-turbo",
    "scope": {
      "personas": ["P1", "P2"],
      "scenarios": ["S1", "S2"],
      "categories": ["C5", "C4"]
    },
    "count": 3,
    "dimensions": ["accuracy", "timeliness", "personalization", "safety"]
  },
  "dingtalk": {
    "enabled": true,
    "webhook_url": "xxx",
    "secret": "xxx"
  }
}
```

## 双模式 API 支持

### 模式 1: DashScope API (推荐)

```python
config = {
    'api_mode': 'dashscope',
    'api_key': 'sk-xxx',
    'model': 'qwen-turbo'
}
```

### 模式 2: qwen-chat-client HTTP API

```python
config = {
    'api_mode': 'qwen_chat',
    'model': 'quark-235b'
}
```

## 注意事项

1. **API Key 安全**: 不要将 API Key 硬编码在代码中，使用环境变量
2. **钉钉关键词**: 钉钉机器人需要设置关键词"【评测报告】"
3. **认证参数过期**: qwen_chat 模式的认证参数（X-Sign, X-Wpk-Reqid）会过期，需要定期更新
