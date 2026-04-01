#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Query Generator - 基于数字人设的搜索 Query 自动生成工具
独立版本，无需外部依赖
"""

import random
from dataclasses import dataclass, field
from typing import List, Dict, Optional


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

    def to_dict(self):
        return {
            'query': self.query,
            'persona': self.persona,
            'scene': self.scene,
            'intent': self.intent,
            'complexity': self.complexity,
            'emotion_level': self.emotion_level,
            'expected_focus': self.expected_focus
        }


@dataclass
class PersonaTemplate:
    """人设模板"""
    id: str
    name: str
    emotion_level: str
    sentence_patterns: List[str]
    time_words: List[str]
    condition_words: List[str]
    question_words: List[str]
    status_words: List[str]
    action_words: List[str] = field(default_factory=list)


@dataclass
class Scene:
    """场景定义"""
    name: str
    needs: List[str]
    urgency_levels: List[str]
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
                       urgency: Optional[str] = None) -> GeneratedQuery:
        """生成单个 Query"""
        persona = self.personas.get(persona_name)
        if not persona:
            raise ValueError(f"未知人设：{persona_name}")

        scene = self.scenes.get(scene_name)
        if not scene:
            raise ValueError(f"未知场景：{scene_name}")

        # 选择需求
        need = self._random_select(scene.needs)

        # 填充模板
        template = self._random_select(persona.sentence_patterns)
        query = self._fill_template(template, persona, need, 
                                    urgency or self._random_select(scene.urgency_levels))
        query = self._clean_query(query)

        # 确定复杂度
        complexity = "高" if len(query) > 20 else ("中" if len(query) > 10 else "低")

        # 确定评测重点
        expected_focus = self._determine_focus(query, scene)

        return GeneratedQuery(
            query=query,
            persona=persona_name,
            scene=scene_name,
            intent=need,
            complexity=complexity,
            emotion_level=persona.emotion_level,
            expected_focus=expected_focus
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

    def _init_personas(self):
        """初始化人设库"""
        # 1. 新手焦虑型妈妈
        self.personas["新手焦虑型妈妈"] = PersonaTemplate(
            id="P001",
            name="新手焦虑型妈妈",
            emotion_level="高",
            sentence_patterns=[
                "{时间}{需求}哪里{好}{疑问}",
                "{时间}想{需求}{条件}{疑问}",
                "宝宝{状况}{时间}{需求}{条件}",
                "{时间}{需求}{条件}靠谱吗"
            ],
            time_words=["urgent", "urgent 求助", "现在", "今天", ""],
            condition_words=["附近", "口碑好的", "有经验的", ""],
            question_words=["有吗", "哪里好", "怎么办", "靠谱吗", "安全吗"],
            status_words=["发烧了", "拉肚子", "不舒服", ""],
            action_words=[]
        )

        # 2. 效率实用型妈妈
        self.personas["效率实用型妈妈"] = PersonaTemplate(
            id="P002",
            name="效率实用型妈妈",
            emotion_level="中",
            sentence_patterns=[
                "{需求}{条件}",
                "{时间}{需求}{条件}",
                "不想{动作}{需求}"
            ],
            time_words=["urgent", "现在", "今天", ""],
            condition_words=["快", "方便", "附近", "不要太远", ""],
            question_words=[],
            status_words=[],
            action_words=["做饭", "出门", "折腾", ""]
        )

        # 3. 品质追求型妈妈
        self.personas["品质追求型妈妈"] = PersonaTemplate(
            id="P003",
            name="品质追求型妈妈",
            emotion_level="中",
            sentence_patterns=[
                "想{需求}{条件}",
                "求推荐{需求}{条件}",
                "{需求}哪里{好}{条件}"
            ],
            time_words=["周末", "假期", ""],
            condition_words=["环境好", "口碑好", "品牌", ""],
            question_words=["有推荐吗", "哪家好"],
            status_words=[]
        )

        # 4. 价格敏感型妈妈
        self.personas["价格敏感型妈妈"] = PersonaTemplate(
            id="P004",
            name="价格敏感型妈妈",
            emotion_level="低",
            sentence_patterns=[
                "{需求}{价格}{疑问}",
                "{价格}{需求}有吗",
                "{需求}哪里{便宜}"
            ],
            time_words=[""],
            condition_words=["性价比高", "团购", "优惠", "便宜", ""],
            question_words=["多少钱", "有优惠吗", "贵不贵"],
            status_words=[]
        )

        # 5. 社交分享型妈妈
        self.personas["社交分享型妈妈"] = PersonaTemplate(
            id="P005",
            name="社交分享型妈妈",
            emotion_level="高",
            sentence_patterns=[
                "求推荐{需求}{条件}",
                "求安利{需求}{条件}",
                "想{需求}{条件}"
            ],
            time_words=["周末", "明天", ""],
            condition_words=["网红", "热门", "好玩的", "适合拍照", ""],
            question_words=["有吗", "求推荐"],
            status_words=[]
        )

        # 6. 谨慎保守型老人
        self.personas["谨慎保守型老人"] = PersonaTemplate(
            id="P006",
            name="谨慎保守型老人",
            emotion_level="高",
            sentence_patterns=[
                "{需求}{条件}{疑问}",
                "{条件}{需求}{疑问}",
                "{需求}{条件}正规吗"
            ],
            time_words=["urgent", "今天", ""],
            condition_words=["正规的", "附近的", "有保障的", ""],
            question_words=["可靠吗", "正规吗", "会不会骗人啊", "安全吗"],
            status_words=[]
        )

        # 7. 求助依赖型老人
        self.personas["求助依赖型老人"] = PersonaTemplate(
            id="P007",
            name="求助依赖型老人",
            emotion_level="高",
            sentence_patterns=[
                "帮帮忙{需求}{条件}",
                "我不会{需求}帮帮我",
                "想{需求}{条件}怎么办"
            ],
            time_words=["urgent", ""],
            condition_words=["简单的", "方便的", "附近的", ""],
            question_words=["怎么办", "怎么弄", "有人帮吗"],
            status_words=[]
        )

        # 8. 潮流探索型 Z 世代
        self.personas["潮流探索型 Z 世代"] = PersonaTemplate(
            id="P008",
            name="潮流探索型 Z 世代",
            emotion_level="中",
            sentence_patterns=[
                "求安利{需求}{条件}",
                "{需求}求推荐{条件}",
                "想冲{需求}{条件}"
            ],
            time_words=["今晚", "周末", ""],
            condition_words=["网红", "出片", "氛围感", "小众", ""],
            question_words=["有吗", "求安利", "怎么样"],
            status_words=[]
        )

    def _init_scenes(self):
        """初始化场景库"""
        self.scenes = {
            "医疗健康": Scene("医疗健康",
                ["儿科医院", "儿童医院", "疫苗接种", "体检", "药店", "推拿", "牙科", "急诊"],
                ["urgent", "urgent 求助", "尽快", ""],
                ["响应速度", "可信度", "专业性"]),

            "餐饮外卖": Scene("餐饮外卖",
                ["儿童餐", "营养餐", "辅食", "月子餐", "亲子餐厅", "外卖", "快餐"],
                ["urgent", "现在", "中午", "晚上", ""],
                ["配送速度", "餐品质量", "适龄性"]),

            "教育早教": Scene("教育早教",
                ["早教中心", "托班", "兴趣班", "幼儿园", "亲子活动", "游泳", "英语"],
                ["近期", "下个月", "暑假", "周末", ""],
                ["师资", "环境", "口碑"]),

            "生活服务": Scene("生活服务",
                ["保洁", "月嫂", "育儿嫂", "儿童摄影", "维修", "洗衣"],
                ["urgent", "本周", "近期", ""],
                ["专业性", "安全性", "价格"]),

            "休闲娱乐": Scene("休闲娱乐",
                ["儿童乐园", "亲子游", "游泳馆", "绘本馆", "亲子酒店", "游乐场", "动物园"],
                ["周末", "假期", "明天", ""],
                ["好玩", "安全", "特色"]),

            "社区服务": Scene("社区服务",
                ["社区医院", "老年食堂", "便民超市", "快递代收", "理发", "维修"],
                ["今天", "近期", ""],
                ["方便", "便宜", "近"]),

            "便民生活": Scene("便民生活",
                ["缴费", "充值", "查询", "预约", "办事", "咨询"],
                ["urgent", "今天", ""],
                ["简单", "方便", "有人帮"]),

            "新潮服务": Scene("新潮服务",
                ["剧本杀", "密室", "VR", "电竞", "自拍馆", "猫咖", "潮玩"],
                ["今晚", "周末", "urgent", ""],
                ["好玩", "出片", "氛围"])
        }

    def _fill_template(self, template: str, persona: PersonaTemplate,
                      need: str, urgency: str) -> str:
        """填充模板"""
        result = template
        result = result.replace("{需求}", need)

        time_word = urgency or self._random_select(persona.time_words) or ""
        result = result.replace("{时间}", time_word)

        if "{条件}" in result:
            condition = self._random_select(persona.condition_words) or ""
            result = result.replace("{条件}", condition)

        if "{疑问}" in result:
            question = self._random_select(persona.question_words) or ""
            result = result.replace("{疑问}", question)

        if "{状况}" in result:
            status = self._random_select(persona.status_words) or ""
            result = result.replace("{状况}", status)

        if "{动作}" in result:
            action = self._random_select(persona.action_words) or ""
            result = result.replace("{动作}", action)

        # 处理额外的模板变量
        if "{好}" in result:
            result = result.replace("{好}", "好")
        if "{价格}" in result:
            result = result.replace("{价格}", "")
        if "{便宜}" in result:
            result = result.replace("{便宜}", "便宜")

        return result

    def _clean_query(self, query: str) -> str:
        """清理 Query"""
        query = query.strip()
        query = " ".join(query.split())

        # 移除首尾标点
        while query and query[0] in "，,。.！!？? ":
            query = query[1:]
        while query and query[-1] in "，,。.！!？? ":
            query = query[:-1]

        # 处理 urgent - 移除多余空格，确保格式统一
        if "urgent" in query:
            # 将 "urgent 求助" 等格式统一处理
            query = query.replace("urgent 求助", "[URGENT]")
            query = query.replace("urgent", "[URGENT]")
            query = query.replace("[URGENT]", " urgent ")
            query = " ".join(query.split())
            # 确保 urgent 在开头
            if "urgent" in query and not query.startswith("urgent"):
                query = query.replace("urgent", "")
                query = "urgent " + query.strip()

        return query.strip()

    def _determine_focus(self, query: str, scene: Scene) -> List[str]:
        """确定评测重点"""
        focus = []
        
        if "urgent" in query or "紧急" in query:
            focus.append("响应速度")
        if any(word in query for word in ["靠谱", "正规", "可靠", "安全"]):
            focus.append("可信度")
        if "附近" in query:
            focus.append("地理位置")
        if any(word in query for word in ["便宜", "价格", "贵", "优惠"]):
            focus.append("价格透明度")
        
        if not focus:
            focus = scene.decision_factors[:2]
        
        return focus

    def _random_select(self, items: List[str]) -> Optional[str]:
        """随机选择"""
        if not items:
            return None
        return self.random.choice(items)


if __name__ == "__main__":
    # 演示使用
    generator = QueryGenerator()
    
    print("=" * 60)
    print("Query Generator 演示")
    print("=" * 60)
    
    # 示例 1
    print("\n【示例 1】新手焦虑型妈妈 - 医疗健康")
    result = generator.generate_single("新手焦虑型妈妈", "医疗健康")
    print(f"Query: {result.query}")
    print(f"意图：{result.intent}")
    print(f"复杂度：{result.complexity}")
    
    # 示例 2
    print("\n【示例 2】谨慎保守型老人 - 生活服务")
    result = generator.generate_single("谨慎保守型老人", "生活服务")
    print(f"Query: {result.query}")
    print(f"意图：{result.intent}")
    print(f"复杂度：{result.complexity}")
    
    # 示例 3
    print("\n【示例 3】潮流探索型 Z 世代 - 休闲娱乐")
    z_gen_key = list(generator.personas.keys())[7]
    result = generator.generate_single(z_gen_key, "休闲娱乐")
    print(f"Query: {result.query}")
    print(f"意图：{result.intent}")
    print(f"复杂度：{result.complexity}")
    
    # 示例 4
    print("\n【示例 4】批量生成 (效率实用型妈妈 - 餐饮外卖，5 条)")
    results = generator.generate_batch("效率实用型妈妈", "餐饮外卖", 5)
    for i, result in enumerate(results, 1):
        print(f"{i}. {result.query}")
    
    # 示例 5
    print("\n【示例 5】多人群对比测试 (教育早教场景)")
    personas = ["新手焦虑型妈妈", "品质追求型妈妈", "价格敏感型妈妈"]
    multi_results = generator.generate_multi_persona(personas, "教育早教", 2)
    for persona_name, results in multi_results.items():
        print(f"\n{persona_name}:")
        for result in results:
            print(f"  - {result.query}")
    
    print("\n" + "=" * 60)
    print("演示完成!")
    print("=" * 60)
