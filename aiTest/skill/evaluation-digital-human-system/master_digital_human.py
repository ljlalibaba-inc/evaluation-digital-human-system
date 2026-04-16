#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Master 数字人 - 搜推大模型测评系统中枢
负责任务调度、编排协调、结果汇总
"""

import json
import os
import time
import uuid
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StageStatus(Enum):
    """阶段状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class TaskConfig:
    """任务配置"""
    name: str
    target_model: str = "qwen-turbo"
    scope: Dict[str, List[str]] = field(default_factory=dict)
    count: int = 100  # 已废弃，请使用 cases_per_combination
    cases_per_combination: int = 2  # 每个P×S×C组合生成的用例数量
    dimensions: List[str] = field(default_factory=lambda: ["accuracy", "timeliness", "personalization", "safety"])
    parallel: bool = False
    batch_size: int = 10
    delay_ms: int = 500
    retry_times: int = 3
    timeout_seconds: int = 300


@dataclass
class StageInfo:
    """阶段信息"""
    name: str
    status: StageStatus = StageStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    progress: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class ExecutionResult:
    """执行结果"""
    execution_id: str
    task_config: TaskConfig
    status: TaskStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    stages: List[StageInfo] = field(default_factory=list)
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "execution_id": self.execution_id,
            "task_config": {
                "name": self.task_config.name,
                "target_model": self.task_config.target_model,
                "scope": self.task_config.scope,
                "count": self.task_config.count,
                "dimensions": self.task_config.dimensions
            },
            "status": self.status.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": (self.end_time - self.start_time).total_seconds() if self.end_time else None,
            "stages": [
                {
                    "name": s.name,
                    "status": s.status.value,
                    "duration_seconds": s.duration_seconds,
                    "progress": s.progress,
                    "error": s.error
                }
                for s in self.stages
            ],
            "results_summary": self._get_results_summary(),
            "errors": self.errors
        }
    
    def _get_results_summary(self) -> Dict:
        """获取结果摘要"""
        if "evaluation" in self.results:
            eval_results = self.results["evaluation"]
            if isinstance(eval_results, list) and len(eval_results) > 0:
                scores = [r.get("overall_score", 0) for r in eval_results if isinstance(r, dict)]
                return {
                    "total_evaluated": len(eval_results),
                    "average_score": sum(scores) / len(scores) if scores else 0,
                    "pass_count": sum(1 for s in scores if s >= 4.0)
                }
        return {}


