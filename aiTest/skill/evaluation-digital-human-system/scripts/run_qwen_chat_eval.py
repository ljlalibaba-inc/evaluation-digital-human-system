#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 qwen_chat API 模式运行完整评测
"""

import os
import sys
import json
import time

# 切换到脚本所在目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from master_digital_human import MasterDigitalHuman, TaskConfig

def main():
    print("=" * 70)
    print("使用 Qwen Chat API 模式执行评测任务")
    print("=" * 70)

    # 初始化Master，使用 qwen_chat 模式
    master = MasterDigitalHuman()

    # 更新 Qwen Agent 配置为 qwen_chat 模式
    master.agents['qwen'].config = {
        'api_mode': 'qwen_chat',
        'model': 'quark-235b',
        'use_production': True
    }
    master.agents['qwen'].api_mode = 'qwen_chat'
    master.agents['qwen'].base_url = 'https://chat2.qianwen.com'
    master.agents['qwen'].model = 'quark-235b'

    print(f"\nAPI 配置:")
    print(f"  API Mode: {master.agents['qwen'].api_mode}")
    print(f"  Base URL: {master.agents['qwen'].base_url}")
    print(f"  Model: {master.agents['qwen'].model}")

    # 创建任务配置
    config = TaskConfig(
        name="Qwen Chat API 评测任务",
        target_model="quark-235b",
        scope={
            "personas": ["P1", "P2"],
            "scenarios": ["S1", "S2"],
            "categories": ["C5", "C4"]
        },
        cases_per_combination=2,
        dimensions=["accuracy", "timeliness", "personalization", "safety"],
        parallel=False,
        batch_size=5,
        delay_ms=500
    )

    # 提交任务
    print("\n提交评测任务...")
    execution = master.submit_task(config)
    print(f"任务ID: {execution.execution_id}")

    # 等待任务完成
    print("\n等待任务执行完成...")
    max_wait = 600  # 最多等待10分钟
    waited = 0

    while execution.status.value == "running" and waited < max_wait:
        time.sleep(2)
        waited += 2

        # 打印进度
        if execution.stages:
            current_stage = execution.stages[-1]
            if waited % 10 == 0:  # 每10秒打印一次
                print(f"  [{waited}s] 当前阶段: {current_stage.name}, 状态: {current_stage.status.value}")
                if current_stage.progress:
                    print(f"  进度: {current_stage.progress}")

    # 检查结果
    if execution.status.value == "completed":
        print("\n评测任务完成!")

        # 生成报告
        report = master.generate_report(execution.execution_id)

        # 打印摘要
        summary = report["execution_summary"]
        print("\n评测报告摘要:")
        print(f"  任务名称: {summary['task_config']['name']}")
        print(f"  执行状态: {summary['status']}")
        print(f"  执行时长: {summary.get('duration_seconds', 0):.2f}秒")

        if summary.get('results_summary'):
            rs = summary['results_summary']
            print(f"\n评测结果:")
            print(f"  总评测数: {rs.get('total_evaluated', 0)}")
            print(f"  平均分: {rs.get('average_score', 0):.2f}")
            print(f"  通过数: {rs.get('pass_count', 0)}")

        # 保存JSON报告
        report_path = f"report_{execution.execution_id}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\nJSON报告已保存: {report_path}")

        # 生成HTML报告
        try:
            print("\n生成HTML报告...")
            from generate_detailed_report import DetailedReportGenerator
            generator = DetailedReportGenerator(report_path)
            html = generator.generate_html()
            html_path = f"report_{execution.execution_id}.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"HTML报告已生成: {html_path}")
        except Exception as e:
            print(f"HTML报告生成失败: {e}")

    elif execution.status.value == "failed":
        print(f"\n评测任务失败!")
        print(f"错误: {execution.errors}")
        sys.exit(1)
    else:
        print(f"\n任务状态: {execution.status.value}")
        print(f"等待超时，当前状态: {execution.status.value}")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("执行完成!")
    print("=" * 70)

if __name__ == "__main__":
    main()
