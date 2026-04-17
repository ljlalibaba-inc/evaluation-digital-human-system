#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速评测测试 - 验证评测结果保存功能
"""

import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.eval_agent import SearchEvalAgent
from agents.qwen_agent import QwenAgent

def test_evaluation_with_save():
    """测试评测并保存结果"""

    print("=" * 70)
    print("快速评测测试 - 验证评测结果保存")
    print("=" * 70)

    # 初始化评测Agent
    eval_config = {
        'evaluation': {
            'use_llm': True,
            'llm_model': 'qwen-plus'  # 使用DashScope支持的模型
        }
    }

    eval_agent = SearchEvalAgent(eval_config)

    # 模拟查询和响应数据
    test_cases = [
        {
            "query_id": "P1_S1_C5_001",
            "query_text": "我是一个忙碌的白领，最近加班特别多，感觉有点感冒了，想买点感冒药",
            "persona": "P1_忙碌的年轻白领",
            "scenario": "S1_应急补给",
            "category": "C5_医药健康",
            "tags": ["P1", "S1", "C5"]
        },
        {
            "query_id": "P2_S1_C4_001",
            "query_text": "我是一个新手妈妈，宝宝突然发烧了，家里没有退烧药了",
            "persona": "P2_新手妈妈",
            "scenario": "S1_应急补给",
            "category": "C4_母婴用品",
            "tags": ["P2", "S1", "C4"]
        }
    ]

    # 模拟响应数据
    mock_responses = [
        {
            "content": "我理解您感冒了需要买药。根据您的需求，我推荐以下药品：\n\n1. 感冒灵颗粒 - 适合缓解感冒症状\n2. 维生素C泡腾片 - 增强免疫力\n\n请注意：用药前请咨询医生或药师，按照说明书服用。",
            "data": {
                "structured_items": [
                    {"itemName": "感冒灵颗粒", "shopName": "大药房", "price": "15.9", "llmRelevantLevelScore": 4.5},
                    {"itemName": "维生素C泡腾片", "shopName": "健康药店", "price": "28.0", "llmRelevantLevelScore": 4.0}
                ],
                "time_commitment": "30分钟送达",
                "personalization_elements": ["针对忙碌白领"],
                "safety_warnings": ["请咨询医生"]
            }
        },
        {
            "content": "宝宝发烧需要及时处理。我为您找到以下商品：\n\n1. 儿童退烧贴 - 物理降温\n2. 婴儿退烧药 - 适合3个月以上宝宝\n\n重要提示：如果宝宝持续高烧，请立即就医。",
            "data": {
                "structured_items": [
                    {"itemName": "儿童退烧贴", "shopName": "母婴店", "price": "35.0", "llmRelevantLevelScore": 4.8},
                    {"itemName": "婴儿退烧药", "shopName": "大药房", "price": "42.5", "llmRelevantLevelScore": 4.5}
                ],
                "time_commitment": "30分钟送达",
                "personalization_elements": ["针对新手妈妈"],
                "safety_warnings": ["持续高烧请就医"]
            }
        }
    ]

    # 执行评测
    print("\n[评测] 开始执行评测...")
    evaluations = []
    dimensions = ["accuracy", "timeliness", "personalization", "safety"]

    for i, (query, response) in enumerate(zip(test_cases, mock_responses)):
        print(f"\n[评测] 评测用例 {i+1}/{len(test_cases)}: {query['query_id']}")
        print(f"[评测] Query: {query['query_text'][:50]}...")

        try:
            eval_result = eval_agent.evaluate(
                query=query,
                response=response,
                dimensions=dimensions
            )
            evaluations.append(eval_result)

            print(f"[评测] 总分: {eval_result.get('overall_score', 0)}")
            print(f"[评测] 模式: {eval_result.get('evaluation_mode', 'unknown')}")
            if eval_result.get('issues'):
                print(f"[评测] 问题: {len(eval_result['issues'])}个")
            if eval_result.get('suggestions'):
                print(f"[评测] 建议: {len(eval_result['suggestions'])}条")

        except Exception as e:
            print(f"[评测] 错误: {e}")
            evaluations.append({"error": str(e)})

    # 保存评测结果
    print("\n[保存] 保存评测结果...")
    execution_id = f"quick_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    results_dir = "./results"
    os.makedirs(results_dir, exist_ok=True)

    save_data = {
        "execution_id": execution_id,
        "saved_at": datetime.now().isoformat(),
        "total_evaluations": len(evaluations),
        "evaluations": evaluations
    }

    filepath = os.path.join(results_dir, f"evaluation_results_{execution_id}.json")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)

    print(f"[保存] ✓ 评测结果已保存: {filepath}")

    # 显示汇总
    print("\n" + "=" * 70)
    print("评测汇总")
    print("=" * 70)

    valid_evals = [e for e in evaluations if 'overall_score' in e]
    if valid_evals:
        avg_score = sum(e['overall_score'] for e in valid_evals) / len(valid_evals)
        pass_count = sum(1 for e in valid_evals if e['overall_score'] >= 4.0)

        print(f"总评测数: {len(evaluations)}")
        print(f"有效评测: {len(valid_evals)}")
        print(f"平均分: {avg_score:.2f}")
        print(f"通过数 (>=4.0): {pass_count}")

        print("\n详细评分:")
        for eval_item in valid_evals:
            print(f"  {eval_item.get('query_id', 'unknown')}: {eval_item['overall_score']}")
            if eval_item.get('scores'):
                for dim, score in eval_item['scores'].items():
                    print(f"    - {dim}: {score}")

    return filepath

if __name__ == "__main__":
    filepath = test_evaluation_with_save()
    print(f"\n评测结果文件: {filepath}")