class MasterDigitalHuman:
    """
    Master 数字人
    搜推大模型测评系统的中枢控制器
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化Master数字人

        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.agents: Dict[str, Any] = {}
        self.executions: Dict[str, ExecutionResult] = {}
        self.executor = ThreadPoolExecutor(max_workers=5)
        self._lock = threading.Lock()

        # 结果保存目录
        import os
        self.results_dir = (config or {}).get('results_dir', './results')
        os.makedirs(self.results_dir, exist_ok=True)

        # 注册原子能力Agent
        self._register_default_agents()
    
    def _register_default_agents(self):
        """注册默认Agent"""
        # 延迟导入，避免循环依赖
        try:
            from agents.testcase_agent import TestCaseAgent
            from agents.qwen_agent import QwenAgent
            from agents.parser_agent import ResultParserAgent
            from agents.eval_agent import SearchEvalAgent
            
            # 获取qwen配置（默认使用qwen_chat模式）
            qwen_config = self.config.get('qwen_config', {})
            # 如果未指定api_mode，默认使用qwen_chat
            if 'api_mode' not in qwen_config:
                qwen_config['api_mode'] = 'qwen_chat'
            
            self.register_agent("testcase", TestCaseAgent())
            self.register_agent("qwen", QwenAgent(qwen_config))
            self.register_agent("parser", ResultParserAgent())
            
            # 获取评测配置
            eval_config = self.config.get('evaluation', {})
            eval_mode_config = eval_config.get('evaluation_mode', {})
            evaluator_config = {
                'evaluation': {
                    'use_llm': eval_mode_config.get('use_llm', True),
                    'llm_model': eval_mode_config.get('llm_model', 'qwen3.6-plus')
                }
            }
            self.register_agent("evaluator", SearchEvalAgent(evaluator_config))
            
        except ImportError as e:
            print(f"警告: 部分Agent导入失败: {e}")
    
    def register_agent(self, name: str, agent: Any):
        """
        注册Agent
        
        Args:
            name: Agent名称
            agent: Agent实例
        """
        self.agents[name] = agent
        print(f"[Master] 注册Agent: {name}")
    
    def submit_task(self, task_config: TaskConfig) -> ExecutionResult:
        """
        提交测评任务
        
        Args:
            task_config: 任务配置
        
        Returns:
            执行结果对象
        """
        execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        
        result = ExecutionResult(
            execution_id=execution_id,
            task_config=task_config,
            status=TaskStatus.PENDING,
            start_time=datetime.now(),
            stages=[]
        )
        
        with self._lock:
            self.executions[execution_id] = result
        
        print(f"[Master] 任务已提交: {execution_id}")
        print(f"[Master] 任务名称: {task_config.name}")
        print(f"[Master] 目标模型: {task_config.target_model}")
        print(f"[Master] 测评数量: {task_config.count}")
        
        # 启动执行
        if task_config.parallel:
            self.executor.submit(self._execute_task_parallel, execution_id)
        else:
            self.executor.submit(self._execute_task_sequential, execution_id)
        
        return result
    
    def _execute_task_sequential(self, execution_id: str):
        """顺序执行任务"""
        result = self.executions[execution_id]
        result.status = TaskStatus.RUNNING
        
        try:
            # Stage 1: 生成测试用例
            self._run_stage(execution_id, "testcase_generation", self._stage_generate_testcases)
            
            # Stage 2: 调用千问模型
            self._run_stage(execution_id, "model_calling", self._stage_call_model)
            
            # Stage 3: 解析结果
            self._run_stage(execution_id, "result_parsing", self._stage_parse_results)
            
            # Stage 4: 评测结果
            self._run_stage(execution_id, "evaluation", self._stage_evaluate)
            
            # 完成
            result.status = TaskStatus.COMPLETED
            result.end_time = datetime.now()
            
            print(f"[Master] 任务完成: {execution_id}")
            
        except Exception as e:
            result.status = TaskStatus.FAILED
            result.end_time = datetime.now()
            result.errors.append(str(e))
            print(f"[Master] 任务失败: {execution_id}, 错误: {e}")
    
    def _execute_task_parallel(self, execution_id: str):
        """并行执行任务（简化版）"""
        # TODO: 实现真正的并行处理
        self._execute_task_sequential(execution_id)
    
    def _run_stage(self, execution_id: str, stage_name: str, stage_func: Callable):
        """运行单个阶段"""
        result = self.executions[execution_id]
        
        # 创建阶段信息
        stage = StageInfo(name=stage_name)
        stage.status = StageStatus.RUNNING
        stage.start_time = datetime.now()
        result.stages.append(stage)
        
        print(f"[Master] 开始阶段: {stage_name}")
        
        try:
            # 执行阶段
            stage_func(execution_id, stage)
            
            stage.status = StageStatus.COMPLETED
            stage.end_time = datetime.now()
            stage.duration_seconds = (stage.end_time - stage.start_time).total_seconds()
            
            print(f"[Master] 阶段完成: {stage_name}, 耗时: {stage.duration_seconds:.2f}s")
            
        except Exception as e:
            stage.status = StageStatus.FAILED
            stage.end_time = datetime.now()
            stage.error = str(e)
            stage.duration_seconds = (stage.end_time - stage.start_time).total_seconds()
            
            print(f"[Master] 阶段失败: {stage_name}, 错误: {e}")
            raise
    
    def _stage_generate_testcases(self, execution_id: str, stage: StageInfo):
        """阶段1: 生成测试用例"""
        result = self.executions[execution_id]
        config = result.task_config

        testcase_agent = self.agents.get("testcase")
        if not testcase_agent:
            raise ValueError("测试用例生成Agent未注册")

        # 准备输入数据，包含qwen_config用于LLM生成query
        input_data = {
            'personas': config.scope.get("personas", []),
            'scenarios': config.scope.get("scenarios", []),
            'categories': config.scope.get("categories", []),
            'cases_per_combination': config.cases_per_combination,
            'mode': 'cartesian',
            'use_llm': True,
            'qwen_config': {
                'api_mode': 'dashscope',
                'model': 'qwen-max'  # 使用最强模型生成query
            },
            'output_dir': self.results_dir  # 保存用例到结果目录
        }

        # 使用execute方法，支持LLM生成
        queries = testcase_agent.execute(input_data)

        result.results["testcases"] = queries
        stage.progress = {"generated": len(queries)}

        print(f"[Master] 生成测试用例: {len(queries)}条")
    
    def _stage_call_model(self, execution_id: str, stage: StageInfo):
        """阶段2: 调用千问模型"""
        result = self.executions[execution_id]
        config = result.task_config
        
        qwen_agent = self.agents.get("qwen")
        if not qwen_agent:
            raise ValueError("千问调用Agent未注册")
        
        queries = result.results.get("testcases", [])
        responses = []
        failed_count = 0
        
        for i, query in enumerate(queries):
            try:
                # 调用千问
                response = qwen_agent.call(
                    query_text=query.query_text if hasattr(query, 'query_text') else query["query_text"],
                    system_prompt=self._get_system_prompt()
                )
                responses.append({
                    "query": query,
                    "response": response
                })
                
                # 更新进度
                stage.progress = {
                    "completed": i + 1,
                    "total": len(queries),
                    "failed": failed_count
                }
                
                # 延迟
                if i < len(queries) - 1:
                    time.sleep(config.delay_ms / 1000)
                
            except Exception as e:
                failed_count += 1
                print(f"[Master] 调用失败 [{i+1}/{len(queries)}]: {e}")
                responses.append({
                    "query": query,
                    "response": None,
                    "error": str(e)
                })
        
        result.results["responses"] = responses
        stage.progress = {
            "completed": len(queries) - failed_count,
            "total": len(queries),
            "failed": failed_count
        }
        
        # 保存千问返回结果到文件
        self._save_qwen_responses(execution_id, responses)
        
        print(f"[Master] 模型调用完成: {len(queries) - failed_count}/{len(queries)}")
    
    def _save_qwen_responses(self, execution_id: str, responses: List[Dict]):
        """保存千问返回结果到文件（包含完整请求信息）"""
        # 构建保存数据
        save_data = {
            "execution_id": execution_id,
            "saved_at": datetime.now().isoformat(),
            "total_responses": len(responses),
            "responses": []
        }
        
        for item in responses:
            response_entry = {
                "query": item["query"].to_dict() if hasattr(item["query"], 'to_dict') else item["query"],
                "response": item["response"].to_dict() if hasattr(item["response"], 'to_dict') else item["response"],
            }
            # 保存完整请求信息（URL、Headers、Body）
            if item.get("response") and item["response"].get("request_info"):
                response_entry["request_info"] = item["response"]["request_info"]
            if "error" in item:
                response_entry["error"] = item["error"]
            save_data["responses"].append(response_entry)
        
        # 保存到文件
        filename = f"qwen_responses_{execution_id}.json"
        filepath = os.path.join(self.results_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        print(f"[Master] 千问返回结果已保存: {filepath}")
    
    def _stage_parse_results(self, execution_id: str, stage: StageInfo):
        """阶段3: 解析结果"""
        result = self.executions[execution_id]
        
        parser_agent = self.agents.get("parser")
        if not parser_agent:
            # 如果没有解析Agent，跳过此阶段
            stage.status = StageStatus.SKIPPED
            print("[Master] 跳过结果解析阶段")
            return
        
        responses = result.results.get("responses", [])
        parsed_results = []
        
        for item in responses:
            try:
                if item.get("response"):
                    parsed = parser_agent.parse(
                        response=item["response"],
                        query=item["query"]
                    )
                    parsed_results.append({
                        "query": item["query"],
                        "response": item["response"],
                        "parsedResponse": parsed
                    })
            except Exception as e:
                print(f"[Master] 解析失败: {e}")
                parsed_results.append({
                    "query": item["query"],
                    "response": item["response"],
                    "parsedResponse": None,
                    "error": str(e)
                })
        
        result.results["parsedResponse"] = parsed_results
        stage.progress = {"parsed": len(parsed_results)}
        
        # 保存解析结果到文件
        self._save_parsed_results(execution_id, parsed_results)
        
        print(f"[Master] 结果解析完成: {len(parsed_results)}条")
    
    def _save_parsed_results(self, execution_id: str, parsed_results: list):
        """保存解析结果到文件"""
        import json
        import os
        
        # 确保 results 目录存在
        os.makedirs("./results", exist_ok=True)
        
        # 构建文件路径
        filepath = f"./results/parsed_results_{execution_id}.json"
        
        # 保存到文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(parsed_results, f, ensure_ascii=False, indent=2)
        
        print(f"[Master] 解析结果已保存: {filepath}")
    
    def _stage_evaluate(self, execution_id: str, stage: StageInfo):
        """阶段4: 评测结果"""
        result = self.executions[execution_id]
        config = result.task_config

        eval_agent = self.agents.get("evaluator")
        if not eval_agent:
            raise ValueError("评测Agent未注册")

        # 使用解析后的结果或原始响应
        items = result.results.get("parsedResponse") or result.results.get("responses", [])
        evaluations = []

        for item in items:
            try:
                query = item.get("query")
                response = item.get("response")

                if response:
                    eval_result = eval_agent.evaluate(
                        query=query,
                        response=response,
                        dimensions=config.dimensions
                    )
                    evaluations.append(eval_result)
            except Exception as e:
                print(f"[Master] 评测失败: {e}")
                evaluations.append({"error": str(e)})

        result.results["evaluation"] = evaluations
        stage.progress = {"evaluated": len(evaluations)}

        # 保存评测结果到文件
        self._save_evaluation_results(execution_id, evaluations)

        print(f"[Master] 评测完成: {len(evaluations)}条")

    def _save_evaluation_results(self, execution_id: str, evaluations: list):
        """保存评测结果到文件"""
        import json
        import os

        # 确保 results 目录存在
        os.makedirs(self.results_dir, exist_ok=True)

        # 构建保存数据
        save_data = {
            "execution_id": execution_id,
            "saved_at": datetime.now().isoformat(),
            "total_evaluations": len(evaluations),
            "evaluations": []
        }

        # 转换评测结果为可序列化格式
        for eval_result in evaluations:
            if hasattr(eval_result, 'to_dict'):
                save_data["evaluations"].append(eval_result.to_dict())
            elif hasattr(eval_result, '__dict__'):
                save_data["evaluations"].append(eval_result.__dict__)
            else:
                save_data["evaluations"].append(eval_result)

        # 构建文件路径
        filepath = os.path.join(self.results_dir, f"evaluation_results_{execution_id}.json")

        # 保存到文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)

        print(f"[Master] 评测结果已保存: {filepath}")
    
    def _get_system_prompt(self) -> str:
        """获取系统Prompt"""
        return """你是一个即时零售平台的智能助手，帮助用户推荐商品、解答购物问题。
