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
        # 已生成的 query 历史（用于去重）
        self._generated_history = []
    
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

        # 清空历史记录（每次生成重新开始）
        self._generated_history = []

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
                            generation_result = self._generate_query_with_llm(
                                persona_id, scenario_id, category_id, case_idx
                            )

                            query = {
                                "query_id": f"Q{query_counter:04d}",
                                "query_text": generation_result["query_text"],
                                "priority": "P0" if query_counter <= 3 else "P1",
                                "tags": [persona_id, scenario_id, category_id],
                                "persona_id": persona_id,
                                "scenario_id": scenario_id,
                                "category_id": category_id,
                                "persona": f"{persona_id}_{persona_data['name']}",
                                "scenario": f"{scenario_id}_{self.SCENARIO_TAGS.get(scenario_id, '')}",
                                "category": f"{category_id}_{self.CATEGORY_TAGS.get(category_id, '')}",
                                "expected_intent": {"intent": "search", "category": category_id},
                                "evaluation_criteria": ["accuracy", "timeliness", "personalization", "safety"],
                                "generation_info": {
                                    "method": generation_result["generation_method"],
                                    "llm_input": generation_result.get("llm_input"),
                                    "llm_output": generation_result.get("llm_output")
                                }
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
    
    # 场景角度提示：为每个 P×S×C 组合提供多种不同的需求角度
    DIVERSITY_ANGLES = {
        "C5": [  # 医药健康
            "突发身体不适（头痛、胃痛、牙痛、过敏等不同症状）",
            "慢性病日常用药补充（降压药、降糖药、维生素等）",
            "家庭常备药品囤货（创可贴、消毒液、体温计等）",
            "季节性健康需求（防晒、驱蚊、润喉、暖宝宝等）",
            "运动/职业相关（护腰、眼药水、咽炎片、肌肉酸痛等）",
            "心理/睡眠相关（助眠、安神、褪黑素等）",
        ],
        "C4": [  # 母婴用品
            "喂养相关（奶粉、奶瓶、辅食工具、吸奶器等）",
            "日常护理（纸尿裤、湿巾、护臀膏、婴儿洗护等）",
            "出行装备（婴儿推车配件、防走失绳、遮阳帽等）",
            "玩具/早教（安抚玩具、牙胶、布书、积木等）",
            "婴儿衣物（连体衣、口水巾、袜子、帽子等）",
            "安全防护（防撞角、插座保护盖、婴儿监控等）",
        ],
        "C1": [  # 生鲜果蔬
            "应季水果（当季特色水果、进口水果等）",
            "做饭食材（肉禽蛋、蔬菜、调味料等）",
            "即食/轻食（沙拉、鲜切水果、酸奶等）",
        ],
        "C2": [  # 休闲零食
            "追剧零食（薯片、坚果、饮料等）",
            "办公室零食（咖啡、饼干、巧克力等）",
            "聚会零食（啤酒、烧烤食材、卤味等）",
        ],
        "C3": [  # 3C数码
            "手机配件（充电线、充电宝、手机壳等）",
            "办公设备（键盘、鼠标、U盘等）",
            "生活电器（小风扇、加湿器等）",
        ],
        "C6": [  # 日用百货
            "清洁用品（洗衣液、拖把、垃圾袋等）",
            "个人护理（牙膏、洗发水、纸巾等）",
            "厨房用品（保鲜膜、收纳盒等）",
        ],
        "C7": [  # 鲜花礼品
            "节日送礼（鲜花、礼盒、蛋糕等）",
            "居家装饰（绿植、香薰、干花等）",
        ],
        "C8": [  # 宠物用品
            "宠物食品（猫粮、狗粮、零食等）",
            "宠物用品（猫砂、牵引绳等）",
        ],
    }

    # 人群特征细化：提供更丰富的人设背景变体
    PERSONA_VARIANTS = {
        "P1": [
            "互联网公司产品经理，经常加班到深夜，独居，注重效率",
            "金融行业分析师，工作压力大，周末喜欢健身，追求品质",
            "创业公司技术负责人，作息不规律，经常出差，喜欢尝试新品",
            "外企市场专员，早出晚归，注重健康饮食，喜欢囤货",
            "设计师，自由职业，作息不固定，喜欢宅家，注重生活品质",
            "销售经理，应酬多，肠胃不好，需要经常备药",
        ],
        "P2": [
            "新手妈妈，宝宝3个月大，全职带娃，经验不足容易焦虑",
            "二胎妈妈，大宝3岁小宝6个月，时间紧张需要高效购物",
            "职场妈妈，白天上班晚上带娃，依赖即时配送",
            "新手妈妈，宝宝1岁刚学走路，需要各种安全防护用品",
            "年轻妈妈，宝宝8个月开始添加辅食，关注食品安全",
            "新手妈妈，宝宝2个月，纯母乳喂养但奶量不够需要混合喂养",
        ],
        "P3": [
            "大三学生，考试周压力大，宿舍生活",
            "研究生，实验室常驻，经常熬夜写论文",
            "大一新生，刚入学不熟悉环境，预算有限",
        ],
        "P4": [
            "精致白领女性，注重护肤和生活品质",
            "都市单身男青年，喜欢尝试网红产品",
        ],
        "P5": [
            "退休阿姨，注重养生，每天买菜做饭",
            "退休大爷，有慢性病需要长期用药",
        ],
        "P6": [
            "双职工家庭，孩子上小学，周末需要采购一周食材",
            "双职工家庭，刚搬新家，需要添置日用品",
        ],
    }

    SCENARIO_CONTEXT = {
        "S1": [  # 应急补给
            "突发状况，急需30分钟内送达",
            "家里某样东西突然用完了，急需补充",
            "身体突然不舒服，需要马上买药",
            "意外情况，需要紧急购买某样东西",
        ],
        "S2": [  # 即时享受
            "下班回家想犒劳自己，想马上享受",
            "突然嘴馋/想用某样东西，想即刻满足",
            "周末宅家，想立刻获得某样商品提升幸福感",
            "晚上突然想吃/用某样东西",
        ],
        "S3": [  # 懒人便利
            "不想出门，希望送货上门",
            "天气不好，懒得出去买",
        ],
        "S4": [  # 计划性消费
            "提前囤货，看到划算的想买",
            "定期补充家里的常用物品",
        ],
        "S5": [  # 节日聚会
            "朋友聚会需要准备",
            "节日送礼需要",
        ],
    }

    def _generate_query_with_llm(self, persona_id: str, scenario_id: str, category_id: str, variant: int = 0) -> Dict:
        """调用大模型生成Query（增强多样性版本）

        Args:
            persona_id: 人群ID
            scenario_id: 场景ID
            category_id: 品类ID
            variant: 变体索引，用于同一组合生成多个不同用例

        Returns:
            包含生成的query文本和大模型调用信息的字典
        """
        if not self.qwen_agent:
            query_text = self._select_query_template(persona_id, scenario_id, category_id, variant)
            return {
                "query_text": query_text,
                "generation_method": "template",
                "llm_input": None,
                "llm_output": None
            }

        persona_name = self.TEST_CASE_TEMPLATES.get(persona_id, {}).get('name', persona_id)
        scenario_name = self.SCENARIO_TAGS.get(scenario_id, scenario_id)
        category_name = self.CATEGORY_TAGS.get(category_id, category_id)

        # 选取人设变体
        persona_variants = self.PERSONA_VARIANTS.get(persona_id, [persona_name])
        persona_detail = persona_variants[variant % len(persona_variants)]

        # 选取需求角度
        angles = self.DIVERSITY_ANGLES.get(category_id, [f"{category_name}相关需求"])
        # 随机打乱后选取，确保不同 variant 选不同角度
        shuffled_angles = angles.copy()
        random.shuffle(shuffled_angles)
        selected_angle = shuffled_angles[variant % len(shuffled_angles)]

        # 选取场景上下文
        scenario_contexts = self.SCENARIO_CONTEXT.get(scenario_id, [scenario_name])
        scenario_detail = scenario_contexts[variant % len(scenario_contexts)]

        # 构建已生成 query 的历史（同一 P×S×C 组合的）
        same_combo_history = [
            h["query_text"] for h in self._generated_history
            if h.get("persona_id") == persona_id
            and h.get("scenario_id") == scenario_id
            and h.get("category_id") == category_id
        ]

        history_block = ""
        if same_combo_history:
            history_list = "\n".join(f"  - {q[:80]}" for q in same_combo_history)
            history_block = f"""

【已有Query - 请勿重复】
以下是同一组合已经生成的Query，你必须生成完全不同的内容（不同的症状/商品/场景/需求）：
{history_list}"""

        # 构建prompt
        system_prompt = """你是一个即时零售场景下的用户Query生成专家。
你的任务是根据给定的人群、场景、品类维度，生成真实、自然、多样化的用户搜索Query。

核心要求：
1. 以第一人称描述，但不要每次都用"我是一个XX"的固定句式开头
2. Query必须体现该人群的真实语言习惯（如妈妈群体会说"宝宝"、白领会说"加班"等）
3. 必须包含对品类的具体需求（具体的商品名或品类关键词）
4. 可以提及配送时效要求，但不要每次都说"30分钟"
5. 每次生成的内容必须在商品类型、具体症状/需求、表达方式上有明显差异
6. 口语化、自然，像真人在搜索框里打的话
7. 只返回Query文本，不要解释、不要编号、不要引号"""

        user_prompt = f"""请生成一条即时零售用户搜索Query：

【人群画像】{persona_detail}
【购物场景】{scenario_name} - {scenario_detail}
【商品品类】{category_name}
【需求角度】请从"{selected_angle}"这个角度出发
【变体要求】这是第{variant + 1}条，请确保与之前的Query在商品种类和表达方式上完全不同{history_block}

请直接输出Query文本："""

        try:
            result = self.qwen_agent.call(
                query_text=user_prompt,
                system_prompt=system_prompt,
                temperature=0.95  # 提高温度增加多样性
            )

            llm_info = {
                "input": {
                    "system_prompt": system_prompt,
                    "user_prompt": user_prompt,
                    "temperature": 0.95,
                    "model": getattr(self.qwen_agent, 'model', 'unknown'),
                    "api_mode": getattr(self.qwen_agent, 'api_mode', 'unknown')
                },
                "output": {
                    "success": result.get('success'),
                    "content": result.get('content'),
                    "raw_response": result.get('raw_response'),
                    "error": result.get('error'),
                    "response_time_ms": result.get('response_time_ms')
                }
            }

            if result.get('success'):
                query_text = result.get('content', '').strip()
                # 清理可能的引号和编号
                query_text = query_text.strip('"').strip("'").strip()
                # 去掉可能的编号前缀如 "1. " "- "
                import re
                query_text = re.sub(r'^[\d]+[\.\、]\s*', '', query_text)
                query_text = re.sub(r'^[-—]\s*', '', query_text)

                if query_text:
                    # 记录到历史
                    self._generated_history.append({
                        "query_text": query_text,
                        "persona_id": persona_id,
                        "scenario_id": scenario_id,
                        "category_id": category_id,
                    })
                    self.log(f"LLM生成Query [{persona_id}×{scenario_id}×{category_id}]: {query_text[:50]}...")
                    return {
                        "query_text": query_text,
                        "generation_method": "llm",
                        "llm_input": llm_info["input"],
                        "llm_output": llm_info["output"]
                    }

            self.log(f"LLM调用失败，使用模板: {result.get('error', 'unknown')}")
            query_text = self._select_query_template(persona_id, scenario_id, category_id, variant)
            return {
                "query_text": query_text,
                "generation_method": "template_fallback",
                "llm_input": llm_info["input"],
                "llm_output": llm_info["output"]
            }

        except Exception as e:
            self.log(f"LLM调用异常: {e}")
            query_text = self._select_query_template(persona_id, scenario_id, category_id, variant)
            return {
                "query_text": query_text,
                "generation_method": "template_fallback",
                "llm_input": {
                    "system_prompt": system_prompt,
                    "user_prompt": user_prompt,
                    "temperature": 0.95,
                    "model": getattr(self.qwen_agent, 'model', 'unknown'),
                    "api_mode": getattr(self.qwen_agent, 'api_mode', 'unknown')
                },
                "llm_output": {
                    "success": False,
                    "error": str(e),
                    "content": None,
                    "raw_response": None
                }
            }

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
