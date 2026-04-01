# Java 调用 HTTP API 指南

## 快速开始

### 1. 启动 HTTP Server

```bash
cd /Users/linjie/Documents/workspace/skill/query-gen/java

# 编译
javac QueryGenHttpServer.java QueryGeneratorV2.java

# 运行（默认端口 5000）
java QueryGenHttpServer

# 或指定端口
java QueryGenHttpServer 8080
```

### 2. 使用 curl 调用

**健康检查：**
```bash
curl http://localhost:5000/health
```

**生成 Query：**
```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "persona": "新手焦虑型妈妈",
    "scene": "母婴用品",
    "count": 5
  }'
```

**获取人设列表：**
```bash
curl http://localhost:5000/personas
```

**获取场景列表：**
```bash
curl http://localhost:5000/scenes
```

---

## Java 代码调用示例

### 方式一：简化版客户端（无外部依赖）

```java
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class QueryGenClient {
    private static final String BASE_URL = "http://localhost:5000";
    private static final HttpClient client = HttpClient.newHttpClient();
    
    public static void main(String[] args) throws Exception {
        // 生成 Query
        String jsonBody = "{" +
            "\"persona\":\"新手焦虑型妈妈\"," +
            "\"scene\":\"母婴用品\"," +
            "\"count\":5" +
        "}";
        
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(BASE_URL + "/generate"))
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(jsonBody))
            .build();
        
        HttpResponse<String> response = client.send(request, 
            HttpResponse.BodyHandlers.ofString());
        
        System.out.println(response.body());
    }
}
```

**编译运行：**
```bash
javac QueryGenClient.java
java QueryGenClient
```

### 方式二：使用 JSON 库（推荐）

添加依赖（Maven）：
```xml
<dependency>
    <groupId>org.json</groupId>
    <artifactId>json</artifactId>
    <version>20231013</version>
</dependency>
```

**完整示例代码：**
```java
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import org.json.JSONObject;
import org.json.JSONArray;

public class QueryGenClientWithJSON {
    private static final String BASE_URL = "http://localhost:5000";
    private static final HttpClient client = HttpClient.newHttpClient();
    
    public static void main(String[] args) throws Exception {
        // 1. 健康检查
        healthCheck();
        
        // 2. 生成 Query
        generateQuery();
        
        // 3. 批量生成并解析结果
        generateBatch();
    }
    
    public static void healthCheck() throws Exception {
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(BASE_URL + "/health"))
            .GET()
            .build();
        
        HttpResponse<String> response = client.send(request, 
            HttpResponse.BodyHandlers.ofString());
        
        JSONObject json = new JSONObject(response.body());
        System.out.println("状态：" + json.getString("status"));
    }
    
    public static void generateQuery() throws Exception {
        JSONObject requestBody = new JSONObject();
        requestBody.put("persona", "新手焦虑型妈妈");
        requestBody.put("scene", "母婴用品");
        requestBody.put("count", 3);
        
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(BASE_URL + "/generate"))
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(requestBody.toString()))
            .build();
        
        HttpResponse<String> response = client.send(request, 
            HttpResponse.BodyHandlers.ofString());
        
        JSONObject json = new JSONObject(response.body());
        JSONArray queries = json.getJSONArray("data");
        
        System.out.println("生成的 Query:");
        for (int i = 0; i < queries.length(); i++) {
            JSONObject q = queries.getJSONObject(i);
            System.out.println((i+1) + ". " + q.getString("query"));
        }
    }
    
    public static void generateBatch() throws Exception {
        JSONObject requestBody = new JSONObject();
        requestBody.put("persona", "效率实用型妈妈");
        requestBody.put("scene", "医药健康");
        requestBody.put("count", 10);
        
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(BASE_URL + "/generate"))
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(requestBody.toString()))
            .build();
        
        HttpResponse<String> response = client.send(request, 
            HttpResponse.BodyHandlers.ofString());
        
        JSONObject json = new JSONObject(response.body());
        JSONArray queries = json.getJSONArray("data");
        
        System.out.println("批量生成 " + queries.length() + " 条 Query:");
        for (int i = 0; i < queries.length(); i++) {
            JSONObject q = queries.getJSONObject(i);
            JSONObject context = q.optJSONObject("context");
            
            System.out.println("\n" + (i+1) + ". " + q.getString("query"));
            if (context != null) {
                System.out.print("   [品牌:" + context.optString("brand", "-"));
                System.out.print(" 规格:" + context.optString("spec", "-"));
                System.out.print(" 价格:" + context.optString("priceRange", "-"));
                System.out.print(" 位置:" + context.optString("location", "-"));
                System.out.print(" 配送:" + context.optString("delivery", "-"));
                System.out.print("]");
            }
        }
    }
}
```

