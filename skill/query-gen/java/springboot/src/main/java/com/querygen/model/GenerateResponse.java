package com.querygen.model;

import java.util.List;

/**
 * 生成响应模型
 */
public class GenerateResponse {
    private boolean success;
    private List<QueryResult> data;
    private String persona;
    private String scene;
    private int count;

    public GenerateResponse() {}

    public GenerateResponse(boolean success, List<QueryResult> data, String persona, String scene, int count) {
        this.success = success;
        this.data = data;
        this.persona = persona;
        this.scene = scene;
        this.count = count;
    }

    public boolean isSuccess() {
        return success;
    }

    public void setSuccess(boolean success) {
        this.success = success;
    }

    public List<QueryResult> getData() {
        return data;
    }

    public void setData(List<QueryResult> data) {
        this.data = data;
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

    public int getCount() {
        return count;
    }

    public void setCount(int count) {
        this.count = count;
    }
}
