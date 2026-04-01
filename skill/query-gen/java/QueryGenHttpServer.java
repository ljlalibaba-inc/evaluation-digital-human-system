import com.sun.net.httpserver.HttpServer;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpExchange;
import java.io.*;
import java.net.InetSocketAddress;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.util.*;

/**
 * Query Generator HTTP Server
 * Java 实现的 RESTful API 服务器
 *
 * 编译: javac QueryGenHttpServer.java QueryGeneratorV2.java
 * 运行: java QueryGenHttpServer [port]
 */
public class QueryGenHttpServer {

    private static QueryGeneratorV2 generator = new QueryGeneratorV2();
    private static final int DEFAULT_PORT = 5000;

    public static void main(String[] args) throws IOException {
        int port = args.length > 0 ? Integer.parseInt(args[0]) : DEFAULT_PORT;

        HttpServer server = HttpServer.create(new InetSocketAddress(port), 0);

        // 注册路由
        server.createContext("/", new RootHandler());
        server.createContext("/health", new HealthHandler());
        server.createContext("/personas", new PersonasHandler());
        server.createContext("/scenes", new ScenesHandler());
        server.createContext("/generate", new GenerateHandler());

        server.setExecutor(null);
        server.start();

        System.out.println("=".repeat(60));
        System.out.println("Query Generator Java HTTP Server");
        System.out.println("=".repeat(60));
        System.out.println("Server running at http://localhost:" + port);
        System.out.println("");
        System.out.println("API Endpoints:");
        System.out.println("  GET  http://localhost:" + port + "/personas");
        System.out.println("  GET  http://localhost:" + port + "/scenes");
        System.out.println("  GET  http://localhost:" + port + "/generate?persona=...&scene=...&count=...");
        System.out.println("  POST http://localhost:" + port + "/generate");
        System.out.println("  GET  http://localhost:" + port + "/health");
        System.out.println("=".repeat(60));
        System.out.println("Press Ctrl+C to stop");
        System.out.println("=".repeat(60));
    }

