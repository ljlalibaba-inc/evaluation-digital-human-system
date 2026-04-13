#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试用例生成 Agent
集成 instant-retail-query-gen Skill
调用大模型为每个P×S×C组合生成query
"""

import json
import random
import time
from typing import List, Dict, Optional
from .base_agent import BaseAgent
from .qwen_agent import QwenAgent


class TestCaseAgent(BaseAgent):
    """
    测试用例生成Agent
    负责基于人群、场景、品类三维模型生成测评Query
    调用大模型为每个P×S×C组合生成query
    """

    def __init__(self, config: Dict = None):
        super().__init__("TestCaseAgent", config)
        self.dataset_path = config.get("dataset_path") if config else None
        self._dataset = None
        # 初始化QwenAgent用于生成query
        self.qwen_agent = QwenAgent(config.get('qwen_config', {})) if config else None
        # 用例保存路径
        self.output_dir = config.get('output_dir', '.') if config else '.'
    
    def _load_dataset(self):
        """加载数据集"""
        if self._dataset is None:
            # 尝试加载聚合版数据集
            try:
                import os
                base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                
                with open(f"{base_path}/../qwen-retail-query-gen/test-queries-aggregated.json", 'r', encoding='utf-8') as f:
                    data1 = json.load(f)
                with open(f"{base_path}/../qwen-retail-query-gen/test-queries-aggregated-p2.json", 'r', encoding='utf-8') as f:
                    data2 = json.load(f)
                
                self._dataset = {**data1.get('data', {}), **data2.get('data', {})}
            except Exception as e:
                self.log(f"加载数据集失败: {e}")
                self._dataset = {}
    
    # 内置测试用例模板（当数据集不可用时使用）
    TEST_CASE_TEMPLATES = {
        "P1": {  # 忙碌的年轻白领
            "name": "忙碌的年轻白领",
            "queries": [
                "我是互联网公司的产品经理，经常加班到深夜，现在突然头痛得厉害，家里没有止痛药了，请推荐一款适合我的止痛药，要求30分钟内送到。",
                "我是加班族，颈椎最近很不舒服，想买一个颈椎按摩仪，有什么推荐？",
                "工作太忙没时间做饭，想点一份健康的外卖，有什么推荐？"
            ]
        },
        "P2": {  # 新手妈妈
            "name": "新手妈妈",
            "queries": [
                "我是新手妈妈，宝宝突然发烧到39度，家里没有退热贴了，急需购买，多久能送到？",
                "宝宝晚上总是哭闹，想买一款安抚玩具，有什么推荐？",
                "需要给宝宝买纸尿裤，哪个品牌比较好？"
            ]
        },
        "P3": {  # 大学生
            "name": "大学生",
            "queries": [
                "我是大学生，宿舍里的零食吃完了，想买一些零食，有什么推荐？",
                "考试周需要咖啡提神，有什么推荐的咖啡？",
                "宿舍需要买一些日用品，有什么优惠？"
            ]
        },
        "P4": {  # 精致白领
            "name": "精致白领",
            "queries": [
                "我想买一些进口水果，有什么推荐？",
                "需要买一款高品质的护肤品，有什么推荐？",
                "想买一束鲜花放在办公室，有什么推荐？"
            ]
        },
        "P5": {  # 退休阿姨
            "name": "退休阿姨",
            "queries": [
                "我想买一些新鲜的蔬菜，有什么推荐？",
                "需要买一款血压计，有什么推荐？",
                "想买一些保健品，有什么推荐？"
            ]
        },
        "P6": {  # 双职工家庭
            "name": "双职工家庭",
            "queries": [
                "我们夫妻都上班，没时间买菜，想买点预制菜，有什么推荐？",
                "家里需要买一些清洁用品，有什么推荐？",
                "周末想在家吃火锅，需要买食材，有什么推荐？"
            ]
        }
    }

    SCENARIO_TAGS = {
        "S1": "应急补给",
        "S2": "即时享受",
        "S3": "懒人便利",
        "S4": "计划性消费",
        "S5": "节日聚会"
    }

    CATEGORY_TAGS = {
        "C1": "生鲜果蔬",
        "C2": "休闲零售",
        "C3": "3C数码",
        "C4": "母婴用品",
        "C5": "医药健康",
        "C6": "日用百货",
        "C7": "鲜花礼品",
        "C8": "宠物用品"
    }

    def generate(
        self,
        personas: Optional[List[str]] = None,
        scenarios: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        count: Optional[int] = None,
        cases_per_combination: int = 2,
        mode: str = "cartesian"
    ) -> List[Dict]:
        """
        生成测试用例

        Args:
            personas: 人群列表，如 ["P1", "P2"]；None表示所有人群
            scenarios: 场景列表，如 ["S1", "S2"]；None表示所有场景
            categories: 品类列表，如 ["C5", "C4"]；None表示所有品类
            count: 生成数量（已废弃，请使用cases_per_combination）
            cases_per_combination: 每个P×S×C组合生成的用例数量，默认2条
            mode: 生成模式
                - "cartesian": 笛卡尔积模式，为每个P×S×C组合生成指定数量用例
                - "sequential": 顺序模式，按列表顺序分配

        Returns:
            Query列表
        """
        self._load_dataset()

        # 确定要使用的维度值
        target_personas = personas if personas else list(self.TEST_CASE_TEMPLATES.keys())
        target_scenarios = scenarios if scenarios else list(self.SCENARIO_TAGS.keys())
        target_categories = categories if categories else list(self.CATEGORY_TAGS.keys())

        self.log(f"目标维度: 人群{target_personas} × 场景{target_scenarios} × 品类{target_categories}")
        self.log(f"每个组合生成: {cases_per_combination}条用例")

        queries = []
        query_counter = 1

        # 笛卡尔积模式：为每个P×S×C组合生成指定数量的用例
        if mode == "cartesian":
            # 计算总组合数
            total_combinations = len(target_personas) * len(target_scenarios) * len(target_categories)
            total_queries = total_combinations * cases_per_combination

            self.log(f"开始生成 {total_queries} 条用例，共 {total_combinations} 个P×S×C组合...")

            for persona_id in target_personas:
                if persona_id not in self.TEST_CASE_TEMPLATES:
                    continue

                persona_data = self.TEST_CASE_TEMPLATES[persona_id]

                for scenario_id in target_scenarios:
                    for category_id in target_categories:
                        # 为每个组合生成指定数量的用例
                        for case_idx in range(cases_per_combination):
                            # 调用大模型生成query
                            query_text = self._generate_query_with_llm(
                                persona_id, scenario_id, category_id, case_idx
                            )

                            query = {
                                "query_id": f"Q{query_counter:04d}",
                                "query_text": query_text,
                                "priority": "P0" if query_counter <= 3 else "P1",
                                "tags": [persona_id, scenario_id, category_id],
                                "persona_id": persona_id,
                                "scenario_id": scenario_id,
                                "category_id": category_id,
                                "persona": f"{persona_id}_{persona_data['name']}",
                                "scenario": f"{scenario_id}_{self.SCENARIO_TAGS.get(scenario_id, '')}",
                                "category": f"{category_id}_{self.CATEGORY_TAGS.get(category_id, '')}",
                                "expected_intent": {"intent": "search", "category": category_id},
                                "evaluation_criteria": ["accuracy", "timeliness", "personalization", "safety"]
                            }
                            queries.append(query)
                            query_counter += 1

                            # 添加延迟避免请求过快
                            if self.qwen_agent and case_idx < cases_per_combination - 1:
                                time.sleep(0.5)

                            # 如果传了count，兼容旧逻辑（限制总数）
                            if count and len(queries) >= count:
                                break

                        if count and len(queries) >= count:
                            break

                    if count and len(queries) >= count:
                        break

                if count and len(queries) >= count:
                    break

        # 顺序模式：按列表顺序分配（兼容旧逻辑）
        else:
            for persona_id in target_personas:
                if persona_id not in self.TEST_CASE_TEMPLATES:
                    continue

                persona_data = self.TEST_CASE_TEMPLATES[persona_id]

                for idx, query_text in enumerate(persona_data["queries"]):
                    scenario_id = target_scenarios[idx % len(target_scenarios)]
                    category_id = target_categories[idx % len(target_categories)]

                    query = {
                        "query_id": f"Q{query_counter:04d}",
                        "query_text": query_text,
                        "priority": "P0" if idx == 0 else "P1",
                        "tags": [persona_id, scenario_id, category_id],
                        "persona_id": persona_id,
                        "scenario_id": scenario_id,
                        "category_id": category_id,
                        "persona": f"{persona_id}_{persona_data['name']}",
                        "scenario": f"{scenario_id}_{self.SCENARIO_TAGS.get(scenario_id, '')}",
                        "category": f"{category_id}_{self.CATEGORY_TAGS.get(category_id, '')}",
                        "expected_intent": {"intent": "search", "category": category_id},
                        "evaluation_criteria": ["accuracy", "timeliness", "personalization", "safety"]
                    }
                    queries.append(query)
                    query_counter += 1

                    if count and len(queries) >= count:
                        break

                if count and len(queries) >= count:
                    break

        total_combinations = len(target_personas) * len(target_scenarios) * len(target_categories)
        expected_count = total_combinations * cases_per_combination
        self.log(f"生成测试用例: {len(queries)}条 (期望: {expected_count}条 = {total_combinations}组合 × {cases_per_combination}条)")

        # 保存用例到文件
        self._save_testcases(queries, target_personas, target_scenarios, target_categories, cases_per_combination)

        return queries

    def _save_testcases(self, queries: List[Dict], personas: List[str], scenarios: List[str], categories: List[str], cases_per_combination: int = 2):
        """保存测试用例到文件

        Args:
            queries: 生成的测试用例列表
            personas: 使用的人群列表
            scenarios: 使用的场景列表
            categories: 使用的品类列表
            cases_per_combination: 每个组合生成的用例数
        """
        import os
        from datetime import datetime

        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)

        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"testcases_{timestamp}_{len(queries)}条.json"
        filepath = os.path.join(self.output_dir, filename)

        # 获取使用的模型信息
        model_info = "template"
        if self.qwen_agent:
            model_info = getattr(self.qwen_agent, 'model', 'unknown')

        # 构建保存的数据结构
        data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_count": len(queries),
                "dimensions": {
                    "personas": personas,
                    "scenarios": scenarios,
                    "categories": categories
                },
                "combinations": len(personas) * len(scenarios) * len(categories),
                "cases_per_combination": cases_per_combination,
                "model": model_info,
                "api_mode": getattr(self.qwen_agent, 'api_mode', 'template') if self.qwen_agent else 'template'
            },
            "testcases": queries
        }

        # 保存到文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        self.log(f"测试用例已保存: {filepath}")

        # 同时保存为最新用例集
        latest_path = os.path.join(self.output_dir, "testcases_latest.json")
        with open(latest_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        self.log(f"最新用例集已更新: {latest_path}")
    
    def _generate_query_with_llm(self, persona_id: str, scenario_id: str, category_id: str, variant: int = 0) -> str:
        """调用大模型生成Query

        Args:
            persona_id: 人群ID
            scenario_id: 场景ID
            category_id: 品类ID
            variant: 变体索引，用于同一组合生成多个不同用例

        Returns:
            生成的query文本
        """
        if not self.qwen_agent:
            # 如果没有配置大模型，使用模板
            return self._select_query_template(persona_id, scenario_id, category_id, variant)

        persona_name = self.TEST_CASE_TEMPLATES.get(persona_id, {}).get('name', persona_id)
        scenario_name = self.SCENARIO_TAGS.get(scenario_id, scenario_id)
        category_name = self.CATEGORY_TAGS.get(category_id, category_id)

        # 构建prompt
        system_prompt = """你是一个即时零售场景下的用户Query生成专家。
