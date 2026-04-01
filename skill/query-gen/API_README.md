# Query Generator HTTP API

基于 query-gen skill 的 RESTful API 封装，支持通过 HTTP 请求生成搜索 Query。

## 快速开始

### 1. 启动服务器

**方式一：使用内置 HTTP Server（无需额外依赖）**
```bash
cd /Users/linjie/.qoderwork/skills/query-gen
python3 api_server.py
# 或指定端口
python3 api_server.py --port 8080
```

**方式二：使用 FastAPI（推荐，功能更完善）**
```bash
# 安装依赖
pip install fastapi uvicorn

# 启动服务器
python3 api_fastapi.py
# 或
uvicorn api_fastapi:app --reload --port 5000
```

### 2. API 端点

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/` | API 信息 |
| GET | `/health` | 健康检查 |
| GET | `/personas` | 获取所有人设 |
| GET | `/scenes` | 获取所有场景 |
| GET | `/generate` | 生成 Query (URL 参数) |
| POST | `/generate` | 生成 Query (JSON body) |
| POST | `/generate/multi` | 多人群对比生成 |
| GET | `/docs` | FastAPI 自动文档 (仅 FastAPI 版本) |

### 3. 调用示例

**生成单个 Query：**
```bash
curl "http://localhost:5000/generate?persona=新手焦虑型妈妈&scene=医药健康"
```

**批量生成：**
```bash
curl "http://localhost:5000/generate?persona=新手焦虑型妈妈&scene=医药健康&count=10"
```

**POST 方式：**
```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "persona": "价格敏感型妈妈",
    "scene": "母婴用品",
    "count": 5
  }'
```

**多人群对比：**
```bash
curl -X POST http://localhost:5000/generate/multi \
  -H "Content-Type: application/json" \
  -d '{
    "personas": ["新手焦虑型妈妈", "效率实用型妈妈"],
    "scene": "医药健康",
    "count_per_persona": 5
  }'
```

### 4. Python 调用示例

```python
import requests

# 生成 Query
response = requests.post(
    "http://localhost:5000/generate",
    json={
        "persona": "新手焦虑型妈妈",
        "scene": "医药健康",
        "count": 5
    }
)
data = response.json()

for item in data['data']:
    print(f"Query: {item['query']}")
    print(f"意图: {item['intent']}")
    print(f"复杂度: {item['complexity']}")
    print("---")
```

### 5. JavaScript/前端调用示例

```javascript
// 生成 Query
fetch('http://localhost:5000/generate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    persona: '新手焦虑型妈妈',
    scene: '医药健康',
    count: 5
  })
})
.then(response => response.json())
.then(data => {
  data.data.forEach(item => {
    console.log('Query:', item.query);
    console.log('意图:', item.intent);
  });
});
```

## 支持的参数

### 人设 (Persona)
- 新手焦虑型妈妈
- 效率实用型妈妈
- 品质追求型妈妈
- 价格敏感型妈妈
- 社交分享型妈妈
- 谨慎保守型老人
- 求助依赖型老人
- 潮流探索型 Z 世代

### 场景 (Scene)
- 医药健康
- 母婴用品
- 餐饮外卖
- 教育早教
- 生活服务
- 休闲娱乐
- 社区服务
- 便民生活
- 新潮服务

## 响应格式

```json
{
  "success": true,
  "data": [
    {
      "query": "孩子发烧，推荐布洛芬退烧药",
      "persona": "新手焦虑型妈妈",
      "scene": "医药健康",
      "intent": "退烧药",
      "complexity": "中",
      "emotion_level": "高",
      "expected_focus": ["正品保障", "配送速度"],
      "context": {
        "situation": "孩子发烧",
        "brand": "",
        "spec": "布洛芬",
        "location": "",
        "delivery": "",
        "price_range": ""
      }
    }
  ],
  "persona": "新手焦虑型妈妈",
  "scene": "医药健康",
  "count": 1
}
```

## 运行示例脚本

```bash
# 确保服务器已启动
python3 api_server.py &

# 运行示例
python3 api_examples.py
```

## 部署建议

### 使用 Gunicorn (生产环境)
```bash
# 安装
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api_fastapi:app -b 0.0.0.0:5000
```

### Docker 部署
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . /app

RUN pip install fastapi uvicorn

EXPOSE 5000

CMD ["python", "api_fastapi.py"]
```

## 注意事项

1. 确保 skill 目录路径正确
2. FastAPI 版本提供更完善的自动文档
3. 内置 HTTP Server 适合简单场景，无需额外依赖
4. 所有 API 支持 CORS，可被前端直接调用
