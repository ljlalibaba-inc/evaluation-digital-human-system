# Query Generator Java HTTP API

Java 实现的 HTTP API 封装，提供两种方式：
1. 内置 HTTP Server（轻量级，无需额外依赖）
2. Spring Boot（生产环境推荐）

## 方式一：内置 HTTP Server

### 编译运行
```bash
cd /Users/linjie/Documents/workspace/skill/query-gen/java

# 编译
javac QueryGenHttpServer.java QueryGeneratorV2.java

# 运行（默认端口 5000）
java QueryGenHttpServer

# 或指定端口
java QueryGenHttpServer 8080
```

### API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | API 信息 |
| GET | `/health` | 健康检查 |
| GET | `/personas` | 获取所有人设 |
| GET | `/scenes` | 获取所有场景 |
| GET | `/generate?persona=...&scene=...&count=...` | 生成 Query |
| POST | `/generate` | 生成 Query (JSON) |

### 调用示例

```bash
# 生成单个 Query
curl "http://localhost:5000/generate?persona=新手焦虑型妈妈&scene=医药健康"

# 批量生成
curl "http://localhost:5000/generate?persona=新手焦虑型妈妈&scene=医药健康&count=10"

# POST 方式
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "persona": "价格敏感型妈妈",
    "scene": "母婴用品",
    "count": 5
  }'
```

---

## 方式二：Spring Boot（推荐）

### 项目结构
```
springboot/
├── pom.xml
├── src/
│   └── main/
│       ├── java/com/querygen/
│       │   ├── QueryGenApplication.java
│       │   ├── controller/
│       │   │   └── QueryGenController.java
│       │   ├── model/
│       │   │   ├── GenerateRequest.java
│       │   │   ├── GenerateResponse.java
│       │   │   └── QueryResult.java
│       │   └── service/
│       │       └── QueryGenService.java
│       └── resources/
│           └── application.properties
```

### 编译运行
```bash
cd /Users/linjie/Documents/workspace/skill/query-gen/java/springboot

# 编译打包
mvn clean package

# 运行
java -jar target/query-gen-api-1.0.0.jar

# 或直接使用 Maven
mvn spring-boot:run
```

### API 端点

与内置 HTTP Server 相同，额外支持：

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/generate/multi` | 多人群对比生成 |
| GET | `/docs` | Swagger UI 文档（如添加 springdoc） |

### 调用示例

```bash
# 获取人设列表
curl http://localhost:5000/personas

# 获取场景列表
curl http://localhost:5000/scenes

# 生成 Query
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "persona": "新手焦虑型妈妈",
    "scene": "医药健康",
    "count": 5
  }'

# 多人群对比
curl -X POST http://localhost:5000/generate/multi \
  -H "Content-Type: application/json" \
  -d '{
    "personas": ["新手焦虑型妈妈", "效率实用型妈妈", "价格敏感型妈妈"],
    "scene": "医药健康",
    "count_per_persona": 5
  }'
```

### Java 客户端调用示例

```java
import java.net.http.*;
import java.net.URI;

public class QueryGenClient {
    private static final String BASE_URL = "http://localhost:5000";

    public static void main(String[] args) throws Exception {
        HttpClient client = HttpClient.newHttpClient();

        // 生成 Query
        String json = "{" +
            "\"persona\": \"新手焦虑型妈妈\"," +
            "\"scene\": \"医药健康\"," +
            "\"count\": 5" +
        "}";

        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(BASE_URL + "/generate"))
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(json))
            .build();

        HttpResponse<String> response = client.send(request,
            HttpResponse.BodyHandlers.ofString());

        System.out.println(response.body());
    }
}
```

---

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
      "emotionLevel": "高",
      "expectedFocus": ["品牌正品", "价格"],
      "context": {}
    }
  ],
  "persona": "新手焦虑型妈妈",
  "scene": "医药健康",
  "count": 1
}
```

---

## 部署建议

### 使用 systemd（Linux）
```ini
# /etc/systemd/system/query-gen.service
[Unit]
Description=Query Generator API
After=network.target

[Service]
Type=simple
User=querygen
WorkingDirectory=/opt/query-gen
ExecStart=/usr/bin/java -jar query-gen-api-1.0.0.jar
Restart=always

[Install]
WantedBy=multi-user.target
```

### Docker 部署
```dockerfile
FROM openjdk:11-jre-slim

WORKDIR /app
COPY target/query-gen-api-1.0.0.jar app.jar

EXPOSE 5000

ENTRYPOINT ["java", "-jar", "app.jar"]
```

```bash
# 构建镜像
docker build -t query-gen-api .

# 运行容器
docker run -p 5000:5000 query-gen-api
```

---

## 性能对比

| 特性 | 内置 HTTP Server | Spring Boot |
|------|-----------------|-------------|
| 启动速度 | 快 | 较慢 |
| 内存占用 | 低 | 较高 |
| 功能丰富度 | 基础 | 丰富 |
| 生产环境 | 适合简单场景 | 推荐 |
| 依赖 | 无 | Maven/Gradle |
| 监控/日志 | 简单 | 完善 |

---

## 注意事项

1. 确保 Java 11 或更高版本
2. 内置 HTTP Server 使用 `com.sun.net.httpserver`，在模块化 JDK 中可能需要添加模块
3. Spring Boot 版本需要正确配置 QueryGeneratorV2 的依赖
4. 所有 API 支持 CORS，可被前端直接调用
