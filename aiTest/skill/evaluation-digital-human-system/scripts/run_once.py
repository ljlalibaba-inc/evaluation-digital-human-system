#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单次评测执行脚本
"""

import os
import sys
import json
import time

# 添加父目录到路径以导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from master_digital_human import MasterDigitalHuman, TaskConfig

def main():
    print("=" * 70)
    print("开始执行单次评测任务")
    print("=" * 70)
    
    # 初始化Master
    master = MasterDigitalHuman()
    
    # 创建任务配置 - 使用较小规模的评测
    config = TaskConfig(
        name="单次评测任务",
        target_model="qwen-turbo",
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
        report_path = f"report_{execution.execution_id}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\nJSON报告已保存: {report_path}")
        
        # 尝试生成HTML报告
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
            print("可以手动运行: python3 generate_detailed_report.py")
        
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
