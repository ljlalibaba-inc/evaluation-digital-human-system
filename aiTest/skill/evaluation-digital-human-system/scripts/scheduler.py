#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时任务调度器
支持定时执行评测任务和发送钉钉通知
"""

import json
import time
import threading
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
import schedule


@dataclass
class ScheduleConfig:
    """定时配置"""
    enabled: bool = True
    # 支持多种定时方式
    daily_time: Optional[str] = None  # 每天执行时间，如 "09:00"
    weekly_day: Optional[int] = None  # 每周几执行，0=周一
    weekly_time: Optional[str] = None  # 每周执行时间
    interval_minutes: Optional[int] = None  # 每隔N分钟执行
    cron_expression: Optional[str] = None  # Cron表达式


@dataclass
class DingTalkConfig:
    """钉钉配置"""
    enabled: bool = False
    webhook_url: str = ""
    secret: str = ""  # 加签密钥
    at_mobiles: List[str] = None  # @的手机号
    at_all: bool = False  # 是否@所有人
    
    def __post_init__(self):
        if self.at_mobiles is None:
            self.at_mobiles = []


class DingTalkNotifier:
    """钉钉通知器"""
    
    def __init__(self, config: DingTalkConfig):
        self.config = config
    
    def _generate_sign(self, timestamp: int) -> str:
        """生成加签"""
        import hmac
        import hashlib
        import base64
        
        secret = self.config.secret
        secret_enc = secret.encode('utf-8')
        string_to_sign = f'{timestamp}\n{secret}'
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = base64.b64encode(hmac_code).decode('utf-8')
        return sign
    
    def send_text(self, message: str, title: str = "") -> bool:
        """发送文本消息"""
        if not self.config.enabled or not self.config.webhook_url:
            print("[DingTalk] 通知未启用或配置不完整")
            return False
        
        timestamp = int(round(time.time() * 1000))
        
        # 构建Webhook URL
        webhook_url = self.config.webhook_url
        if self.config.secret:
            sign = self._generate_sign(timestamp)
            webhook_url = f"{webhook_url}&timestamp={timestamp}&sign={sign}"
        
        # 构建消息
        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": title or "【评测报告】大模型数字人",
                "text": message
            },
            "at": {
                "atMobiles": self.config.at_mobiles,
                "isAtAll": self.config.at_all
            }
        }
        
        try:
            response = requests.post(
                webhook_url,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get('errcode') == 0:
                print(f"[DingTalk] 消息发送成功")
                return True
            else:
                print(f"[DingTalk] 消息发送失败: {result.get('errmsg')}")
                return False
                
        except Exception as e:
            print(f"[DingTalk] 发送异常: {e}")
            return False
    
    def send_evaluation_report(self, report_data: Dict) -> bool:
        """发送评测报告"""
        summary = report_data.get('execution_summary', {})
        results = report_data.get('detailed_results', [])
        
        # 统计数据
        total = summary.get('results_summary', {}).get('total_evaluated', 0)
        avg_score = summary.get('results_summary', {}).get('average_score', 0)
        pass_count = summary.get('results_summary', {}).get('pass_count', 0)
        pass_rate = (pass_count / total * 100) if total > 0 else 0
        
        # 确定等级和颜色
        if avg_score >= 4.5:
            level = "优秀 🟢"
            color = "#52c41a"
        elif avg_score >= 4.0:
            level = "良好 🔵"
            color = "#1890ff"
        elif avg_score >= 3.5:
            level = "一般 🟠"
            color = "#faad14"
        else:
            level = "需改进 🔴"
            color = "#f5222d"
        
        # 构建Markdown消息（必须包含关键词"评测报告"）
        message = f"""## 🤖 大模型数字人【评测报告】

### 📊 评测概览

| 指标 | 数值 |
|------|------|
| **评测时间** | {datetime.now().strftime('%Y-%m-%d %H:%M')} |
| **测试用例** | {total} 个 |
| **平均分** | <font color='{color}'>**{avg_score:.2f}**</font> / 5.0 |
| **通过率** | {pass_rate:.1f}% |
| **整体评级** | <font color='{color}'>**{level}**</font> |

### 📋 评测明细

