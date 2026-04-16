#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
结果解析 Agent
集成 result_parse Skill
"""

import json
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
        raw_response = response.get('raw_response', {})
        
        # 提取结构化商品数据（从 multi_load/iframe 消息）
        structured_items = self._extract_structured_items(raw_response)
        
        # 如果content为空但有结构化数据，生成文本摘要
        if not content and structured_items:
            content = self._generate_summary_from_items(structured_items)
        
        result = {
            "original_response": content,
            "data": {
                "structured_items": structured_items,
                "recommended_products": self._extract_products(content) if not structured_items else [item.get('itemName', '') for item in structured_items],
                "time_commitment": self._extract_time_commitment(content),
                "personalization_elements": self._extract_personalization(content),
                "safety_warnings": self._extract_safety_warnings(content),
                "intent_recognition": self._analyze_intent(content, query),
                "price_mentions": self._extract_prices(content) if not structured_items else [f"{item.get('price', '')}元" for item in structured_items if item.get('price')],
                "brand_mentions": self._extract_brands(content) if not structured_items else [item.get('brandName', '') for item in structured_items if item.get('brandName')]
            }
        }
        
        return result
    
    def _extract_structured_items(self, raw_response: Dict) -> List[Dict]:
        """
        从 multi_load/iframe 类型的消息中提取结构化商品数据
        
        从 raw_response 中最后一个包含 multi_load/iframe 的消息结构中提取
        提取路径: 
        - 商品数据: data.messages[].meta_data.multi_load[].content.resultData.searchShopItems.guiItemList
        - 推荐类型: data.messages[].meta_data.multi_load[].content.resultData.recommendType
        """
        items = []
        
        try:
            # 获取 raw_lines 或 content
            raw_lines = raw_response.get('raw_lines', [])
            if not raw_lines and raw_response.get('content'):
                raw_lines = [raw_response.get('content')]
            
            # 收集所有包含 multi_load/iframe 的消息
            multi_load_messages = []
            
            for line in raw_lines:
                try:
                    data = json.loads(line) if isinstance(line, str) else line
                    
                    # 获取 messages 数组
                    messages = data.get('data', {}).get('messages', [])
                    
                    for msg in messages:
                        # 检查 mime_type 是否为 multi_load/iframe
                        mime_type = msg.get('mime_type', '')
                        if mime_type == 'multi_load/iframe':
                            multi_load_messages.append(msg)
                except (json.JSONDecodeError, Exception) as e:
                    continue
            
            # 从最后一个 multi_load/iframe 消息中提取数据
            if multi_load_messages:
                last_msg = multi_load_messages[-1]
                meta_data = last_msg.get('meta_data', {})
                multi_load_list = meta_data.get('multi_load', [])
                
                # multi_load 是列表，遍历每个元素
                for multi_load in multi_load_list:
                    # 处理 multi_load 可能是列表的情况
                    if isinstance(multi_load, list):
                        for ml_item in multi_load:
                            if isinstance(ml_item, dict):
                                items.extend(self._extract_from_multi_load_item(ml_item))
                    elif isinstance(multi_load, dict):
                        items.extend(self._extract_from_multi_load_item(multi_load))
                    
        except Exception as e:
            self.log(f"提取结构化商品数据失败: {e}")
        
        return items
    
    def _extract_from_multi_load_item(self, multi_load: Dict) -> List[Dict]:
        """从单个 multi_load 项中提取商品数据"""
        items = []
        try:
            content_data = multi_load.get('content', {})
            if not isinstance(content_data, dict):
                return items
            result_data = content_data.get('resultData', {})
            # searchShopItems 是列表，每个元素是一个店铺
            search_shop_items = result_data.get('searchShopItems', [])
            # 从 resultData 层级获取 recommendType（适用于整个结果集）
            recommend_type = result_data.get('recommendType', '')
            
            for shop in search_shop_items:
                if not isinstance(shop, dict):
                    continue
                # 从店铺中提取商品列表
                gui_item_list = shop.get('guiItemList', [])
                shop_name = shop.get('shopName', '')
                shop_rating = shop.get('rating', '')
                shop_distance = shop.get('distance', '')
                
                for item in gui_item_list:
                    if not isinstance(item, dict):
                        continue
                    extracted_item = {
                        "itemName": item.get("itemName", ""),
                        "price": item.get("price", ""),
                        "llmRelevantLevelScore": item.get("llmRelevantLevelScore", ""),
                        "brandName": item.get("brandName", ""),
                        "distance": shop_distance,
                        "shopName": shop_name,
                        "rating": shop_rating,
                        "recommendType": recommend_type
                    }
                    # 只添加有有效数据的项
                    if extracted_item["itemName"]:
                        items.append(extracted_item)
        except Exception as e:
            self.log(f"提取单个 multi_load 项失败: {e}")
        
        return items
    
    def _generate_summary_from_items(self, items: List[Dict]) -> str:
        """从结构化商品数据生成文本摘要"""
        if not items:
            return ""
        
        summary_parts = []
        summary_parts.append(f"为您找到 {len(items)} 个相关商品：\\n")
        
        for i, item in enumerate(items[:5], 1):  # 最多显示5个
            name = item.get('itemName', '')
            price = item.get('price', '')
            shop = item.get('shopName', '')
            distance = item.get('distance', '')
            rating = item.get('rating', '')
            
            parts = [f"{i}. {name}"]
            if price:
                parts.append(f"价格：{price}元")
            if shop:
                parts.append(f"店铺：{shop}")
            if distance:
                parts.append(f"距离：{distance}m")
            if rating:
                parts.append(f"评分：{rating}")
            
            summary_parts.append("，".join(parts))
        
        if len(items) > 5:
            summary_parts.append(f"\\n...还有 {len(items) - 5} 个商品")
        
        return "\\n".join(summary_parts)
    
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
