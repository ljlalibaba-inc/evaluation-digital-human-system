# 定时执行和钉钉通知使用说明

## 功能概述

系统新增以下能力：

1. **定时执行**: 支持每天定时、每周定时、间隔执行等多种方式
2. **钉钉通知**: 支持评测结果自动发送到钉钉群
3. **报告生成**: 自动生成HTML和JSON格式报告

## 文件说明

| 文件 | 功能 |
|------|------|
| `scheduler.py` | 定时调度器和钉钉通知器 |
| `run_scheduled_evaluation.py` | 定时评测运行器 |
| `system_config.json` | 系统配置文件 |

## 快速开始

### 1. 配置钉钉通知（可选）

编辑 `system_config.json`：

```json
{
  "dingtalk": {
    "enabled": true,
    "webhook_url": "https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN",
    "secret": "",
    "at_mobiles": ["13800138000"],
    "at_all": false
  }
}
```

**获取Webhook URL步骤**：
1. 打开钉钉群 → 群设置 → 智能群助手
2. 添加机器人 → 自定义
3. 复制Webhook地址
4. （可选）启用加签，复制密钥到 `secret`

### 2. 配置定时任务

编辑 `system_config.json`：

```json
{
  "schedule": {
    "enabled": true,
    "daily_time": "09:00",      // 每天9点执行
    "interval_minutes": null     // 或每N分钟执行
  }
}
```

### 3. 启动定时任务

```bash
# 方式1: 启动定时调度（后台运行）
python3 run_scheduled_evaluation.py --mode schedule

# 方式2: 立即执行一次
python3 run_scheduled_evaluation.py --mode once

# 方式3: 指定时间执行
python3 run_scheduled_evaluation.py --mode schedule --time "14:30"

# 方式4: 指定间隔执行（每30分钟）
python3 run_scheduled_evaluation.py --mode schedule --interval 30

# 方式5: 启用钉钉通知执行
python3 run_scheduled_evaluation.py --mode once --webhook "YOUR_WEBHOOK_URL"
```

## 钉钉通知效果

### 消息格式

```
🤖 大模型数字人评测报告

📊 评测概览
━━━━━━━━━━━━━━━━━━━━━
评测时间: 2026-04-09 09:00
测试用例: 10 个
平均分: 4.25 / 5.0
通过率: 80.0%
整体评级: 良好 🔵

📋 评测明细
━━━━━━━━━━━━━━━━━━━━━
| 人设       | 场景     | 品类     | 得分  | 状态 |
|------------|----------|----------|-------|------|
| 忙碌白领   | 应急补给 | 医药健康 | 4.56  | ✅   |
| 新手妈妈   | 应急补给 | 母婴用品 | 3.50  | ⚠️   |
...

⚠️ 发现问题
━━━━━━━━━━━━━━━━━━━━━
- 医药品类缺少安全提示
- 个性化程度不够

📎 详细报告请查看系统
```

### 消息特性

- ✅ 支持Markdown格式
- ✅ 颜色标记（优秀/良好/一般/需改进）
- ✅ @指定成员
- ✅ 手机端友好

## 配置详解

### 评测配置 (evaluation)

```json
{
  "evaluation": {
    "name": "评测任务名称",
    "target_model": "qwen-turbo",
    "scope": {
      "personas": ["P1", "P2", "P3"],    // 人群: P1-P6
      "scenarios": ["S1", "S2"],         // 场景: S1-S5
      "categories": ["C5", "C4"]         // 品类: C1-C8
    },
    "count": 10,                          // 测试用例数量
    "dimensions": ["accuracy", "safety"]  // 评测维度
  }
}
```

### 定时配置 (schedule)

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `daily_time` | 每天执行时间 | `"09:00"` |
| `weekly_day` | 每周几执行 | `0`=周一, `6`=周日 |
| `weekly_time` | 每周执行时间 | `"14:00"` |
| `interval_minutes` | 间隔分钟数 | `30` |

### 钉钉配置 (dingtalk)

| 配置项 | 说明 | 必填 |
|--------|------|------|
| `enabled` | 是否启用 | 是 |
| `webhook_url` | Webhook地址 | 是 |
| `secret` | 加签密钥 | 否 |
| `at_mobiles` | @的手机号列表 | 否 |
| `at_all` | 是否@所有人 | 否 |

### 输出配置 (output)

```json
{
  "output": {
    "save_html": true,      // 保存HTML报告
    "save_json": true,      // 保存JSON报告
    "send_dingtalk": true   // 发送钉钉通知
  }
}
```

## 使用示例

### 示例1: 每天9点自动评测并发送钉钉

```bash
# 1. 配置钉钉和定时
# 编辑 system_config.json

# 2. 启动定时任务
python3 run_scheduled_evaluation.py --mode schedule

# 3. 系统会在每天9点自动执行并发送报告
```

### 示例2: 每小时执行一次

```bash
# 修改配置
python3 run_scheduled_evaluation.py --mode schedule --interval 60
```

### 示例3: 手动执行并发送钉钉

```bash
python3 run_scheduled_evaluation.py --mode once \
  --webhook "https://oapi.dingtalk.com/robot/send?access_token=xxx"
```

### 示例4: 查看当前配置

```bash
python3 run_scheduled_evaluation.py --mode config
```

## 常见问题

### Q1: 钉钉收不到通知？

检查清单：
- [ ] `enabled` 设置为 `true`
- [ ] `webhook_url` 正确且未过期
- [ ] 机器人未被禁言
- [ ] 网络连接正常

### Q2: 如何停止定时任务？

按 `Ctrl+C` 或在另一个终端执行：
```bash
pkill -f run_scheduled_evaluation.py
```

### Q3: 如何修改定时时间？

编辑 `system_config.json` 或命令行指定：
```bash
python3 run_scheduled_evaluation.py --mode schedule --time "15:30"
```

### Q4: 报告文件保存在哪里？

报告保存在当前目录：
- `report_EXECID.json` - JSON格式
- `report_EXECID.html` - HTML格式

## 高级用法

### 自定义钉钉消息

编辑 `scheduler.py` 中的 `send_evaluation_report` 方法，自定义消息格式。

### 多群通知

创建多个 `DingTalkNotifier` 实例，分别配置不同的Webhook。

### 条件通知

只在评测结果异常时发送通知：

```python
if avg_score < 4.0 or pass_rate < 80:
    notifier.send_evaluation_report(report)
```

## 系统架构

```
┌─────────────────────────────────────────┐
│         ScheduledEvaluationSystem       │
│  ┌──────────────┐  ┌──────────────┐    │
│  │ Master数字人  │  │  调度器       │    │
│  └──────────────┘  └──────────────┘    │
│         │                 │             │
│         └────────┬────────┘             │
│                  │                      │
│  ┌───────────────▼───────────────┐      │
│  │      EvaluationScheduler      │      │
│  │  ┌─────────────────────────┐  │      │
│  │  │   DingTalkNotifier      │  │      │
│  │  │  - send_evaluation()    │  │      │
│  │  │  - send_text()          │  │      │
│  │  └─────────────────────────┘  │      │
│  └───────────────────────────────┘      │
└─────────────────────────────────────────┘
```
