# 代码提交摘要

## 提交信息

**Commit**: b27ab54  
**消息**: feat: 增强数字人评测系统，支持表格格式输出  
**时间**: 2026-04-16  
**变更**: 8 files changed, 1958 insertions(+), 365 deletions(-)

## 主要变更文件

### 核心代码文件

| 文件 | 变更 | 说明 |
|------|------|------|
| `agents/eval_agent.py` | +1020/-0 | 增强评测Agent，支持表格格式输出 |
| `agents/parser_agent.py` | +157/-0 | 优化解析Agent |
| `agents/qwen_agent.py` | +228/-0 | 支持DashScope API模式 |
| `master_digital_human.py` | +104/-0 | 添加评测结果保存功能 |
| `scripts/generate_detailed_report.py` | +782/-0 | 增强报告生成，支持表格数据 |
| `scripts/run_once.py` | +4/-0 | 更新运行脚本 |
| `scripts/run_qwen_chat_eval.py` | +16/-0 | 更新评测脚本 |
| `system_config.json` | +12/-0 | 更新系统配置 |

### 新增配置文件

- `.env` - 环境变量配置（API Key）
- `system_config_backup_20260416_200611.json` - 配置备份
- `system_config_template.json` - 配置模板

### 新增文档

- `SETUP_GUIDE.md` - API Key设置指南
- `SYSTEM_CONFIG_GUIDE.md` - 系统配置说明
- `EVALUATION_DATA_FORMAT.md` - 评测数据格式
- `ENHANCED_PROMPT_GUIDE.md` - Prompt增强说明
- `PROMPT_ENHANCEMENT_SUMMARY.md` - 增强总结
- `EVALUATION_SAVE_GUIDE.md` - 结果保存指南

### 新增工具脚本

- `quick_eval_test.py` - 快速评测测试
- `run_full_evaluation.py` - 完整评测执行
- `generate_table_report.py` - 表格格式报告生成
- `test_table_format_mock.py` - 表格格式测试
- `test_table_prompt.py` - Prompt测试
- `send_eval_notification.py` - 钉钉通知发送

## 核心功能增强

### 1. 表格格式评测输出

新增 `evaluation_table` 格式，每行包含：
- `query` - 用户查询
- `score` - 1-5分评分
- `core_intent_match` - 核心意图匹配说明
- `attribute_consistency` - 属性一致性说明
- `timeliness_availability` - 时效性与可用性说明
- `rating` - 评分等级
- `reasoning` - 详细理由

### 2. DashScope API 支持

- 支持 `qwen-plus`、`qwen-turbo`、`qwen-max` 模型
- 通过 `DASHSCOPE_API_KEY` 环境变量配置
- 更稳定的 API 调用

### 3. 完整数据保存

评测结果保存三个层次：
1. 基础评测结果（scores、issues、suggestions）
2. 完整入参（query、response、dimensions、timestamp）
3. LLM评测详情（model、prompt、raw_response、parsed_result）

### 4. 增强 Prompt

- 电商搜索算法专家角色定位
- 三大核心评估标准（意图匹配、属性一致性、时效性）
- 明确的1-5分评分等级定义
- 详细的输出格式要求

## 使用方式

### 设置 API Key

```bash
export DASHSCOPE_API_KEY="sk-24d72e0867ac4f4f8c06a59c0c32b556"
```

### 运行快速评测

```bash
python3 quick_eval_test.py
```

### 运行完整评测

```bash
python3 run_full_evaluation.py
```

### 生成报告

```bash
python3 generate_table_report.py ./results/evaluation_results_xxx.json
```

## 评测结果示例

表格数据示例：

| Query | Score | Rating | 核心意图匹配 |
|-------|-------|--------|-------------|
| 忙碌白领买感冒药 | 4 | 高度相关 | 感冒灵颗粒直接匹配感冒症状... |
| 忙碌白领买感冒药 | 3 | 一般相关 | 维生素C作为辅助保健品... |

## 注意事项

1. **API Key 安全**: `.env` 文件已添加到 `.gitignore`，不会被提交
2. **模型名称**: 使用 `qwen-plus` 而非 `qwen3.6-plus`
3. **数据保存**: 评测结果自动保存到 `results/` 目录
4. **报告生成**: 支持 JSON 和 HTML 两种格式
