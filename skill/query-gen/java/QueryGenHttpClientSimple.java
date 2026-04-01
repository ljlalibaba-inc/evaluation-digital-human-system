import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Query Generator Java HTTP Client (简化版 - 无外部依赖)
 * 
 * 编译：javac QueryGenHttpClientSimple.java
 * 运行：java QueryGenHttpClientSimple
 */
public class QueryGenHttpClientSimple {
    
    private static final String BASE_URL = "http://localhost:5000";
    private static final HttpClient client = HttpClient.newHttpClient();
    
    public static void main(String[] args) {
        System.out.println("=".repeat(70));
        System.out.println("Query Generator Java HTTP Client (简化版)");
        System.out.println("=".repeat(70));
        
        try {
            // 测试 1: 健康检查
            healthCheck();
            
            // 测试 2: 生成 Query
            generateQuery();
            
            // 测试 3: 批量生成
            generateBatch();
            
        } catch (Exception e) {
            System.err.println("错误：" + e.getMessage());
            e.printStackTrace();
        }
        
        System.out.println("=".repeat(70));
    }
    
    /**
     * 健康检查
     */
    public static void healthCheck() throws Exception {
        System.out.println("\n【测试 1】健康检查");
        System.out.println("-".repeat(70));
        
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(BASE_URL + "/health"))
            .GET()
            .build();
        
        HttpResponse<String> response = client.send(request, 
            HttpResponse.BodyHandlers.ofString());
        
        System.out.println("响应：" + response.body());
    }
    
    /**
     * 生成单个 Query
     */
    public static void generateQuery() throws Exception {
        System.out.println("\n【测试 2】生成 Query (POST 方式)");
        System.out.println("-".repeat(70));
        
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
        
        // 简单解析 JSON 提取 query 字段
        String responseBody = response.body();
        System.out.println("生成结果:");
        extractQueries(responseBody);
    }
    
    /**
     * 批量生成 Query
     */
    public static void generateBatch() throws Exception {
        System.out.println("\n【测试 3】批量生成 (10 条)");
        System.out.println("-".repeat(70));
        
        String jsonBody = "{" +
            "\"persona\":\"价格敏感型妈妈\"," +
            "\"scene\":\"医药健康\"," +
            "\"count\":10" +
        "}";
        
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(BASE_URL + "/generate"))
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(jsonBody))
            .build();
        
        HttpResponse<String> response = client.send(request, 
            HttpResponse.BodyHandlers.ofString());
        
        String responseBody = response.body();
        System.out.println("生成结果:");
        extractQueries(responseBody);
    }
    
    /**
     * 从 JSON 响应中提取 query 列表 (简单正则解析)
     */
    public static void extractQueries(String json) {
        Pattern pattern = Pattern.compile("\"query\"\\s*:\\s*\"([^\"]+)\"");
        Matcher matcher = pattern.matcher(json);
        
        int count = 1;
        while (matcher.find()) {
            String query = matcher.group(1);
            // 解码 Unicode
            query = decodeUnicode(query);
            System.out.println(count + ". " + query);
            count++;
        }
    }
    
    /**
     * 解码 Unicode 转义字符
     */
    public static String decodeUnicode(String str) {
        Pattern pattern = Pattern.compile("\\\\u([0-9a-fA-F]{4})");
        Matcher matcher = pattern.matcher(str);
        
        StringBuffer sb = new StringBuffer();
        while (matcher.find()) {
            char ch = (char) Integer.parseInt(matcher.group(1), 16);
            matcher.appendReplacement(sb, String.valueOf(ch));
        }
        matcher.appendTail(sb);
        return sb.toString();
    }
}
