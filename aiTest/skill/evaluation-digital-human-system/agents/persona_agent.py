#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人群(Persona)生成 Agent
基于即时零售场景生成多样化用户人群画像
"""

from typing import Dict, List, Optional
from .base_agent import BaseAgent


class PersonaAgent(BaseAgent):
    """
    用户人群生成Agent
    负责生成即时零售场景下的多样化用户人群画像
    """

    # 预定义的人群模板
    PERSONA_TEMPLATES = {
        "P1": {
            "id": "P1",
            "name": "忙碌的年轻白领",
            "description": "互联网公司产品经理，工作压力大，经常加班，时间碎片化",
            "demographics": {
                "age_range": "25-35岁",
                "gender": "不限",
                "income": "中高收入",
                "location": "一二线城市"
            },
            "characteristics": [
                "工作节奏快，时间敏感",
                "注重效率，追求便利",
                "对品质有一定要求",
                "习惯移动支付和线上购物"
            ],
            "pain_points": [
                "没时间线下购物",
                "加班多，需要应急补给",
                "对配送时效要求高"
            ],
            "shopping_behavior": {
                "preferred_time": "晚上8-11点",
                "order_frequency": "每周3-5次",
                "avg_order_value": "50-150元",
                "preferred_categories": ["C5", "C2", "C6"]
            },
            "priority": "P0"
        },
        "P2": {
            "id": "P2",
            "name": "新手妈妈",
            "description": "有0-3岁宝宝的年轻妈妈，关注母婴用品和宝宝健康",
            "demographics": {
                "age_range": "26-35岁",
                "gender": "女性",
                "income": "中等收入",
                "location": "一二线城市"
            },
            "characteristics": [
                "对母婴用品品质要求高",
                "关注产品安全性",
                "时间被宝宝占据，需要便利",
                "容易焦虑，需要快速响应"
            ],
            "pain_points": [
                "宝宝用品突然用完",
                "深夜急需母婴用品",
                "对产品质量和安全敏感"
            ],
            "shopping_behavior": {
                "preferred_time": "白天或深夜",
                "order_frequency": "每周5-7次",
                "avg_order_value": "100-300元",
                "preferred_categories": ["C4", "C5", "C6"]
            },
            "priority": "P0"
        },
        "P3": {
            "id": "P3",
            "name": "大学生",
            "description": "在校大学生，预算有限，追求性价比和便利性",
            "demographics": {
                "age_range": "18-25岁",
                "gender": "不限",
                "income": "低收入",
                "location": "高校周边"
            },
            "characteristics": [
                "价格敏感，追求性价比",
                "喜欢尝试新鲜事物",
                "社交需求强",
                "时间灵活但懒惰"
            ],
            "pain_points": [
                "预算有限",
                "宿舍生活不便",
                "深夜饿了需要零食"
            ],
            "shopping_behavior": {
                "preferred_time": "晚上或凌晨",
                "order_frequency": "每周2-4次",
                "avg_order_value": "20-80元",
                "preferred_categories": ["C2", "C1", "C6"]
            },
            "priority": "P1"
        },
        "P4": {
            "id": "P4",
            "name": "精致白领",
            "description": "注重生活品质的职场精英，追求精致生活方式",
            "demographics": {
                "age_range": "28-40岁",
                "gender": "不限",
                "income": "高收入",
                "location": "一线城市核心区域"
            },
            "characteristics": [
                "注重生活品质",
                "对品牌有要求",
                "愿意为品质付费",
                "追求个性化服务"
            ],
            "pain_points": [
                "没时间精致生活",
                "需要高品质产品",
                "追求独特体验"
            ],
            "shopping_behavior": {
                "preferred_time": "下班后或周末",
                "order_frequency": "每周2-3次",
                "avg_order_value": "200-500元",
                "preferred_categories": ["C1", "C7", "C2"]
            },
            "priority": "P1"
        },
        "P5": {
            "id": "P5",
            "name": "退休阿姨",
            "description": "退休在家的中老年女性，注重健康和性价比",
            "demographics": {
                "age_range": "55-70岁",
                "gender": "女性",
                "income": "固定退休金",
                "location": "社区周边"
            },
            "characteristics": [
                "注重健康和养生",
                "价格敏感，喜欢比价",
                "信任口碑和传统",
                "学习新科技有难度"
            ],
            "pain_points": [
                "行动不便",
                "需要健康食品",
                "对智能设备不熟悉"
            ],
            "shopping_behavior": {
                "preferred_time": "上午",
                "order_frequency": "每周1-2次",
                "avg_order_value": "30-100元",
                "preferred_categories": ["C1", "C5", "C6"]
            },
            "priority": "P2"
        },
        "P6": {
            "id": "P6",
            "name": "双职工家庭",
            "description": "夫妻双方都工作，有孩子需要照顾，时间紧张",
            "demographics": {
                "age_range": "30-45岁",
                "gender": "不限",
                "income": "中高收入",
                "location": "一二线城市"
            },
            "characteristics": [
                "时间极其紧张",
                "需要高效解决方案",
                "注重家庭需求",
                "批量采购习惯"
            ],
            "pain_points": [
                "没时间做饭",
                "需要快速解决三餐",
                "家庭用品消耗快"
            ],
            "shopping_behavior": {
                "preferred_time": "晚上或周末",
                "order_frequency": "每周3-5次",
                "avg_order_value": "150-400元",
                "preferred_categories": ["C1", "C6", "C2"]
            },
            "priority": "P1"
        }
    }

    def __init__(self, config: Dict = None):
        super().__init__("PersonaAgent", config)

    def generate(
        self,
        persona_ids: Optional[List[str]] = None,
        priority_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        生成人群画像

        Args:
            persona_ids: 指定人群ID列表，如 ["P1", "P2"]
            priority_filter: 按优先级过滤，如 "P0", "P1"

        Returns:
            人群画像列表
        """
        personas = []

        # 如果指定了ID，只返回指定的人群
        if persona_ids:
            for pid in persona_ids:
                if pid in self.PERSONA_TEMPLATES:
                    personas.append(self.PERSONA_TEMPLATES[pid].copy())
        else:
            # 返回所有人群
            for pid, persona in self.PERSONA_TEMPLATES.items():
                # 如果有过滤条件
                if priority_filter and persona.get("priority") != priority_filter:
                    continue
                personas.append(persona.copy())

        self.log(f"生成人群画像: {len(personas)}个")
        return personas

    def get_persona_by_id(self, persona_id: str) -> Optional[Dict]:
        """根据ID获取人群画像"""
        return self.PERSONA_TEMPLATES.get(persona_id, {}).copy()

    def get_persona_names(self) -> Dict[str, str]:
        """获取人群ID到名称的映射"""
        return {pid: p["name"] for pid, p in self.PERSONA_TEMPLATES.items()}

    def execute(self, input_data: Dict) -> List[Dict]:
        """执行生成任务"""
        return self.generate(
            persona_ids=input_data.get('persona_ids'),
            priority_filter=input_data.get('priority_filter')
        )
