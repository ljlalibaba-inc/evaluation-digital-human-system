#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Query Generator 简单演示
"""

from query_generator import QueryGenerator

# 创建生成器
generator = QueryGenerator()

print("=" * 60)
print("Query Generator 演示")
print("=" * 60)

# 示例 1: 新手焦虑型妈妈 + 医疗健康场景
print("\n【示例 1】新手焦虑型妈妈 - 医疗健康")
result = generator.generate_single("新手焦虑型妈妈", "医疗健康")
print(f"Query: {result.query}")
print(f"意图：{result.intent}")
print(f"复杂度：{result.complexity}")

# 示例 2: 谨慎保守型老人 + 生活服务场景
print("\n【示例 2】谨慎保守型老人 - 生活服务")
result = generator.generate_single("谨慎保守型老人", "生活服务")
print(f"Query: {result.query}")
print(f"意图：{result.intent}")
print(f"复杂度：{result.complexity}")

# 示例 3: 潮流探索型 Z 世代 + 休闲娱乐
print("\n【示例 3】潮流探索型 Z 世代 - 休闲娱乐")
z_gen_key = list(generator.personas.keys())[7]  # 潮流探索型 Z 世代
result = generator.generate_single(z_gen_key, "休闲娱乐")
print(f"Query: {result.query}")
print(f"意图：{result.intent}")
print(f"复杂度：{result.complexity}")

# 示例 4: 批量生成
print("\n【示例 4】批量生成 (效率实用型妈妈 - 餐饮外卖，5 条)")
results = generator.generate_batch("效率实用型妈妈", "餐饮外卖", 5)
for i, result in enumerate(results, 1):
    print(f"{i}. {result.query}")

# 示例 5: 多人群对比
print("\n【示例 5】多人群对比测试 (教育早教场景)")
personas = ["新手焦虑型妈妈", "品质追求型妈妈", "价格敏感型妈妈"]
multi_results = generator.generate_multi_persona(personas, "教育早教", 2)
for persona_name, results in multi_results.items():
    print(f"\n{persona_name}:")
    for result in results:
        print(f"  - {result.query}")

print("\n" + "=" * 60)
print("演示完成!")
print("=" * 60)
