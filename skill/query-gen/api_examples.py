#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Query Generator API 调用示例
展示了如何使用 HTTP API 调用 query-gen skill
"""

import requests
import json

# API 基础地址
BASE_URL = "http://localhost:5000"


def example_1_basic_generate():
    """示例1: 基础生成 - 单个 query"""
    print("=" * 60)
    print("示例1: 基础生成")
    print("=" * 60)

    # GET 方式
    response = requests.get(
        f"{BASE_URL}/generate",
        params={
            "persona": "新手焦虑型妈妈",
            "scene": "医药健康",
            "count": 3
        }
    )
    data = response.json()
    print(f"状态: {'成功' if data['success'] else '失败'}")
    print(f"人设: {data['persona']}")
    print(f"场景: {data['scene']}")
    print("\n生成的 Query:")
    for i, item in enumerate(data['data'], 1):
        print(f"  {i}. {item['query']}")
        print(f"     意图: {item['intent']}, 复杂度: {item['complexity']}")
    print()


def example_2_post_generate():
    """示例2: POST 方式生成"""
    print("=" * 60)
    print("示例2: POST 方式生成")
    print("=" * 60)

    response = requests.post(
        f"{BASE_URL}/generate",
        json={
            "persona": "价格敏感型妈妈",
            "scene": "母婴用品",
            "count": 5
        }
    )
    data = response.json()
    print(f"生成 {data['count']} 条 Query:")
    for item in data['data']:
        print(f"  - {item['query']}")
    print()


def example_3_multi_persona():
    """示例3: 多人群对比"""
    print("=" * 60)
    print("示例3: 多人群对比")
    print("=" * 60)

    response = requests.post(
        f"{BASE_URL}/generate/multi",
        json={
            "personas": ["新手焦虑型妈妈", "效率实用型妈妈", "价格敏感型妈妈"],
            "scene": "医药健康",
            "count_per_persona": 3
        }
    )
    data = response.json()
    for persona, queries in data['data'].items():
        print(f"\n【{persona}】")
        for item in queries:
            print(f"  - {item['query']}")
    print()


def example_4_get_metadata():
    """示例4: 获取元数据"""
    print("=" * 60)
    print("示例4: 获取元数据")
    print("=" * 60)

    # 获取所有人设
    response = requests.get(f"{BASE_URL}/personas")
    personas = response.json()
    print(f"支持的人设 ({personas['count']}个):")
    for p in personas['data']:
        desc = personas.get('descriptions', {}).get(p, '')
        print(f"  - {p}: {desc}")

    # 获取所有场景
    response = requests.get(f"{BASE_URL}/scenes")
    scenes = response.json()
    print(f"\n支持的场景 ({scenes['count']}个):")
    for s in scenes['data']:
        print(f"  - {s}")
    print()


def example_5_different_scenes():
    """示例5: 不同场景生成"""
    print("=" * 60)
    print("示例5: 不同场景生成")
    print("=" * 60)

    scenes = ["医药健康", "母婴用品", "餐饮外卖", "教育早教"]
    persona = "新手焦虑型妈妈"

    for scene in scenes:
        response = requests.get(
            f"{BASE_URL}/generate",
            params={"persona": persona, "scene": scene, "count": 2}
        )
        data = response.json()
        print(f"\n【{scene}】")
        for item in data['data']:
            print(f"  - {item['query']}")
    print()


def example_6_error_handling():
    """示例6: 错误处理"""
    print("=" * 60)
    print("示例6: 错误处理")
    print("=" * 60)

    # 错误的人设名称
    response = requests.get(
        f"{BASE_URL}/generate",
        params={"persona": "不存在的人设", "scene": "医药健康"}
    )
    print(f"错误请求状态码: {response.status_code}")
    print(f"错误信息: {response.json().get('detail', '未知错误')}")
    print()


def example_7_health_check():
    """示例7: 健康检查"""
    print("=" * 60)
    print("示例7: 健康检查")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/health")
    print(f"健康状态: {response.json()}")
    print()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Query Generator API 调用示例")
    print(f"API 地址: {BASE_URL}")
    print("=" * 60 + "\n")

    try:
        # 运行所有示例
        example_7_health_check()
        example_4_get_metadata()
        example_1_basic_generate()
        example_2_post_generate()
        example_3_multi_persona()
        example_5_different_scenes()
        example_6_error_handling()

    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到 API 服务器")
        print(f"请确保服务器已启动: python api_server.py 或 python api_fastapi.py")
        print()
