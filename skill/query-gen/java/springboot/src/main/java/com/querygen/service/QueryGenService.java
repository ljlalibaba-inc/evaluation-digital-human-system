package com.querygen.service;

import com.querygen.model.QueryResult;
import org.springframework.stereotype.Service;

import java.util.*;

/**
 * Query Generator Service
 * 封装 QueryGeneratorV2 的调用
 */
@Service
public class QueryGenService {

    // 使用反射或复制 QueryGeneratorV2 的实现
    // 这里简化实现，实际应该引入 QueryGeneratorV2

    private final Map<String, PersonaInfo> personas = new HashMap<>();
    private final Map<String, SceneInfo> scenes = new HashMap<>();
    private final Random random = new Random();

    public QueryGenService() {
        initPersonas();
        initScenes();
    }

    public Set<String> getAllPersonaNames() {
        return personas.keySet();
    }

    public Set<String> getAllSceneNames() {
        return scenes.keySet();
    }

    public List<QueryResult> generateBatch(String personaName, String sceneName, int count) {
        List<QueryResult> results = new ArrayList<>();
        for (int i = 0; i < count; i++) {
            results.add(generateSingle(personaName, sceneName));
        }
        return results;
    }

    public Map<String, List<QueryResult>> generateMultiPersona(
            List<String> personaNames, String sceneName, int countPerPersona) {
        Map<String, List<QueryResult>> results = new LinkedHashMap<>();
        for (String personaName : personaNames) {
            results.put(personaName, generateBatch(personaName, sceneName, countPerPersona));
        }
        return results;
    }

    private QueryResult generateSingle(String personaName, String sceneName) {
        PersonaInfo persona = personas.get(personaName);
        SceneInfo scene = scenes.get(sceneName);

        if (persona == null || scene == null) {
            throw new IllegalArgumentException("Unknown persona or scene");
        }

        String need = randomSelect(scene.needs);
        String query = buildQuery(persona, scene, need);

        return new QueryResult(
            query,
            personaName,
            sceneName,
            need,
            query.length() > 25 ? "高" : (query.length() > 15 ? "中" : "低"),
            persona.emotionLevel,
            Arrays.asList("品牌正品", "价格"),
            new HashMap<>()
        );
    }

    private String buildQuery(PersonaInfo persona, SceneInfo scene, String need) {
        // 简化的 query 构建逻辑
        List<String> patterns = persona.patterns;
        String pattern = randomSelect(patterns);

        // 替换占位符
        String query = pattern.replace("{需求}", need);

        // 随机添加价格范围
        if (random.nextDouble() < 0.3 && !persona.priceRanges.isEmpty()) {
            String priceRange = randomSelect(persona.priceRanges);
            query = priceRange + query;
        }

        return query;
    }

    private <T> T randomSelect(List<T> list) {
        return list.get(random.nextInt(list.size()));
    }

    private void initPersonas() {
        personas.put("新手焦虑型妈妈", new PersonaInfo("高", Arrays.asList(
            "推荐{需求}", "需要{需求}", "找{需求}"
        ), Arrays.asList("100元以内", "200元以内", "实惠的")));

        personas.put("效率实用型妈妈", new PersonaInfo("中", Arrays.asList(
            "{需求}", "找{需求}", "要{需求}"
        ), Arrays.asList("200元以内", "300元以内", "性价比高的")));

        personas.put("品质追求型妈妈", new PersonaInfo("中", Arrays.asList(
            "求推荐{需求}", "想选{需求}", "{需求}哪个好"
        ), Arrays.asList("500元以内", "1000元以内", "高品质的")));

        personas.put("价格敏感型妈妈", new PersonaInfo("低", Arrays.asList(
            "{需求}哪里便宜", "想买实惠的{需求}", "{需求}有优惠吗"
        ), Arrays.asList("50元以内", "100元以内", "便宜点", "实惠的")));

        personas.put("社交分享型妈妈", new PersonaInfo("高", Arrays.asList(
            "求安利{需求}", "想试试{需求}", "{需求}怎么样"
        ), Arrays.asList("100元以内", "200元以内")));

        personas.put("谨慎保守型老人", new PersonaInfo("高", Arrays.asList(
            "找正规的{需求}", "{需求}可靠吗", "需要{需求}"
        ), Arrays.asList("50元以内", "100元以内", "实惠的")));

        personas.put("求助依赖型老人", new PersonaInfo("高", Arrays.asList(
            "帮帮忙找{需求}", "不会弄{需求}", "想{需求}怎么办"
        ), Arrays.asList("50元以内", "便宜的")));

        personas.put("潮流探索型 Z 世代", new PersonaInfo("中", Arrays.asList(
            "求安利{需求}", "想冲{需求}", "{需求}怎么样"
        ), Arrays.asList("100元以内", "200元以内", "性价比高的")));
    }

    private void initScenes() {
        scenes.put("医药健康", new SceneInfo(Arrays.asList(
            "退烧药", "感冒药", "过敏药", "益生菌", "维生素", "钙片", "口罩", "体温计"
        )));

        scenes.put("母婴用品", new SceneInfo(Arrays.asList(
            "奶粉", "纸尿裤", "辅食", "玩具", "童装", "婴儿车"
        )));

        scenes.put("餐饮外卖", new SceneInfo(Arrays.asList(
            "儿童餐", "营养餐", "辅食", "月子餐", "亲子餐厅", "外卖"
        )));

        scenes.put("教育早教", new SceneInfo(Arrays.asList(
            "早教中心", "托班", "兴趣班", "幼儿园", "亲子活动"
        )));

        scenes.put("生活服务", new SceneInfo(Arrays.asList(
            "保洁", "月嫂", "育儿嫂", "儿童摄影", "维修"
        )));

        scenes.put("休闲娱乐", new SceneInfo(Arrays.asList(
            "儿童乐园", "亲子游", "游泳馆", "绘本馆"
        )));

        scenes.put("社区服务", new SceneInfo(Arrays.asList(
            "社区医院", "老年食堂", "便民超市", "快递代收"
        )));

        scenes.put("便民生活", new SceneInfo(Arrays.asList(
            "缴费", "充值", "查询", "预约"
        )));

        scenes.put("新潮服务", new SceneInfo(Arrays.asList(
            "剧本杀", "密室", "VR", "电竞", "自拍馆", "猫咖"
        )));
    }

    // 内部类
    private static class PersonaInfo {
        String emotionLevel;
        List<String> patterns;
        List<String> priceRanges;

        PersonaInfo(String emotionLevel, List<String> patterns, List<String> priceRanges) {
            this.emotionLevel = emotionLevel;
            this.patterns = patterns;
            this.priceRanges = priceRanges;
        }
    }

    private static class SceneInfo {
        List<String> needs;

        SceneInfo(List<String> needs) {
            this.needs = needs;
        }
    }
}
