import java.util.*;

/**
 * Query Generator CLI - Java 命令行工具
 */
public class QueryGenCLI {

    public static void main(String[] args) {
        if (args.length == 0 || args[0].equals("--help") || args[0].equals("-h")) {
            printHelp();
            return;
        }

        QueryGeneratorV2 generator = new QueryGeneratorV2();

        // 解析参数
        Map<String, String> params = parseArgs(args);

        // 处理 --list
        if (params.containsKey("list") || params.containsKey("list-personas")) {
            System.out.println("=".repeat(60));
            System.out.println("支持的人设:");
            System.out.println("=".repeat(60));
            for (String persona : generator.getAllPersonaNames()) {
                System.out.println("  - " + persona);
            }
            System.out.println();
        }

        if (params.containsKey("list") || params.containsKey("list-scenes")) {
            System.out.println("=".repeat(60));
            System.out.println("支持的场景:");
            System.out.println("=".repeat(60));
            for (String scene : generator.getAllSceneNames()) {
                System.out.println("  - " + scene);
            }
            System.out.println();
        }

        if (params.containsKey("list") || params.containsKey("list-personas") || params.containsKey("list-scenes")) {
            return;
        }

        // 验证参数
        boolean multiMode = params.containsKey("multi");
        String format = params.getOrDefault("format", "text");
        int count = Integer.parseInt(params.getOrDefault("count", "1"));

        if (!multiMode) {
            // 单人群模式
            String persona = params.get("persona");
            String scene = params.get("scene");

            if (persona == null || scene == null) {
                System.err.println("错误: 非多人群模式下，--persona 和 --scene 是必需的");
                System.exit(1);
            }

            List<QueryGeneratorV2.GeneratedQuery> queries = generator.generateBatch(persona, scene, count);
            String output = formatBatchOutput(queries, format);

            if (params.containsKey("output")) {
                System.out.println(output);
                System.out.println("结果已保存到: " + params.get("output"));
            } else {
                System.out.println(output);
            }

        } else {
            // 多人群模式
            String personasStr = params.get("personas");
            String scene = params.get("scene");

            if (personasStr == null || scene == null) {
                System.err.println("错误: 多人群模式下，--personas 和 --scene 是必需的");
                System.exit(1);
            }

            List<String> personaList = Arrays.asList(personasStr.split(","));
            Map<String, List<QueryGeneratorV2.GeneratedQuery>> results =
                generator.generateMultiPersona(personaList, scene, count);
            String output = formatMultiOutput(results, format);

            if (params.containsKey("output")) {
                System.out.println(output);
                System.out.println("结果已保存到: " + params.get("output"));
            } else {
                System.out.println(output);
            }
        }
    }

    private static Map<String, String> parseArgs(String[] args) {
        Map<String, String> params = new HashMap<>();

        for (int i = 0; i < args.length; i++) {
            String arg = args[i];
            switch (arg) {
                case "--persona":
                case "-p":
                    params.put("persona", args[++i]);
                    break;
                case "--scene":
                case "-s":
                    params.put("scene", args[++i]);
                    break;
                case "--count":
                case "-c":
                    params.put("count", args[++i]);
                    break;
                case "--multi":
                case "-m":
                    params.put("multi", "true");
                    break;
                case "--personas":
                    params.put("personas", args[++i]);
                    break;
                case "--format":
                case "-f":
                    params.put("format", args[++i]);
                    break;
                case "--output":
                case "-o":
                    params.put("output", args[++i]);
                    break;
                case "--list":
                case "-l":
                    params.put("list", "true");
                    break;
                case "--list-personas":
                    params.put("list-personas", "true");
                    break;
                case "--list-scenes":
                    params.put("list-scenes", "true");
                    break;
            }
        }

        return params;
    }

    private static String formatBatchOutput(List<QueryGeneratorV2.GeneratedQuery> queries, String format) {
        if ("json".equals(format)) {
            StringBuilder sb = new StringBuilder();
            sb.append("[\n");
            for (int i = 0; i < queries.size(); i++) {
                QueryGeneratorV2.GeneratedQuery q = queries.get(i);
                sb.append("  {\n");
                sb.append("    \"query\": \"").append(escapeJson(q.getQuery())).append("\",\n");
                sb.append("    \"persona\": \"").append(q.getPersona()).append("\",\n");
                sb.append("    \"scene\": \"").append(q.getScene()).append("\",\n");
                sb.append("    \"intent\": \"").append(q.getIntent()).append("\",\n");
                sb.append("    \"complexity\": \"").append(q.getComplexity()).append("\",\n");
                sb.append("    \"emotionLevel\": \"").append(q.getEmotionLevel()).append("\"\n");
                sb.append("  }");
                if (i < queries.size() - 1) sb.append(",");
                sb.append("\n");
            }
            sb.append("]");
            return sb.toString();

        } else if ("csv".equals(format)) {
            StringBuilder sb = new StringBuilder();
            sb.append("query,persona,scene,intent,complexity,emotionLevel\n");
            for (QueryGeneratorV2.GeneratedQuery q : queries) {
                sb.append("\"").append(q.getQuery()).append("\",");
                sb.append(q.getPersona()).append(",");
                sb.append(q.getScene()).append(",");
                sb.append(q.getIntent()).append(",");
                sb.append(q.getComplexity()).append(",");
                sb.append(q.getEmotionLevel()).append("\n");
            }
            return sb.toString();

        } else { // text
            StringBuilder sb = new StringBuilder();
            sb.append("=".repeat(60)).append("\n");
            sb.append("生成结果: ").append(queries.get(0).getPersona())
              .append(" - ").append(queries.get(0).getScene()).append("\n");
            sb.append("=".repeat(60)).append("\n");

            for (int i = 0; i < queries.size(); i++) {
                QueryGeneratorV2.GeneratedQuery q = queries.get(i);
                sb.append("\n【").append(i + 1).append("】\n");
                sb.append("  Query: ").append(q.getQuery()).append("\n");
                sb.append("  意图: ").append(q.getIntent()).append("\n");
                sb.append("  复杂度: ").append(q.getComplexity()).append("\n");
                sb.append("  情感强度: ").append(q.getEmotionLevel()).append("\n");
                sb.append("  评测重点: ").append(String.join(", ", q.getExpectedFocus())).append("\n");
            }

            sb.append("\n").append("=".repeat(60)).append("\n");
            return sb.toString();
        }
    }

