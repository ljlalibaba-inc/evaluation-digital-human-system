import java.util.*;

/**
 * Query 生成器 - 独立版本
 * 基于数字人设自动生成搜索 Query
 */
public class QueryGenerator {

    private final Random random = new Random();
    private final Map<String, PersonaTemplate> personas = new HashMap<>();
    private final Map<String, Scene> scenes = new HashMap<>();

    public QueryGenerator() {
        initPersonas();
        initScenes();
    }

    /**
     * 生成单个 Query
     */
    public GeneratedQuery generateSingle(String personaName, String sceneName) {
        return generateSingle(personaName, sceneName, null);
    }

    /**
     * 生成单个 Query（带紧急程度）
     */
    public GeneratedQuery generateSingle(String personaName, String sceneName, String urgency) {
        PersonaTemplate persona = personas.get(personaName);
        if (persona == null) {
            throw new IllegalArgumentException("未知人设：" + personaName);
        }

        Scene scene = scenes.get(sceneName);
        if (scene == null) {
            throw new IllegalArgumentException("未知场景：" + sceneName);
        }

        // 选择需求
        String need = randomSelect(scene.getNeeds());

        // 填充模板
        String template = randomSelect(persona.getSentencePatterns());
        String query = fillTemplate(template, persona, need, urgency != null ? urgency : randomSelect(scene.getUrgencyLevels()));
        query = cleanQuery(query);

        // 确定复杂度
        String complexity = query.length() > 20 ? "高" : (query.length() > 10 ? "中" : "低");

        // 确定评测重点
        List<String> expectedFocus = determineFocus(query, scene);

        return new GeneratedQuery(query, personaName, sceneName, need, complexity, 
                                 persona.getEmotionLevel(), expectedFocus);
    }

    /**
     * 批量生成 Query
     */
    public List<GeneratedQuery> generateBatch(String personaName, String sceneName, int count) {
        List<GeneratedQuery> queries = new ArrayList<>();
        for (int i = 0; i < count; i++) {
            queries.add(generateSingle(personaName, sceneName));
        }
        return queries;
    }

    /**
     * 多人群对比生成
     */
    public Map<String, List<GeneratedQuery>> generateMultiPersona(List<String> personaNames, 
                                                                  String sceneName, 
                                                                  int countPerPersona) {
        Map<String, List<GeneratedQuery>> results = new LinkedHashMap<>();
        for (String personaName : personaNames) {
            results.put(personaName, generateBatch(personaName, sceneName, countPerPersona));
        }
        return results;
    }

    /**
     * 获取所有人设名称
     */
    public Set<String> getAllPersonaNames() {
        return personas.keySet();
    }

    /**
     * 获取所有场景名称
     */
    public Set<String> getAllSceneNames() {
        return scenes.keySet();
    }

    // ==================== 私有方法 ====================

