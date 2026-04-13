#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自定义 Query 评测执行脚本
测试特定 query: "帮忙下单可口可乐"
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
    print("开始执行自定义 Query 评测任务")
    print("Query: 帮忙下单可口可乐")
    print("=" * 70)

    # 初始化Master
    master = MasterDigitalHuman()

    # 创建任务配置 - 只测试特定 query
    config = TaskConfig(
        name="自定义Query评测-帮忙下单可口可乐",
        target_model="qwen-turbo",
        scope={
            "personas": ["P1"],  # 忙碌的年轻白领
            "scenarios": ["S2"],  # 即时享受
            "categories": ["C2"]  # 休闲零售
        },
        cases_per_combination=1,
        dimensions=["accuracy", "timeliness", "personalization"],
        parallel=False,
        batch_size=1,
        delay_ms=500
    )

    # 提交任务
    print("\n提交评测任务...")
    execution = master.submit_task(config)
    print(f"任务ID: {execution.execution_id}")

    # 等待任务完成
    print("\n等待任务执行完成...")
    max_wait = 300  # 最多等待5分钟
    waited = 0

    while execution.status.value == "running" and waited < max_wait:
        time.sleep(2)
        waited += 2

        # 打印进度
        if execution.stages:
            current_stage = execution.stages[-1]
            print(f"  当前阶段: {current_stage.name}, 状态: {current_stage.status.value}")
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
        report_path = f"report_custom_{execution.execution_id}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\nJSON报告已保存: {report_path}")

        # 尝试生成HTML报告
        try:
            print("\n生成HTML报告...")
            from generate_detailed_report import DetailedReportGenerator
            generator = DetailedReportGenerator(report_path)
            html = generator.generate_html()
            html_path = f"report_custom_{execution.execution_id}.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"HTML报告已生成: {html_path}")
        except Exception as e:
            print(f"HTML报告生成失败: {e}")

        # 打印详细的请求和响应信息
        print("\n" + "=" * 70)
        print("详细评测结果")
        print("=" * 70)

        responses = report.get('results', {}).get('responses', [])
        for i, item in enumerate(responses[:3]):  # 只显示前3条
            query = item.get('query', {})
            response = item.get('response', {})
            request_info = response.get('request_info', {})

            print(f"\n--- 评测项 {i+1} ---")
            print(f"Query: {query.get('query_text', 'N/A')}")
            print(f"URL: {request_info.get('url', 'N/A')[:80]}...")
            print(f"Response Time: {response.get('response_time_ms', 0)}ms")
            print(f"Success: {response.get('success', False)}")

            # 显示响应内容预览
            raw_response = response.get('raw_response', {})
            raw_lines = raw_response.get('raw_lines', [])
            print(f"Response Lines: {len(raw_lines)}")

            # 提取文本内容
            for line in raw_lines:
                try:
                    data = json.loads(line)
                    if 'data' in data and 'messages' in data['data']:
                        for msg in data['data']['messages']:
                            if msg.get('mime_type') == 'text/plain' and msg.get('content'):
                                print(f"Response Text: {msg['content'][:200]}...")
                                break
                except:
                    pass

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
