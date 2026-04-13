#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时评测任务运行器
集成Master数字人、调度器和钉钉通知
"""

import json
import os
import sys
import time
from datetime import datetime

# 导入系统组件
from master_digital_human import MasterDigitalHuman, TaskConfig
from scheduler import EvaluationScheduler, ScheduleConfig, DingTalkConfig


class ScheduledEvaluationSystem:
    """定时评测系统"""
    
    def __init__(self, config_file: str = "system_config.json"):
        self.config_file = config_file
        self.config = self._load_config()
        
        # 初始化组件
        self.master = MasterDigitalHuman()
        self.scheduler = EvaluationScheduler()
        
        # 设置钉钉
        dingtalk_cfg = self.config.get('dingtalk', {})
        self.scheduler.set_dingtalk(DingTalkConfig(**dingtalk_cfg))
        
        # 设置定时
        schedule_cfg = self.config.get('schedule', {})
        self.scheduler.set_schedule(ScheduleConfig(**schedule_cfg))
        
        # 绑定任务回调
        self.scheduler.set_task_callback(self._run_evaluation)
    
    def _load_config(self) -> dict:
        """加载配置"""
        default_config = {
            "evaluation": {
                "name": "定时评测任务",
                "target_model": "qwen-turbo",
                "scope": {
                    "personas": ["P1", "P2", "P3", "P4", "P5", "P6"],
                    "scenarios": ["S1", "S2", "S3", "S4", "S5"],
                    "categories": ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"]
                },
                "count": 5,  # 已废弃，请使用 cases_per_combination
                "cases_per_combination": 2,  # 每个P×S×C组合生成2条用例
                "dimensions": ["accuracy", "timeliness", "personalization", "safety"]
            },
            "schedule": {
                "enabled": True,
                "daily_time": "09:00",
                "weekly_day": None,
                "weekly_time": None,
                "interval_minutes": None
            },
            "dingtalk": {
                "enabled": False,
                "webhook_url": "",
                "secret": "",
                "at_mobiles": [],
                "at_all": False
            },
            "output": {
                "save_html": True,
                "save_json": True,
                "send_dingtalk": True
            }
        }
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # 合并默认配置
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                    elif isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            if sub_key not in config[key]:
                                config[key][sub_key] = sub_value
                return config
        except FileNotFoundError:
            # 创建默认配置文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            return default_config
    
    def _run_evaluation(self) -> dict:
        """运行评测任务"""
        print(f"\n{'='*80}")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始执行定时评测任务")
        print(f"{'='*80}\n")
        
        eval_config = self.config.get('evaluation', {})
        
        # 创建任务配置
        task_config = TaskConfig(
            name=eval_config.get('name', '定时评测'),
            target_model=eval_config.get('target_model', 'qwen-turbo'),
            scope=eval_config.get('scope', {}),
            cases_per_combination=eval_config.get('cases_per_combination', 2),
            dimensions=eval_config.get('dimensions', ['accuracy', 'safety']),
            delay_ms=500
        )
        
        # 提交任务
        execution = self.master.submit_task(task_config)
        
        # 等待完成
        from master_digital_human import TaskStatus
        while execution.status == TaskStatus.RUNNING:
            time.sleep(1)
        
        # 检查结果
        if execution.status == TaskStatus.COMPLETED:
            print(f"\n✓ 评测任务完成: {execution.execution_id}")
            
            # 生成报告
            report = self.master.generate_report(execution.execution_id)
            
            # 保存报告
            self._save_reports(report, execution.execution_id)
            
            return report
        else:
            print(f"\n✗ 评测任务失败: {execution.errors}")
            raise Exception(f"评测失败: {execution.errors}")
    
    def _save_reports(self, report: dict, execution_id: str):
        """保存报告"""
        output_config = self.config.get('output', {})
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 保存JSON
        if output_config.get('save_json', True):
            json_file = f"report_{execution_id}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"✓ JSON报告已保存: {json_file}")
        
        # 生成并保存HTML
        if output_config.get('save_html', True):
            try:
                from generate_html_report import HTMLReportGenerator
                
                # 先保存JSON，然后HTML生成器会读取
                json_file = f"report_{execution_id}.json"
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(report, f, ensure_ascii=False, indent=2)
                
                # 生成HTML
                generator = HTMLReportGenerator(json_file)
                html = generator.generate_html()
                
                html_file = f"report_{execution_id}.html"
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(html)
                print(f"✓ HTML报告已保存: {html_file}")
                
            except Exception as e:
                print(f"⚠ HTML报告生成失败: {e}")
    
    def start_scheduler(self):
        """启动定时调度"""
        print("=" * 80)
        print("启动定时评测系统")
        print("=" * 80)
        print()
        
        # 显示配置
        schedule_cfg = self.config.get('schedule', {})
        dingtalk_cfg = self.config.get('dingtalk', {})
        eval_cfg = self.config.get('evaluation', {})
        
        # 计算预期用例数
        scope = eval_cfg.get('scope', {})
        personas = scope.get('personas', [])
        scenarios = scope.get('scenarios', [])
        categories = scope.get('categories', [])
        cases_per_combo = eval_cfg.get('cases_per_combination', 2)
        expected_count = len(personas) * len(scenarios) * len(categories) * cases_per_combo

        print("【当前配置】")
        print(f"  评测任务: {eval_cfg.get('name')}")
        print(f"  目标模型: {eval_cfg.get('target_model')}")
        print(f"  维度范围: {len(personas)}人群 × {len(scenarios)}场景 × {len(categories)}品类")
        print(f"  每组合用例: {cases_per_combo} 条")
        print(f"  预期用例数: {expected_count} 条")
        
        if schedule_cfg.get('daily_time'):
            print(f"  执行时间: 每天 {schedule_cfg.get('daily_time')}")
        elif schedule_cfg.get('interval_minutes'):
            print(f"  执行间隔: 每 {schedule_cfg.get('interval_minutes')} 分钟")
        
        print(f"  钉钉通知: {'已启用' if dingtalk_cfg.get('enabled') else '未启用'}")
        print()
        
        # 启动调度器
        self.scheduler.start()
        
        # 显示状态
        status = self.scheduler.get_status()
        print(f"【调度器状态】")
        print(f"  运行状态: {'运行中' if status['running'] else '已停止'}")
        print(f"  定时任务: {status['jobs']} 个")
        print(f"  下次执行: {status['next_run'] or '未设置'}")
        print()
        
        print("=" * 80)
        print("系统运行中，按 Ctrl+C 停止...")
        print("=" * 80)
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n用户中断，正在停止系统...")
            self.stop()
    
    def stop(self):
        """停止系统"""
        self.scheduler.stop()
        print("✓ 系统已停止")
    
    def run_once(self):
        """立即执行一次"""
        print("=" * 80)
        print("手动执行评测任务")
        print("=" * 80)
        print()
        
        try:
            report = self._run_evaluation()
            
            # 发送钉钉通知
            if self.config.get('output', {}).get('send_dingtalk', True):
                if self.config.get('dingtalk', {}).get('enabled'):
                    self.scheduler.dingtalk.send_evaluation_report(report)
            
            print("\n✓ 任务执行完成")
            
        except Exception as e:
            print(f"\n✗ 任务执行失败: {e}")
            # 发送失败通知
            if self.config.get('dingtalk', {}).get('enabled'):
                self.scheduler.dingtalk.send_text(
                    f"## ⚠️ 评测任务执行失败\n\n"
                    f"**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"**错误**: {str(e)}\n\n请检查系统日志",
                    title="评测任务失败通知"
                )


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='定时评测系统')
    parser.add_argument('--mode', choices=['schedule', 'once', 'config'], 
                       default='once', help='运行模式')
    parser.add_argument('--webhook', help='钉钉Webhook URL')
    parser.add_argument('--time', help='定时执行时间 (如: 09:00)')
    parser.add_argument('--interval', type=int, help='执行间隔 (分钟)')
    
    args = parser.parse_args()
    
    # 创建系统
    system = ScheduledEvaluationSystem()
    
    # 更新配置（如果提供了参数）
    if args.webhook:
        dingtalk_cfg = system.config.get('dingtalk', {})
        dingtalk_cfg['enabled'] = True
        dingtalk_cfg['webhook_url'] = args.webhook
        system.scheduler.set_dingtalk(DingTalkConfig(**dingtalk_cfg))
        system.config['dingtalk'] = dingtalk_cfg
    
    if args.time or args.interval:
        schedule_cfg = system.config.get('schedule', {})
        if args.time:
            schedule_cfg['daily_time'] = args.time
            schedule_cfg['interval_minutes'] = None
        elif args.interval:
            schedule_cfg['interval_minutes'] = args.interval
            schedule_cfg['daily_time'] = None
        system.scheduler.set_schedule(ScheduleConfig(**schedule_cfg))
        system.config['schedule'] = schedule_cfg
    
    # 运行
    if args.mode == 'schedule':
        system.start_scheduler()
    elif args.mode == 'once':
        system.run_once()
    elif args.mode == 'config':
        print(f"配置文件: {system.config_file}")
        print(json.dumps(system.config, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
