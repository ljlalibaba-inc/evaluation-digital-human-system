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
import java.util.stream.Stream;

/**
 * @Author 灵盛
 * @create 2025/6/8 16:49
 */
@Slf4j
public class LLMReasoningChatStreamDemo_DSR1 {
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
        request.setModel("DeepSeek-R1");
        List<ChatMessage> messages = new ArrayList<ChatMessage>(2) {{
            add(new ChatSystemMessage("You are a helpful assistant."));
            add(new ChatUserTextMessage("你好。"));
        }};
        request.setMessages(messages);
        request.setStream(true);

        // 控制参数
        request.setMaxTokens(4000);
        request.setTemperature(0.8);
        request.setTopP(1.0);
        request.setFrequencyPenalty(1.0);
        request.setPresencePenalty(1.0);

        // 设置超时时间
        // 参考文档：https://aliyuque.antfin.com/gdorir/ahrwo0/kch0a4r11vge0h1m?singleDoc# 《超时时间控制》
        request.setTimeoutMs(60_000);
        request.setPerEventTimeoutMs(20_000);

        // 设置扩展字段
        // 支持设置用户自定义参数，记录在pvLog中
        // 支持将非标准的控制参数传递给后端服务，例如max_new_tokens，top_k, 参考文档：https://aliyuque.antfin.com/gdorir/ahrwo0/xgvt7ckyxqli6iq7?singleDoc#
        // 《generate_config》
        Map<String, Object> extendFields = new HashMap<String, Object>(4) {{
            put("top_k", 1);
        }};
        request.setExtendFields(extendFields);

        // 请求LLM并打印结果
        ChatStreamResult streamResult = myClient.chatStream(request).toCompletableFuture().join();
        Stream<ChatResponse> stream = streamResult.blockingStream();

        stream.forEach(chatResponse -> {

            if (chatResponse.getErrorCode() != null && !chatResponse.getErrorCode().equals(200)) {
                // 参考文档: https://aliyuque.antfin.com/gdorir/ahrwo0/nnn4oru407wl070o?singleDoc# 《错误状态码》
                //          https://aliyuque.antfin.com/gdorir/ahrwo0/tc2e94g9w7wh085l?singleDoc# 《如何通过Trace查看请求的详细信息？》
                log.error("response: {}", chatResponse);
                log.error("error_msg: {}", chatResponse.getMessage());
                log.error("error_code: {}", chatResponse.getErrorCode());
                log.error("trace_id: {}", chatResponse.getExtendFields().get("traceId"));
                log.error("request_id: {}", chatResponse.getExtendFields().get("requestId"));
            } else {
                log.info("response: {}", chatResponse.getChoices().get(0).getDelta().getContent());
//                log.info("response: {}", chatResponse.getChoices().get(0).getDelta().getFunctionCall());
            }
        });
    }
}
