import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import org.json.JSONObject;
import org.json.JSONArray;

/**
 * Query Generator Java HTTP Client 示例
 * 
 * 编译：javac -cp ".:json-20231013.jar" QueryGenHttpClient.java
 * 运行：java -cp ".:json-20231013.jar" QueryGenHttpClient
 * 
 * 依赖：org.json (下载：https://mvnrepository.com/artifact/org.json/json)
 */
public class QueryGenHttpClient {
    
    private static final String BASE_URL = "http://localhost:5000";
    private static final HttpClient client = HttpClient.newHttpClient();
    
    public static void main(String[] args) {
        System.out.println("=".repeat(70));
        System.out.println("Query Generator Java HTTP Client 示例");
        System.out.println("=".repeat(70));
        
        try {
            // 测试 1: 健康检查
            healthCheck();
            
            // 测试 2: 获取人设列表
            getPersonas();
            
            // 测试 3: 获取场景列表
            getScenes();
            
            // 测试 4: 生成 Query (POST 方式 - 推荐)
            generateQuery();
            
            // 测试 5: 批量生成
            generateBatch();
            
            // 测试 6: 多人群对比
            generateMultiPersona();
            
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
        
        JSONObject json = new JSONObject(response.body());
        System.out.println("状态：" + json.getString("status"));
        System.out.println("服务：" + json.getString("service"));
    }
    
    /**
     * 获取所有人设
     */
    public static void getPersonas() throws Exception {
        System.out.println("\n【测试 2】获取人设列表");
        System.out.println("-".repeat(70));
        
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(BASE_URL + "/personas"))
            .GET()
            .build();
        
        HttpResponse<String> response = client.send(request, 
            HttpResponse.BodyHandlers.ofString());
        
        JSONObject json = new JSONObject(response.body());
        JSONArray personas = json.getJSONArray("data");
        
        System.out.println("支持的人设 (" + personas.length() + "个):");
        for (int i = 0; i < personas.length(); i++) {
            System.out.println("  " + (i+1) + ". " + personas.getString(i));
        }
    }
    
    /**
     * 获取所有场景
     */
    public static void getScenes() throws Exception {
        System.out.println("\n【测试 3】获取场景列表");
        System.out.println("-".repeat(70));
        
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(BASE_URL + "/scenes"))
            .GET()
            .build();
        
        HttpResponse<String> response = client.send(request, 
            HttpResponse.BodyHandlers.ofString());
        
        JSONObject json = new JSONObject(response.body());
        JSONArray scenes = json.getJSONArray("data");
        
        System.out.println("支持的场景 (" + scenes.length() + "个):");
        for (int i = 0; i < scenes.length(); i++) {
            System.out.println("  " + (i+1) + ". " + scenes.getString(i));
        }
    }
    
    /**
     * 生成单个 Query
     */
    public static void generateQuery() throws Exception {
        System.out.println("\n【测试 4】生成 Query (POST 方式)");
        System.out.println("-".repeat(70));
        
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
        
        System.out.println("人设：" + json.getString("persona"));
        System.out.println("场景：" + json.getString("scene"));
        System.out.println("数量：" + json.getInt("count") + "条");
        System.out.println("\n生成的 Query:");
        
        for (int i = 0; i < queries.length(); i++) {
            JSONObject q = queries.getJSONObject(i);
            JSONObject context = q.optJSONObject("context");
            
            System.out.println("\n" + (i+1) + ". " + q.getString("query"));
            if (context != null) {
                System.out.print("   [");
                System.out.print("品牌:" + context.optString("brand", "-") + " ");
                System.out.print("规格:" + context.optString("spec", "-") + " ");
                System.out.print("价格:" + context.optString("priceRange", "-") + " ");
                System.out.print("位置:" + context.optString("location", "-") + " ");
                System.out.print("配送:" + context.optString("delivery", "-"));
                System.out.print("]");
            }
            System.out.println();
        }
    }
    
    /**
     * 批量生成 Query
     */
    public static void generateBatch() throws Exception {
        System.out.println("\n【测试 5】批量生成 Query (10 条)");
        System.out.println("-".repeat(70));
        
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
        
        System.out.println("生成 " + queries.length() + " 条 Query:");
        for (int i = 0; i < queries.length(); i++) {
            JSONObject q = queries.getJSONObject(i);
            System.out.println((i+1) + ". " + q.getString("query"));
        }
    }
    
    /**
     * 多人群对比生成
     */
    public static void generateMultiPersona() throws Exception {
        System.out.println("\n【测试 6】多人群对比生成");
        System.out.println("-".repeat(70));
        
        JSONObject requestBody = new JSONObject();
        JSONArray personas = new JSONArray();
        personas.put("新手焦虑型妈妈");
        personas.put("价格敏感型妈妈");
        requestBody.put("personas", personas);
        requestBody.put("scene", "母婴用品");
        requestBody.put("count_per_persona", 3);
        
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(BASE_URL + "/generate/multi"))
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(requestBody.toString()))
            .build();
        
        HttpResponse<String> response = client.send(request, 
            HttpResponse.BodyHandlers.ofString());
        
        JSONObject json = new JSONObject(response.body());
        JSONObject results = json.getJSONObject("data");
        
        for (String persona : results.keySet()) {
            System.out.println("\n【" + persona + "】");
            JSONArray queries = results.getJSONArray(persona);
            for (int i = 0; i < queries.length(); i++) {
                JSONObject q = queries.getJSONObject(i);
                System.out.println("  " + (i+1) + ". " + q.getString("query"));
            }
        }
    }
}
