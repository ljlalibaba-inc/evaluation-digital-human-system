package com.alibaba.example.baseknowledge.model;

import com.alibaba.example.baseknowledge.model.WhaleChatMessage ;
import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import com.alibaba.whale.client.core.SDKFactory;
import com.alibaba.whale.client.protocol.LMResponse;
import com.alibaba.whale.client.protocol.Output;
import com.alibaba.whale.client.protocol.TextGeneration;
import com.alibaba.whale.client.protocol.chat.ChatMessage;
import com.alibaba.whale.client.protocol.chat.ChatRequest;
import com.alibaba.whale.client.protocol.chat.ChatResult;

import java.util.HashMap;
import java.util.List;
import java.util.concurrent.ForkJoinPool;
import java.util.stream.Collectors;

/**
 * @Author 灵盛
 * @create 2025/6/7 4:40 PM
 * 最基础的chat调用
 */
public class LLMChatTextDemo_Qwen2_5 {

    public String Qwen2_5() {
        // 初始化client
        SDKFactory.TextGenerationConfig config = new SDKFactory.TextGenerationConfig();
        String LLMApiKey = "H94D1Y1YAF";
        config.setExecutorService(ForkJoinPool.commonPool());
        config.setApiKey(LLMApiKey);
        // 线上或预发环境无需设置ServiceLocation, 本地测试或日常环境需设置serviceLocator为https://whale-wave.alibaba-inc.com
        config.setServiceLocator(() -> "https://whale-wave.alibaba-inc.com");
        TextGeneration<LMResponse> myClient = SDKFactory.defaultTextGeneration(config);

        // 构造request, 若需要使用chatapi格式, 可构建com.alibaba.whale.client.protocol.LMChatApiRequest
        // 参考文档：https://aliyuque.antfin.com/gdorir/ahrwo0/cc2opobdstl8f4wi?singleDoc# 《request_format》
        ChatRequest chatRequest = new ChatRequest();
        chatRequest.setOutputType(Output.FULL_TEXT);
        chatRequest.setStream(false);
        // 模型名
        String LLMModel = "Qwen-72B-Chat-Latest";
        chatRequest.setModel(LLMModel);
        chatRequest.setTimeoutMs(300 * 1000);
        String prompt = "[{\"role\":\"user\",\"content\":\"你是谁\"}]";
        System.out.println("prompt: " + prompt);
        JSONArray promptArray = JSONObject.parseArray(prompt);
        List<WhaleChatMessage> messageList = promptArray.toJavaList(WhaleChatMessage.class);
        chatRequest.setMessages(messageList.stream().map(e -> new ChatMessage(e.getRole(), e.getContent())).collect(Collectors.toList()));

        // 设置generateConfig
        // 支持将非标准的控制参数传递给后端服务，例如max_new_tokens，top_k, 参考文档：https://aliyuque.antfin.com/gdorir/ahrwo0/xgvt7ckyxqli6iq7?singleDoc#《generate_config》
        HashMap<String, Object> generateConfig = new HashMap<String, Object>(4) {{
            put("max_new_tokens", 200);
            put("top_p", 0.8);
            put("temperature", 1.0);
            put("top_k", 0);
        }};
        generateConfig.put("request_format", "chatapi");
        chatRequest.setExtendFields(generateConfig);

        // 请求LLM并打印结果
        ChatResult chatResult = myClient.chat(chatRequest).toCompletableFuture().join();
        // 结果信息即错误码查看，
        // 参考文档: https://aliyuque.antfin.com/gdorir/ahrwo0/nnn4oru407wl070o?singleDoc# 《错误状态码》
        //          https://aliyuque.antfin.com/gdorir/ahrwo0/tc2e94g9w7wh085l?singleDoc# 《如何通过Trace查看请求的详细信息？》
        System.out.println("模型调用结果为: " + JSONObject.toJSONString(chatResult));
        // 因为现在whale错误码混乱，非200也能拿到返回结果，拿到结果就返回，否则继续调下一个模型
        String finalResponse = "";
        try {
            finalResponse = JSONObject.toJSONString(chatResult.getResponse().getChoices().get(0).getMessage());
        } catch (Exception e) {
            System.out.println(e);
        }
        return finalResponse;
    }

    public static void main(String[] args) {
        LLMChatTextDemo_Qwen2_5 qwen2_5 = new LLMChatTextDemo_Qwen2_5();
        System.out.println(qwen2_5.Qwen2_5());

    }
}
