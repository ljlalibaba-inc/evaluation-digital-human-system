# Java HTTP API 使用说明

## ⚠️ 重要提示

**Java HTTP Server 无法直接处理 URL 中未编码的非 ASCII 字符（如中文）**。这是 Java `com.sun.net.httpserver.HttpServer` 的固有限制。

## ✅ 推荐用法：POST 方式

```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "persona": "效率实用型妈妈",
    "scene": "母婴用品",
    "count": 5
  }'
```

**优点：**
- 无需 URL 编码
- 支持所有 Unicode 字符
- 请求体结构清晰
- 无长度限制

## ✅ 可选用法：GET 方式（需要 URL 编码）

```bash
# 正确：URL 编码后的中文
curl "http://localhost:5000/generate?persona=%E6%95%88%E7%8E%87%E5%AE%9E%E7%94%A8%E5%9E%8B%E5%A6%88%E5%A6%88&scene=%E6%AF%8D%E5%A9%B4%E7%94%A8%E5%93%81&count=5"

# 错误：未编码的中文会导致 400 Bad Request
curl "http://localhost:5000/generate?persona=效率实用型妈妈&scene=母婴用品&count=5"
# ❌ URISyntaxException
```

**如何获取 URL 编码：**

使用 Python：
```bash
python3 -c "import urllib.parse; print(urllib.parse.quote('效率实用型妈妈'))"
# 输出：%E6%95%88%E7%8E%87%E5%AE%9E%E7%94%A8%E5%9E%8B%E5%A6%88%E5%A6%88
```

使用在线工具：
- https://www.urlencoder.org/
- 搜索 "URL encode"

## 📋 完整调用示例

### 1. 健康检查
```bash
curl http://localhost:5000/health
```

### 2. 获取人设列表
```bash
curl http://localhost:5000/personas
```

### 3. 获取场景列表
```bash
curl http://localhost:5000/scenes
```

### 4. 生成 Query（POST - 推荐）
```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"persona":"新手焦虑型妈妈","scene":"医药健康","count":5}'
```

### 5. 生成 Query（GET - 需要编码）
```bash
curl "http://localhost:5000/generate?persona=%E6%96%B0%E6%89%8B%E7%84%A6%E8%99%91%E5%9E%8B%E5%A6%88%E5%A6%88&scene=%E5%8C%BB%E8%8D%AF%E5%81%A5%E5%BA%B7&count=5"
```

## 🔧 启动服务器

```bash
cd /Users/linjie/Documents/workspace/skill/query-gen/java

# 编译
javac QueryGenHttpServer.java QueryGeneratorV2.java

# 运行（默认端口 5000）
java QueryGenHttpServer

# 或指定端口
java QueryGenHttpServer 8080
```

## 📊 响应格式

```json
{
  "success": true,
  "persona": "新手焦虑型妈妈",
  "scene": "医药健康",
  "count": 3,
  "data": [
    {
      "query": "孩子发烧，推荐布洛芬退烧药",
      "persona": "新手焦虑型妈妈",
      "scene": "医药健康",
      "intent": "退烧药",
      "complexity": "中",
      "emotion_level": "高",
      "expected_focus": ["正品保障", "配送速度"]
    }
  ]
}
```

## 🛠️ 为什么 GET 方式的中文会失败？

Java 的 `HttpServer.getRequestURI()` 方法在解析 URI 时会验证是否符合 RFC 2396 标准。未编码的非 ASCII 字符（如中文）不符合该标准，因此会抛出 `URISyntaxException`。

**解决方案对比：**

| 方案 | 优点 | 缺点 |
|------|------|------|
| POST + JSON | 无需编码，结构清晰 | 稍微复杂一点 |
| GET + URL 编码 | 简单直接 | 需要手动编码中文 |
| GET + 未编码中文 | ❌ 不可用 | 会抛出异常 |

## 💡 最佳实践

**始终使用 POST 方式调用包含中文参数的接口**：

```bash
# ✅ 推荐
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"persona":"<中文人设>","scene":"<中文场景>","count":5}'

# ❌ 避免
curl "http://localhost:5000/generate?persona=<中文>&scene=<中文>"
```