    private static String formatMultiOutput(Map<String, List<QueryGeneratorV2.GeneratedQuery>> results, String format) {
        if ("json".equals(format)) {
            StringBuilder sb = new StringBuilder();
            sb.append("{\n");
            int personaCount = 0;
            for (Map.Entry<String, List<QueryGeneratorV2.GeneratedQuery>> entry : results.entrySet()) {
                sb.append("  \"").append(entry.getKey()).append("\": [\n");
                List<QueryGeneratorV2.GeneratedQuery> queries = entry.getValue();
                for (int i = 0; i < queries.size(); i++) {
                    QueryGeneratorV2.GeneratedQuery q = queries.get(i);
                    sb.append("    {\"query\": \"").append(escapeJson(q.getQuery())).append("\"}");
                    if (i < queries.size() - 1) sb.append(",");
                    sb.append("\n");
                }
                sb.append("  ]");
                if (++personaCount < results.size()) sb.append(",");
                sb.append("\n");
            }
            sb.append("}");
            return sb.toString();

        } else { // text
            StringBuilder sb = new StringBuilder();
            sb.append("=".repeat(60)).append("\n");
            sb.append("多人群对比结果").append("\n");
            sb.append("=".repeat(60)).append("\n");

            for (Map.Entry<String, List<QueryGeneratorV2.GeneratedQuery>> entry : results.entrySet()) {
                sb.append("\n【").append(entry.getKey()).append("】\n");
                List<QueryGeneratorV2.GeneratedQuery> queries = entry.getValue();
                for (int i = 0; i < queries.size(); i++) {
                    sb.append("  ").append(i + 1).append(". ")
                      .append(queries.get(i).getQuery()).append("\n");
                }
            }

            sb.append("\n").append("=".repeat(60)).append("\n");
            return sb.toString();
        }
    }

    private static String escapeJson(String s) {
        return s.replace("\\", "\\\\")
                .replace("\"", "\\\"")
                .replace("\n", "\\n")
                .replace("\r", "\\r")
                .replace("\t", "\\t");
    }

    private static void printHelp() {
        System.out.println("Query Generator CLI - Java 命令行工具");
        System.out.println();
        System.out.println("用法: java QueryGenCLI [选项]");
        System.out.println();
        System.out.println("选项:");
        System.out.println("  --persona, -p <名称>     人设名称");
        System.out.println("  --scene, -s <名称>       场景名称");
        System.out.println("  --count, -c <数量>       生成数量 (默认: 1)");
        System.out.println("  --multi, -m              多人群对比模式");
        System.out.println("  --personas <列表>        多个人设，用逗号分隔");
        System.out.println("  --format, -f <格式>      输出格式: text/json/csv (默认: text)");
        System.out.println("  --output, -o <路径>      输出文件路径");
        System.out.println("  --list, -l               列出所有人设和场景");
        System.out.println("  --list-personas          列出所有人设");
        System.out.println("  --list-scenes            列出所有场景");
        System.out.println("  --help, -h               显示帮助");
        System.out.println();
        System.out.println("示例:");
        System.out.println("  # 列出所有人设和场景");
        System.out.println("  java QueryGenCLI --list");
        System.out.println();
        System.out.println("  # 生成单个 Query");
        System.out.println("  java QueryGenCLI --persona \"新手焦虑型妈妈\" --scene \"医疗健康\"");
        System.out.println();
        System.out.println("  # 批量生成 10 条");
        System.out.println("  java QueryGenCLI -p \"新手焦虑型妈妈\" -s \"医疗健康\" -c 10");
        System.out.println();
        System.out.println("  # 多人群对比");
        System.out.println("  java QueryGenCLI --multi --personas \"新手焦虑型妈妈,谨慎保守型老人\" -s \"医疗健康\" -c 5");
        System.out.println();
        System.out.println("  # 输出 JSON 格式");
        System.out.println("  java QueryGenCLI -p \"新手焦虑型妈妈\" -s \"医疗健康\" -c 5 -f json");
    }
}
