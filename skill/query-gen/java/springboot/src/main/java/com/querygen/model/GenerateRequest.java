package com.querygen.model;

/**
 * 生成请求模型
 */
public class GenerateRequest {
    private String persona = "新手焦虑型妈妈";
    private String scene = "医药健康";
    private int count = 1;

    public GenerateRequest() {}

    public GenerateRequest(String persona, String scene, int count) {
        this.persona = persona;
        this.scene = scene;
        this.count = count;
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
