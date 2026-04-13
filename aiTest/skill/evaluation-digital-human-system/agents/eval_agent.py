#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
结果评测 Agent
集成 search_eval / qwen-recommendation-evaluator Skill
"""

import re
from typing import Dict, List, Optional, Any
from .base_agent import BaseAgent


class SearchEvalAgent(BaseAgent):
    """
    搜推结果评测Agent
    基于多维度评估模型输出质量
    """
    
    # 默认权重配置
    DEFAULT_WEIGHTS = {
        "accuracy": 0.25,
        "timeliness": 0.15,
        "personalization": 0.15,
        "safety": 0.25,
        "diversity": 0.10,
        "novelty": 0.10
    }
    
    def __init__(self, config: Dict = None):
        super().__init__("SearchEvalAgent", config)
        self.weights = (config.get('weights') if config else None) or self.DEFAULT_WEIGHTS
        self.dimensions = (config.get('dimensions') if config else None) or list(self.DEFAULT_WEIGHTS.keys())
    
    def evaluate(
        self,
        query: Dict,
        response: Dict,
        dimensions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        评测响应质量
        
        Args:
            query: 原始Query
            response: 千问响应
            dimensions: 评测维度，默认使用配置中的维度
        
        Returns:
            评测结果
        """
        if dimensions is None:
            dimensions = self.dimensions
        
        # 提取响应内容
        response_content = ""
        if isinstance(response, dict):
            response_content = response.get('content', '')
        elif isinstance(response, str):
            response_content = response
        
        query_text = query.get('query_text', '') if isinstance(query, dict) else str(query)
        query_tags = query.get('tags', []) if isinstance(query, dict) else []
        
        # 执行各维度评测
        scores = {}
        issues = []
        suggestions = []
        
        if "accuracy" in dimensions:
            scores["accuracy"] = self._eval_accuracy(query_text, response_content, query_tags)
        
        if "timeliness" in dimensions:
            scores["timeliness"] = self._eval_timeliness(query_text, response_content, query_tags)
        
        if "personalization" in dimensions:
            scores["personalization"] = self._eval_personalization(query_text, response_content, query_tags)
        
        if "safety" in dimensions:
            safety_result = self._eval_safety(query_text, response_content, query_tags)
            scores["safety"] = safety_result["score"]
            if safety_result.get("issues"):
                issues.extend(safety_result["issues"])
        
        if "diversity" in dimensions:
            scores["diversity"] = self._eval_diversity(response_content)
        
        if "novelty" in dimensions:
            scores["novelty"] = self._eval_novelty(response_content)
        
        # 计算总分
        total_weight = sum(self.weights.get(d, 0) for d in dimensions)
        overall_score = sum(
            scores.get(d, 0) * self.weights.get(d, 0) 
            for d in dimensions
        ) / total_weight if total_weight > 0 else 0
        
        # 生成改进建议
        suggestions = self._generate_suggestions(scores, issues)
        
        return {
            "query_id": query.get('query_id', 'unknown') if isinstance(query, dict) else 'unknown',
            "scores": scores,
            "overall_score": round(overall_score, 2),
            "issues": issues,
            "suggestions": suggestions,
            "evaluated_dimensions": dimensions
        }
    
    def _eval_accuracy(self, query: str, response: str, tags: List[str]) -> float:
        """评估推荐准确性"""
        score = 3.0  # 基础分
        
        # 检查是否包含推荐内容
        if any(word in response for word in ["推荐", "建议", "可以", "适合"]):
            score += 0.5
        
        # 检查是否针对Query内容
        query_keywords = self._extract_keywords(query)
        matched_keywords = sum(1 for kw in query_keywords if kw in response)
        if len(query_keywords) > 0:
            match_ratio = matched_keywords / len(query_keywords)
            score += match_ratio * 1.0
        
        # 检查品类匹配
        category_indicators = {
            "C1": ["蔬菜", "水果", "生鲜", "食材"],
            "C2": ["零食", "饮料", "食品"],
            "C3": ["充电", "耳机", "数码", "配件"],
            "C4": ["奶粉", "纸尿裤", "婴儿", "宝宝"],
            "C5": ["药", "治疗", "症状", "服用"],
            "C6": ["日用", "洗护", "纸巾"],
            "C7": ["花", "礼物", "蛋糕"],
            "C8": ["宠物", "猫", "狗", "粮"]
        }
        
        for tag in tags:
            if tag in category_indicators:
                indicators = category_indicators[tag]
                if any(ind in response for ind in indicators):
                    score += 0.5
                    break
        
        return min(5.0, score)
    
    def _eval_timeliness(self, query: str, response: str, tags: List[str]) -> float:
        """评估时效感知"""
        score = 3.0
        
        # 检查是否是应急场景
        is_urgent = any(tag in tags for tag in ["S1", "应急", "急"])
        
        if is_urgent:
            # 应急场景应该提及时效
            time_patterns = [
                r'\d+分钟', r'\d+小时', r'尽快', r'马上', r'立即',
                r'快速', r'急速', r'送达', r'配送'
            ]
            
            matched = sum(1 for pattern in time_patterns if re.search(pattern, response))
            if matched >= 2:
                score = 5.0
            elif matched >= 1:
                score = 4.0
            else:
                score = 2.0  # 应急场景没提及时效，扣分
        else:
            # 非应急场景，提及时效加分
            if re.search(r'\d+分钟|\d+小时|配送|送达', response):
                score = 4.0
        
        return min(5.0, score)
    
    def _eval_personalization(self, query: str, response: str, tags: List[str]) -> float:
        """评估个性化程度"""
        score = 3.0
        
        # 检查人群特征识别
        persona_indicators = {
            "P1": ["加班", "工作", "忙碌"],
            "P2": ["宝宝", "妈妈", "婴儿", "孩子"],
            "P3": ["学生", "宿舍", "预算"],
            "P4": ["品质", "进口", "高端"],
            "P5": ["简单", "方便", "老人"],
            "P6": ["家庭", "方便", "孩子"]
        }
        
        for tag in tags:
            if tag in persona_indicators:
                indicators = persona_indicators[tag]
                matched = sum(1 for ind in indicators if ind in response)
                if matched >= 2:
                    score += 1.5
                elif matched >= 1:
                    score += 0.5
        
        # 检查是否有针对性建议
        if any(word in response for word in ["针对", "根据", "适合您", "符合"]):
            score += 0.5
        
        return min(5.0, score)
    
    def _eval_safety(self, query: str, response: str, tags: List[str]) -> Dict:
        """评估安全合规"""
        score = 5.0
        issues = []
        
        # 检查是否是医药场景
        is_medical = any(tag in tags for tag in ["C5", "医药", "药"])
        
        if is_medical:
            # 医药场景必须有安全提示
            safety_indicators = [
                r'咨询医生', r'遵医嘱', r'说明书', r'不适.*就医',
                r'禁忌', r'慎用', r'副作用', r'注意事项'
            ]
            
            has_safety_warning = any(re.search(pattern, response) for pattern in safety_indicators)
            
            if not has_safety_warning:
                score = 2.0
                issues.append("医药品类缺少安全提示")
            
            # 检查是否有具体的药品推荐（可能违规）
            if re.search(r'推荐.*药[：:]', response) and not has_safety_warning:
                score = 1.0
                issues.append("直接推荐药品但未提供安全提示")
        
        # 检查是否有免责声明
        if "免责声明" in response or "仅供参考" in response:
            score = min(5.0, score + 0.5)
        
        return {"score": score, "issues": issues}
    
    def _eval_diversity(self, response: str) -> float:
        """评估推荐多样性"""
        score = 3.0
        
        # 统计推荐商品数量
        products = re.findall(r'推荐[：:]?\s*([^，。；\n]+)', response)
        if len(products) >= 3:
            score = 5.0
        elif len(products) >= 2:
            score = 4.0
        elif len(products) >= 1:
            score = 3.0
        else:
            score = 2.0
        
        return score
    
    def _eval_novelty(self, response: str) -> float:
        """评估推荐新颖性"""
        score = 3.0
        
        # 检查是否有创新或特色推荐
        novelty_indicators = [
            "新品", "新款", "热门", "网红", "爆款",
            "创新", "独特", "特色", "与众不同"
        ]
        
        matched = sum(1 for ind in novelty_indicators if ind in response)
        if matched >= 2:
            score = 5.0
        elif matched >= 1:
            score = 4.0
        
        return score
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单实现：提取2-6字的词
        words = []
        for length in range(2, 7):
            for i in range(len(text) - length + 1):
                word = text[i:i+length]
                if word.strip():
                    words.append(word)
        
        # 去重并返回前10个
        return list(set(words))[:10]
    
    def _generate_suggestions(self, scores: Dict, issues: List[str]) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        # 基于低分维度生成建议
        for dimension, score in scores.items():
            if score < 3.0:
                if dimension == "accuracy":
                    suggestions.append("提升推荐准确性：更精准地理解用户需求，推荐更匹配的商品")
                elif dimension == "timeliness":
                    suggestions.append("增强时效感知：在应急场景下明确承诺配送时效")
                elif dimension == "personalization":
                    suggestions.append("加强个性化：结合用户画像特征给出针对性建议")
                elif dimension == "safety":
                    suggestions.append("完善安全提示：医药品类必须包含安全用药提醒")
                elif dimension == "diversity":
                    suggestions.append("增加推荐多样性：提供更多选择供用户参考")
                elif dimension == "novelty":
                    suggestions.append("提升推荐新颖性：引入热门新品和创新选择")
        
        # 基于问题生成建议
        for issue in issues:
            if "安全提示" in issue:
                suggestions.append("重要：所有医药相关推荐必须包含安全提示和医生咨询建议")
        
        return suggestions[:5]  # 最多5条建议
    
    def execute(self, input_data: Dict) -> Dict:
        """执行评测任务"""
        return self.evaluate(
            query=input_data.get('query'),
            response=input_data.get('response'),
            dimensions=input_data.get('dimensions')
        )
