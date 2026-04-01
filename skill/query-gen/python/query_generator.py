#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Query Generator V2 - 改进版，支持更丰富的表达方式
"""

import random
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple


@dataclass
class GeneratedQuery:
    """生成的 Query 对象"""
    query: str
    persona: str
    scene: str
    intent: str
    complexity: str
    emotion_level: str
    expected_focus: List[str] = field(default_factory=list)
    context: Dict = field(default_factory=dict)  # 新增：存储生成上下文

    def to_dict(self):
        return {
            'query': self.query,
            'persona': self.persona,
            'scene': self.scene,
            'intent': self.intent,
            'complexity': self.complexity,
            'emotion_level': self.emotion_level,
            'expected_focus': self.expected_focus,
            'context': self.context
        }


@dataclass
class PersonaTemplate:
    """人设模板 - V2 增强版"""
    id: str
    name: str
    emotion_level: str
    # 句子模板 - 支持更复杂的结构
    sentence_patterns: List[str]
    # 各种词汇库
    time_words: List[str]
    location_constraints: List[str]  # 地理位置约束
    brand_preferences: List[str]  # 品牌偏好表达
    quality_indicators: List[str]  # 质量指标
    urgency_indicators: List[str]  # 紧急程度表达
    polite_phrases: List[str]  # 礼貌用语
    emotional_phrases: List[str]  # 情感表达
    action_verbs: List[str]  # 动作动词
    price_ranges: List[str] = field(default_factory=list)  # 价格范围（新增）


@dataclass
class Scene:
    """场景定义 - V2 增强版"""
    name: str
    needs: List[str]
    sub_needs: Dict[str, List[str]]  # 子需求，如奶粉->["飞鹤", "美赞臣"]
    brands: Dict[str, List[str]]  # 各需求对应的品牌
    decision_factors: List[str]


class QueryGenerator:
    """Query 生成器"""

    def __init__(self):
        self.personas: Dict[str, PersonaTemplate] = {}
        self.scenes: Dict[str, Scene] = {}
        self.random = random.Random()
        self._init_personas()
        self._init_scenes()

    def generate_single(self, persona_name: str, scene_name: str,
                       need: Optional[str] = None) -> GeneratedQuery:
        """生成单个 Query"""
        persona = self.personas.get(persona_name)
        if not persona:
            raise ValueError(f"未知人设：{persona_name}")

        scene = self.scenes.get(scene_name)
        if not scene:
            raise ValueError(f"未知场景：{scene_name}")

        # 选择需求
        if need is None:
            need = self._random_select(scene.needs)

        # 构建 query 组件
        components = self._build_query_components(persona, scene, need)

        # 组装 query
        query = self._assemble_query(components, persona)
        query = self._clean_query(query)

        # 确定复杂度
        complexity = "高" if len(query) > 25 else ("中" if len(query) > 15 else "低")

        # 确定评测重点
        expected_focus = self._determine_focus(query, scene, components)

        return GeneratedQuery(
            query=query,
            persona=persona_name,
            scene=scene_name,
            intent=need,
            complexity=complexity,
            emotion_level=persona.emotion_level,
            expected_focus=expected_focus,
            context=components
        )

    def generate_batch(self, persona_name: str, scene_name: str,
                      count: int = 10) -> List[GeneratedQuery]:
        """批量生成 Query"""
        return [
            self.generate_single(persona_name, scene_name)
            for _ in range(count)
        ]

    def generate_multi_persona(self, persona_names: List[str], scene_name: str,
                              count_per_persona: int = 5) -> Dict[str, List[GeneratedQuery]]:
        """多人群对比生成"""
        results = {}
        for persona_name in persona_names:
            results[persona_name] = self.generate_batch(
                persona_name, scene_name, count_per_persona
            )
        return results

    def get_all_persona_names(self) -> List[str]:
        """获取所有人设名称"""
        return list(self.personas.keys())

    def get_all_scene_names(self) -> List[str]:
        """获取所有场景名称"""
        return list(self.scenes.keys())

    def _build_query_components(self, persona: PersonaTemplate,
                               scene: Scene, need: str) -> Dict:
        """构建 query 的各个组件"""
        components = {
            'situation': '',  # 情境描述
            'need': need,     # 核心需求
            'spec': '',       # 具体规格/型号
            'constraint': '', # 约束条件
            'brand': '',      # 品牌要求
            'location': '',   # 地理位置
            'delivery': '',   # 配送要求（新增）
            'time': '',       # 时间要求
            'polite': '',     # 礼貌用语
            'emotion': '',    # 情感表达
            'action': ''      # 动作动词
        }

        # 根据人设特征填充组件

        # 1. 情境描述 - 所有人设都可能有情境
        if persona.id == "P001":  # 新手焦虑型妈妈 - 85% 概率
            situations = [
                "孩子发烧", "宝宝不舒服", "小孩拉肚子", "孩子咳嗽", "宝宝过敏了"
            ]
            if random.random() < 0.85:
                components['situation'] = self._random_select(situations)
        
        elif persona.id == "P002":  # 效率实用型妈妈 - 40% 概率
            situations = ["今天", "现在", "马上", ""]
            time_context = random.choice(situations)
            if time_context:
                components['situation'] = time_context
        
        elif persona.id == "P003":  # 品质追求型妈妈 - 50% 概率
            situations = ["想给宝宝最好的", "为了宝宝健康", "注重品质", ""]
            if random.random() < 0.5:
                components['situation'] = self._random_select(situations)
        
        elif persona.id == "P004":  # 价格敏感型妈妈 - 40% 概率
            situations = ["想趁活动买", "有促销吗", "想找实惠的", ""]
            if random.random() < 0.4:
                components['situation'] = self._random_select(situations)
        
        elif persona.id == "P005":  # 社交分享型妈妈 - 60% 概率
            situations = ["看大家都在用", "朋友推荐的", "网上很火的", "最近流行的", ""]
            if random.random() < 0.6:
                components['situation'] = self._random_select(situations)
        
        elif persona.id == "P006":  # 谨慎保守型老人 - 70% 概率
            situations = ["担心被骗", "怕不靠谱", "想要有保障的", "不太会用", ""]
            if random.random() < 0.7:
                components['situation'] = self._random_select(situations)
        
        elif persona.id == "P007":  # 求助依赖型老人 - 75% 概率
            situations = ["不会弄", "不知道怎么选", "第一次买", "儿女不在身边", ""]
            if random.random() < 0.75:
                components['situation'] = self._random_select(situations)
        
        elif persona.id == "P008":  # 潮流探索型 Z 世代 - 50% 概率
            situations = ["想试试新的", "跟风入", "种草很久了", "网红同款", ""]
            if random.random() < 0.5:
                components['situation'] = self._random_select(situations)

        # 2. 具体规格/型号（让需求更明确）- 70% 概率
        if need in scene.sub_needs and random.random() < 0.7:
            spec = self._random_select(scene.sub_needs[need])
            components['spec'] = spec

        # 3. 地理位置约束 - 提高到 80%
        if random.random() < 0.8:
            distance = random.choice(["3公里", "5公里", "10公里", "附近", "周边"])
            components['location'] = f"{distance}内"

        # 3.5 配送相关约束（所有场景都适用）- 提高到 60%
        if random.random() < 0.6:
            delivery_constraints = [
                "30分钟达", "1小时达", "2小时达", "当日达", "次日达",
                "急送", "快送", "同城配送", "小时达"
            ]
            components['delivery'] = random.choice(delivery_constraints)

        # 4. 品牌要求（针对特定需求）- 提高到 90%
        if need in scene.brands and random.random() < 0.9:
            brand = self._random_select(scene.brands[need])
            components['brand'] = brand

        # 5. 礼貌用语
        if persona.polite_phrases and random.random() < 0.3:
            components['polite'] = self._random_select(persona.polite_phrases)

        # 6. 情感表达 - 所有人设都可能有情感，不同人设概率不同
        if persona.emotional_phrases:
            emotion_prob = 0.5  # 默认 50%
            if persona.id == "P001":
                emotion_prob = 0.7  # 新手焦虑型妈妈 70%
            elif persona.id == "P003":
                emotion_prob = 0.6  # 品质追求型妈妈 60%
            elif persona.id == "P005":
                emotion_prob = 0.6  # 社交分享型妈妈 60%
            elif persona.id == "P006":
                emotion_prob = 0.6  # 谨慎保守型老人 60%
            elif persona.id == "P007":
                emotion_prob = 0.7  # 求助依赖型老人 70%
            elif persona.id == "P008":
                emotion_prob = 0.5  # 潮流探索型 Z 世代 50%
            
            if random.random() < emotion_prob:
                components['emotion'] = self._random_select(persona.emotional_phrases)

        # 7. 动作动词
        if persona.action_verbs:
            components['action'] = self._random_select(persona.action_verbs)

        # 8. 时间要求
        if random.random() < 0.3:
            time_req = random.choice([" urgent", "尽快", "今天", "现在", "马上"])
            components['time'] = time_req

        # 9. 价格范围（所有场景适用，不同人设概率不同）- 整体提高概率
        price_range_prob = 0.5  # 默认从 30% 提高到 50%
        if persona.id == "P004":  # 价格敏感型妈妈更高概率
            price_range_prob = 0.8  # 从 60% 提高到 80%
        elif persona.id == "P003":  # 品质追求型妈妈较低概率
            price_range_prob = 0.4  # 从 20% 提高到 40%
        
        if persona.price_ranges and random.random() < price_range_prob:
            components['price_range'] = self._random_select(persona.price_ranges)

        return components

    def _assemble_query(self, components: Dict, persona: PersonaTemplate) -> str:
        """根据组件组装 query - 使用更自然的表达方式"""

        # 根据人设选择不同的组装策略
        if persona.id == "P001":  # 新手焦虑型妈妈
            return self._assemble_anxious_mom_query(components)
        elif persona.id == "P002":  # 效率实用型妈妈
            return self._assemble_efficient_mom_query(components)
        elif persona.id == "P003":  # 品质追求型妈妈
            return self._assemble_quality_mom_query(components)
        else:
            # 默认策略
            return self._assemble_default_query(components, persona)

    def _assemble_anxious_mom_query(self, components: Dict) -> str:
        """组装新手焦虑型妈妈的 query"""

        # 清理空值
        c = {k: (v if v else "") for k, v in components.items()}

        # 构建完整需求（规格 + 需求）
        full_need = c['need']
        if c['spec']:
            full_need = c['spec'] + c['need']
        c['need'] = full_need

        # 品牌需要加"的"
        if c['brand']:
            c['brand'] = c['brand'] + "的"

        # 位置需要处理 - 规范化表达
        if c['location']:
            # 清理 "附近内" 这种重复
            c['location'] = c['location'].replace("附近内", "附近")
            c['location'] = c['location'].replace("周边内", "周边")
            # 确保 "X公里内" 格式正确
            if "公里" in c['location'] and not c['location'].endswith("内"):
                c['location'] = c['location'] + "内"

        # 处理配送要求
        delivery_part = ""
        if c['delivery']:
            delivery_part = f"，要求{c['delivery']}"

        # 处理价格范围
        price_part = ""
        if c.get('price_range'):
            price_part = f"{c['price_range']}"

        patterns = [
            # 情境 + 动作 + 品牌 + 价格 + 完整需求 + 位置 + 配送 + 礼貌
            lambda c: f"{c['situation']}，{c['action']}{c['brand']}{price_part}{c['need']}{c['location']}{delivery_part}{c['polite']}",
            # 情境 + 情感 + 动作 + 价格 + 完整需求 + 位置 + 配送
            lambda c: f"{c['situation']}，{c['emotion']}，{c['action']}{price_part}{c['need']}{c['location']}{delivery_part}",
            # 时间 + 情境 + 动作 + 品牌 + 价格 + 完整需求 + 配送
            lambda c: f"{c['time']}{c['situation']}，{c['action']}{c['brand']}{price_part}{c['need']}{delivery_part}",
            # 动作 + 品牌 + 价格 + 完整需求 + 位置 + 配送 + 礼貌
            lambda c: f"{c['action']}{c['brand']}{price_part}{c['need']}{c['location']}{delivery_part}{c['polite']}",
            # 情境 + 动作 + 价格 + 完整需求 + 位置 + 配送
            lambda c: f"{c['situation']}，{c['action']}{price_part}{c['need']}{c['location']}{delivery_part}",
        ]

        # 选择模板并组装
        pattern = self._random_select(patterns)
        query = pattern(c)

        # 清理多余的标点
        query = query.replace("，，", "，")
        query = query.replace("  ", " ")
        query = query.strip("，")

        return query

    def _assemble_efficient_mom_query(self, components: Dict) -> str:
        """组装效率实用型妈妈的 query"""
        c = {k: (v if v else "") for k, v in components.items()}

        # 如果有价格范围，加入价格因素
        if c.get('price_range'):
            patterns = [
                lambda c: f"{c['time']}{c['price_range']}{c['need']}{c['location']}",
                lambda c: f"{c['action']}{c['price_range']}{c['need']}{c['location']}",
                lambda c: f"{c['price_range']}{c['need']}{c['location']}",
            ]
        else:
            patterns = [
                lambda c: f"{c['time']}{c['need']}{c['location']}",
                lambda c: f"{c['action']}{c['need']}{c['location']}",
                lambda c: f"{c['need']}{c['location']}",
            ]

        pattern = self._random_select(patterns)
        query = pattern(c)
        return query.strip()

    def _assemble_quality_mom_query(self, components: Dict) -> str:
        """组装品质追求型妈妈的 query"""
        c = {k: (v if v else "") for k, v in components.items()}

        if c['brand']:
            c['brand'] = c['brand'] + "的"

        # 如果有价格范围，加入价格因素
        if c.get('price_range'):
            patterns = [
                lambda c: f"求推荐{c['price_range']}{c['brand']}{c['need']}",
                lambda c: f"想{c['action']}{c['price_range']}{c['brand']}{c['need']}",
                lambda c: f"{c['price_range']}{c['brand']}{c['need']}哪个好",
            ]
        else:
            patterns = [
                lambda c: f"求推荐{c['brand']}{c['need']}",
                lambda c: f"想{c['action']}{c['brand']}{c['need']}",
                lambda c: f"{c['need']}哪个{c['brand']}好",
            ]

        pattern = self._random_select(patterns)
        query = pattern(c)
        return query.strip()

    def _assemble_default_query(self, components: Dict, persona: PersonaTemplate) -> str:
        """默认组装策略"""
        # 价格敏感型妈妈使用特殊处理
        if persona.id == "P004":
            return self._assemble_price_sensitive_query(components, persona)

        template = self._random_select(persona.sentence_patterns)
        
        # 替换所有可能的占位符
        query = template
        query = query.replace("{需求}", components.get('need', ''))
        query = query.replace("{位置}", components.get('location', ''))
        query = query.replace("{品牌}", components.get('brand', ''))
        query = query.replace("{动作}", components.get('action', ''))
        query = query.replace("{情境}", components.get('situation', ''))
        query = query.replace("{时间}", components.get('time', ''))
        query = query.replace("{礼貌}", components.get('polite', ''))
        query = query.replace("{情感}", components.get('emotion', ''))
        query = query.replace("{价格范围}", components.get('price_range', ''))
        
        return query

    def _assemble_price_sensitive_query(self, components: Dict, persona: PersonaTemplate) -> str:
        """组装价格敏感型妈妈的 query"""
        c = {k: (v if v else "") for k, v in components.items()}

        # 如果有价格范围，使用包含价格的模板
        if c.get('price_range'):
            patterns = [
                lambda c: f"{c['price_range']}{c['need']}推荐一下",
                lambda c: f"{c['need']}{c['price_range']}有吗",
                lambda c: f"想买{c['price_range']}的{c['need']}",
                lambda c: f"{c['price_range']}的{c['need']}哪里买",
            ]
            pattern = self._random_select(patterns)
            return pattern(c)
        else:
            # 没有价格范围时使用默认模板
            patterns = [
                lambda c: f"{c['need']}哪里便宜",
                lambda c: f"求推荐性价比高的{c['need']}",
                lambda c: f"{c['need']}有优惠吗",
            ]
            pattern = self._random_select(patterns)
            return pattern(c)

    def _clean_query(self, query: str) -> str:
        """清理 Query"""
        query = query.strip()

        # 移除多余的标点
        query = query.replace("，，", "，")
        query = query.replace("  ", " ")

        # 处理 urgent
        if "urgent" in query.lower():
            query = query.replace("urgent", " urgent ")
            query = " ".join(query.split())
            if not query.startswith("urgent"):
                query = query.replace("urgent", "").strip()
                query = "urgent " + query

        return query.strip()

    def _determine_focus(self, query: str, scene: Scene, components: Dict) -> List[str]:
        """确定评测重点"""
        focus = []

        if "urgent" in query or "尽快" in query or "马上" in query:
            focus.append("响应速度")

        if "公里" in query or "附近" in query or "周边" in query:
            focus.append("地理位置")

        if any(brand in query for brand in ["飞鹤", "美赞臣", "惠氏", "雅培", "贝因美"]):
            focus.append("品牌匹配")

        if "靠谱" in query or "正规" in query or "安全" in query:
            focus.append("可信度")

        if not focus:
            focus = scene.decision_factors[:2]

        return focus

    def _init_personas(self):
        """初始化人设库 - V2"""

        # 1. 新手焦虑型妈妈
        self.personas["新手焦虑型妈妈"] = PersonaTemplate(
            id="P001",
            name="新手焦虑型妈妈",
            emotion_level="高",
            sentence_patterns=[
                "{情境}，{时间}{动作}{需求}{品牌}{位置}{礼貌}",
                "{情境}，求推荐{品牌}{需求}{位置}{礼貌}",
                "{时间}{情境}，{动作}{品牌}{需求}{位置}"
            ],
            time_words=[" urgent", "尽快", "现在", "今天", ""],
            location_constraints=["3公里内", "5公里内", "10公里内", "附近", "周边", "就近"],
            brand_preferences=["品牌的", "大牌", "知名", ""],
            quality_indicators=["靠谱的", "安全的", "正规的", "口碑好的"],
            urgency_indicators=[" urgent", "急需", "紧急", "快"],
            polite_phrases=["辛苦推荐", "麻烦推荐一下", "求推荐", "谢谢"],
            emotional_phrases=["着急", "担心", "焦虑", "不知道怎么办"],
            action_verbs=["推荐", "找", "需要", "想买"],
            price_ranges=["100元以内", "200元以内", "300元以内", "实惠的", "性价比高的"]
        )

        # 2. 效率实用型妈妈
        self.personas["效率实用型妈妈"] = PersonaTemplate(
            id="P002",
            name="效率实用型妈妈",
            emotion_level="中",
            sentence_patterns=[
                "{需求}{位置}",
                "{时间}{需求}{位置}",
                "{动作}{需求}"
            ],
            time_words=[" urgent", "现在", "马上", ""],
            location_constraints=["附近", "周边", "就近", "不要太远"],
            brand_preferences=["", ""],
            quality_indicators=["快的", "方便的", ""],
            urgency_indicators=[" urgent", "快"],
            polite_phrases=[""],
            emotional_phrases=[""],
            action_verbs=["找", "需要", "要"],
            price_ranges=["200元以内", "300元以内", "500元以内", "1000元以内", "性价比高的"]
        )

        # 3. 品质追求型妈妈
        self.personas["品质追求型妈妈"] = PersonaTemplate(
            id="P003",
            name="品质追求型妈妈",
            emotion_level="中",
            sentence_patterns=[
                "求推荐{品牌}{需求}",
                "想{动作}{品牌}{需求}",
                "{需求}哪个品牌好"
            ],
            time_words=["周末", "假期", ""],
            location_constraints=["环境好的", "高端的", ""],
            brand_preferences=["进口", "高端", "大牌", "知名"],
            quality_indicators=["高品质的", "专业的", "口碑好的"],
            urgency_indicators=[""],
            polite_phrases=["求推荐", "推荐一下"],
            emotional_phrases=["注重品质", "追求体验"],
            action_verbs=["买", "选", "推荐"],
            price_ranges=["300元以内", "500元以内", "1000元以内", "2000元以内", "高品质的"]
        )

        # 4. 价格敏感型妈妈
        self.personas["价格敏感型妈妈"] = PersonaTemplate(
            id="P004",
            name="价格敏感型妈妈",
            emotion_level="低",
            sentence_patterns=[
                "{需求}哪里便宜",
                "求推荐性价比高的{需求}",
                "{需求}有优惠吗",
                "{价格范围}{需求}推荐一下",
                "{需求}{价格范围}有吗",
                "想买{价格范围}的{需求}"
            ],
            time_words=[""],
            location_constraints=["附近的", ""],
            brand_preferences=["性价比高的", ""],
            quality_indicators=["实惠的", "划算的"],
            urgency_indicators=[""],
            polite_phrases=["求推荐"],
            emotional_phrases=[""],
            action_verbs=["找", "买"],
            # 新增：价格范围词汇
            price_ranges=["50元以内", "100元以内", "200元以内", "300元以内", "500元以内",
                         "50块左右", "100块左右", "200块左右", "便宜点", "实惠的", "平价的"]
        )

        # 5. 社交分享型妈妈
        self.personas["社交分享型妈妈"] = PersonaTemplate(
            id="P005",
            name="社交分享型妈妈",
            emotion_level="高",
            sentence_patterns=[
                "求安利{需求}",
                "想{动作}{需求}",
                "{需求}求推荐"
            ],
            time_words=["周末", "明天", ""],
            location_constraints=["网红", "热门的", ""],
            brand_preferences=["网红", "热门"],
            quality_indicators=["好玩的", "适合拍照的"],
            urgency_indicators=[""],
            polite_phrases=["求安利", "推荐一下"],
            emotional_phrases=["想试试", "跟风"],
            action_verbs=["打卡", "体验", "试试"],
            price_ranges=["100元以内", "200元以内", "300元以内", "500元以内",
                         "100块左右", "200块左右", "性价比高的"]
        )

        # 6. 谨慎保守型老人
        self.personas["谨慎保守型老人"] = PersonaTemplate(
            id="P006",
            name="谨慎保守型老人",
            emotion_level="高",
            sentence_patterns=[
                "{需求}{位置}正规吗",
                "{位置}{需求}可靠吗",
                "想找正规的{需求}"
            ],
            time_words=[" urgent", "今天", ""],
            location_constraints=["附近的", "正规的", ""],
            brand_preferences=["老牌子", "知名的", ""],
            quality_indicators=["正规的", "有保障的", "可靠的"],
            urgency_indicators=[" urgent"],
            polite_phrases=["麻烦", "请"],
            emotional_phrases=["担心被骗", "怕不靠谱"],
            action_verbs=["找", "需要"],
            price_ranges=["50元以内", "100元以内", "200元以内", "实惠的", "便宜的"]
        )

        # 7. 求助依赖型老人
        self.personas["求助依赖型老人"] = PersonaTemplate(
            id="P007",
            name="求助依赖型老人",
            emotion_level="高",
            sentence_patterns=[
                "帮帮忙{动作}{需求}",
                "我不会{动作}{需求}，帮帮我",
                "想{需求}，{位置}怎么办"
            ],
            time_words=[" urgent", ""],
            location_constraints=["附近的", "简单的", ""],
            brand_preferences=[""],
            quality_indicators=["简单的", "方便的"],
            urgency_indicators=[" urgent"],
            polite_phrases=["帮帮忙", "帮帮我", "麻烦"],
            emotional_phrases=["不会弄", "不知道怎么"],
            action_verbs=["找", "弄", "办"],
            price_ranges=["50元以内", "100元以内", "便宜的", "实惠的"]
        )

        # 8. 潮流探索型 Z 世代
        self.personas["潮流探索型 Z 世代"] = PersonaTemplate(
            id="P008",
            name="潮流探索型 Z 世代",
            emotion_level="中",
            sentence_patterns=[
                "求安利{需求}",
                "想冲{需求}",
                "{需求}怎么样"
            ],
            time_words=["今晚", "周末", ""],
            location_constraints=["网红", "出片的", "氛围感", ""],
            brand_preferences=["小众", "网红", "潮牌"],
            quality_indicators=["出片的", "氛围感", "小众的"],
            urgency_indicators=[""],
            polite_phrases=["求安利"],
            emotional_phrases=["想试试", "种草"],
            action_verbs=["冲", "打卡", "体验"],
            price_ranges=["100元以内", "200元以内", "300元以内", "500元以内",
                         "100块左右", "200块左右", "性价比高的"]
        )

    def _init_scenes(self):
        """初始化场景库 - V2"""
        self.scenes = {
            "医药健康": Scene("医药健康",
                ["退烧药", "感冒药", "过敏药", "益生菌", "维生素", "钙片", "口罩", "体温计", "血压计", "血糖仪", "药店"],
                {
                    "退烧药": ["布洛芬", "对乙酰氨基酚", "美林", "泰诺林", "小儿退热栓", "退热贴"],
                    "感冒药": ["小儿氨酚黄那敏", "999感冒灵", "板蓝根", "连花清瘟", "蒲地蓝", "小柴胡", "抗病毒口服液"],
                    "过敏药": ["氯雷他定", "西替利嗪", "扑尔敏", "孟鲁司特钠"],
                    "益生菌": ["妈咪爱", "合生元", "康萃乐", "Life-Space", "培菲康", "金双歧"],
                    "维生素": ["D3", "AD", "复合", "DHA", "C", "B"],
                    "钙片": ["钙尔奇", "迪巧", "朗迪", "Swisse", "葡萄糖酸钙", "乳钙"],
                    "口罩": ["N95", "医用外科", "儿童口罩", "KN95", "一次性医用"],
                    "体温计": ["电子", "耳温", "额温", "水银", "红外"],
                    "血压计": ["欧姆龙", "鱼跃", "可孚", "电子血压计", "手腕式", "上臂式"],
                    "血糖仪": ["罗氏", "强生", "欧姆龙", "鱼跃", "三诺", "艾科"],
                    "药店": ["24小时", "连锁", "医保定点", "网上药店"]
                },
                {
                    "退烧药": ["强生", "美林", "泰诺林", "仁和", "葵花药业", "哈药", "修正"],
                    "感冒药": ["999", "白云山", "以岭", "仁和", "同仁堂", "香雪", "云南白药"],
                    "过敏药": ["开瑞坦", "息斯敏", "仙特明", "顺尔宁", "贝分"],
                    "益生菌": ["合生元", "妈咪爱", "康萃乐", "Life-Space", "培菲康", "金双歧", "拜奥"],
                    "维生素": ["伊可新", "星鲨", "汤臣倍健", "Swisse", "善存", "21金维他"],
                    "钙片": ["钙尔奇", "迪巧", "朗迪", "Swisse", "三精", "龙牡"],
                    "口罩": ["稳健", "振德", "3M", "霍尼韦尔", "袋鼠医生", "可孚", "海氏海诺"],
                    "体温计": ["博朗", "欧姆龙", "鱼跃", "可孚", "迈克大夫", "华盛昌"],
                    "血压计": ["欧姆龙", "鱼跃", "可孚", "松下", "九安", "乐心"],
                    "血糖仪": ["罗氏", "强生", "欧姆龙", "鱼跃", "三诺", "艾科", "雅培"],
                    "药店": ["海王星辰", "老百姓大药房", "国大药房", "同仁堂", "大参林", "益丰大药房", "一心堂", "叮当快药"]
                },
                ["正品保障", "配送速度", "价格", "品牌信赖"]),

            "母婴用品": Scene("母婴用品",
                ["奶粉", "纸尿裤", "辅食", "玩具", "童装", "婴儿车"],
                {
                    "奶粉": ["1段", "2段", "3段", "羊奶", "有机", "水解蛋白"],
                    "纸尿裤": ["NB码", "S码", "M码", "L码", "拉拉裤", "超薄透气", "夜用"],
                    "辅食": ["6个月", "9个月", "12个月", "高铁", "无添加", "有机"],
                    "玩具": ["益智", "积木", "毛绒", "早教", "安抚", "咬胶"],
                    "童装": ["纯棉", "加厚", "连体", "分体", "0-3个月", "3-6个月"],
                    "婴儿车": ["轻便", "可躺", "双向", "高景观", "一键收车", "避震"]
                },
                {
                    "奶粉": ["飞鹤", "美赞臣", "惠氏", "雅培", "贝因美", "爱他美", "雀巢", "伊利"],
                    "纸尿裤": ["花王", "帮宝适", "好奇", "尤妮佳", "大王"],
                    "辅食": ["嘉宝", "亨氏", "小皮", "贝拉米"],
                    "玩具": ["费雪", "乐高", "伟易达", "面包超人"],
                    "童装": ["英氏", "巴拉巴拉", "丽婴房", "全棉时代"],
                    "婴儿车": ["好孩子", "昆塔斯", "虎贝尔", "bebebus"]
                },
                ["品牌正品", "价格", "配送速度"]),

            "餐饮外卖": Scene("餐饮外卖",
                ["儿童餐", "营养餐", "辅食", "月子餐", "亲子餐厅", "外卖", "快餐"],
                {},
                {},
                ["配送速度", "餐品质量", "适龄性"]),

            "教育早教": Scene("教育早教",
                ["早教中心", "托班", "兴趣班", "幼儿园", "亲子活动", "游泳", "英语"],
                {},
                {},
                ["师资", "环境", "口碑"]),

            "生活服务": Scene("生活服务",
                ["保洁", "月嫂", "育儿嫂", "儿童摄影", "维修", "洗衣"],
                {},
                {},
                ["专业性", "安全性", "价格"]),

            "休闲娱乐": Scene("休闲娱乐",
                ["儿童乐园", "亲子游", "游泳馆", "绘本馆", "亲子酒店", "游乐场", "动物园"],
                {},
                {},
                ["好玩", "安全", "特色"]),

            "社区服务": Scene("社区服务",
                ["社区医院", "老年食堂", "便民超市", "快递代收", "理发", "维修"],
                {},
                {},
                ["方便", "便宜", "近"]),

            "便民生活": Scene("便民生活",
                ["缴费", "充值", "查询", "预约", "办事", "咨询"],
                {},
                {},
                ["简单", "方便", "有人帮"]),

            "新潮服务": Scene("新潮服务",
                ["剧本杀", "密室", "VR", "电竞", "自拍馆", "猫咖", "潮玩"],
                {},
                {},
                ["好玩", "出片", "氛围"])
        }

    def _random_select(self, items: List[str]) -> Optional[str]:
        """随机选择"""
        if not items:
            return None
        return self.random.choice(items)


if __name__ == "__main__":
    # 演示使用
    generator = QueryGeneratorV2()

    print("=" * 70)
    print("Query Generator V2 演示")
    print("=" * 70)

    # 示例 1: 新手焦虑型妈妈 - 医疗健康
    print("\n【示例 1】新手焦虑型妈妈 - 医疗健康（药店）")
    for i in range(5):
        result = generator.generate_single("新手焦虑型妈妈", "医疗健康", need="药店")
        print(f"  {i+1}. {result.query}")
        if result.context.get('situation'):
            print(f"     情境: {result.context['situation']}")

    # 示例 2: 新手焦虑型妈妈 - 母婴用品（奶粉）
    print("\n【示例 2】新手焦虑型妈妈 - 母婴用品（奶粉）")
    for i in range(5):
        result = generator.generate_single("新手焦虑型妈妈", "母婴用品", need="奶粉")
        print(f"  {i+1}. {result.query}")
        if result.context.get('brand'):
            print(f"     品牌: {result.context['brand']}")

    # 示例 3: 效率实用型妈妈
    print("\n【示例 3】效率实用型妈妈 - 医疗健康")
    for i in range(3):
        result = generator.generate_single("效率实用型妈妈", "医疗健康")
        print(f"  {i+1}. {result.query}")

    print("\n" + "=" * 70)
    print("演示完成!")
    print("=" * 70)