    // 基础响应方法
    private static void sendJson(HttpExchange exchange, int statusCode, String json) throws IOException {
        byte[] bytes = json.getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().set("Content-Type", "application/json; charset=UTF-8");
        exchange.getResponseHeaders().set("Access-Control-Allow-Origin", "*");
        exchange.getResponseHeaders().set("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
        exchange.getResponseHeaders().set("Access-Control-Allow-Headers", "Content-Type");
        exchange.sendResponseHeaders(statusCode, bytes.length);
        OutputStream os = exchange.getResponseBody();
        os.write(bytes);
        os.close();
    }

    private static void sendError(HttpExchange exchange, int statusCode, String message) throws IOException {
        String json = String.format("{\"success\": false, \"error\": \"%s\"}", escapeJson(message));
        sendJson(exchange, statusCode, json);
    }

    private static String escapeJson(String s) {
        return s.replace("\\", "\\\\")
                .replace("\"", "\\\"")
                .replace("\n", "\\n")
                .replace("\r", "\\r")
                .replace("\t", "\\t");
    }

    // 根路径处理器
    static class RootHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if (!"GET".equals(exchange.getRequestMethod())) {
                sendError(exchange, 405, "Method Not Allowed");
                return;
            }

            String json = "{" +
                "\"service\": \"Query Generator Java API\"," +
                "\"version\": \"2.0.0\"," +
                "\"endpoints\": {" +
                "  \"personas\": \"/personas\"," +
                "  \"scenes\": \"/scenes\"," +
                "  \"generate\": \"/generate\"" +
                "}" +
            "}";
            sendJson(exchange, 200, json);
        }
    }

    // 健康检查处理器
    static class HealthHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            String json = "{\"success\": true, \"status\": \"healthy\", \"service\": \"query-gen-java-api\"}";
            sendJson(exchange, 200, json);
        }
    }

    // 人设列表处理器
    static class PersonasHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if (!"GET".equals(exchange.getRequestMethod())) {
                sendError(exchange, 405, "Method Not Allowed");
                return;
            }

            Set<String> personas = generator.getAllPersonaNames();
            StringBuilder json = new StringBuilder();
            json.append("{\"success\": true, \"data\": [");
            boolean first = true;
            for (String persona : personas) {
                if (!first) json.append(",");
                json.append("\"").append(escapeJson(persona)).append("\"");
                first = false;
            }
            json.append("], \"count\": ").append(personas.size()).append("}");

            sendJson(exchange, 200, json.toString());
        }
    }

    // 场景列表处理器
    static class ScenesHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if (!"GET".equals(exchange.getRequestMethod())) {
                sendError(exchange, 405, "Method Not Allowed");
                return;
            }

            Set<String> scenes = generator.getAllSceneNames();
            StringBuilder json = new StringBuilder();
            json.append("{\"success\": true, \"data\": [");
            boolean first = true;
            for (String scene : scenes) {
                if (!first) json.append(",");
                json.append("\"").append(escapeJson(scene)).append("\"");
                first = false;
            }
            json.append("], \"count\": ").append(scenes.size()).append("}");

            sendJson(exchange, 200, json.toString());
        }
    }

    // 生成 Query 处理器
    static class GenerateHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            String method = exchange.getRequestMethod();

            if ("OPTIONS".equals(method)) {
                sendJson(exchange, 200, "{}");
                return;
            }

            String persona = "新手焦虑型妈妈";
            String scene = "医药健康";
            int count = 1;

            try {
                if ("GET".equals(method)) {
                    // 解析 URL 参数
                    String queryString = null;
                    // getRequestURI() 对未编码的中文字符会返回 null 而不是抛异常
                    try {
                        queryString = exchange.getRequestURI().getQuery();
                    } catch (Throwable t) {
                        // 任何异常都说明 URL 有问题
                        sendError(exchange, 400, "中文参数需要 URL 编码，或使用 POST 方式");
                        return;
                    }
                    
                    if (queryString != null && !queryString.isEmpty()) {
                        Map<String, String> params = parseQuery(queryString);
                        if (params.containsKey("persona")) {
                            persona = java.net.URLDecoder.decode(params.get("persona"), "UTF-8");
                        }
                        if (params.containsKey("scene")) {
                            scene = java.net.URLDecoder.decode(params.get("scene"), "UTF-8");
                        }
                        if (params.containsKey("count")) {
                            count = Integer.parseInt(params.get("count"));
                        }
                    }
                } else if ("POST".equals(method)) {
                    // 解析 JSON body
                    String body = readBody(exchange);
                    Map<String, String> json = parseJson(body);
                    if (json.containsKey("persona")) persona = json.get("persona");
                    if (json.containsKey("scene")) scene = json.get("scene");
                    if (json.containsKey("count")) count = Integer.parseInt(json.get("count"));
                } else {
                    sendError(exchange, 405, "Method Not Allowed");
                    return;
                }

                // 生成 Query
                List<QueryGeneratorV2.GeneratedQuery> queries = generator.generateBatch(persona, scene, count);

                // 构建响应 JSON
                StringBuilder json = new StringBuilder();
                json.append("{\"success\": true, ");
                json.append("\"persona\": \"").append(escapeJson(persona)).append("\", ");
                json.append("\"scene\": \"").append(escapeJson(scene)).append("\", ");
                json.append("\"count\": ").append(queries.size()).append(", ");
                json.append("\"data\": [");

                boolean first = true;
                for (QueryGeneratorV2.GeneratedQuery q : queries) {
                    if (!first) json.append(", ");
                    json.append(queryToJson(q));
                    first = false;
                }

                json.append("]}");
                sendJson(exchange, 200, json.toString());

            } catch (Exception e) {
                sendError(exchange, 500, e.getMessage());
            }
        }

        private String readBody(HttpExchange exchange) throws IOException {
            InputStream is = exchange.getRequestBody();
            ByteArrayOutputStream baos = new ByteArrayOutputStream();
            byte[] buffer = new byte[1024];
            int len;
            while ((len = is.read(buffer)) != -1) {
                baos.write(buffer, 0, len);
            }
            return baos.toString("UTF-8");
        }

        private Map<String, String> parseQuery(String query) {
            Map<String, String> map = new HashMap<>();
            for (String param : query.split("&")) {
                String[] parts = param.split("=", 2);
                if (parts.length == 2) {
                    map.put(parts[0], parts[1]);
                }
            }
            return map;
        }

        private Map<String, String> parseJson(String json) {
            Map<String, String> map = new HashMap<>();
            // 简单 JSON 解析（生产环境建议使用 Jackson/Gson）
            json = json.trim();
            if (json.startsWith("{") && json.endsWith("}")) {
                json = json.substring(1, json.length() - 1);
                String[] pairs = json.split(",");
                for (String pair : pairs) {
                    String[] kv = pair.split(":", 2);
                    if (kv.length == 2) {
                        String key = kv[0].trim().replace("\"", "");
                        String value = kv[1].trim().replace("\"", "");
                        map.put(key, value);
                    }
                }
            }
            return map;
        }

        private String queryToJson(QueryGeneratorV2.GeneratedQuery q) {
            StringBuilder json = new StringBuilder();
            json.append("{");
            json.append("\"query\": \"").append(escapeJson(q.getQuery())).append("\", ");
            json.append("\"persona\": \"").append(escapeJson(q.getPersona())).append("\", ");
            json.append("\"scene\": \"").append(escapeJson(q.getScene())).append("\", ");
            json.append("\"intent\": \"").append(escapeJson(q.getIntent())).append("\", ");
            json.append("\"complexity\": \"").append(escapeJson(q.getComplexity())).append("\", ");
            json.append("\"emotion_level\": \"").append(escapeJson(q.getEmotionLevel())).append("\", ");
            json.append("\"expected_focus\": [");
            List<String> focus = q.getExpectedFocus();
            for (int i = 0; i < focus.size(); i++) {
                if (i > 0) json.append(", ");
                json.append("\"").append(escapeJson(focus.get(i))).append("\"");
            }
            json.append("], ");
            
            // 添加 context 字段
            Map<String, Object> context = q.getContext();
            json.append("\"context\": {");
            if (context != null && !context.isEmpty()) {
                boolean first = true;
                for (Map.Entry<String, Object> entry : context.entrySet()) {
                    if (!first) json.append(", ");
                    json.append("\"").append(entry.getKey()).append("\": \"");
                    json.append(escapeJson(entry.getValue() != null ? entry.getValue().toString() : "")).append("\"");
                    first = false;
                }
            }
            json.append("}");
            
            json.append("}");
            return json.toString();
        }
    }
}
