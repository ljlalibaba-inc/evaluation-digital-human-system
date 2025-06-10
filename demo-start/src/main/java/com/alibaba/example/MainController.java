package com.alibaba.example;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ResponseBody;

/**
 * Spring Mvc的根路径、健康检查等。
 */
@Controller
public class MainController {

    /**
     * 健康检查，系统部署需要
     * 请不要删除！！
     */
    @GetMapping("/checkpreload.htm")
    public @ResponseBody String checkPreload() {
        return "success";
    }

    @GetMapping("/")
    public String index(){
        return "index.html";
    }





}

