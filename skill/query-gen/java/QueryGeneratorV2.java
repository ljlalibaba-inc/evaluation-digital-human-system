import java.util.*;

/**
 * Query 生成器 V2 - 改进版，支持更丰富的表达方式
 * 基于数字人设自动生成搜索 Query
 */
public class QueryGeneratorV2 {

    private final Random random = new Random();
    private final Map<String, PersonaTemplate> personas = new HashMap<>();
    private final Map<String, Scene> scenes = new HashMap<>();

    public QueryGeneratorV2() {
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
     * 生成单个 Query（指定需求）
     */
    public GeneratedQuery generateSingle(String personaName, String sceneName, String need) {
        PersonaTemplate persona = personas.get(personaName);
        if (persona == null) {
            throw new IllegalArgumentException("未知人设：" + personaName);
        }

        Scene scene = scenes.get(sceneName);
        if (scene == null) {
            throw new IllegalArgumentException("未知场景：" + sceneName);
        }

        // 选择需求
        if (need == null) {
            need = randomSelect(scene.getNeeds());
        }

        // 构建 query 组件
        QueryComponents components = buildQueryComponents(persona, scene, need);

        // 组装 query
        String query = assembleQuery(components, persona);
        query = cleanQuery(query);

        // 确定复杂度
        String complexity = query.length() > 25 ? "高" : (query.length() > 15 ? "中" : "低");

        // 确定评测重点
        List<String> expectedFocus = determineFocus(query, scene, components);

        return new GeneratedQuery(query, personaName, sceneName, need, complexity,
                                 persona.getEmotionLevel(), expectedFocus, components.toMap());
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

    private QueryComponents buildQueryComponents(PersonaTemplate persona, Scene scene, String need) {
        QueryComponents components = new QueryComponents();
        components.setNeed(need);

        // 1. 情境描述 - 所有人设都可能有情境
        if ("P001".equals(persona.getId())) { 
            // 新手焦虑型妈妈 - 85% 概率
            List<String> situations = Arrays.asList(
                "孩子发烧", "宝宝不舒服", "小孩拉肚子", "孩子咳嗽", "宝宝过敏了"
            );
            if (random.nextDouble() < 0.85) {
                components.setSituation(randomSelect(situations));
            }
        } else if ("P002".equals(persona.getId())) {
            // 效率实用型妈妈 - 40% 概率，简单情境
            List<String> situations = Arrays.asList("今天", "现在", "马上", "");
            String timeContext = randomSelect(situations);
            if (!timeContext.isEmpty()) {
                components.setSituation(timeContext);
            }
        } else if ("P003".equals(persona.getId())) {
            // 品质追求型妈妈 - 50% 概率，注重场景
            List<String> situations = Arrays.asList("想给宝宝最好的", "为了宝宝健康", "注重品质", "");
            if (random.nextDouble() < 0.5) {
                components.setSituation(randomSelect(situations));
            }
        } else if ("P004".equals(persona.getId())) {
            // 价格敏感型妈妈 - 40% 概率，关注优惠时机
            List<String> situations = Arrays.asList("想趁活动买", "有促销吗", "想找实惠的", "");
            if (random.nextDouble() < 0.4) {
                components.setSituation(randomSelect(situations));
            }
        } else if ("P005".equals(persona.getId())) {
            // 社交分享型妈妈 - 60% 概率，跟风场景
            List<String> situations = Arrays.asList("看大家都在用", "朋友推荐的", "网上很火的", "最近流行的", "");
            if (random.nextDouble() < 0.6) {
                components.setSituation(randomSelect(situations));
            }
        } else if ("P006".equals(persona.getId())) {
            // 谨慎保守型老人 - 70% 概率，担心安全
            List<String> situations = Arrays.asList("担心被骗", "怕不靠谱", "想要有保障的", "不太会用", "");
            if (random.nextDouble() < 0.7) {
                components.setSituation(randomSelect(situations));
            }
        } else if ("P007".equals(persona.getId())) {
            // 求助依赖型老人 - 75% 概率，需要帮助
            List<String> situations = Arrays.asList("不会弄", "不知道怎么选", "第一次买", "儿女不在身边", "");
            if (random.nextDouble() < 0.75) {
                components.setSituation(randomSelect(situations));
            }
        } else if ("P008".equals(persona.getId())) {
            // 潮流探索型 Z 世代 - 50% 概率，追新潮
            List<String> situations = Arrays.asList("想试试新的", "跟风入", "种草很久了", "网红同款", "");
            if (random.nextDouble() < 0.5) {
                components.setSituation(randomSelect(situations));
            }
        }

        // 2. 具体规格/型号（让需求更明确）- 70% 概率
        Map<String, List<String>> subNeeds = scene.getSubNeeds();
        if (subNeeds.containsKey(need) && random.nextDouble() < 0.7) {
            components.setSpec(randomSelect(subNeeds.get(need)));
        }

        // 3. 地理位置约束 - 提高到 80%
        if (random.nextDouble() < 0.8) {
            List<String> distances = Arrays.asList("3公里内", "5公里内", "10公里内", "附近", "周边");
            components.setLocation(randomSelect(distances));
        }

        // 3.5 配送相关约束（所有场景都适用）- 提高到 60%
        if (random.nextDouble() < 0.6) {
            List<String> deliveryConstraints = Arrays.asList(
                "30分钟达", "1小时达", "2小时达", "当日达", "次日达",
                "急送", "快送", "同城配送", "小时达"
            );
            components.setDelivery(randomSelect(deliveryConstraints));
        }

        // 4. 品牌要求 - 提高到 90%
        Map<String, List<String>> brands = scene.getBrands();
        if (brands.containsKey(need) && random.nextDouble() < 0.9) {
            components.setBrand(randomSelect(brands.get(need)));
        }

        // 5. 礼貌用语
        if (!persona.getPolitePhrases().isEmpty() && random.nextDouble() < 0.3) {
            components.setPolite(randomSelect(persona.getPolitePhrases()));
        }

        // 6. 情感表达 - 所有人设都可能有情感，不同人设概率不同
        if (!persona.getEmotionalPhrases().isEmpty()) {
            double emotionProb = 0.5;  // 默认 50%
            if ("P001".equals(persona.getId())) {
                emotionProb = 0.7;  // 新手焦虑型妈妈 70%
            } else if ("P003".equals(persona.getId())) {
                emotionProb = 0.6;  // 品质追求型妈妈 60%
            } else if ("P005".equals(persona.getId())) {
                emotionProb = 0.6;  // 社交分享型妈妈 60%
            } else if ("P006".equals(persona.getId())) {
                emotionProb = 0.6;  // 谨慎保守型老人 60%
            } else if ("P007".equals(persona.getId())) {
                emotionProb = 0.7;  // 求助依赖型老人 70%
            } else if ("P008".equals(persona.getId())) {
                emotionProb = 0.5;  // 潮流探索型 Z 世代 50%
            }
            if (random.nextDouble() < emotionProb) {
                components.setEmotion(randomSelect(persona.getEmotionalPhrases()));
            }
        }

        // 7. 动作动词
        if (!persona.getActionVerbs().isEmpty()) {
            components.setAction(randomSelect(persona.getActionVerbs()));
        }

        // 8. 时间要求
        if (random.nextDouble() < 0.3) {
            List<String> timeReqs = Arrays.asList("urgent", "尽快", "今天", "现在", "马上");
            components.setTime(randomSelect(timeReqs));
        }

        // 9. 价格范围（所有场景适用，不同人设概率不同）- 整体提高概率
        double priceRangeProb = 0.5;  // 默认从 30% 提高到 50%
        if ("P004".equals(persona.getId())) {  // 价格敏感型妈妈更高概率
            priceRangeProb = 0.8;  // 从 60% 提高到 80%
        } else if ("P003".equals(persona.getId())) {  // 品质追求型妈妈较低概率
            priceRangeProb = 0.4;  // 从 20% 提高到 40%
        }
        
        if (!persona.getPriceRanges().isEmpty() && random.nextDouble() < priceRangeProb) {
            components.setPriceRange(randomSelect(persona.getPriceRanges()));
        }

        return components;
    }

    private String assembleQuery(QueryComponents components, PersonaTemplate persona) {
        // 根据人设选择不同的组装策略
        if ("P001".equals(persona.getId())) { // 新手焦虑型妈妈
            return assembleAnxiousMomQuery(components);
        } else if ("P002".equals(persona.getId())) { // 效率实用型妈妈
            return assembleEfficientMomQuery(components);
        } else if ("P003".equals(persona.getId())) { // 品质追求型妈妈
            return assembleQualityMomQuery(components);
        } else if ("P004".equals(persona.getId())) { // 价格敏感型妈妈
            return assemblePriceSensitiveMomQuery(components);
        } else {
            // 默认策略
            return assembleDefaultQuery(components, persona);
        }
    }

    private String assembleAnxiousMomQuery(QueryComponents components) {
        // 清理空值
        String situation = components.getSituation() != null ? components.getSituation() : "";
        String time = components.getTime() != null ? components.getTime() : "";
        String emotion = components.getEmotion() != null ? components.getEmotion() : "";
        String action = components.getAction() != null ? components.getAction() : "";
        String need = components.getNeed() != null ? components.getNeed() : "";
        String spec = components.getSpec() != null ? components.getSpec() : "";
        String brand = components.getBrand() != null ? components.getBrand() : "";
        String location = components.getLocation() != null ? components.getLocation() : "";
        String delivery = components.getDelivery() != null ? components.getDelivery() : "";
        String polite = components.getPolite() != null ? components.getPolite() : "";

        // 构建完整需求（规格 + 需求）
        String fullNeed = need;
        if (!spec.isEmpty()) {
            fullNeed = spec + need;
        }

        // 品牌需要加"的"
        if (!brand.isEmpty()) {
            brand = brand + "的";
        }

        // 位置需要处理 - 规范化表达
        if (!location.isEmpty()) {
            location = location.replace("附近内", "附近").replace("周边内", "周边");
            if (location.contains("公里") && !location.endsWith("内")) {
                location = location + "内";
            }
        }

        // 处理配送要求
        String deliveryPart = "";
        if (!delivery.isEmpty()) {
            deliveryPart = "，要求" + delivery;
        }

        // 处理价格范围
        String priceRange = components.getPriceRange() != null ? components.getPriceRange() : "";
        String pricePart = priceRange;

        // 随机选择模板
        int pattern = random.nextInt(5);
        String query;

        switch (pattern) {
            case 0: // 情境 + 动作 + 品牌 + 价格 + 完整需求 + 位置 + 配送 + 礼貌
                query = (situation.isEmpty() ? "" : situation + "，") +
                        action + brand + pricePart + fullNeed + location + deliveryPart +
                        (polite.isEmpty() ? "" : "，" + polite);
                break;
            case 1: // 情境 + 情感 + 动作 + 价格 + 完整需求 + 位置 + 配送
                query = (situation.isEmpty() ? "" : situation + "，") +
                        (emotion.isEmpty() ? "" : emotion + "，") +
                        action + pricePart + fullNeed + location + deliveryPart;
                break;
            case 2: // 时间 + 情境 + 动作 + 品牌 + 价格 + 完整需求 + 配送
                query = time +
                        (situation.isEmpty() ? "" : situation + "，") +
                        action + brand + pricePart + fullNeed + deliveryPart;
                break;
            case 3: // 动作 + 品牌 + 价格 + 完整需求 + 位置 + 配送 + 礼貌
                query = action + brand + pricePart + fullNeed + location + deliveryPart +
                        (polite.isEmpty() ? "" : "，" + polite);
                break;
            default: // 情境 + 动作 + 价格 + 完整需求 + 位置 + 配送
                query = (situation.isEmpty() ? "" : situation + "，") +
                        action + pricePart + fullNeed +
                        (location.isEmpty() ? "" : location) + deliveryPart;
                break;
        }

        // 清理多余的标点
        query = query.replace("，，", "，");
        query = query.replace("  ", " ");
        query = query.trim();
        while (query.startsWith("，")) query = query.substring(1);
        while (query.endsWith("，")) query = query.substring(0, query.length() - 1);

        return query.trim();
    }

    private String assembleEfficientMomQuery(QueryComponents components) {
        String time = components.getTime() != null ? components.getTime() : "";
        String need = components.getNeed() != null ? components.getNeed() : "";
        String location = components.getLocation() != null ? components.getLocation() : "";
        String action = components.getAction() != null ? components.getAction() : "";
        String priceRange = components.getPriceRange() != null ? components.getPriceRange() : "";

        // 随机选择模板
        int pattern = random.nextInt(3);

        // 如果有价格范围，加入价格因素
        if (!priceRange.isEmpty()) {
            switch (pattern) {
                case 0:
                    return time + priceRange + need + location;
                case 1:
                    return action + priceRange + need + location;
                default:
                    return priceRange + need + location;
            }
        } else {
            switch (pattern) {
                case 0:
                    return time + need + location;
                case 1:
                    return action + need + location;
                default:
                    return need + location;
            }
        }
    }

    private String assembleQualityMomQuery(QueryComponents components) {
        String need = components.getNeed() != null ? components.getNeed() : "";
        String brand = components.getBrand() != null ? components.getBrand() : "";
        String action = components.getAction() != null ? components.getAction() : "";
        String priceRange = components.getPriceRange() != null ? components.getPriceRange() : "";

        if (!brand.isEmpty()) {
            brand = brand + "的";
        }

        // 随机选择模板
        int pattern = random.nextInt(3);

        // 如果有价格范围，加入价格因素
        if (!priceRange.isEmpty()) {
            switch (pattern) {
                case 0:
                    return "求推荐" + priceRange + brand + need;
                case 1:
                    return "想" + action + priceRange + brand + need;
                default:
                    return priceRange + brand + need + "哪个好";
            }
        } else {
            switch (pattern) {
                case 0:
                    return "求推荐" + brand + need;
                case 1:
                    return "想" + action + brand + need;
                default:
                    return need + "哪个" + brand + "好";
            }
        }
    }

    private String assembleDefaultQuery(QueryComponents components, PersonaTemplate persona) {
        String template = randomSelect(persona.getSentencePatterns());
        if (template == null) template = "{需求}";
        
        // 替换所有可能的占位符
        String need = components.getNeed() != null ? components.getNeed() : "";
        String location = components.getLocation() != null ? components.getLocation() : "";
        String brand = components.getBrand() != null ? components.getBrand() : "";
        String action = components.getAction() != null ? components.getAction() : "";
        String situation = components.getSituation() != null ? components.getSituation() : "";
        String time = components.getTime() != null ? components.getTime() : "";
        String polite = components.getPolite() != null ? components.getPolite() : "";
        String emotion = components.getEmotion() != null ? components.getEmotion() : "";
        String priceRange = components.getPriceRange() != null ? components.getPriceRange() : "";
        
        return template
            .replace("{需求}", need)
            .replace("{位置}", location)
            .replace("{品牌}", brand)
            .replace("{动作}", action)
            .replace("{情境}", situation)
            .replace("{时间}", time)
            .replace("{礼貌}", polite)
            .replace("{情感}", emotion)
            .replace("{价格范围}", priceRange);
    }

    private String assemblePriceSensitiveMomQuery(QueryComponents components) {
        // 清理空值
        String need = components.getNeed() != null ? components.getNeed() : "";
        String priceRange = components.getPriceRange() != null ? components.getPriceRange() : "";

        // 如果有价格范围，使用包含价格的模板
        if (!priceRange.isEmpty()) {
            int pattern = random.nextInt(4);
            switch (pattern) {
                case 0:
                    return priceRange + need + "推荐一下";
                case 1:
                    return need + priceRange + "有吗";
                case 2:
                    return "想买" + priceRange + "的" + need;
                default:
                    return priceRange + "的" + need + "哪里买";
            }
        } else {
            // 没有价格范围时使用默认模板
            int pattern = random.nextInt(3);
            switch (pattern) {
                case 0:
                    return need + "哪里便宜";
                case 1:
                    return "求推荐性价比高的" + need;
                default:
                    return need + "有优惠吗";
            }
        }
    }

    private String cleanQuery(String query) {
        query = query.trim();

        // 移除多余的标点
        query = query.replace("，，", "，");
        query = query.replace("  ", " ");

        // 处理 urgent
        if (query.toLowerCase().contains("urgent")) {
            query = query.replaceAll("(?i)urgent", " urgent ");
            query = query.trim().replaceAll("\\s+", " ");
            if (!query.toLowerCase().startsWith("urgent")) {
                query = query.replaceAll("(?i)urgent", "").trim();
                query = "urgent " + query;
            }
        }

        return query.trim();
    }

    private List<String> determineFocus(String query, Scene scene, QueryComponents components) {
        List<String> focus = new ArrayList<>();

        if (query.contains("urgent") || query.contains("尽快") || query.contains("马上")) {
            focus.add("响应速度");
        }
        if (query.contains("公里") || query.contains("附近") || query.contains("周边")) {
            focus.add("地理位置");
        }
        if (components.getBrand() != null && !components.getBrand().isEmpty()) {
            focus.add("品牌匹配");
        }
        if (query.contains("靠谱") || query.contains("正规") || query.contains("可靠") || query.contains("安全")) {
            focus.add("可信度");
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

    private void initPersonas() {
        // 1. 新手焦虑型妈妈
        personas.put("新手焦虑型妈妈", new PersonaTemplate(
            "P001", "新手焦虑型妈妈", "高",
            Arrays.asList("{情境}，{时间}{动作}{需求}{品牌}{位置}{礼貌}"),
            Arrays.asList(" urgent", "尽快", "现在", "今天", ""),
            Arrays.asList("附近", "口碑好的", "有经验的", ""),
            Arrays.asList("有吗", "哪里好", "怎么办", "靠谱吗", "安全吗"),
            Arrays.asList("发烧了", "拉肚子", "不舒服", ""),
            Collections.emptyList(),
            // V2 新增字段
            Arrays.asList("3公里内", "5公里内", "10公里内", "附近", "周边", "就近"),
            Arrays.asList("品牌的", "大牌", "知名", ""),
            Arrays.asList("靠谱的", "安全的", "正规的", "口碑好的"),
            Arrays.asList(" urgent", "急需", "紧急", "快"),
            Arrays.asList("辛苦推荐", "麻烦推荐一下", "求推荐", "谢谢"),
            Arrays.asList("着急", "担心", "焦虑", "不知道怎么办"),
            Arrays.asList("推荐", "找", "需要", "想买"),
            Arrays.asList("100元以内", "200元以内", "300元以内", "实惠的", "性价比高的")
        ));

        // 2. 效率实用型妈妈
        personas.put("效率实用型妈妈", new PersonaTemplate(
            "P002", "效率实用型妈妈", "中",
            Arrays.asList("{需求}{位置}", "{时间}{需求}{位置}", "{动作}{需求}"),
            Arrays.asList(" urgent", "现在", "马上", ""),
            Arrays.asList("附近", "周边", "就近", "不要太远"),
            Arrays.asList(""),
            Arrays.asList(""),
            Arrays.asList("做饭", "出门", "折腾", ""),
            // V2 新增字段
            Arrays.asList("附近", "周边", "就近", "不要太远"),
            Arrays.asList("", ""),
            Arrays.asList("快的", "方便的", ""),
            Arrays.asList(" urgent", "快"),
            Arrays.asList(""),
            Arrays.asList(""),
            Arrays.asList("找", "需要", "要"),
            Arrays.asList("200元以内", "300元以内", "500元以内", "1000元以内", "性价比高的")
        ));

        // 3. 品质追求型妈妈
        personas.put("品质追求型妈妈", new PersonaTemplate(
            "P003", "品质追求型妈妈", "中",
            Arrays.asList("求推荐{品牌}{需求}", "想{动作}{品牌}{需求}", "{需求}哪个品牌好"),
            Arrays.asList("周末", "假期", ""),
            Arrays.asList("环境好的", "高端的", ""),
            Arrays.asList("有推荐吗", "哪家好"),
            Collections.emptyList(),
            Collections.emptyList(),
            // V2 新增字段
            Arrays.asList("环境好的", "高端的", ""),
            Arrays.asList("进口", "高端", "大牌", "知名"),
            Arrays.asList("高品质的", "专业的", "口碑好的"),
            Arrays.asList(""),
            Arrays.asList("求推荐", "推荐一下"),
            Arrays.asList("注重品质", "追求体验"),
            Arrays.asList("买", "选", "推荐"),
            Arrays.asList("300元以内", "500元以内", "1000元以内", "2000元以内", "高品质的")
        ));

        // 4. 价格敏感型妈妈
        List<String> priceRanges = Arrays.asList(
            "50元以内", "100元以内", "200元以内", "300元以内", "500元以内",
            "50块左右", "100块左右", "200块左右", "便宜点", "实惠的", "平价的"
        );

        personas.put("价格敏感型妈妈", new PersonaTemplate(
            "P004", "价格敏感型妈妈", "低",
            Arrays.asList("{需求}哪里便宜", "求推荐性价比高的{需求}", "{需求}有优惠吗",
                         "{价格范围}{需求}推荐一下", "{需求}{价格范围}有吗", "想买{价格范围}的{需求}"),
            Arrays.asList(""),
            Arrays.asList("附近的", ""),
            Arrays.asList("多少钱", "有优惠吗", "贵不贵"),
            Collections.emptyList(),
            Collections.emptyList(),
            // V2 新增字段
            Arrays.asList("附近的", ""),
            Arrays.asList("性价比高的", ""),
            Arrays.asList("实惠的", "划算的"),
            Arrays.asList(""),
            Arrays.asList("求推荐"),
            Arrays.asList(""),
            Arrays.asList("找", "买"),
            priceRanges  // 新增：价格范围
        ));

        // 5. 社交分享型妈妈
        personas.put("社交分享型妈妈", new PersonaTemplate(
            "P005", "社交分享型妈妈", "高",
            Arrays.asList("求安利{需求}", "想{动作}{需求}", "{需求}求推荐"),
            Arrays.asList("周末", "明天", ""),
            Arrays.asList("网红", "热门的", ""),
            Arrays.asList("有吗", "求推荐"),
            Collections.emptyList(),
            Collections.emptyList(),
            // V2 新增字段
            Arrays.asList("网红", "热门的", ""),
            Arrays.asList("网红", "热门"),
            Arrays.asList("好玩的", "适合拍照的"),
            Arrays.asList(""),
            Arrays.asList("求安利", "推荐一下"),
            Arrays.asList("想试试", "跟风"),
            Arrays.asList("打卡", "体验", "试试"),
            Arrays.asList("100元以内", "200元以内", "300元以内", "500元以内",
                         "100块左右", "200块左右", "性价比高的")
        ));

        // 6. 谨慎保守型老人
        personas.put("谨慎保守型老人", new PersonaTemplate(
            "P006", "谨慎保守型老人", "高",
            Arrays.asList("{需求}{位置}正规吗", "{位置}{需求}可靠吗", "想找正规的{需求}"),
            Arrays.asList(" urgent", "今天", ""),
            Arrays.asList("附近的", "正规的", ""),
            Arrays.asList("可靠吗", "正规吗", "会不会骗人啊", "安全吗"),
            Collections.emptyList(),
            Collections.emptyList(),
            // V2 新增字段
            Arrays.asList("附近的", "正规的", ""),
            Arrays.asList("老牌子", "知名的", ""),
            Arrays.asList("正规的", "有保障的", "可靠的"),
            Arrays.asList(" urgent"),
            Arrays.asList("麻烦", "请"),
            Arrays.asList("担心被骗", "怕不靠谱"),
            Arrays.asList("找", "需要"),
            Arrays.asList("50元以内", "100元以内", "200元以内", "实惠的", "便宜的")
        ));

        // 7. 求助依赖型老人
        personas.put("求助依赖型老人", new PersonaTemplate(
            "P007", "求助依赖型老人", "高",
            Arrays.asList("帮帮忙{动作}{需求}", "我不会{动作}{需求}，帮帮我", "想{需求}，{位置}怎么办"),
            Arrays.asList(" urgent", ""),
            Arrays.asList("附近的", "简单的", ""),
            Arrays.asList("怎么办", "怎么弄", "有人帮吗"),
            Collections.emptyList(),
            Collections.emptyList(),
            // V2 新增字段
            Arrays.asList("附近的", "简单的", ""),
            Arrays.asList(""),
            Arrays.asList("简单的", "方便的"),
            Arrays.asList(" urgent"),
            Arrays.asList("帮帮忙", "帮帮我", "麻烦"),
            Arrays.asList("不会弄", "不知道怎么"),
            Arrays.asList("找", "弄", "办"),
            Arrays.asList("50元以内", "100元以内", "200元以内", "实惠的", "便宜的")
        ));

        // 8. 潮流探索型 Z 世代
        personas.put("潮流探索型 Z 世代", new PersonaTemplate(
            "P008", "潮流探索型 Z 世代", "中",
            Arrays.asList("求安利{需求}", "想冲{需求}", "{需求}怎么样"),
            Arrays.asList("今晚", "周末", ""),
            Arrays.asList("网红", "出片的", "氛围感", ""),
            Arrays.asList("有吗", "求安利", "怎么样"),
            Collections.emptyList(),
            Collections.emptyList(),
            // V2 新增字段
            Arrays.asList("网红", "出片的", "氛围感", ""),
            Arrays.asList("小众", "网红", "潮牌"),
            Arrays.asList("出片的", "氛围感", "小众的"),
            Arrays.asList(""),
            Arrays.asList("求安利"),
            Arrays.asList("想试试", "种草"),
            Arrays.asList("冲", "打卡", "体验"),
            Arrays.asList("100元以内", "200元以内", "300元以内", "500元以内",
                         "100块左右", "200块左右", "性价比高的")
        ));
    }

    private void initScenes() {
        // 医药健康
        Map<String, List<String>> medicalBrands = new HashMap<>();
        medicalBrands.put("退烧药", Arrays.asList("强生", "美林", "泰诺林", "仁和", "葵花药业", "哈药", "修正"));
        medicalBrands.put("感冒药", Arrays.asList("999", "白云山", "以岭", "仁和", "同仁堂", "香雪", "云南白药"));
        medicalBrands.put("过敏药", Arrays.asList("开瑞坦", "息斯敏", "仙特明", "顺尔宁", "贝分"));
        medicalBrands.put("益生菌", Arrays.asList("合生元", "妈咪爱", "康萃乐", "Life-Space", "培菲康", "金双歧", "拜奥"));
        medicalBrands.put("维生素", Arrays.asList("伊可新", "星鲨", "汤臣倍健", "Swisse", "善存", "21金维他"));
        medicalBrands.put("钙片", Arrays.asList("钙尔奇", "迪巧", "朗迪", "Swisse", "三精", "龙牡"));
        medicalBrands.put("口罩", Arrays.asList("稳健", "振德", "3M", "霍尼韦尔", "袋鼠医生", "可孚", "海氏海诺"));
        medicalBrands.put("体温计", Arrays.asList("博朗", "欧姆龙", "鱼跃", "可孚", "迈克大夫", "华盛昌"));
        medicalBrands.put("血压计", Arrays.asList("欧姆龙", "鱼跃", "可孚", "松下", "九安", "乐心"));
        medicalBrands.put("血糖仪", Arrays.asList("罗氏", "强生", "欧姆龙", "鱼跃", "三诺", "艾科", "雅培"));
        medicalBrands.put("药店", Arrays.asList("海王星辰", "老百姓大药房", "国大药房", "同仁堂", "大参林", "益丰大药房", "一心堂", "叮当快药"));

        Map<String, List<String>> medicalSpecs = new HashMap<>();
        medicalSpecs.put("退烧药", Arrays.asList("布洛芬", "对乙酰氨基酚", "美林", "泰诺林", "小儿退热栓", "退热贴"));
        medicalSpecs.put("感冒药", Arrays.asList("小儿氨酚黄那敏", "999感冒灵", "板蓝根", "连花清瘟", "蒲地蓝", "小柴胡", "抗病毒口服液"));
        medicalSpecs.put("过敏药", Arrays.asList("氯雷他定", "西替利嗪", "扑尔敏", "孟鲁司特钠"));
        medicalSpecs.put("益生菌", Arrays.asList("妈咪爱", "合生元", "康萃乐", "Life-Space", "培菲康", "金双歧"));
        medicalSpecs.put("维生素", Arrays.asList("D3", "AD", "复合", "DHA", "C", "B"));
        medicalSpecs.put("钙片", Arrays.asList("钙尔奇", "迪巧", "朗迪", "Swisse", "葡萄糖酸钙", "乳钙"));
        medicalSpecs.put("口罩", Arrays.asList("N95", "医用外科", "儿童口罩", "KN95", "一次性医用"));
        medicalSpecs.put("体温计", Arrays.asList("电子", "耳温", "额温", "水银", "红外"));
        medicalSpecs.put("血压计", Arrays.asList("电子血压计", "手腕式", "上臂式"));
        medicalSpecs.put("血糖仪", Arrays.asList("免调码", "智能", "家用"));
        medicalSpecs.put("药店", Arrays.asList("24小时", "连锁", "医保定点", "网上药店"));

        scenes.put("医药健康", new Scene("医药健康",
            Arrays.asList("退烧药", "感冒药", "过敏药", "益生菌", "维生素", "钙片", "口罩", "体温计", "血压计", "血糖仪", "药店"),
            medicalSpecs,
            medicalBrands,
            Arrays.asList("正品保障", "配送速度", "价格", "品牌信赖")));

        // 母婴用品
        Map<String, List<String>> babyBrands = new HashMap<>();
        babyBrands.put("奶粉", Arrays.asList("飞鹤", "美赞臣", "惠氏", "雅培", "贝因美", "爱他美", "雀巢", "伊利"));
        babyBrands.put("纸尿裤", Arrays.asList("花王", "帮宝适", "好奇", "尤妮佳", "大王"));
        babyBrands.put("辅食", Arrays.asList("嘉宝", "亨氏", "小皮", "贝拉米"));
        babyBrands.put("玩具", Arrays.asList("费雪", "乐高", "伟易达", "面包超人"));
        babyBrands.put("童装", Arrays.asList("英氏", "巴拉巴拉", "丽婴房", "全棉时代"));
        babyBrands.put("婴儿车", Arrays.asList("好孩子", "昆塔斯", "虎贝尔", "bebebus"));

        Map<String, List<String>> babySpecs = new HashMap<>();
        babySpecs.put("奶粉", Arrays.asList("1段", "2段", "3段", "羊奶", "有机", "水解蛋白"));
        babySpecs.put("纸尿裤", Arrays.asList("NB码", "S码", "M码", "L码", "拉拉裤", "超薄透气", "夜用"));
        babySpecs.put("辅食", Arrays.asList("6个月", "9个月", "12个月", "高铁", "无添加", "有机"));
        babySpecs.put("玩具", Arrays.asList("益智", "积木", "毛绒", "早教", "安抚", "咬胶"));
        babySpecs.put("童装", Arrays.asList("纯棉", "加厚", "连体", "分体", "0-3个月", "3-6个月"));
        babySpecs.put("婴儿车", Arrays.asList("轻便", "可躺", "双向", "高景观", "一键收车", "避震"));

        scenes.put("母婴用品", new Scene("母婴用品",
            Arrays.asList("奶粉", "纸尿裤", "辅食", "玩具", "童装", "婴儿车"),
            babySpecs,  // 使用定义的 specs 而不是空 HashMap
            babyBrands,
            Arrays.asList("品牌正品", "价格", "配送速度")));

        // 餐饮外卖
        scenes.put("餐饮外卖", new Scene("餐饮外卖",
            Arrays.asList("儿童餐", "营养餐", "辅食", "月子餐", "亲子餐厅", "外卖", "快餐"),
            new HashMap<>(),
            new HashMap<>(),
            Arrays.asList("配送速度", "餐品质量", "适龄性")));

        // 教育早教
        scenes.put("教育早教", new Scene("教育早教",
            Arrays.asList("早教中心", "托班", "兴趣班", "幼儿园", "亲子活动", "游泳", "英语"),
            new HashMap<>(),
            new HashMap<>(),
            Arrays.asList("师资", "环境", "口碑")));

        // 生活服务
        scenes.put("生活服务", new Scene("生活服务",
            Arrays.asList("保洁", "月嫂", "育儿嫂", "儿童摄影", "维修", "洗衣"),
            new HashMap<>(),
            new HashMap<>(),
            Arrays.asList("专业性", "安全性", "价格")));

        // 休闲娱乐
        scenes.put("休闲娱乐", new Scene("休闲娱乐",
            Arrays.asList("儿童乐园", "亲子游", "游泳馆", "绘本馆", "亲子酒店", "游乐场", "动物园"),
            new HashMap<>(),
            new HashMap<>(),
            Arrays.asList("好玩", "安全", "特色")));

        // 社区服务
        scenes.put("社区服务", new Scene("社区服务",
            Arrays.asList("社区医院", "老年食堂", "便民超市", "快递代收", "理发", "维修"),
            new HashMap<>(),
            new HashMap<>(),
            Arrays.asList("方便", "便宜", "近")));

        // 便民生活
        scenes.put("便民生活", new Scene("便民生活",
            Arrays.asList("缴费", "充值", "查询", "预约", "办事", "咨询"),
            new HashMap<>(),
            new HashMap<>(),
            Arrays.asList("简单", "方便", "有人帮")));

        // 新潮服务
        scenes.put("新潮服务", new Scene("新潮服务",
            Arrays.asList("剧本杀", "密室", "VR", "电竞", "自拍馆", "猫咖", "潮玩"),
            new HashMap<>(),
            new HashMap<>(),
            Arrays.asList("好玩", "出片", "氛围")));
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
        private Map<String, Object> context;

        GeneratedQuery() {}

        GeneratedQuery(String query, String persona, String scene, String intent,
                      String complexity, String emotionLevel, List<String> expectedFocus,
                      Map<String, Object> context) {
            this.query = query;
            this.persona = persona;
            this.scene = scene;
            this.intent = intent;
            this.complexity = complexity;
            this.emotionLevel = emotionLevel;
            this.expectedFocus = expectedFocus;
            this.context = context;
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
        public Map<String, Object> getContext() { return context; }
        public void setContext(Map<String, Object> context) { this.context = context; }

        @Override
        public String toString() {
            return String.format("GeneratedQuery{query='%s', persona='%s', scene='%s'}",
                               query, persona, scene);
        }
    }

    static class QueryComponents {
        private String situation;
        private String need;
        private String spec;
        private String constraint;
        private String brand;
        private String location;
        private String delivery;  // 新增：配送要求
        private String time;
        private String polite;
        private String emotion;
        private String action;
        private String priceRange;  // 新增：价格范围

        public String getSituation() { return situation; }
        public void setSituation(String situation) { this.situation = situation; }
        public String getNeed() { return need; }
        public void setNeed(String need) { this.need = need; }
        public String getSpec() { return spec; }
        public void setSpec(String spec) { this.spec = spec; }
        public String getConstraint() { return constraint; }
        public void setConstraint(String constraint) { this.constraint = constraint; }
        public String getBrand() { return brand; }
        public void setBrand(String brand) { this.brand = brand; }
        public String getLocation() { return location; }
        public void setLocation(String location) { this.location = location; }
        public String getDelivery() { return delivery; }
        public void setDelivery(String delivery) { this.delivery = delivery; }
        public String getTime() { return time; }
        public void setTime(String time) { this.time = time; }
        public String getPolite() { return polite; }
        public void setPolite(String polite) { this.polite = polite; }
        public String getEmotion() { return emotion; }
        public void setEmotion(String emotion) { this.emotion = emotion; }
        public String getAction() { return action; }
        public void setAction(String action) { this.action = action; }
        public String getPriceRange() { return priceRange; }
        public void setPriceRange(String priceRange) { this.priceRange = priceRange; }

        public Map<String, Object> toMap() {
            Map<String, Object> map = new HashMap<>();
            map.put("situation", situation != null ? situation : "");
            map.put("need", need != null ? need : "");
            map.put("spec", spec != null ? spec : "");
            map.put("constraint", constraint != null ? constraint : "");
            map.put("brand", brand != null ? brand : "");
            map.put("location", location != null ? location : "");
            map.put("time", time != null ? time : "");
            map.put("polite", polite != null ? polite : "");
            map.put("emotion", emotion != null ? emotion : "");
            map.put("action", action != null ? action : "");
            map.put("priceRange", priceRange != null ? priceRange : "");
            map.put("delivery", delivery != null ? delivery : "");
            return map;
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
        // V2 新增字段
        private final List<String> locationConstraints;
        private final List<String> brandPreferences;
        private final List<String> qualityIndicators;
        private final List<String> urgencyIndicators;
        private final List<String> politePhrases;
        private final List<String> emotionalPhrases;
        private final List<String> actionVerbs;
        private final List<String> priceRanges;  // 新增：价格范围

        PersonaTemplate(String id, String name, String emotionLevel,
                       List<String> sentencePatterns, List<String> timeWords,
                       List<String> conditionWords, List<String> questionWords,
                       List<String> statusWords, List<String> actionWords,
                       // V2 新增
                       List<String> locationConstraints, List<String> brandPreferences,
                       List<String> qualityIndicators, List<String> urgencyIndicators,
                       List<String> politePhrases, List<String> emotionalPhrases,
                       List<String> actionVerbs) {
            this(id, name, emotionLevel, sentencePatterns, timeWords, conditionWords,
                 questionWords, statusWords, actionWords, locationConstraints,
                 brandPreferences, qualityIndicators, urgencyIndicators,
                 politePhrases, emotionalPhrases, actionVerbs, Collections.emptyList());
        }

        PersonaTemplate(String id, String name, String emotionLevel,
                       List<String> sentencePatterns, List<String> timeWords,
                       List<String> conditionWords, List<String> questionWords,
                       List<String> statusWords, List<String> actionWords,
                       // V2 新增
                       List<String> locationConstraints, List<String> brandPreferences,
                       List<String> qualityIndicators, List<String> urgencyIndicators,
                       List<String> politePhrases, List<String> emotionalPhrases,
                       List<String> actionVerbs, List<String> priceRanges) {
            this.id = id;
            this.name = name;
            this.emotionLevel = emotionLevel;
            this.sentencePatterns = sentencePatterns;
            this.timeWords = timeWords;
            this.conditionWords = conditionWords;
            this.questionWords = questionWords;
            this.statusWords = statusWords;
            this.actionWords = actionWords;
            // V2
            this.locationConstraints = locationConstraints;
            this.brandPreferences = brandPreferences;
            this.qualityIndicators = qualityIndicators;
            this.urgencyIndicators = urgencyIndicators;
            this.politePhrases = politePhrases;
            this.emotionalPhrases = emotionalPhrases;
            this.actionVerbs = actionVerbs;
            this.priceRanges = priceRanges != null ? priceRanges : Collections.emptyList();
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
        // V2 getters
        public List<String> getLocationConstraints() { return locationConstraints; }
        public List<String> getBrandPreferences() { return brandPreferences; }
        public List<String> getQualityIndicators() { return qualityIndicators; }
        public List<String> getUrgencyIndicators() { return urgencyIndicators; }
        public List<String> getPolitePhrases() { return politePhrases; }
        public List<String> getEmotionalPhrases() { return emotionalPhrases; }
        public List<String> getActionVerbs() { return actionVerbs; }
        public List<String> getPriceRanges() { return priceRanges; }  // 新增
    }

    static class Scene {
        private final String name;
        private final List<String> needs;
        private final Map<String, List<String>> subNeeds;
        private final Map<String, List<String>> brands;
        private final List<String> decisionFactors;

        Scene(String name, List<String> needs, Map<String, List<String>> subNeeds,
              Map<String, List<String>> brands, List<String> decisionFactors) {
            this.name = name;
            this.needs = needs;
            this.subNeeds = subNeeds;
            this.brands = brands;
            this.decisionFactors = decisionFactors;
        }

        public String getName() { return name; }
        public List<String> getNeeds() { return needs; }
        public Map<String, List<String>> getSubNeeds() { return subNeeds; }
        public Map<String, List<String>> getBrands() { return brands; }
        public List<String> getDecisionFactors() { return decisionFactors; }
    }
}