你的任务是根据给定的人群、场景、品类维度，生成真实、自然的用户搜索Query。
要求：
1. 以第一人称"我"开头，描述用户的身份和需求
2. Query要符合该人群的语言习惯和购物需求
3. 体现该场景的特点（如应急、即时、计划性等）
4. 包含对品类的具体需求
5. 可以提及配送时效要求（如30分钟送达）
6. 只返回Query文本，不要解释"""

        user_prompt = f"""请为以下维度生成一条用户搜索Query：

【人群】{persona_name} ({persona_id})
【场景】{scenario_name} ({scenario_id})
【品类】{category_name} ({category_id})
【变体】第{variant + 1}条（同一组合的不同表达）

请生成一条自然、真实的用户Query："""

        try:
            result = self.qwen_agent.call(
                query_text=user_prompt,
                system_prompt=system_prompt,
                temperature=0.8
            )

            if result.get('success'):
                query_text = result.get('content', '').strip()
                # 清理可能的引号
                query_text = query_text.strip('"').strip("'")
                if query_text:
                    self.log(f"LLM生成Query [{persona_id}×{scenario_id}×{category_id}]: {query_text[:50]}...")
                    return query_text

            # 如果调用失败，使用模板
            self.log(f"LLM调用失败，使用模板: {result.get('error', 'unknown')}")
            return self._select_query_template(persona_id, scenario_id, category_id, variant)

        except Exception as e:
            self.log(f"LLM调用异常: {e}")
            return self._select_query_template(persona_id, scenario_id, category_id, variant)

    def _select_query_template(self, persona_id: str, scenario_id: str, category_id: str, variant: int = 0) -> str:
        """根据P/S/C维度选择最合适的Query模板（备用方案）

        Args:
            persona_id: 人群ID
            scenario_id: 场景ID
            category_id: 品类ID
            variant: 变体索引，用于同一组合生成多个不同用例
        """
        # 基础模板库（每个P×S×C组合可以有多个变体）
        templates = {
            # P1: 忙碌的年轻白领
            ("P1", "S1", "C5"): [
                "我是互联网公司的产品经理，经常加班到深夜，现在突然头痛得厉害，家里没有止痛药了，请推荐一款适合我的止痛药，要求30分钟内送到。",
                "加班到凌晨2点，胃疼得厉害，需要买胃药，多久能送到？"
            ],
            ("P1", "S2", "C3"): [
                "我是加班族，颈椎最近很不舒服，想买一个颈椎按摩仪，有什么推荐？",
                "想要一个便携式充电宝，出差用，有什么推荐？"
            ],
            ("P1", "S3", "C2"): [
                "工作太忙没时间做饭，想点一份健康的外卖，有什么推荐？",
                "晚上饿了，想买一些速食面，有什么好吃的推荐？"
            ],
            # P2: 新手妈妈
            ("P2", "S1", "C5"): [
                "我是新手妈妈，宝宝突然发烧到39度，家里没有退热贴了，急需购买，多久能送到？",
                "宝宝拉肚子，需要买婴儿益生菌， urgent！"
            ],
            ("P2", "S2", "C4"): [
                "宝宝晚上总是哭闹，想买一款安抚玩具，有什么推荐？",
                "想给宝宝买一款安全的磨牙棒，有什么推荐？"
            ],
            ("P2", "S4", "C4"): [
                "需要给宝宝买纸尿裤，哪个品牌比较好？",
                "宝宝该换大码衣服了，有什么舒适的婴儿服装推荐？"
            ],
            # P3: 大学生
            ("P3", "S2", "C2"): [
                "我是大学生，宿舍里的零食吃完了，想买一些零食，有什么推荐？",
                "周末想在宿舍看电影，想买一些薯片和饮料"
            ],
            ("P3", "S1", "C6"): [
                "考试周需要咖啡提神，有什么推荐的咖啡？",
                "明天要交论文，需要买打印纸和墨盒， urgent！"
            ],
            ("P3", "S3", "C6"): [
                "宿舍需要买一些日用品，有什么优惠？",
                "洗衣液用完了，想买大瓶装的，有什么推荐？"
            ],
            # P4: 精致白领
            ("P4", "S2", "C1"): [
                "我想买一些进口水果，有什么推荐？",
                "想买一些有机蔬菜，品质好一点的"
            ],
            ("P4", "S5", "C7"): [
                "需要买一款高品质的护肤品，有什么推荐？",
                "闺蜜生日，想买一份高档化妆品礼盒"
            ],
            ("P4", "S2", "C7"): [
                "想买一束鲜花放在办公室，有什么推荐？",
                "想买一个香薰蜡烛，提升居家氛围"
            ],
            # P5: 退休阿姨
            ("P5", "S4", "C1"): [
                "我想买一些新鲜的蔬菜，有什么推荐？",
                "今天想买点排骨煲汤，有什么好的？"
            ],
            ("P5", "S1", "C5"): [
                "需要买一款血压计，有什么推荐？",
                "血糖有点高，需要买血糖仪，哪个牌子准？"
            ],
            ("P5", "S4", "C5"): [
                "想买一些保健品，有什么推荐？",
                "想买点钙片，老年人补钙的"
            ],
            # P6: 双职工家庭
            ("P6", "S3", "C1"): [
                "我们夫妻都上班，没时间买菜，想买点预制菜，有什么推荐？",
                "想买一些冷冻水饺，晚上回来煮着吃"
            ],
            ("P6", "S4", "C6"): [
                "家里需要买一些清洁用品，有什么推荐？",
                "想买一些厨房用纸和垃圾袋"
            ],
            ("P6", "S5", "C1"): [
                "周末想在家吃火锅，需要买食材，有什么推荐？",
                "孩子生日，想在家做顿大餐，需要买海鲜"
            ],
        }

        key = (persona_id, scenario_id, category_id)

        # 尝试精确匹配
        if key in templates:
            variants = templates[key]
            return variants[variant % len(variants)]

        # 尝试匹配P+S
        matching_ps = [(k, v) for k, v in templates.items() if k[0] == persona_id and k[1] == scenario_id]
        if matching_ps:
            _, variants = matching_ps[variant % len(matching_ps)]
            return variants[variant % len(variants)]

        # 尝试匹配P+C
        matching_pc = [(k, v) for k, v in templates.items() if k[0] == persona_id and k[2] == category_id]
        if matching_pc:
            _, variants = matching_pc[variant % len(matching_pc)]
            return variants[variant % len(variants)]

        # 返回该人群的默认模板
        if persona_id in self.TEST_CASE_TEMPLATES:
            queries = self.TEST_CASE_TEMPLATES[persona_id]["queries"]
            return queries[variant % len(queries)]

        return "请推荐一些商品"
    
    def execute(self, input_data: Dict) -> List[Dict]:
        """执行生成任务

        Args:
            input_data: 包含以下字段
                - personas: 人群列表
                - scenarios: 场景列表
                - categories: 品类列表
                - cases_per_combination: 每个组合生成的用例数
                - mode: 生成模式
                - use_llm: 是否使用大模型生成query（默认True）
                - qwen_config: 大模型配置
                - output_dir: 用例保存目录
        """
        # 如果配置了使用LLM，初始化QwenAgent
        if input_data.get('use_llm', True) and input_data.get('qwen_config'):
            self.qwen_agent = QwenAgent(input_data.get('qwen_config'))

        # 设置输出目录
        if input_data.get('output_dir'):
            self.output_dir = input_data.get('output_dir')

        return self.generate(
            personas=input_data.get('personas'),
            scenarios=input_data.get('scenarios'),
            categories=input_data.get('categories'),
            count=input_data.get('count'),
            cases_per_combination=input_data.get('cases_per_combination', 2),
            mode=input_data.get('mode', 'cartesian')
        )
