package com.alibaba.example.baseknowledge.model;

import com.alibaba.whale.client.core.SDKFactory;
import com.alibaba.whale.client.protocol.LMResponse;
import com.alibaba.whale.client.protocol.TextGeneration;
import com.alibaba.whale.client.protocol.chat.*;
import lombok.extern.slf4j.Slf4j;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * @Author 灵盛
 * @create 2025/6/8 18:10
 */
@Slf4j
public class LLMRichMediaDemo_DSQW {
    public static void main(String[] args) {
        // 初始化client
        SDKFactory.TextGenerationConfig config = new SDKFactory.TextGenerationConfig();
        config.setApiKey("H94D1Y1YAF");

        // 按需修改线程池配置
        ExecutorService executorService = Executors.newCachedThreadPool();
        config.setExecutorService(executorService);

        // 显示指定后端服务endpoint，仅用于本地测试，线上可不用设置不建议使用，因为该方法会直接显式固定后端服务的domain，使得无法在处理容灾情况时动态切换后端服务的Domain
        // 本地测试无法访问Vipserver, 因此本地测试需要显式指定serviceLocator为 https://whale-wave.alibaba-inc.com
        config.setServiceLocator(() -> "https://whale-wave.alibaba-inc.com");

        TextGeneration<LMResponse> myClient = SDKFactory.defaultTextGeneration(config);

        // 构造request
        ChatRequest request = new ChatRequest();
        request.setModel("Qwen2.5-VL-7B-Instruct");
//        request.setModel("deepseek-vl2");
        request.setStream(false);

        ChatImageURL chatImageURL = new ChatImageURL();
        chatImageURL.setUrl("https://www.baidu.com/img/baidu_sylogo1.gif");
        List<ChatMediaContent> chatMediaContents = new ArrayList<ChatMediaContent>(1) {{
            add(new ChatMediaContent("image_url", chatImageURL));
            add(new ChatMediaContent("text", "描述这个图片，用中文回答"));
        }};

        List<ChatMessage> messages = new ArrayList<ChatMessage>(2) {{
            add(new ChatSystemMessage("你是一个人工智能，可以理解图片的内容并描述。"));
            add(new ChatUserMediaMessage(chatMediaContents));
        }};
        request.setMessages(messages);

        // 控制参数
        request.setMaxTokens(1000);
        request.setTemperature(1.0);
        request.setTopP(0.8);

        // 设置超时时间
        // 参考文档：https://aliyuque.antfin.com/gdorir/ahrwo0/kch0a4r11vge0h1m?singleDoc# 《超时时间控制》
        request.setTimeoutMs(60_000);

        // 设置扩展字段
        // 支持设置用户自定义参数，记录在pvLog中
        // 支持将非标准的控制参数传递给后端服务，例如max_new_tokens，top_k, 参考文档：https://aliyuque.antfin.com/gdorir/ahrwo0/xgvt7ckyxqli6iq7?singleDoc#
        // 《generate_config》
        Map<String, Object> extendFields = new HashMap<String, Object>(4) { };
        request.setExtendFields(extendFields);

        // 请求LLM并打印结果
        ChatResult chatResult = myClient.chat(request).toCompletableFuture().join();

        if (chatResult.isSuccess()) {
            log.info("response: {}", chatResult.getResponse());
        } else {
            log.error("response: {}", chatResult.getResponse());
            log.error("error_msg: {}", chatResult.getErrorMessage());
            log.error("error_code: {}", chatResult.getErrorCode());
            log.error("trace_id: {}", chatResult.getTraceId());
            log.error("request_id: {}", chatResult.getRequestId());
        }
    }
}
