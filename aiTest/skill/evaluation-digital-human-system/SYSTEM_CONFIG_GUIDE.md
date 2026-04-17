# 系统配置指南

## 配置文件说明

系统配置文件 `system_config.json` 包含数字人评测系统的所有配置项。

## 配置结构

```json
{
  "evaluation": { ... },    // 评测配置
  "schedule": { ... },      // 定时任务配置
  "dingtalk": { ... },      // 钉钉通知配置
  "output": { ... }         // 输出配置
}
```

## 详细配置项

### 1. 评测配置 (evaluation)

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `name` | string | 评测任务名称 | "千问大模型定时评测" |
| `target_model` | string | 被评测的目标模型 | "qwen-turbo" |
| `scope` | object | 评测范围 | - |
| `scope.personas` | array | 用户画像列表 | ["P1", "P2"] |
| `scope.scenarios` | array | 场景列表 | ["S1", "S2"] |
| `scope.categories` | array | 品类列表 | ["C5", "C4"] |
| `count` | number | 每个组合的用例数量 | 3 |
| `dimensions` | array | 评测维度 | ["accuracy", "timeliness", ...] |
| `evaluation_mode` | object | 评测模式配置 | - |
| `evaluation_mode.use_llm` | boolean | 是否使用LLM评测 | true |
| `evaluation_mode.llm_model` | string | LLM模型名称 | "qwen3.6-plus" |
| `evaluation_mode.available_models` | array | 可用模型列表 | ["qwen3.6-plus", "gpt-5.4-mini-0317-global"] |

**用户画像 (Personas)**:
- P1: 忙碌的年轻白领
- P2: 新手妈妈
- P3: 大学生
- P4: 精致白领
- P5: 退休阿姨
- P6: 双职工家庭

**场景 (Scenarios)**:
- S1: 应急补给
- S2: 即时享受
- S3: 懒人便利
- S4: 计划性消费
- S5: 节日聚会

**品类 (Categories)**:
- C1: 生鲜果蔬
- C2: 休闲零售
- C3: 3C数码
- C4: 母婴用品
- C5: 医药健康
- C6: 日用百货
- C7: 鲜花礼品
- C8: 宠物用品

**评测维度 (Dimensions)**:
- accuracy: 需求匹配度
- timeliness: 时效可信度
- personalization: 个性化程度
- safety: 安全引导
- diversity: 商品多样性
- novelty: 推荐新颖性
- shop_quality: 店铺质量
- product_richness: 商品丰富性

### 2. 定时任务配置 (schedule)

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `enabled` | boolean | 是否启用定时任务 | false |
| `daily_time` | string | 每日执行时间 | "09:00" |
| `weekly_day` | number | 每周几执行 (0=周一) | null |
| `weekly_time` | string | 每周执行时间 | null |
| `interval_minutes` | number | 间隔分钟数 | null |

**配置示例**:

每日执行:
```json
{
  "enabled": true,
  "daily_time": "09:00"
}
```

每周一执行:
```json
{
  "enabled": true,
  "weekly_day": 0,
  "weekly_time": "09:00"
}
```

### 3. 钉钉通知配置 (dingtalk)

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `enabled` | boolean | 是否启用钉钉通知 | true |
| `webhook_url` | string | 钉钉机器人Webhook地址 | "https://oapi.dingtalk.com/robot/send?access_token=xxx" |
| `secret` | string | 钉钉机器人加签密钥 | "SECxxx" |
| `at_mobiles` | array | @的手机号列表 | [] |
| `at_all` | boolean | 是否@所有人 | false |

**获取钉钉Webhook**:
1. 在钉钉群中添加机器人
2. 选择"自定义"机器人
3. 设置安全方式为"加签"
4. 复制Webhook地址和加签密钥

### 4. 输出配置 (output)

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `save_html` | boolean | 是否保存HTML报告 | true |
| `save_json` | boolean | 是否保存JSON数据 | true |
| `send_dingtalk` | boolean | 是否发送钉钉通知 | true |

## 当前配置备份

配置文件已备份至: `system_config_backup_20260416_200611.json`

## 配置修改方法

### 方法一: 直接编辑文件

```bash
# 使用编辑器打开配置文件
vim system_config.json

# 或使用VS Code
code system_config.json
```

### 方法二: 使用脚本修改

```python
import json

# 读取配置
with open('system_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 修改配置
config['evaluation']['dimensions'] = ['accuracy', 'timeliness', 'safety']
config['schedule']['enabled'] = True

# 保存配置
with open('system_config.json', 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)
```

## 配置验证

修改配置后，建议运行测试验证:

```bash
# 运行快速评测测试
python3 quick_eval_test.py
```

## 注意事项

1. **API密钥安全**: 不要将包含真实API密钥的配置文件提交到Git
2. **备份配置**: 修改前建议备份配置文件
3. **JSON格式**: 确保配置文件是有效的JSON格式
4. **权限设置**: 配置文件应设置为仅所有者可读写 (chmod 600)