    private void initPersonas() {
        // 1. 新手焦虑型妈妈
        personas.put("新手焦虑型妈妈", new PersonaTemplate(
            "P001", "新手焦虑型妈妈", "高",
            Arrays.asList("{时间}{需求}哪里{好}{疑问}", "{时间}想{需求}{条件}{疑问}", 
                        "宝宝{状况}{时间}{需求}{条件}", "{时间}{需求}{条件}靠谱吗"),
            Arrays.asList("urgent", "urgent 求助", "现在", "今天", ""),
            Arrays.asList("附近", "口碑好的", "有经验的", ""),
            Arrays.asList("有吗", "哪里好", "怎么办", "靠谱吗", "安全吗"),
            Arrays.asList("发烧了", "拉肚子", "不舒服", "")
        ));

        // 2. 效率实用型妈妈
        personas.put("效率实用型妈妈", new PersonaTemplate(
            "P002", "效率实用型妈妈", "中",
            Arrays.asList("{需求}{条件}", "{时间}{需求}{条件}", "不想{动作}{需求}"),
            Arrays.asList("urgent", "现在", "今天", ""),
            Arrays.asList("快", "方便", "附近", "不要太远", ""),
            Collections.emptyList(),
            Arrays.asList("做饭", "出门", "折腾", "")
        ));

        // 3. 品质追求型妈妈
        personas.put("品质追求型妈妈", new PersonaTemplate(
            "P003", "品质追求型妈妈", "中",
            Arrays.asList("想{需求}{条件}", "求推荐{需求}{条件}", "{需求}哪里{好}{条件}"),
            Arrays.asList("周末", "假期", ""),
            Arrays.asList("环境好", "口碑好", "品牌", ""),
            Arrays.asList("有推荐吗", "哪家好"),
            Collections.emptyList()
        ));

        // 4. 价格敏感型妈妈
        personas.put("价格敏感型妈妈", new PersonaTemplate(
            "P004", "价格敏感型妈妈", "低",
            Arrays.asList("{需求}{价格}{疑问}", "{价格}{需求}有吗", "{需求}哪里{便宜}"),
            Arrays.asList(""),
            Arrays.asList("性价比高", "团购", "优惠", "便宜", ""),
            Arrays.asList("多少钱", "有优惠吗", "贵不贵"),
            Collections.emptyList()
        ));

        // 5. 社交分享型妈妈
        personas.put("社交分享型妈妈", new PersonaTemplate(
            "P005", "社交分享型妈妈", "高",
            Arrays.asList("求推荐{需求}{条件}", "求安利{需求}{条件}", "想{需求}{条件}"),
            Arrays.asList("周末", "明天", ""),
            Arrays.asList("网红", "热门", "好玩的", "适合拍照", ""),
            Arrays.asList("有吗", "求推荐"),
            Collections.emptyList()
        ));

        // 6. 谨慎保守型老人
        personas.put("谨慎保守型老人", new PersonaTemplate(
            "P006", "谨慎保守型老人", "高",
            Arrays.asList("{需求}{条件}{疑问}", "{条件}{需求}{疑问}", "{需求}{条件}正规吗"),
            Arrays.asList("urgent", "今天", ""),
            Arrays.asList("正规的", "附近的", "有保障的", ""),
            Arrays.asList("可靠吗", "正规吗", "会不会骗人啊", "安全吗"),
            Collections.emptyList()
        ));

        // 7. 求助依赖型老人
        personas.put("求助依赖型老人", new PersonaTemplate(
            "P007", "求助依赖型老人", "高",
            Arrays.asList("帮帮忙{需求}{条件}", "我不会{需求}帮帮我", "想{需求}{条件}怎么办"),
            Arrays.asList("urgent", ""),
            Arrays.asList("简单的", "方便的", "附近的", ""),
            Arrays.asList("怎么办", "怎么弄", "有人帮吗"),
            Collections.emptyList()
        ));

        // 8. 潮流探索型 Z 世代
        personas.put("潮流探索型 Z 世代", new PersonaTemplate(
            "P008", "潮流探索型 Z 世代", "中",
            Arrays.asList("求安利{需求}{条件}", "{需求}求推荐{条件}", "想冲{需求}{条件}"),
            Arrays.asList("今晚", "周末", ""),
            Arrays.asList("网红", "出片", "氛围感", "小众", ""),
            Arrays.asList("有吗", "求安利", "怎么样"),
            Collections.emptyList()
        ));
    }

