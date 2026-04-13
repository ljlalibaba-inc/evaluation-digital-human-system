#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 qwen_chat API 模式（使用用户提供的 curl 参数）
"""

import sys
import os

# 切换到脚本所在目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from agents.qwen_agent import QwenAgent

def main():
    print("=" * 70)
    print("测试 Qwen Chat API 模式")
    print("=" * 70)

    # 使用 qwen_chat 模式（使用您提供的 curl 参数）
    agent = QwenAgent({
        'api_mode': 'qwen_chat',
        'model': 'quark-235b'
    })

    print(f"\nAPI 配置:")
    print(f"  API Mode: {agent.api_mode}")
    print(f"  Base URL: {agent.base_url}")
    print(f"  Model: {agent.model}")
    print(f"  X-Sign: {agent.x_sign[:40]}...")
    print(f"  X-Wpk-Reqid: {agent.wpk_reqid}")

    # 测试调用
    print("\n发送测试请求: '帮忙下单可口可乐'")
    print("-" * 70)

    result = agent.call('帮忙下单可口可乐')

    print(f"\n响应结果:")
    print(f"  Success: {result['success']}")
    print(f"  Response Time: {result['response_time_ms']}ms")

    if result['success']:
        print(f"\n  Content:")
        print(f"  {result['content'][:500]}...")
    else:
        print(f"\n  Error: {result.get('error', 'Unknown error')}")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
