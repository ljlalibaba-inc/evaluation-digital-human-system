#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
结果解析 Agent
集成 result_parse Skill
"""

import re
from typing import Dict, List, Optional, Any
from .base_agent import BaseAgent


class ResultParserAgent(BaseAgent):
    """
    结果解析Agent
    负责解析千问响应，提取结构化信息
    """
    
    def __init__(self, config: Dict = None):
        super().__init__("ResultParserAgent", config)
    
    def parse(self, response: Dict, query: Dict) -> Dict[str, Any]:
        """
        解析响应结果
        
        Args:
            response: 千问响应
            query: 原始Query
        
        Returns:
            解析后的结构化数据
        """
        if not response or not response.get('success'):
            return {"error": "响应为空或调用失败"}
        
        content = response.get('content', '')
        
        result = {
            "original_response": content,
            "recommended_products": self._extract_products(content),
            "time_commitment": self._extract_time_commitment(content),
            "personalization_elements": self._extract_personalization(content),
            "safety_warnings": self._extract_safety_warnings(content),
            "intent_recognition": self._analyze_intent(content, query),
            "price_mentions": self._extract_prices(content),
            "brand_mentions": self._extract_brands(content)
        }
        
        return result
    
    def _extract_products(self, content: str) -> List[str]:
        """提取推荐的商品"""
        products = []
        
        # 匹配推荐商品的模式
        patterns = [
            r'推荐[您你]?[：:]?\s*([^，。；\n]+)',
            r'建议[您你]?[：:]?\s*([^，。；\n]+)',
            r'可以[考虑试试][：:]?\s*([^，。；\n]+)',
            r'([^，。；\n]{3,20})[是款不错]?的?选择',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            products.extend([m.strip() for m in matches if len(m.strip()) > 2])
        
        return list(set(products))[:5]  # 去重，最多5个
    
    def _extract_time_commitment(self, content: str) -> Optional[str]:
        """提取时效承诺"""
        patterns = [
            r'(\d+)[分钟小时]?\s*内?送达',
            r'(\d+)[分钟小时]?\s*内?送到',
            r'(\d+)[分钟小时]?\s*达',
            r'[支持提供]?(\d+)[分钟小时]?[快速]?配送',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(0)
        
        return None
    
    def _extract_personalization(self, content: str) -> List[str]:
        """提取个性化元素"""
        elements = []
        
        # 检查是否包含用户特征相关的内容
        indicators = [
            (r'[针对根据].{2,10}[需求情况]', "考虑用户需求"),
            (r'[适合推荐].{2,10}[使用尝试]', "适用性说明"),
            (r'[如果假设].{2,10}[建议推荐]', "条件判断"),
            (r'[您你]的.{2,10}[情况需求]', "用户特征"),
        ]
        
        for pattern, desc in indicators:
            if re.search(pattern, content):
                elements.append(desc)
        
        return elements
    
    def _extract_safety_warnings(self, content: str) -> List[str]:
        """提取安全提示"""
        warnings = []
        
        # 医药相关的安全提示
        medical_patterns = [
            r'[请务必]咨询医生',
            r'[请按照]说明书',
            r'[如有]不适.*就医',
            r'[注意]禁忌',
            r'[孕妇儿童]慎用',
        ]
        
        for pattern in medical_patterns:
            if re.search(pattern, content):
                match = re.search(pattern, content)
                warnings.append(match.group(0))
        
        return warnings
    
    def _analyze_intent(self, content: str, query: Dict) -> Dict[str, Any]:
        """分析意图识别情况"""
        query_tags = query.get('tags', [])
        
        recognized = {
            "persona_recognized": False,
            "scenario_recognized": False,
            "category_recognized": False
        }
        
        # 检查是否识别了人群特征
        persona_keywords = {
            "P1": ["加班", "工作", "忙碌", "办公室"],
            "P2": ["宝宝", "孩子", "妈妈", "婴儿"],
            "P3": ["学生", "宿舍", "预算", "便宜"],
            "P4": ["品质", "进口", "高端", "精致"],
            "P5": ["简单", "方便", "老人", "退休"],
            "P6": ["家庭", "孩子", "方便", "定时"]
        }
        
        for tag in query_tags:
            if tag.startswith('P') and tag in persona_keywords:
                keywords = persona_keywords[tag]
                if any(kw in content for kw in keywords):
                    recognized["persona_recognized"] = True
        
        # 检查是否识别了场景特征
        scenario_keywords = {
            "S1": ["急", "快", "马上", "立即"],
            "S2": ["享受", "犒劳", "喜欢", "想"],
            "S3": ["方便", "省事", "不用", "直接"],
            "S4": ["定期", "囤货", "计划", "每周"],
            "S5": ["礼物", "送", "聚会", "节日"]
        }
        
        for tag in query_tags:
            if tag.startswith('S') and tag in scenario_keywords:
                keywords = scenario_keywords[tag]
                if any(kw in content for kw in keywords):
                    recognized["scenario_recognized"] = True
        
        # 检查是否识别了品类特征
        category_keywords = {
            "C1": ["新鲜", "蔬菜", "水果", "食材"],
            "C2": ["零食", "饮料", "吃", "喝"],
            "C3": ["充电", "耳机", "配件", "数码"],
            "C4": ["奶粉", "纸尿裤", "宝宝", "婴儿"],
            "C5": ["药", "治疗", "症状", "服用"],
            "C6": ["日用", "洗护", "纸巾", "清洁"],
            "C7": ["花", "礼物", "蛋糕", "送"],
            "C8": ["猫", "狗", "宠物", "粮"]
        }
        
        for tag in query_tags:
            if tag.startswith('C') and tag in category_keywords:
                keywords = category_keywords[tag]
                if any(kw in content for kw in keywords):
                    recognized["category_recognized"] = True
        
        return recognized
    
    def _extract_prices(self, content: str) -> List[str]:
        """提取价格信息"""
        price_pattern = r'(\d+)[元块]?[左右]?[以内]?'
        matches = re.findall(price_pattern, content)
        return [f"{m}元" for m in matches[:3]]
    
    def _extract_brands(self, content: str) -> List[str]:
        """提取品牌提及"""
        # 常见品牌词
        brand_keywords = [
            "帮宝适", "花王", "好奇", "爱他美", "美赞臣",
            "苹果", "华为", "小米", "三星", "索尼",
            "可口可乐", "百事", "农夫山泉", "伊利", "蒙牛"
        ]
        
        mentioned = []
        for brand in brand_keywords:
            if brand in content:
                mentioned.append(brand)
        
        return mentioned[:5]
    
    def execute(self, input_data: Dict) -> Dict:
        """执行解析任务"""
        return self.parse(
            response=input_data.get('response'),
            query=input_data.get('query')
        )
