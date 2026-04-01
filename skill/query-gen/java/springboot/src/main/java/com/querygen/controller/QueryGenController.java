package com.querygen.controller;

import com.querygen.model.GenerateRequest;
import com.querygen.model.GenerateResponse;
import com.querygen.model.QueryResult;
import com.querygen.service.QueryGenService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * Query Generator REST Controller
 */
@RestController
@RequestMapping("/")
@CrossOrigin(origins = "*")
public class QueryGenController {

    @Autowired
    private QueryGenService queryGenService;

    @GetMapping("/")
    public Map<String, Object> root() {
        return Map.of(
            "service", "Query Generator Java API",
            "version", "2.0.0",
            "endpoints", Map.of(
                "personas", "/personas",
                "scenes", "/scenes",
                "generate", "/generate"
            )
        );
    }

    @GetMapping("/health")
    public Map<String, Object> health() {
        return Map.of(
            "success", true,
            "status", "healthy",
            "service", "query-gen-java-api"
        );
    }

    @GetMapping("/personas")
    public Map<String, Object> getPersonas() {
        Set<String> personas = queryGenService.getAllPersonaNames();
        return Map.of(
            "success", true,
            "data", personas,
            "count", personas.size(),
            "descriptions", Map.of(
                "新手焦虑型妈妈", "0-1岁宝宝，第一胎，谨慎焦虑",
                "效率实用型妈妈", "职场妈妈，时间碎片化，追求效率",
                "品质追求型妈妈", "经济条件好，注重品质和体验",
                "价格敏感型妈妈", "精打细算，关注性价比",
                "社交分享型妈妈", "爱新鲜事物，爱分享，跟风",
                "谨慎保守型老人", "60岁+，数字素养低，害怕被骗",
                "求助依赖型老人", "不熟悉操作，习惯求助",
                "潮流探索型 Z 世代", "18-25岁，追新潮，注重体验"
            )
        );
    }

    @GetMapping("/scenes")
    public Map<String, Object> getScenes() {
        Set<String> scenes = queryGenService.getAllSceneNames();
        return Map.of(
            "success", true,
            "data", scenes,
            "count", scenes.size()
        );
    }

    @GetMapping("/generate")
    public GenerateResponse generateGet(
            @RequestParam(defaultValue = "新手焦虑型妈妈") String persona,
            @RequestParam(defaultValue = "医药健康") String scene,
            @RequestParam(defaultValue = "1") int count) {

        List<QueryResult> queries = queryGenService.generateBatch(persona, scene, count);
        return new GenerateResponse(true, queries, persona, scene, queries.size());
    }

    @PostMapping("/generate")
    public GenerateResponse generatePost(@RequestBody GenerateRequest request) {
        List<QueryResult> queries = queryGenService.generateBatch(
            request.getPersona(),
            request.getScene(),
            request.getCount()
        );
        return new GenerateResponse(true, queries, request.getPersona(), request.getScene(), queries.size());
    }

    @PostMapping("/generate/multi")
    public Map<String, Object> generateMulti(@RequestBody Map<String, Object> request) {
        @SuppressWarnings("unchecked")
        List<String> personas = (List<String>) request.get("personas");
        String scene = (String) request.getOrDefault("scene", "医药健康");
        int countPerPersona = (int) request.getOrDefault("count_per_persona", 5);

        Map<String, List<QueryResult>> results = queryGenService.generateMultiPersona(
            personas, scene, countPerPersona
        );

        return Map.of(
            "success", true,
            "data", results,
            "scene", scene,
            "count_per_persona", countPerPersona
        );
    }
}
