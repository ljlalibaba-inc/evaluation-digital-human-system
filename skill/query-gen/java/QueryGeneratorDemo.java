import java.util.*;

/**
 * Query Generator 演示程序
 */
public class QueryGeneratorDemo {
    public static void main(String[] args) {
        QueryGenerator generator = new QueryGenerator();
        
        System.out.println("============================================================");
        System.out.println("Query Generator 演示");
        System.out.println("============================================================");
        
        // 示例 1: 新手焦虑型妈妈 + 医疗健康场景
        System.out.println("\n【示例 1】新手焦虑型妈妈 - 医疗健康");
        QueryGenerator.GeneratedQuery result1 = generator.generateSingle("新手焦虑型妈妈", "医疗健康");
        System.out.println("Query: " + result1.getQuery());
        System.out.println("意图：" + result1.getIntent());
        System.out.println("复杂度：" + result1.getComplexity());
        
        // 示例 2: 谨慎保守型老人 + 生活服务场景
        System.out.println("\n【示例 2】谨慎保守型老人 - 生活服务");
        QueryGenerator.GeneratedQuery result2 = generator.generateSingle("谨慎保守型老人", "生活服务");
        System.out.println("Query: " + result2.getQuery());
        System.out.println("意图：" + result2.getIntent());
        System.out.println("复杂度：" + result2.getComplexity());
        
        // 示例 3: 潮流探索型 Z 世代 + 休闲娱乐（通过 API 获取正确名称）
        System.out.println("\n【示例 3】潮流探索型 Z 世代 - 休闲娱乐");
        String zGenName = null;
        for (String name : generator.getAllPersonaNames()) {
            if (name.contains("Z 世代")) {
                zGenName = name;
                break;
            }
        }
        if (zGenName != null) {
            QueryGenerator.GeneratedQuery result3 = generator.generateSingle(zGenName, "休闲娱乐");
            System.out.println("Query: " + result3.getQuery());
            System.out.println("意图：" + result3.getIntent());
            System.out.println("复杂度：" + result3.getComplexity());
        }
        
        // 示例 4: 批量生成
        System.out.println("\n【示例 4】批量生成 (效率实用型妈妈 - 餐饮外卖，5 条)");
        List<QueryGenerator.GeneratedQuery> batchResults = 
            generator.generateBatch("效率实用型妈妈", "餐饮外卖", 5);
        for (int i = 0; i < batchResults.size(); i++) {
            System.out.println((i + 1) + ". " + batchResults.get(i).getQuery());
        }
        
        // 示例 5: 多人群对比
        System.out.println("\n【示例 5】多人群对比测试 (教育早教场景)");
        List<String> personas = Arrays.asList("新手焦虑型妈妈", "品质追求型妈妈", "价格敏感型妈妈");
        Map<String, List<QueryGenerator.GeneratedQuery>> multiResults = 
            generator.generateMultiPersona(personas, "教育早教", 2);
        for (Map.Entry<String, List<QueryGenerator.GeneratedQuery>> entry : multiResults.entrySet()) {
            System.out.println("\n" + entry.getKey() + ":");
            for (QueryGenerator.GeneratedQuery query : entry.getValue()) {
                System.out.println("  - " + query.getQuery());
            }
        }
        
        System.out.println("\n============================================================");
        System.out.println("演示完成!");
        System.out.println("============================================================");
    }
}
