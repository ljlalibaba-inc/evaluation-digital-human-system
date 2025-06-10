package com.alibaba.example.baseknowledge.embedding;

import com.alibaba.whale.client.core.SDKFactory;
import com.alibaba.whale.client.protocol.LMResponse;
import com.alibaba.whale.client.protocol.TextGeneration;
import com.alibaba.whale.client.protocol.tokenizer.TokenizerRequest;
import com.alibaba.whale.client.protocol.tokenizer.TokenizerResult;
import lombok.extern.slf4j.Slf4j;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * @Author 灵盛
 * @create 2025/6/8 18:23
 */
@Slf4j
public class TokenizerEncodeDemo_qwen {
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
        TokenizerRequest request = new TokenizerRequest();
        request.setModel("bge_large_en_v15");
//        request.setModel("bge-m3-ft");
//        request.setPrompt("你是谁？");
        request.setPrompt("[\n" +
                "    {\n" +
                "      \"role\": \"user\",\n" +
                "      \"content\": \"你是谁\"\n" +
                "    }\n" +
                "  ]");
        request.setReturnOffsetsMapping(true);

        // 设置超时时间
        // 参考文档：https://aliyuque.antfin.com/gdorir/ahrwo0/kch0a4r11vge0h1m?singleDoc# 《超时时间控制》
        request.setTimeoutMs(60_000);

        // 请求LLM并打印结果
        TokenizerResult result = myClient.tokenizer(request).toCompletableFuture().join();

        if (result.isSuccess()) {
            log.info("data: {}", result.getResponse());
            log.info("token num: {}", result.getResponse().getTokenIds().size());

        } else {
            // 参考文档: https://aliyuque.antfin.com/gdorir/ahrwo0/nnn4oru407wl070o?singleDoc# 《错误状态码》
            //          https://aliyuque.antfin.com/gdorir/ahrwo0/tc2e94g9w7wh085l?singleDoc# 《如何通过Trace查看请求的详细信息？》
            log.error("data: {}", result.getResponse());
            log.error("error_msg: {}", result.getErrorMessage());
            log.error("error_code: {}", result.getErrorCode());
            log.error("trace_id: {}", result.getTraceId());
            log.error("request_id: {}", result.getRequestId());
        }
    }
}