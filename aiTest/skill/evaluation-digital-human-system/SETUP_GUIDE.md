# DashScope API Key 设置指南

## 获取 API Key

1. 访问阿里云百炼平台：https://dashscope.console.aliyun.com/apiKey
2. 登录阿里云账号
3. 创建新的 API Key
4. 复制 API Key（格式类似：`sk-xxxxxxxxxxxxxxxx`）

## 设置方式

### 方式一：临时设置（当前终端）

```bash
export DASHSCOPE_API_KEY="sk-您的实际API密钥"
```

### 方式二：写入配置文件（推荐）

编辑项目根目录下的 `.env` 文件：

```bash
vim .env
```

将内容修改为：

```
DASHSCOPE_API_KEY=sk-您的实际API密钥
```

### 方式三：写入系统环境变量（永久有效）

**macOS/Linux:**

编辑 `~/.bashrc` 或 `~/.zshrc`：

```bash
echo 'export DASHSCOPE_API_KEY="sk-您的实际API密钥"' >> ~/.zshrc
source ~/.zshrc
```

**Windows:**

```cmd
setx DASHSCOPE_API_KEY "sk-您的实际API密钥"
```

## 验证设置

```bash
# 检查环境变量是否设置成功
echo $DASHSCOPE_API_KEY

# 运行评测测试
cd /Users/linjie/Documents/workspace/aiTest/skill/evaluation-digital-human-system
python3 quick_eval_test.py
```

## 注意事项

1. **API Key 安全**: 不要将包含真实 API Key 的文件提交到 Git
2. **已添加到 .gitignore**: `.env` 文件已在 `.gitignore` 中，不会被提交
3. **免费额度**: 新用户有免费调用额度，注意查看使用情况
4. **模型支持**: DashScope 支持 qwen-turbo、qwen-plus、qwen-max 等模型

## 支持的模型

| 模型名称 | 说明 |
|---------|------|
| qwen-turbo | 通义千问 Turbo，速度快，成本低 |
| qwen-plus | 通义千问 Plus，平衡性能 |
| qwen-max | 通义千问 Max，最强性能 |
| qwen3.6-plus | 新版千问模型 |

## 故障排查

### 401 错误（Unauthorized）

- API Key 无效或已过期
- 检查 API Key 是否正确复制
- 确认阿里云账号有百炼平台权限

### 429 错误（Rate Limit）

- 请求频率过高
- 降低并发数或增加延迟

### 500 错误（Server Error）

- 服务端错误，稍后重试
- 检查模型名称是否正确
