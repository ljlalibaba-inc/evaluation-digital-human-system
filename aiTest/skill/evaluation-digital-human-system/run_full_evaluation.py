#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
执行完整的数字人评测流程（非演示模式）
"""

import json
import time
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from master_digital_human import MasterDigitalHuman, TaskConfig, TaskStatus

def run_full_evaluation():
    """执行完整评测"""
    print("=" * 70)
    print("Master 数字人 - 完整评测执行")
    print("=" * 70)

    # 读取系统配置
    with open('system_config.json', 'r', encoding='utf-8') as f:
        system_config = json.load(f)

    eval_config = system_config.get('evaluation', {})

    # 初始化Master
    master = MasterDigitalHuman(system_config)

    # 创建任务配置
    config = TaskConfig(
        name=eval_config.get('name', '千问即时零售评测'),
        target_model=eval_config.get('target_model', 'qwen-turbo'),
        scope=eval_config.get('scope', {
            "personas": ["P1", "P2"],
            "scenarios": ["S1", "S2"],
            "categories": ["C5", "C4"]
        }),
        cases_per_combination=2,  # 每个P×S×C组合生成2条用例
        dimensions=eval_config.get('dimensions', ['accuracy', 'timeliness', 'personalization', 'safety']),
        parallel=False,
        batch_size=10,
        delay_ms=500,
        retry_times=3,
        timeout_seconds=300
    )

    # 提交任务
    print("\n[执行] 提交测评任务...")
    execution = master.submit_task(config)
    print(f"[执行] 任务ID: {execution.execution_id}")

    # 等待任务完成
    print("\n[执行] 等待任务执行完成...")
    max_wait = 1800  # 最多等待30分钟
    waited = 0
    check_interval = 5

    last_stage = None
    last_progress = None

    while execution.status == TaskStatus.RUNNING and waited < max_wait:
        time.sleep(check_interval)
        waited += check_interval

        # 只在阶段或进度变化时打印
        if execution.stages:
            current_stage = execution.stages[-1]
            current_progress = current_stage.progress

            if current_stage.name != last_stage or current_progress != last_progress:
                print(f"[执行] 当前阶段: {current_stage.name}, 状态: {current_stage.status.value}")
                if current_progress:
                    print(f"[执行] 进度: {current_progress}")
                last_stage = current_stage.name
                last_progress = current_progress

    # 检查结果
    print("\n" + "=" * 70)
    if execution.status == TaskStatus.COMPLETED:
        print("[执行] 任务执行完成!")

        # 生成报告
        report = master.generate_report(execution.execution_id)

        print("\n[执行] 测评报告摘要:")
        summary = report["execution_summary"]
        print(f"  - 任务名称: {summary['task_config']['name']}")
        print(f"  - 执行状态: {summary['status']}")
        print(f"  - 执行时长: {summary['duration_seconds']:.2f}秒")
        print(f"  - 阶段数: {len(summary['stages'])}")

        for stage in summary['stages']:
            print(f"    · {stage['name']}: {stage['status']} ({stage['duration_seconds']:.2f}s)")

        if summary.get('results_summary'):
            print(f"\n  - 测评结果:")
            print(f"    · 总评测数: {summary['results_summary'].get('total_evaluated', 0)}")
            print(f"    · 平均分: {summary['results_summary'].get('average_score', 0):.2f}")
            print(f"    · 通过数: {summary['results_summary'].get('pass_count', 0)}")

        # 保存报告
        report_path = f"report_{execution.execution_id}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n[执行] 报告已保存: {report_path}")

        return execution.execution_id

    elif execution.status == TaskStatus.FAILED:
        print("[执行] 任务执行失败!")
        print(f"[执行] 错误: {execution.errors}")
        return None
    else:
        print(f"[执行] 任务状态: {execution.status.value}")
        print(f"[执行] 等待超时或任务未完成")
        return None

if __name__ == "__main__":
    execution_id = run_full_evaluation()
    if execution_id:
        print(f"\n执行ID: {execution_id}")
        print("可以继续生成HTML报告:")
        print(f"  python3 generate_report_from_results.py")
        print(f"  python3 scripts/generate_detailed_report.py ./report_{execution_id}.json")