    private void initScenes() {
        scenes.put("医疗健康", new Scene("医疗健康",
            Arrays.asList("儿科医院", "儿童医院", "疫苗接种", "体检", "药店", "推拿", "牙科", "急诊"),
            Arrays.asList("urgent", "urgent 求助", "尽快", ""),
            Arrays.asList("响应速度", "可信度", "专业性")));

        scenes.put("餐饮外卖", new Scene("餐饮外卖",
            Arrays.asList("儿童餐", "营养餐", "辅食", "月子餐", "亲子餐厅", "外卖", "快餐"),
            Arrays.asList("urgent", "现在", "中午", "晚上", ""),
            Arrays.asList("配送速度", "餐品质量", "适龄性")));

        scenes.put("教育早教", new Scene("教育早教",
            Arrays.asList("早教中心", "托班", "兴趣班", "幼儿园", "亲子活动", "游泳", "英语"),
            Arrays.asList("近期", "下个月", "暑假", "周末", ""),
            Arrays.asList("师资", "环境", "口碑")));

        scenes.put("生活服务", new Scene("生活服务",
            Arrays.asList("保洁", "月嫂", "育儿嫂", "儿童摄影", "维修", "洗衣"),
            Arrays.asList("urgent", "本周", "近期", ""),
            Arrays.asList("专业性", "安全性", "价格")));

        scenes.put("休闲娱乐", new Scene("休闲娱乐",
            Arrays.asList("儿童乐园", "亲子游", "游泳馆", "绘本馆", "亲子酒店", "游乐场", "动物园"),
            Arrays.asList("周末", "假期", "明天", ""),
            Arrays.asList("好玩", "安全", "特色")));

        scenes.put("社区服务", new Scene("社区服务",
            Arrays.asList("社区医院", "老年食堂", "便民超市", "快递代收", "理发", "维修"),
            Arrays.asList("今天", "近期", ""),
            Arrays.asList("方便", "便宜", "近")));

        scenes.put("便民生活", new Scene("便民生活",
            Arrays.asList("缴费", "充值", "查询", "预约", "办事", "咨询"),
            Arrays.asList("urgent", "今天", ""),
            Arrays.asList("简单", "方便", "有人帮")));

        scenes.put("新潮服务", new Scene("新潮服务",
            Arrays.asList("剧本杀", "密室", "VR", "电竞", "自拍馆", "猫咖", "潮玩"),
            Arrays.asList("今晚", "周末", "urgent", ""),
            Arrays.asList("好玩", "出片", "氛围")));
    }

    private String fillTemplate(String template, PersonaTemplate persona, String need, String urgency) {
        String result = template;
        result = result.replace("{需求}", need);

        String timeWord = urgency != null ? urgency : randomSelect(persona.getTimeWords());
        result = result.replace("{时间}", timeWord != null ? timeWord : "");

        if (result.contains("{条件}")) {
            List<String> constraints = persona.getConditionWords();
            if (!constraints.isEmpty()) {
                String condition = randomSelect(constraints);
                result = result.replace("{条件}", condition != null ? condition : "");
            } else {
                result = result.replace("{条件}", "");
            }
        }

        if (result.contains("{疑问}")) {
            List<String> questions = persona.getQuestionWords();
            String question = !questions.isEmpty() ? randomSelect(questions) : "";
            result = result.replace("{疑问}", question != null ? question : "");
        }

        if (result.contains("{状况}")) {
            List<String> status = persona.getStatusWords();
            String statusWord = !status.isEmpty() ? randomSelect(status) : "";
            result = result.replace("{状况}", statusWord != null ? statusWord : "");
        }

        if (result.contains("{动作}")) {
            List<String> actions = persona.getActionWords();
            String action = !actions.isEmpty() ? randomSelect(actions) : "";
            result = result.replace("{动作}", action != null ? action : "");
        }

        // 处理额外的模板变量
        if (result.contains("{好}")) {
            result = result.replace("{好}", "好");
        }
        if (result.contains("{价格}")) {
            result = result.replace("{价格}", "");
        }
        if (result.contains("{便宜}")) {
            result = result.replace("{便宜}", "便宜");
        }

        return result;
    }

    private String cleanQuery(String query) {
        query = query.trim().replaceAll("\\s+", " ");
        query = query.replaceAll("^[，,。.！!？?\\s]+", "").replaceAll("[，,。.！!？?\\s]+$", "");

        // 处理 urgent - 移除多余空格，确保格式统一
        if (query.contains("urgent")) {
            query = query.replace("urgent 求助", "[URGENT]");
            query = query.replace("urgent", "[URGENT]");
            query = query.replace("[URGENT]", " urgent ");
            query = query.trim().replaceAll("\\s+", " ");
            // 确保 urgent 在开头
            if (query.contains("urgent") && !query.startsWith("urgent")) {
                query = query.replace("urgent", "").trim();
                query = "urgent " + query;
            }
        }

        return query.trim();
    }