**编译运行：**
```bash
# 下载 org.json jar 包
wget https://repo1.maven.org/maven2/org/json/json/20231013/json-20231013.jar

# 编译
javac -cp ".:json-20231013.jar" QueryGenClientWithJSON.java

# 运行
java -cp ".:json-20231013.jar" QueryGenClientWithJSON
```

---

## 完整 API 端点

| 方法 | 路径 | 说明 | 参数 |
|------|------|------|------|
| GET | `/health` | 健康检查 | 无 |
| GET | `/personas` | 获取所有人设 | 无 |
| GET | `/scenes` | 获取所有场景 | 无 |
| GET | `/generate` | 生成 Query | persona, scene, count |
| POST | `/generate` | 生成 Query | JSON body |
| POST | `/generate/multi` | 多人群对比 | personas[], scene, count_per_persona |

---

## 请求响应格式

### 生成 Query 请求

```json
{
  "persona": "新手焦虑型妈妈",
  "scene": "母婴用品",
  "count": 5
}
```

### 生成 Query 响应

```json
{
  "success": true,
  "persona": "新手焦虑型妈妈",
  "scene": "母婴用品",
  "count": 5,
  "data": [
    {
      "query": "孩子发烧，想买 100 元以内奶粉 3 公里内，要求 30 分钟达",
      "persona": "新手焦虑型妈妈",
      "scene": "母婴用品",
      "intent": "奶粉",
      "complexity": "中",
      "emotion_level": "高",
      "expected_focus": ["地理位置", "品牌匹配"],
      "context": {
        "brand": "飞鹤",
        "spec": "",
        "priceRange": "100 元以内",
        "location": "3 公里内",
        "delivery": "30 分钟达",
        "situation": "孩子发烧",
        "time": "",
        "action": "想买"
      }
    }
  ]
}
```

---

## 错误处理

```java
try {
    HttpResponse<String> response = client.send(request, 
        HttpResponse.BodyHandlers.ofString());
    
    int statusCode = response.statusCode();
    if (statusCode != 200) {
        System.err.println("HTTP 错误：" + statusCode);
        return;
    }
    
    // 处理响应...
    
} catch (Exception e) {
    System.err.println("请求失败：" + e.getMessage());
    e.printStackTrace();
}
```

---

## Spring Boot 集成

如果使用 Spring Boot，可以使用 `RestTemplate` 或 `WebClient`：

```java
@Service
public class QueryGenService {
    
    @Autowired
    private RestTemplate restTemplate;
    
    private static final String API_URL = "http://localhost:5000/generate";
    
    public List<QueryResult> generateQueries(String persona, String scene, int count) {
        Map<String, Object> request = new HashMap<>();
        request.put("persona", persona);
        request.put("scene", scene);
        request.put("count", count);
        
        ResponseEntity<Map> response = restTemplate.postForEntity(
            API_URL,
            request,
            Map.class
        );
        
        // 解析响应...
        return parseResults(response.getBody());
    }
}
```

---

## 注意事项

1. **中文编码**：POST 请求的 JSON body 自动处理中文，无需特殊编码
2. **GET 请求**：如果使用 GET 方式，中文参数需要 URL 编码
3. **端口**：默认端口 5000，可通过命令行参数修改
4. **并发**：单实例支持多个并发请求
5. **超时**：建议设置合理的超时时间（默认 60 秒）

---

## 测试工具

提供的示例代码：
- `QueryGenHttpClientSimple.java` - 简化版（无依赖）
- `QueryGenHttpClient.java` - 完整版（需 org.json）

编译运行：
```bash
# 简化版
javac QueryGenHttpClientSimple.java
java QueryGenHttpClientSimple

# 完整版（需要 JSON 库）
javac -cp ".:json-20231013.jar" QueryGenHttpClient.java
java -cp ".:json-20231013.jar" QueryGenHttpClient
```
