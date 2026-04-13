#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜推大模型测评数字人系统 - 完整演示
"""

import json
import sys
import os

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from master_digital_human import MasterDigitalHuman, TaskConfig, TaskStatus


def print_banner():
    """打印横幅"""
    print("=" * 80)
    print(" " * 20 + "搜推大模型测评数字人系统")
    print(" " * 15 + "Search & Recommendation LLM Evaluation System")
    print("=" * 80)
    print()


def print_architecture():
    """打印架构图"""
    print("【系统架构】")
    print("""
    ┌─────────────────────────────────────────────────────────────┐
    │                    Master 数字人                             │
    │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
    │  │  任务触发器   │  │  编排中心     │  │  结果汇总器   │      │
    │  └──────────────┘  └──────────────┘  └──────────────┘      │
    └─────────────────────┬───────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
    ┌───▼─────┐    ┌────▼────┐    ┌──────▼──────┐
    │ 测试用例 │    │  千问    │    │  结果解析    │
    │ 生成Agent│    │ 调用Agent│    │   Agent     │
    └────┬────┘    └────┬────┘    └──────┬──────┘
         │              │                │
         └──────────────┼────────────────┘
                        │
               ┌────────▼────────┐
               │   结果评测Agent  │
               └─────────────────┘
    """)


def demo_full_workflow():
    """演示完整工作流程"""
    print_banner()
    print_architecture()
    
    print("\n" + "=" * 80)
    print("演示：完整测评工作流程")
    print("=" * 80)
    
    # 1. 初始化Master数字人
    print("\n【步骤1】初始化Master数字人...")
    master = MasterDigitalHuman()
    print("✓ Master数字人已初始化")
    print("  - 已注册Agent: testcase, qwen, parser, evaluator")
    
    # 2. 配置测评任务
    print("\n【步骤2】配置测评任务...")
    config = TaskConfig(
        name="千问即时零售场景测评-演示",
        target_model="qwen-turbo",
        scope={
            "personas": ["P1", "P2"],  # 加班族、新手妈妈
            "scenarios": ["S1", "S2"],  # 应急补给、即时享受
            "categories": ["C5", "C4"]  # 医药健康、母婴用品
        },
        count=3,  # 演示用3条
        dimensions=["accuracy", "timeliness", "personalization", "safety"],
        parallel=False,
        batch_size=3,
        delay_ms=100
    )
    print(f"✓ 任务配置完成")
    print(f"  - 任务名称: {config.name}")
    print(f"  - 目标模型: {config.target_model}")
    print(f"  - 测评数量: {config.count}")
    print(f"  - 测评维度: {', '.join(config.dimensions)}")
    
    # 3. 提交任务
    print("\n【步骤3】提交测评任务...")
    execution = master.submit_task(config)
    print(f"✓ 任务已提交")
    print(f"  - 执行ID: {execution.execution_id}")
    print(f"  - 初始状态: {execution.status.value}")
    
    # 4. 监控执行
    print("\n【步骤4】监控任务执行...")
    import time
    
    max_wait = 30
    waited = 0
    
    while execution.status == TaskStatus.RUNNING and waited < max_wait:
        time.sleep(1)
        waited += 1
        
        # 打印当前阶段
        if execution.stages:
            current = execution.stages[-1]
            progress = current.progress
            progress_str = f"({progress})" if progress else ""
            print(f"  [{waited}s] 当前阶段: {current.name} - {current.status.value} {progress_str}")
    
    # 5. 检查结果
    print("\n【步骤5】获取执行结果...")
    
    if execution.status == TaskStatus.COMPLETED:
        print("✓ 任务执行成功!")
        
        # 打印各阶段耗时
        print("\n  各阶段执行情况:")
        for stage in execution.stages:
            status_icon = "✓" if stage.status.value == "completed" else "✗"
            print(f"    {status_icon} {stage.name}: {stage.duration_seconds:.2f}s")
        
        # 6. 生成报告
        print("\n【步骤6】生成测评报告...")
        report = master.generate_report(execution.execution_id)
        
        # 打印报告摘要
        summary = report["execution_summary"]
        print("\n  测评报告摘要:")
        print(f"    - 报告ID: {report['report_id']}")
        print(f"    - 执行时长: {summary['duration_seconds']:.2f}秒")
        
        if summary.get('results_summary'):
            rs = summary['results_summary']
            print(f"    - 评测Query数: {rs.get('total_evaluated', 0)}")
            print(f"    - 平均得分: {rs.get('average_score', 0):.2f}/5.0")
            print(f"    - 通过数(≥4.0): {rs.get('pass_count', 0)}")
        
        # 保存报告
        report_file = f"report_{execution.execution_id}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n  ✓ 报告已保存: {report_file}")
        
    elif execution.status == TaskStatus.FAILED:
        print("✗ 任务执行失败!")
        print(f"  错误: {execution.errors}")
    else:
        print(f"? 任务状态: {execution.status.value}")
    
    print("\n" + "=" * 80)


def demo_single_agents():
    """演示单个Agent调用"""
    print("\n" + "=" * 80)
    print("演示：单个Agent独立调用")
    print("=" * 80)
    
    # 1. 测试用例生成Agent
    print("\n【Agent 1】测试用例生成Agent")
    from agents.testcase_agent import TestCaseAgent
    
    testcase_agent = TestCaseAgent()
    queries = testcase_agent.generate(
        personas=["P1"],
        scenarios=["S1"],
        categories=["C5"],
        count=2
    )
    
    print(f"✓ 生成 {len(queries)} 条测试用例")
    for q in queries:
        print(f"  - {q['query_id']}: {q['query_text'][:50]}...")
    
    # 2. 千问调用Agent
    print("\n【Agent 2】千问调用Agent")
    from agents.qwen_agent import QwenAgent
    
    qwen_agent = QwenAgent()
    
    if queries:
        response = qwen_agent.call(
            query_text=queries[0]['query_text'],
            system_prompt="你是即时零售助手"
        )
        
        if response['success']:
            print(f"✓ 调用成功")
            print(f"  响应时间: {response['response_time_ms']}ms")
            print(f"  响应预览: {response['content'][:60]}...")
        else:
            print(f"✗ 调用失败: {response.get('error')}")
    
    # 3. 结果解析Agent
    print("\n【Agent 3】结果解析Agent")
    from agents.parser_agent import ResultParserAgent
    
    parser_agent = ResultParserAgent()
    
    if queries and response.get('success'):
        parsed = parser_agent.parse(
            response=response,
            query=queries[0]
        )
        
        print(f"✓ 解析完成")
        print(f"  推荐商品: {parsed.get('recommended_products', [])}")
        print(f"  时效承诺: {parsed.get('time_commitment')}")
        print(f"  个性化元素: {parsed.get('personalization_elements', [])}")
        print(f"  安全提示: {parsed.get('safety_warnings', [])}")
    
    # 4. 结果评测Agent
    print("\n【Agent 4】结果评测Agent")
    from agents.eval_agent import SearchEvalAgent
    
    eval_agent = SearchEvalAgent()
    
    if queries and response.get('success'):
        eval_result = eval_agent.evaluate(
            query=queries[0],
            response=response,
            dimensions=["accuracy", "timeliness", "personalization", "safety"]
        )
        
        print(f"✓ 评测完成")
        print(f"  各维度得分:")
        for dim, score in eval_result['scores'].items():
            print(f"    - {dim}: {score}/5.0")
        print(f"  总分: {eval_result['overall_score']}/5.0")
        
        if eval_result.get('issues'):
            print(f"  发现问题: {eval_result['issues']}")
        
        if eval_result.get('suggestions'):
            print(f"  改进建议: {eval_result['suggestions'][:2]}")
    
    print("\n" + "=" * 80)


def demo_custom_workflow():
    """演示自定义工作流"""
    print("\n" + "=" * 80)
    print("演示：自定义工作流编排")
    print("=" * 80)
    
    print("\n【场景】只测试医药健康品类的安全合规性")
    
    # 初始化
    master = MasterDigitalHuman()
    
    # 配置专项测评
    config = TaskConfig(
        name="医药品类安全合规专项测评",
        target_model="qwen-turbo",
        scope={
            "personas": ["P1", "P2", "P5"],  # 多个人群
            "scenarios": ["S1"],  # 应急场景
            "categories": ["C5"]  # 只测医药
        },
        count=3,
        dimensions=["safety", "accuracy"],  # 重点测安全和准确性
        delay_ms=200
    )
    
    print(f"\n任务配置:")
    print(f"  - 目标: {config.name}")
    print(f"  - 范围: 医药健康品类应急场景")
    print(f"  - 重点: 安全合规性检查")
    
    # 执行
    execution = master.submit_task(config)
    
    import time
    while execution.status == TaskStatus.RUNNING:
        time.sleep(1)
    
    # 结果
    if execution.status == TaskStatus.COMPLETED:
        print("\n✓ 专项测评完成")
        
        # 检查安全评分
        eval_results = execution.results.get('evaluation', [])
        safety_scores = [r.get('scores', {}).get('safety', 0) for r in eval_results if isinstance(r, dict)]
        
        if safety_scores:
            avg_safety = sum(safety_scores) / len(safety_scores)
            print(f"\n  安全合规评分: {avg_safety:.2f}/5.0")
            
            if avg_safety >= 4.5:
                print("  ✓ 安全合规性良好")
            elif avg_safety >= 3.5:
                print("  △ 安全合规性一般，需要改进")
            else:
                print("  ✗ 安全合规性较差，需要重点关注")
            
            # 检查问题
            all_issues = []
            for r in eval_results:
                if isinstance(r, dict) and 'issues' in r:
                    all_issues.extend(r['issues'])
            
            if all_issues:
                print(f"\n  发现的安全问题:")
                for issue in set(all_issues):
                    print(f"    - {issue}")
    
    print("\n" + "=" * 80)


def main():
    """主函数"""
    print_banner()
    
    print("请选择演示模式:")
    print("  1. 完整工作流程演示")
    print("  2. 单个Agent独立调用演示")
    print("  3. 自定义工作流演示")
    print("  4. 全部演示")
    print()
    
    # 检查是否有命令行参数
    import sys
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        try:
            choice = input("请输入选项 (1-4): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n使用默认选项: 全部演示")
            choice = "4"
    
    if choice == "1":
        demo_full_workflow()
    elif choice == "2":
        demo_single_agents()
    elif choice == "3":
        demo_custom_workflow()
    elif choice == "4":
        demo_full_workflow()
        demo_single_agents()
        demo_custom_workflow()
    else:
        print("无效选项，默认执行完整工作流程演示")
        demo_full_workflow()
    
    print("\n" + "=" * 80)
    print("演示完成! 感谢使用搜推大模型测评数字人系统")
    print("=" * 80)


if __name__ == "__main__":
    main()
