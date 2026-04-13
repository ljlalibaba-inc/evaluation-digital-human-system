# 浏览器认证参数提取指南

本文档介绍如何从浏览器获取千问 API 所需的认证参数（x-sign 和 wpk_reqid 等）。

## 方法对比

| 方法 | 难度 | 自动化程度 | 推荐度 |
|------|------|-----------|--------|
| 方法1: 浏览器控制台脚本 | ⭐⭐ | 高 | ⭐⭐⭐⭐⭐ |
| 方法2: 手动复制 cURL | ⭐⭐⭐ | 中 | ⭐⭐⭐⭐ |
| 方法3: Python 交互工具 | ⭐⭐ | 中 | ⭐⭐⭐⭐ |

---

## 方法1: 浏览器控制台脚本（推荐）

### 步骤

1. **访问千问聊天页面**
   ```
   https://chat2.qianwen.com
   ```

2. **打开开发者工具**
   - 按 `F12` 或右键 → 检查
   - 切换到 `Console` (控制台) 标签

3. **粘贴拦截脚本**
   - 打开 `utils/qwen_auth_sniffer.js`
   - 复制全部代码
   - 粘贴到控制台，按回车

4. **发送测试消息**
   - 在聊天框发送任意消息
   - 认证参数会自动捕获

5. **获取配置**
   - 配置已自动复制到剪贴板
   - 或在控制台输入命令查看：
   ```javascript
   qwenAuthSniffer.getLatestConfig()  // 查看最新配置
   qwenAuthSniffer.exportConfig()     // 导出为JSON文件
   ```

### 使用捕获的配置

```python
import json

# 加载配置
with open('qwen_auth_config_xxx.json', 'r') as f:
    qwen_config = json.load(f)

# 使用配置创建Agent
from master_digital_human import MasterDigitalHuman

master_config = {
    'results_dir': './results',
    'qwen_config': qwen_config
}

master = MasterDigitalHuman(master_config)
```

---

## 方法2: 手动复制 cURL

### 步骤

1. **打开开发者工具** (F12)

2. **发送一条消息**

3. **找到 chat 请求**
   - 切换到 `Network` (网络) 标签
   - 找到 `/api/v2/chat` 请求

4. **复制为 cURL**
   - 右键点击请求
   - `Copy` → `Copy as cURL (bash)`

5. **使用 Python 工具提取**
   ```bash
   cd /Users/linjie/Documents/workspace/aiTest/skill/evaluation-digital-human-system
   python3 utils/browser_auth_extractor.py
   ```
   
   选择选项 1，粘贴 cURL 命令

---

## 方法3: Python 交互工具

### 使用步骤

```bash
python3 utils/browser_auth_extractor.py
```

按照提示操作：
1. 选择输入方式（cURL 或原始请求头）
2. 粘贴从浏览器复制的内容
3. 工具自动提取参数
4. 选择是否保存配置文件

---

## 配置文件示例

提取的配置文件格式：

```json
{
  "api_mode": "qwen_chat",
  "stream": true,
  "model": "quark-235b",
  "x_sign": "a1b2c3d4e5f6...",
  "wpk_reqid": "abc123def456",
  "app_key": "your_app_key",
  "app_ver": "5.1.20",
  "bx_version": "1.0.0",
  "pv": "1.0",
  "device_id": "your_device_id",
  "wpk_bid": "your_wpk_bid",
  "umt": "your_umt",
  "mini_wua": "your_mini_wua",
  "sgext": "your_sgext",
  "captured_at": "2024-01-15T10:30:00.000Z"
}
```

---

## 注意事项

### ⚠️ 安全提醒

1. **保密性**: x-sign 和 wpk_reqid 是敏感信息，请勿：
   - 提交到版本控制（Git）
   - 分享给他人
   - 在公开场合展示

2. **有效期**: 认证参数有过期时间，通常需要：
   - 定期重新提取
   - 或配置自动刷新

3. **文件保护**: 建议将配置文件添加到 `.gitignore`：
   ```
   config/qwen_auth_config.json
   *_auth_config.json
   ```

### 🔧 故障排除

**问题1: 未找到 /api/v2/chat 请求**
- 确保已发送消息
- 检查是否过滤了请求（清除过滤器）
- 刷新页面重试

**问题2: 复制的配置无法使用**
- 检查 x-sign 和 wpk_reqid 是否存在
- 确认参数未过期（重新提取）
- 验证其他必填参数是否完整

**问题3: 脚本无法粘贴到控制台**
- 部分网站有安全策略限制
- 尝试在地址栏输入 `javascript:` 后粘贴
- 或使用方法2手动复制

---

## 自动化方案

如需自动获取认证参数，可配置 `auto_refresh_auth`：

```python
master_config = {
    'qwen_config': {
        'api_mode': 'qwen_chat',
        'stream': True,
        'auto_refresh_auth': True,
        'login_config': {
            'login_url': 'https://your-login-api.com/login',
            'login_type': 'password',
            'credentials': {
                'username': 'your_username',
                'password': 'your_password'
            },
            'x_sign_path': 'data.x_sign',
            'wpk_reqid_path': 'data.wpk_reqid'
        }
    }
}
```

> 注意：需要知道登录接口的具体信息才能使用自动刷新。

---

## 相关文件

- `utils/qwen_auth_sniffer.js` - 浏览器控制台脚本（推荐）
- `utils/browser_auth_extractor.py` - Python 交互提取工具
- `utils/qwen_auth_bookmarklet.js` - 浏览器书签工具
- `config/qwen_streaming_example.py` - 配置示例
