#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试特定 Query: 帮忙下单可口可乐
"""

import os
import sys
import json

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from agents.qwen_agent import QwenAgent
from agents.eval_agent import SearchEvalAgent


def main():
    print("=" * 70)
    print("测试 Query: 帮忙下单可口可乐")
    print("=" * 70)

    # 初始化 Agent
    config = {
        'api_mode': 'qwen_chat',
        'use_production': True
    }
    agent = QwenAgent(config)

    # 构建测试用例
    test_case = {
        "query_id": "test_coke_001",
        "query_text": "帮忙下单可口可乐",
        "persona": {
            "id": "P1",
            "name": "忙碌的年轻白领",
            "description": "工作繁忙，经常加班，时间紧张"
        },
        "scenario": {
            "id": "S2",
            "name": "即时享受",
            "description": "想要快速获得商品，享受即时满足"
        },
        "category": {
            "id": "C2",
            "name": "休闲零售",
            "description": "零食饮料等休闲食品"
        }
    }

    print("\n--- 测试用例信息 ---")
    print(f"Query: {test_case['query_text']}")
    print(f"人设: {test_case['persona']['name']}")
    print(f"场景: {test_case['scenario']['name']}")
    print(f"品类: {test_case['category']['name']}")

    # 调用千问接口（传入位置信息）
    print("\n--- 调用千问接口 ---")
    location_value = "OjXQtFFvLVxCMGjtmzqsHukhbBzSFPUTBhnMW6ESWx0Xg4lMBneYMkWPTRbb1P5SgePoDrH30F4tag7ZVvta54EPno2z70Y0bgirylSMG7G2RUgixokCMljvGvWD75p+LNrQC8PpURqgvMnPj5kqFDQa3TihFvZ9JXtWE76fANbYV07zuAgay7jW6hCwwrbY+xNzjPqFLQMxSgP5Jx6UKMmogBc81h9Ek6poiSthbsM8c78KxwIKtvbNq84oSOA5OyOqdbA82zJi5/p8ALLoYcf1cAHOGOdVH/19yhGVs7v5d4qK9Pb5C+X5iqanzX0jFW1q8leAjHrHW8DBrDosvzhNxQEicNK7D0xfjzKLrnnrAIe26pSaezpzFRxoIjXZ0ha2IGEgqbLsIm5IQMFA6+nOqnq/2DsNCa8q9QoHfIEbJL8ZA/lBEekUgddXhU0IP+gCbEIAHJ3FD2xezuy7KKrzLISFT0H0/ahsxxt/mi44YflMywq7ng7+mUD5HsFZUjW8MsAi+mLkJG9Fe7KAuS7apvxKFFlxuqLsGdE+i72FJbWDPUgHohItdGr70erVVx4wIDT5zXANWxwB57zsm0nY"
    result = agent.call(test_case['query_text'], address=location_value)

    print(f"Success: {result['success']}")
    print(f"Response Time: {result['response_time_ms']}ms")

    if not result['success']:
        print(f"Error: {result.get('error', 'Unknown error')}")
        return

    # 获取请求信息
    request_info = result.get('request_info', {})
    print(f"\n--- 请求信息 ---")
    print(f"URL: {request_info.get('url', 'N/A')[:100]}...")
    print(f"Model: {request_info.get('model', 'N/A')}")

    # 解析响应
    raw_response = result.get('raw_response', {})
    raw_lines = raw_response.get('raw_lines', [])
    print(f"\n--- 响应信息 ---")
    print(f"Response Lines: {len(raw_lines)}")

    # 提取各类消息
    messages_by_type = {}
    text_contents = []

    for line in raw_lines:
        try:
            data = json.loads(line)
            if 'data' in data and 'messages' in data['data']:
                for msg in data['data']['messages']:
                    mime_type = msg.get('mime_type', 'unknown')
                    if mime_type not in messages_by_type:
                        messages_by_type[mime_type] = []
                    messages_by_type[mime_type].append(msg)

                    if mime_type == 'text/plain' and msg.get('content'):
                        text_contents.append(msg['content'])
        except:
            pass

    print(f"\n--- 消息类型分布 ---")
    for mime_type, msgs in messages_by_type.items():
        print(f"  {mime_type}: {len(msgs)} 条")

    if text_contents:
        print(f"\n--- 文本响应内容 ---")
        for i, text in enumerate(text_contents):
            print(f"\n[{i+1}] {text}")

    # 进行评测
    print(f"\n--- 评测结果 ---")
    eval_agent = SearchEvalAgent()

    eval_result = eval_agent.evaluate(
        query=test_case,
        response=result,
        dimensions=["accuracy", "timeliness", "personalization"]
    )

    print(f"Overall Score: {eval_result.get('overall_score', 0):.2f}")
    print(f"Scores: {eval_result.get('scores', {})}")

    if eval_result.get('issues'):
        print(f"\nIssues:")
        for issue in eval_result['issues']:
            print(f"  - {issue}")

    if eval_result.get('suggestions'):
        print(f"\nSuggestions:")
        for suggestion in eval_result['suggestions']:
            print(f"  - {suggestion}")

    # 保存完整结果
    output = {
        "test_case": test_case,
        "request_info": request_info,
        "response": {
            "success": result['success'],
            "response_time_ms": result['response_time_ms'],
            "content": text_contents,
            "message_types": list(messages_by_type.keys())
        },
        "evaluation": eval_result
    }

    output_path = "test_coke_order_result.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n--- 结果已保存 ---")
    print(f"文件: {output_path}")

    print("\n" + "=" * 70)
    print("测试完成!")
    print("=" * 70)


if __name__ == "__main__":
    main()
