public class QueryGeneratorV2Test {
    public static void main(String[] args) {
        QueryGeneratorV2 generator = new QueryGeneratorV2();
        
        System.out.println("=".repeat(70));
        System.out.println("测试所有人设 - 修复模板变量替换问题");
        System.out.println("=".repeat(70));
        
        String[] personas = {
            "新手焦虑型妈妈",
            "效率实用型妈妈", 
            "品质追求型妈妈",
            "价格敏感型妈妈",
            "社交分享型妈妈",
            "谨慎保守型老人",
            "求助依赖型老人",
            "潮流探索型 Z 世代"
        };
        
        for (String personaName : personas) {
            System.out.println("\n【" + personaName + "】");
            for (int i = 0; i < 5; i++) {
                QueryGeneratorV2.GeneratedQuery result = generator.generateSingle(personaName, "母婴用品");
                System.out.println((i+1) + ". " + result.getQuery());
                // 检查是否有未替换的占位符
                if (result.getQuery().contains("{") || result.getQuery().contains("}")) {
                    System.out.println("   ⚠️ 警告：发现未替换的占位符！");
                }
            }
        }
    }
}