请根据用户的需求，提供个性化、准确的推荐和建议。
注意：涉及医药相关问题时，请务必提醒用户咨询专业医生。"""
    
    def get_execution(self, execution_id: str) -> Optional[ExecutionResult]:
        """获取执行结果"""
        return self.executions.get(execution_id)
    
    def get_all_executions(self) -> List[ExecutionResult]:
        """获取所有执行结果"""
        return list(self.executions.values())
    
    def cancel_execution(self, execution_id: str) -> bool:
        """取消执行"""
        with self._lock:
            result = self.executions.get(execution_id)
            if result and result.status == TaskStatus.RUNNING:
                result.status = TaskStatus.CANCELLED
                result.end_time = datetime.now()
                return True
        return False
    
    def generate_report(self, execution_id: str) -> Dict:
        """生成测评报告"""
        result = self.executions.get(execution_id)
        if not result:
            return {"error": "执行记录不存在"}

        # 构建完整的results数据，包含原始响应和解析结果
        full_results = {
            "testcases": [],
            "responses": [],
            "parsed": [],
            "evaluation": []
        }

        # 转换testcases为可序列化格式
        testcases = result.results.get("testcases", [])
        for tc in testcases:
            if hasattr(tc, 'to_dict'):
                full_results["testcases"].append(tc.to_dict())
            elif hasattr(tc, '__dict__'):
                full_results["testcases"].append(tc.__dict__)
            else:
                full_results["testcases"].append(tc)

        # 转换responses为可序列化格式
        responses = result.results.get("responses", [])
        for resp in responses:
            item = {"query": None, "response": None}
            if isinstance(resp, dict):
                query = resp.get("query")
                if hasattr(query, 'to_dict'):
                    item["query"] = query.to_dict()
                elif hasattr(query, '__dict__'):
                    item["query"] = query.__dict__
                else:
                    item["query"] = query

                response = resp.get("response")
                if hasattr(response, 'to_dict'):
                    item["response"] = response.to_dict()
                elif hasattr(response, '__dict__'):
                    item["response"] = response.__dict__
                else:
                    item["response"] = response

                if "error" in resp:
                    item["error"] = resp["error"]
            full_results["responses"].append(item)

        # 转换parsed为可序列化格式
        parsed_list = result.results.get("parsedResponse", [])
        for p in parsed_list:
            if isinstance(p, dict):
                item = {"query": None, "response": None, "parsed": None}
                query = p.get("query")
                if hasattr(query, 'to_dict'):
                    item["query"] = query.to_dict()
                elif hasattr(query, '__dict__'):
                    item["query"] = query.__dict__
                else:
                    item["query"] = query

                response = p.get("response")
                if hasattr(response, 'to_dict'):
                    item["response"] = response.to_dict()
                elif hasattr(response, '__dict__'):
                    item["response"] = response.__dict__
                else:
                    item["response"] = response

                parsed = p.get("parsedResponse")
                if hasattr(parsed, 'to_dict'):
                    item["parsedResponse"] = parsed.to_dict()
                elif hasattr(parsed, '__dict__'):
                    item["parsedResponse"] = parsed.__dict__
                else:
                    item["parsedResponse"] = parsed

                if "error" in p:
                    item["error"] = p["error"]
                full_results["parsed"].append(item)

        # 转换evaluation为可序列化格式
        evaluations = result.results.get("evaluation", [])
        for ev in evaluations:
            if hasattr(ev, 'to_dict'):
                full_results["evaluation"].append(ev.to_dict())
            elif hasattr(ev, '__dict__'):
                full_results["evaluation"].append(ev.__dict__)
            else:
                full_results["evaluation"].append(ev)

        return {
            "report_id": f"rpt_{execution_id}",
            "execution_summary": result.to_dict(),
            "detailed_results": full_results["evaluation"],
            "results": full_results,
            "generated_at": datetime.now().isoformat()
        }


# ==================== 使用示例 ====================

def demo():
    """演示"""
    print("=" * 70)
    print("Master 数字人 - 搜推大模型测评系统")
    print("=" * 70)
    
    # 初始化Master
    master = MasterDigitalHuman()
    
    # 创建任务配置
    config = TaskConfig(
        name="千问即时零售测评-演示",
        target_model="qwen-turbo",
        scope={
            "personas": ["P1", "P2"],
            "scenarios": ["S1", "S2"],
            "categories": ["C5", "C4"]
        },
        count=5,  # 演示用，只测5条
        dimensions=["accuracy", "timeliness", "safety"],
        parallel=False,
        batch_size=5,
        delay_ms=100
    )
    
    # 提交任务
    print("\n[演示] 提交测评任务...")
    execution = master.submit_task(config)
    print(f"[演示] 任务ID: {execution.execution_id}")
    
    # 模拟监控
    print("\n[演示] 监控任务执行...")
    max_wait = 60  # 最多等待60秒
    waited = 0
    
    while execution.status == TaskStatus.RUNNING and waited < max_wait:
        time.sleep(2)
        waited += 2
        
        # 打印进度
        if execution.stages:
            current_stage = execution.stages[-1]
            print(f"[演示] 当前阶段: {current_stage.name}, 状态: {current_stage.status.value}")
            if current_stage.progress:
                print(f"[演示] 进度: {current_stage.progress}")
    
    # 检查结果
    if execution.status == TaskStatus.COMPLETED:
        print("\n[演示] 任务执行完成!")
        
        # 生成报告
        report = master.generate_report(execution.execution_id)
        
        print("\n[演示] 测评报告摘要:")
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
        print(f"\n[演示] 报告已保存: {report_path}")
        
    elif execution.status == TaskStatus.FAILED:
        print(f"\n[演示] 任务执行失败!")
        print(f"[演示] 错误: {execution.errors}")
    else:
        print(f"\n[演示] 任务状态: {execution.status.value}")
    
    print("\n" + "=" * 70)
    print("演示完成!")
    print("=" * 70)


if __name__ == "__main__":
    demo()
