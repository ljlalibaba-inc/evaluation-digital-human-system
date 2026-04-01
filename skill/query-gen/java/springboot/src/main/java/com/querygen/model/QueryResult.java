package com.querygen.model;

import java.util.List;
import java.util.Map;

/**
 * Query 结果模型
 */
public class QueryResult {
    private String query;
    private String persona;
    private String scene;
    private String intent;
    private String complexity;
    private String emotionLevel;
    private List<String> expectedFocus;
    private Map<String, Object> context;

    public QueryResult() {}

    public QueryResult(String query, String persona, String scene, String intent,
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

    public String getQuery() {
        return query;
    }

    public void setQuery(String query) {
        this.query = query;
    }

    public String getPersona() {
        return persona;
    }

    public void setPersona(String persona) {
        this.persona = persona;
    }

    public String getScene() {
        return scene;
    }

    public void setScene(String scene) {
        this.scene = scene;
    }

    public String getIntent() {
        return intent;
    }

    public void setIntent(String intent) {
        this.intent = intent;
    }

    public String getComplexity() {
        return complexity;
    }

    public void setComplexity(String complexity) {
        this.complexity = complexity;
    }

    public String getEmotionLevel() {
        return emotionLevel;
    }

    public void setEmotionLevel(String emotionLevel) {
        this.emotionLevel = emotionLevel;
    }

    public List<String> getExpectedFocus() {
        return expectedFocus;
    }

    public void setExpectedFocus(List<String> expectedFocus) {
        this.expectedFocus = expectedFocus;
    }

    public Map<String, Object> getContext() {
        return context;
    }

    public void setContext(Map<String, Object> context) {
        this.context = context;
    }
}
