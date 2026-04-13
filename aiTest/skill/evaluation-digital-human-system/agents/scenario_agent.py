#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
场景(Scenario)生成 Agent
基于即时零售场景生成多样化使用场景
"""

from typing import Dict, List, Optional
from .base_agent import BaseAgent


class ScenarioAgent(BaseAgent):
    """
    使用场景生成Agent
    负责生成即时零售场景下的多样化使用场景
    """

    # 预定义的场景模板
    SCENARIO_TEMPLATES = {
        "S1": {
            "id": "S1",
            "name": "应急补给",
            "description": "突发需求，需要快速获取商品解决燃眉之急",
            "characteristics": [
                "需求紧急，时间敏感",
                "通常是非计划性购买",
                "对配送时效要求极高",
                "愿意支付溢价换取速度"
            ],
            "typical_queries": [
                "突然头痛需要止痛药",
                "宝宝发烧需要退热贴",
                "手机没电需要充电宝",
                "临时需要打印纸"
            ],
            "time_sensitivity": "极高",
            "price_sensitivity": "低",
            "preferred_categories": ["C5", "C4", "C6", "C3"],
            "peak_hours": ["深夜", "凌晨", "突发时刻"],
            "priority": "P0"
        },
        "S2": {
            "id": "S2",
            "name": "即时享受",
            "description": "追求即时满足感，想要立即获得商品或服务",
            "characteristics": [
                "冲动消费倾向",
                "追求即时满足",
                "情绪驱动购买",
                "注重体验感"
            ],
            "typical_queries": [
                "突然想吃冰淇淋",
                "想喝奶茶",
                "想买束花装点心情",
                "想买个玩具奖励自己"
            ],
            "time_sensitivity": "高",
            "price_sensitivity": "中",
            "preferred_categories": ["C2", "C7", "C8", "C1"],
            "peak_hours": ["下午茶时间", "晚上", "周末"],
            "priority": "P0"
        },
        "S3": {
            "id": "S3",
            "name": "懒人便利",
            "description": "追求便利性，不愿意出门或动手",
            "characteristics": [
                "追求便利性",
                "时间成本高",
                "习惯性依赖",
                "注重服务体验"
            ],
            "typical_queries": [
                "不想出门买菜",
                "需要上门送药",
                "懒得去超市",
                "需要代办服务"
            ],
            "time_sensitivity": "中",
            "price_sensitivity": "中",
            "preferred_categories": ["C1", "C6", "C5", "C2"],
            "peak_hours": ["晚上", "周末", "恶劣天气"],
            "priority": "P1"
        },
        "S4": {
            "id": "S4",
            "name": "计划性消费",
            "description": "有计划的日常采购，注重性价比和品质",
            "characteristics": [
                "计划性强",
                "注重性价比",
                "品质导向",
                "批量采购"
            ],
            "typical_queries": [
                "每周采购生鲜",
                "补充日用品",
                "购买下周食材",
                "囤货促销商品"
            ],
            "time_sensitivity": "低",
            "price_sensitivity": "高",
            "preferred_categories": ["C1", "C6", "C2", "C4"],
            "peak_hours": ["周末", "工作日晚间"],
            "priority": "P1"
        },
        "S5": {
            "id": "S5",
            "name": "节日/聚会",
            "description": "特殊场合需求，如节日庆祝、朋友聚会",
            "characteristics": [
                "场景化需求",
                "注重仪式感",
                "品质要求高",
                "时间集中"
            ],
            "typical_queries": [
                "情人节需要鲜花",
                "聚会需要零食饮料",
                "生日需要蛋糕",
                "节日需要礼品"
            ],
            "time_sensitivity": "高",
            "price_sensitivity": "中",
            "preferred_categories": ["C7", "C2", "C1", "C8"],
            "peak_hours": ["节日前夕", "周末晚上", "特殊日期"],
            "priority": "P1"
        }
    }

    def __init__(self, config: Dict = None):
        super().__init__("ScenarioAgent", config)

    def generate(
        self,
        scenario_ids: Optional[List[str]] = None,
        priority_filter: Optional[str] = None,
        persona_id: Optional[str] = None
    ) -> List[Dict]:
        """
        生成使用场景

        Args:
            scenario_ids: 指定场景ID列表，如 ["S1", "S2"]
            priority_filter: 按优先级过滤
            persona_id: 根据人群ID推荐适合的场景

        Returns:
            场景列表
        """
        scenarios = []

        # 如果指定了人群，推荐适合该人群的场景
        if persona_id and not scenario_ids:
            scenarios = self._recommend_for_persona(persona_id)
        elif scenario_ids:
            # 返回指定场景
            for sid in scenario_ids:
                if sid in self.SCENARIO_TEMPLATES:
                    scenarios.append(self.SCENARIO_TEMPLATES[sid].copy())
        else:
            # 返回所有场景
            for sid, scenario in self.SCENARIO_TEMPLATES.items():
                if priority_filter and scenario.get("priority") != priority_filter:
                    continue
                scenarios.append(scenario.copy())

        self.log(f"生成使用场景: {len(scenarios)}个")
        return scenarios

    def _recommend_for_persona(self, persona_id: str) -> List[Dict]:
        """为特定人群推荐适合的场景"""
        # 人群场景映射
        persona_scenario_map = {
            "P1": ["S1", "S2", "S3"],  # 白领：应急、享受、便利
            "P2": ["S1", "S4", "S3"],  # 新手妈妈：应急、计划、便利
            "P3": ["S2", "S3", "S5"],  # 大学生：享受、便利、聚会
            "P4": ["S2", "S5", "S4"],  # 精致白领：享受、聚会、计划
            "P5": ["S4", "S3", "S1"],  # 退休阿姨：计划、便利、应急
            "P6": ["S3", "S4", "S1"],  # 双职工：便利、计划、应急
        }

        recommended_ids = persona_scenario_map.get(persona_id, ["S1", "S2", "S3"])
        return [self.SCENARIO_TEMPLATES[sid].copy() for sid in recommended_ids]

    def get_scenario_by_id(self, scenario_id: str) -> Optional[Dict]:
        """根据ID获取场景"""
        return self.SCENARIO_TEMPLATES.get(scenario_id, {}).copy()

    def get_scenario_names(self) -> Dict[str, str]:
        """获取场景ID到名称的映射"""
        return {sid: s["name"] for sid, s in self.SCENARIO_TEMPLATES.items()}

    def get_queries_for_scenario(self, scenario_id: str) -> List[str]:
        """获取场景的典型Query示例"""
        scenario = self.SCENARIO_TEMPLATES.get(scenario_id)
        if scenario:
            return scenario.get("typical_queries", [])
        return []

    def execute(self, input_data: Dict) -> List[Dict]:
        """执行生成任务"""
        return self.generate(
            scenario_ids=input_data.get('scenario_ids'),
            priority_filter=input_data.get('priority_filter'),
            persona_id=input_data.get('persona_id')
        )