| 人设 | 场景 | 品类 | 得分 | 状态 |
|------|------|------|------|------|
"""
        
        # 添加明细
        for result in results[:10]:  # 最多显示10条
            query_id = result.get('query_id', '')
            score = result.get('overall_score', 0)
            issues = result.get('issues', [])
            
            # 获取基本信息
            persona = self._get_persona_name(query_id)
            scenario = self._get_scenario_name(query_id)
            category = self._get_category_name(query_id)
            
            # 状态图标
            if issues:
                status = "⚠️"
            elif score >= 4.0:
                status = "✅"
            else:
                status = "❌"
            
            message += f"| {persona} | {scenario} | {category} | {score:.2f} | {status} |\n"
        
        # 添加问题汇总
        all_issues = []
        for result in results:
            issues = result.get('issues', [])
            all_issues.extend(issues)
        
        if all_issues:
            message += f"\n### ⚠️ 发现问题\n\n"
            unique_issues = list(set(all_issues))[:5]  # 最多显示5个问题
            for issue in unique_issues:
                message += f"- {issue}\n"
        
        message += f"\n---\n📎 详细【评测报告】请查看系统"
        
        return self.send_text(message, title="【评测报告】大模型数字人")
    
    def _get_persona_name(self, query_id: str) -> str:
        """获取人群名称"""
        query_num = int(query_id.replace('Q', ''))
        if query_num in [1, 16, 28, 33, 44, 56, 62, 68, 79, 91]:
            return "忙碌白领"
        elif query_num in [2, 10, 17, 24, 32, 40, 46, 58, 64, 70]:
            return "新手妈妈"
        elif query_num in [6, 15, 20, 26, 31, 37, 43, 49, 55, 61]:
            return "大学生"
        elif query_num in [5, 13, 18, 23, 29, 34, 39, 45, 51, 57]:
            return "精致白领"
        elif query_num in [8, 19, 25, 30, 35, 41, 47, 53, 59, 65]:
            return "退休阿姨"
        else:
            return "双职工家庭"
    
    def _get_scenario_name(self, query_id: str) -> str:
        """获取场景名称"""
        query_num = int(query_id.replace('Q', ''))
        if query_num in [1, 2, 3, 16, 17, 18]:
            return "应急补给"
        elif query_num in [4, 5, 6, 15, 20, 22]:
            return "即时享受"
        elif query_num in [7, 8, 9, 19, 35]:
            return "懒人便利"
        elif query_num in [10, 11, 12, 24, 26]:
            return "计划消费"
        else:
            return "节日聚会"
    
    def _get_category_name(self, query_id: str) -> str:
        """获取品类名称"""
        query_num = int(query_id.replace('Q', ''))
        if query_num in [3, 5, 11, 14]:
            return "生鲜果蔬"
        elif query_num in [4, 6, 15, 20]:
            return "休闲零售"
        elif query_num in [18, 26, 31, 37]:
            return "3C数码"
        elif query_num in [2, 9, 10, 17]:
            return "母婴用品"
        elif query_num in [1, 16, 19, 30]:
            return "医药健康"
        elif query_num in [7, 8, 12, 21]:
            return "日用百货"
        elif query_num in [13, 14, 23, 25]:
            return "鲜花礼品"
        else:
            return "宠物用品"


class EvaluationScheduler:
    """评测任务调度器"""
    
    def __init__(self, config_file: str = "scheduler_config.json"):
        self.config_file = config_file
        self.config = self._load_config()
        self.scheduler = schedule
        self.running = False
        self.scheduler_thread = None
        self.dingtalk = DingTalkNotifier(self.config.get('dingtalk', DingTalkConfig()))
        self.task_callback: Optional[Callable] = None
    
    def _load_config(self) -> Dict:
        """加载配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'schedule': asdict(ScheduleConfig()),
                'dingtalk': asdict(DingTalkConfig())
            }
    
    def _save_config(self):
        """保存配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def set_schedule(self, config: ScheduleConfig):
        """设置定时配置"""
        self.config['schedule'] = asdict(config)
        self._save_config()
        self._setup_jobs()
    
    def set_dingtalk(self, config: DingTalkConfig):
        """设置钉钉配置"""
        self.config['dingtalk'] = asdict(config)
        self.dingtalk = DingTalkNotifier(config)
        self._save_config()
    
    def set_task_callback(self, callback: Callable):
        """设置任务回调函数"""
        self.task_callback = callback
    
    def _setup_jobs(self):
        """设置定时任务"""
        schedule_config = ScheduleConfig(**self.config.get('schedule', {}))
        
        if not schedule_config.enabled:
            return
        
        # 清除现有任务
        self.scheduler.clear()
        
        # 每天定时执行
        if schedule_config.daily_time:
            self.scheduler.every().day.at(schedule_config.daily_time).do(self._run_scheduled_task)
            print(f"[Scheduler] 已设置每天 {schedule_config.daily_time} 执行")
        
        # 每周定时执行
        if schedule_config.weekly_day is not None and schedule_config.weekly_time:
            days = [
                self.scheduler.every().monday,
                self.scheduler.every().tuesday,
                self.scheduler.every().wednesday,
                self.scheduler.every().thursday,
                self.scheduler.every().friday,
                self.scheduler.every().saturday,
                self.scheduler.every().sunday
            ]
            days[schedule_config.weekly_day].at(schedule_config.weekly_time).do(self._run_scheduled_task)
            print(f"[Scheduler] 已设置每周{schedule_config.weekly_day + 1} {schedule_config.weekly_time} 执行")
        
        # 间隔执行
        if schedule_config.interval_minutes:
            self.scheduler.every(schedule_config.interval_minutes).minutes.do(self._run_scheduled_task)
            print(f"[Scheduler] 已设置每隔 {schedule_config.interval_minutes} 分钟执行")
    
    def _run_scheduled_task(self):
        """执行定时任务"""
        print(f"\n[Scheduler] 定时任务触发: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if self.task_callback:
            try:
                # 执行评测任务
                result = self.task_callback()
                
                # 发送钉钉通知
                if result and self.config.get('dingtalk', {}).get('enabled'):
                    self.dingtalk.send_evaluation_report(result)
                    
            except Exception as e:
                print(f"[Scheduler] 任务执行失败: {e}")
                # 发送失败通知
                if self.config.get('dingtalk', {}).get('enabled'):
                    self.dingtalk.send_text(
                        f"## ⚠️ 评测任务执行失败\n\n"
                        f"**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"**错误**: {str(e)}\n\n请检查系统日志",
                        title="评测任务失败通知"
                    )
    
    def start(self):
        """启动调度器"""
        if self.running:
            print("[Scheduler] 调度器已在运行")
            return
        
        self._setup_jobs()
        self.running = True
        
        def run_scheduler():
            while self.running:
                self.scheduler.run_pending()
                time.sleep(1)
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        print("[Scheduler] 调度器已启动")
    
    def stop(self):
        """停止调度器"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        print("[Scheduler] 调度器已停止")
    
    def run_once(self) -> Dict:
        """立即执行一次"""
        print("[Scheduler] 手动触发任务执行")
        self._run_scheduled_task()
        return {"status": "triggered"}
    
    def get_next_run_time(self) -> Optional[str]:
        """获取下次执行时间"""
        next_run = self.scheduler.next_run
        if next_run:
            return next_run.strftime('%Y-%m-%d %H:%M:%S')
        return None
    
    def get_status(self) -> Dict:
        """获取调度器状态"""
        return {
            "running": self.running,
            "next_run": self.get_next_run_time(),
            "jobs": len(self.scheduler.jobs),
            "dingtalk_enabled": self.config.get('dingtalk', {}).get('enabled', False)
        }