    private List<String> determineFocus(String query, Scene scene) {
        List<String> focus = new ArrayList<>();
        
        if (query.contains("urgent") || query.contains("紧急")) {
            focus.add("响应速度");
        }
        if (query.contains("靠谱") || query.contains("正规") || query.contains("可靠") || query.contains("安全")) {
            focus.add("可信度");
        }
        if (query.contains("附近")) {
            focus.add("地理位置");
        }
        if (query.contains("便宜") || query.contains("价格") || query.contains("贵") || query.contains("优惠")) {
            focus.add("价格透明度");
        }
        
        if (focus.isEmpty()) {
            List<String> defaultFocus = scene.getDecisionFactors();
            focus.addAll(defaultFocus.subList(0, Math.min(2, defaultFocus.size())));
        }
        
        return focus;
    }

    private <T> T randomSelect(List<T> list) {
        if (list == null || list.isEmpty()) return null;
        return list.get(random.nextInt(list.size()));
    }

    // ==================== 内部类 ====================

    static class GeneratedQuery {
        private String query;
        private String persona;
        private String scene;
        private String intent;
        private String complexity;
        private String emotionLevel;
        private List<String> expectedFocus;

        GeneratedQuery() {}

        GeneratedQuery(String query, String persona, String scene, String intent,
                      String complexity, String emotionLevel, List<String> expectedFocus) {
            this.query = query;
            this.persona = persona;
            this.scene = scene;
            this.intent = intent;
            this.complexity = complexity;
            this.emotionLevel = emotionLevel;
            this.expectedFocus = expectedFocus;
        }

        public String getQuery() { return query; }
        public void setQuery(String query) { this.query = query; }
        public String getPersona() { return persona; }
        public void setPersona(String persona) { this.persona = persona; }
        public String getScene() { return scene; }
        public void setScene(String scene) { this.scene = scene; }
        public String getIntent() { return intent; }
        public void setIntent(String intent) { this.intent = intent; }
        public String getComplexity() { return complexity; }
        public void setComplexity(String complexity) { this.complexity = complexity; }
        public String getEmotionLevel() { return emotionLevel; }
        public void setEmotionLevel(String emotionLevel) { this.emotionLevel = emotionLevel; }
        public List<String> getExpectedFocus() { return expectedFocus; }
        public void setExpectedFocus(List<String> expectedFocus) { this.expectedFocus = expectedFocus; }

        @Override
        public String toString() {
            return String.format("GeneratedQuery{query='%s', persona='%s', scene='%s'}", 
                               query, persona, scene);
        }
    }

    static class PersonaTemplate {
        private final String id;
        private final String name;
        private final String emotionLevel;
        private final List<String> sentencePatterns;
        private final List<String> timeWords;
        private final List<String> conditionWords;
        private final List<String> questionWords;
        private final List<String> statusWords;
        private final List<String> actionWords;

        PersonaTemplate(String id, String name, String emotionLevel,
                       List<String> sentencePatterns, List<String> timeWords,
                       List<String> conditionWords, List<String> questionWords,
                       List<String> statusWords) {
            this.id = id;
            this.name = name;
            this.emotionLevel = emotionLevel;
            this.sentencePatterns = sentencePatterns;
            this.timeWords = timeWords;
            this.conditionWords = conditionWords;
            this.questionWords = questionWords;
            this.statusWords = statusWords;
            this.actionWords = statusWords; // 简化处理
        }

        public String getId() { return id; }
        public String getName() { return name; }
        public String getEmotionLevel() { return emotionLevel; }
        public List<String> getSentencePatterns() { return sentencePatterns; }
        public List<String> getTimeWords() { return timeWords; }
        public List<String> getConditionWords() { return conditionWords; }
        public List<String> getQuestionWords() { return questionWords; }
        public List<String> getStatusWords() { return statusWords; }
        public List<String> getActionWords() { return actionWords; }
    }

    static class Scene {
        private final String name;
        private final List<String> needs;
        private final List<String> urgencyLevels;
        private final List<String> decisionFactors;

        Scene(String name, List<String> needs, List<String> urgencyLevels, List<String> decisionFactors) {
            this.name = name;
            this.needs = needs;
            this.urgencyLevels = urgencyLevels;
            this.decisionFactors = decisionFactors;
        }

        public String getName() { return name; }
        public List<String> getNeeds() { return needs; }
        public List<String> getUrgencyLevels() { return urgencyLevels; }
        public List<String> getDecisionFactors() { return decisionFactors; }
    }
}
