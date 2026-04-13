#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
品类(Category)生成 Agent
基于即时零售场景生成多样化商品品类
"""

from typing import Dict, List, Optional
from .base_agent import BaseAgent


class CategoryAgent(BaseAgent):
    """
    商品品类生成Agent
    负责生成即时零售场景下的多样化商品品类
    """

    # 预定义的品类模板
    CATEGORY_TEMPLATES = {
        "C1": {
            "id": "C1",
            "name": "生鲜果蔬",
            "description": "新鲜蔬菜、水果、肉类、海鲜等生鲜食品",
            "subcategories": [
                "叶菜类", "根茎类", "菌菇类", "瓜果类",
                "柑橘类", "浆果类", "热带水果", "时令水果",
                "猪肉", "牛肉", "羊肉", "禽类", "海鲜水产"
            ],
            "characteristics": [
                "时效性要求极高",
                "品质敏感",
                "保质期短",
                "需要冷链"
            ],
            "typical_products": [
                "有机蔬菜", "进口水果", "冷鲜肉", "活鲜"
            ],
            "price_range": "10-200元",
            "delivery_requirement": "30-60分钟",
            "priority": "P0"
        },
        "C2": {
            "id": "C2",
            "name": "休闲零售",
            "description": "零食、饮料、糖果、坚果等休闲食品",
            "subcategories": [
                "膨化食品", "糖果巧克力", "坚果炒货", "肉干肉脯",
                "饼干糕点", "果冻布丁", "饮料", "茶饮咖啡"
            ],
            "characteristics": [
                "冲动消费多",
                "品牌敏感",
                "复购率高",
                "场景化需求"
            ],
            "typical_products": [
                "进口零食", "网红零食", "健康零食", "功能饮料"
            ],
            "price_range": "5-100元",
            "delivery_requirement": "30分钟",
            "priority": "P1"
        },
        "C3": {
            "id": "C3",
            "name": "3C数码",
            "description": "手机配件、电脑配件、智能设备等数码产品",
            "subcategories": [
                "手机配件", "电脑配件", "充电设备", "耳机音箱",
                "智能穿戴", "摄影器材", "游戏设备", "办公设备"
            ],
            "characteristics": [
                "功能性导向",
                "品牌敏感",
                "价格较高",
                "技术参数重要"
            ],
            "typical_products": [
                "充电宝", "数据线", "蓝牙耳机", "手机壳",
                "键盘鼠标", "U盘存储", "智能手环"
            ],
            "price_range": "20-500元",
            "delivery_requirement": "30-60分钟",
            "priority": "P1"
        },
        "C4": {
            "id": "C4",
            "name": "母婴用品",
            "description": "婴儿食品、用品、玩具、护理等母婴相关产品",
            "subcategories": [
                "奶粉", "辅食", "纸尿裤", "婴儿湿巾",
                "婴儿洗护", "婴儿服饰", "玩具", "喂养用品"
            ],
            "characteristics": [
                "安全性要求极高",
                "品质敏感",
                "品牌忠诚度高",
                "应急需求多"
            ],
            "typical_products": [
                "进口奶粉", "有机辅食", "品牌纸尿裤", "婴儿湿巾",
                "奶瓶奶嘴", "婴儿推车", "安全座椅"
            ],
            "price_range": "30-500元",
            "delivery_requirement": "30分钟",
            "priority": "P0"
        },
        "C5": {
            "id": "C5",
            "name": "医药健康",
            "description": "药品、保健品、医疗器械等健康相关产品",
            "subcategories": [
                "感冒药", "止痛药", "消化药", "外用药",
                "维生素", "保健品", "医疗器械", "急救用品"
            ],
            "characteristics": [
                "安全合规要求极高",
                "时效性要求高",
                "专业性强",
                "需要药师指导"
            ],
            "typical_products": [
                "退烧药", "创可贴", "体温计", "维生素C",
                "口罩", "消毒液", "血压计", "血糖仪"
            ],
            "price_range": "10-300元",
            "delivery_requirement": "30分钟",
            "priority": "P0"
        },
        "C6": {
            "id": "C6",
            "name": "日用百货",
            "description": "洗护用品、清洁用品、纸品等日用商品",
            "subcategories": [
                "洗发护发", "沐浴露", "牙膏牙刷", "护肤品",
                "洗衣液", "清洁剂", "纸品", "家居用品"
            ],
            "characteristics": [
                "刚需高频",
                "品牌敏感",
                "囤货倾向",
                "价格敏感"
            ],
            "typical_products": [
                "洗发水", "沐浴露", "洗衣液", "抽纸",
                "牙膏", "护肤品", "清洁剂", "垃圾袋"
            ],
            "price_range": "10-200元",
            "delivery_requirement": "30-60分钟",
            "priority": "P1"
        },
        "C7": {
            "id": "C7",
            "name": "鲜花礼品",
            "description": "鲜花、蛋糕、礼品等情感表达类商品",
            "subcategories": [
                "玫瑰", "百合", "康乃馨", "混合花束",
                "生日蛋糕", "巧克力", "礼品盒", "贺卡"
            ],
            "characteristics": [
                "场景化需求强",
                "时效性要求高",
                "品质要求高",
                "情感价值高"
            ],
            "typical_products": [
                "红玫瑰花束", "生日蛋糕", "巧克力礼盒", "鲜花礼盒"
            ],
            "price_range": "50-500元",
            "delivery_requirement": "准时达",
            "priority": "P1"
        },
        "C8": {
            "id": "C8",
            "name": "宠物用品",
            "description": "宠物食品、用品、玩具、护理等宠物相关产品",
            "subcategories": [
                "猫粮", "狗粮", "宠物零食", "宠物玩具",
                "宠物用品", "宠物护理", "宠物药品", "宠物服饰"
            ],
            "characteristics": [
                "品质要求高",
                "品牌忠诚度高",
                "情感消费",
                "复购率高"
            ],
            "typical_products": [
                "进口猫粮", "天然狗粮", "宠物玩具", "猫砂",
                "宠物零食", "宠物洗护", "宠物牵引"
            ],
            "price_range": "20-300元",
            "delivery_requirement": "30-60分钟",
            "priority": "P2"
        }
    }

    def __init__(self, config: Dict = None):
        super().__init__("CategoryAgent", config)

    def generate(
        self,
        category_ids: Optional[List[str]] = None,
        priority_filter: Optional[str] = None,
        persona_id: Optional[str] = None,
        scenario_id: Optional[str] = None
    ) -> List[Dict]:
        """
        生成商品品类

        Args:
            category_ids: 指定品类ID列表，如 ["C5", "C4"]
            priority_filter: 按优先级过滤
            persona_id: 根据人群推荐适合的品类
            scenario_id: 根据场景推荐适合的品类

        Returns:
            品类列表
        """
        categories = []

        # 如果指定了人群和场景，推荐适合的品类
        if (persona_id or scenario_id) and not category_ids:
            categories = self._recommend_for_context(persona_id, scenario_id)
        elif category_ids:
            # 返回指定品类
            for cid in category_ids:
                if cid in self.CATEGORY_TEMPLATES:
                    categories.append(self.CATEGORY_TEMPLATES[cid].copy())
        else:
            # 返回所有品类
            for cid, category in self.CATEGORY_TEMPLATES.items():
                if priority_filter and category.get("priority") != priority_filter:
                    continue
                categories.append(category.copy())

        self.log(f"生成商品品类: {len(categories)}个")
        return categories

    def _recommend_for_context(
        self,
        persona_id: Optional[str] = None,
        scenario_id: Optional[str] = None
    ) -> List[Dict]:
        """根据人群和场景推荐品类"""
        # 人群品类偏好
        persona_category_map = {
            "P1": ["C5", "C2", "C6", "C3"],  # 白领：医药、零食、日用、数码
            "P2": ["C4", "C5", "C6", "C7"],  # 新手妈妈：母婴、医药、日用、礼品
            "P3": ["C2", "C1", "C6", "C3"],  # 大学生：零食、生鲜、日用、数码
            "P4": ["C1", "C7", "C2", "C6"],  # 精致白领：生鲜、礼品、零食、日用
            "P5": ["C1", "C5", "C6", "C2"],  # 退休阿姨：生鲜、医药、日用、零食
            "P6": ["C1", "C6", "C2", "C4"],  # 双职工：生鲜、日用、零食、母婴
        }

        # 场景品类偏好
        scenario_category_map = {
            "S1": ["C5", "C4", "C6", "C3"],  # 应急：医药、母婴、日用、数码
            "S2": ["C2", "C7", "C8", "C1"],  # 享受：零食、礼品、宠物、生鲜
            "S3": ["C1", "C6", "C5", "C2"],  # 便利：生鲜、日用、医药、零食
            "S4": ["C1", "C6", "C2", "C4"],  # 计划：生鲜、日用、零食、母婴
            "S5": ["C7", "C2", "C1", "C8"],  # 聚会：礼品、零食、生鲜、宠物
        }

        recommended_ids = set()

        if persona_id and persona_id in persona_category_map:
            recommended_ids.update(persona_category_map[persona_id])

        if scenario_id and scenario_id in scenario_category_map:
            recommended_ids.update(scenario_category_map[scenario_id])

        if not recommended_ids:
            recommended_ids = set(self.CATEGORY_TEMPLATES.keys())

        return [self.CATEGORY_TEMPLATES[cid].copy() for cid in recommended_ids]

    def get_category_by_id(self, category_id: str) -> Optional[Dict]:
        """根据ID获取品类"""
        return self.CATEGORY_TEMPLATES.get(category_id, {}).copy()

    def get_category_names(self) -> Dict[str, str]:
        """获取品类ID到名称的映射"""
        return {cid: c["name"] for cid, c in self.CATEGORY_TEMPLATES.items()}

    def get_subcategories(self, category_id: str) -> List[str]:
        """获取品类的子类目"""
        category = self.CATEGORY_TEMPLATES.get(category_id)
        if category:
            return category.get("subcategories", [])
        return []

    def execute(self, input_data: Dict) -> List[Dict]:
        """执行生成任务"""
        return self.generate(
            category_ids=input_data.get('category_ids'),
            priority_filter=input_data.get('priority_filter'),
            persona_id=input_data.get('persona_id'),
            scenario_id=input_data.get('scenario_id')
        )