def demo():
    """演示"""
    print("=" * 80)
    print("定时任务调度器演示")
    print("=" * 80)
    
    # 创建调度器
    scheduler = EvaluationScheduler()
    
    # 配置钉钉（可选）
    dingtalk_config = DingTalkConfig(
        enabled=False,  # 设置为True并填写webhook_url以启用
        webhook_url="https://oapi.dingtalk.com/robot/send?access_token=xxx",
        secret="",  # 加签密钥
        at_mobiles=["13800138000"],
        at_all=False
    )
    scheduler.set_dingtalk(dingtalk_config)
    
    # 配置定时任务
    schedule_config = ScheduleConfig(
        enabled=True,
        daily_time="09:00",  # 每天9点执行
        # interval_minutes=5,  # 或者每5分钟执行
    )
    scheduler.set_schedule(schedule_config)
    
    # 设置任务回调
    def mock_evaluation_task():
        """模拟评测任务"""
        print("[Demo] 执行评测任务...")
        # 这里应该调用实际的评测逻辑
        return {
            "execution_summary": {
                "results_summary": {
                    "total_evaluated": 3,
                    "average_score": 4.13,
                    "pass_count": 2
                }
            },
            "detailed_results": [
                {"query_id": "Q001", "overall_score": 4.56, "issues": []},
                {"query_id": "Q017", "overall_score": 3.50, "issues": ["缺少安全提示"]},
                {"query_id": "Q056", "overall_score": 4.34, "issues": []}
            ]
        }
    
    scheduler.set_task_callback(mock_evaluation_task)
    
    # 启动调度器
    scheduler.start()
    
    print(f"\n调度器状态: {scheduler.get_status()}")
    print(f"下次执行: {scheduler.get_next_run_time()}")
    
    # 模拟运行
    print("\n调度器运行中，按 Ctrl+C 停止...")
    try:
        time.sleep(60)  # 运行1分钟
    except KeyboardInterrupt:
        print("\n用户中断")
    
    scheduler.stop()
    print("\n演示结束")


if __name__ == "__main__":
    demo()
