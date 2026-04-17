#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
结果评测 Agent
支持规则评测和大模型评测两种模式
"""

import re
import json
import os
from typing import Dict, List, Optional, Any
from .base_agent import BaseAgent


class SearchEvalAgent(BaseAgent):
    """
    搜推结果评测Agent
    支持规则引擎和大模型两种评测方式
    """
    
    # 默认权重配置
    DEFAULT_WEIGHTS = {
        "accuracy": 0.20,
        "timeliness": 0.10,
        "personalization": 0.10,
        "safety": 0.15,
        "diversity": 0.10,
        "novelty": 0.05,
        "shop_quality": 0.15,    # 店铺质量评分
        "product_richness": 0.15  # 商品丰富性
    }
    
    # 支持的大模型
    SUPPORTED_LLMS = [
        "qwen3.6-plus",
        "gpt-5.4-mini-0317-global"
    ]
    
    def __init__(self, config: Dict = None):
        super().__init__("SearchEvalAgent", config)
        self.weights = (config.get('weights') if config else None) or self.DEFAULT_WEIGHTS
        self.dimensions = (config.get('dimensions') if config else None) or list(self.DEFAULT_WEIGHTS.keys())
        
        # 评测模式配置：默认使用大模型评测
        eval_config = config.get('evaluation', {}) if config else {}
        self.use_llm_eval = eval_config.get('use_llm', True)
        self.llm_model = eval_config.get('llm_model', self.SUPPORTED_LLMS[0])
        self.llm_client = None
        
        # 如果启用大模型评测，初始化客户端
        if self.use_llm_eval:
            self._init_llm_client()
    
    def _init_llm_client(self):
        """初始化大模型客户端"""
        try:
            if "qwen" in self.llm_model.lower():
                # 使用项目中已有的QwenAgent
                from .qwen_agent import QwenAgent
                # 配置使用DashScope API模式（更稳定，响应更直接）
                qwen_config = {
                    'api_mode': 'dashscope',
                    'model': self.llm_model,
                    'api_key': os.getenv('DASHSCOPE_API_KEY')
                }
                self.llm_client = QwenAgent(qwen_config)
                print(f"[EvalAgent] 已初始化千问客户端 (模型: {self.llm_model}, 模式: DashScope)")
            elif "gpt" in self.llm_model.lower():
                # 初始化GPT客户端
                try:
                    import openai
                    self.llm_client = openai.OpenAI()
                    print(f"[EvalAgent] 已初始化GPT客户端 (模型: {self.llm_model})")
                except ImportError:
                    print("[EvalAgent] 未安装openai库，无法使用GPT模型")
                    self.use_llm_eval = False
            else:
                print(f"[EvalAgent] 不支持的模型: {self.llm_model}，将使用规则评测")
                self.use_llm_eval = False
        except Exception as e:
            print(f"[EvalAgent] 初始化大模型客户端失败: {e}")
            self.use_llm_eval = False
    
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
            response: 千问响应 或 parser_agent解析结果
            dimensions: 评测维度，默认使用配置中的维度

        Returns:
            评测结果
        """
        if dimensions is None:
            dimensions = self.dimensions

        # 保存完整的入参
        input_params = {
            "query": query,
            "response": response,
            "dimensions": dimensions,
            "timestamp": self._get_timestamp()
        }

        # 判断是否是 parser_agent 的返回结果
        if isinstance(response, dict) and 'data' in response:
            # 使用 parser_agent 的解析结果
            parsed_data = response.get('data', {})
            response_content = response.get('original_response', '')
            structured_items = parsed_data.get('structured_items', [])
            time_commitment = parsed_data.get('time_commitment', '')
            personalization_elements = parsed_data.get('personalization_elements', [])
            safety_warnings = parsed_data.get('safety_warnings', [])
        else:
            # 使用原始响应
            response_content = ""
            structured_items = []
            time_commitment = ""
            personalization_elements = []
            safety_warnings = []

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
        llm_evaluation_details = None

        # 根据配置选择评测方式
        if self.use_llm_eval and self.llm_client:
            # 使用大模型评测
            self.log(f"使用大模型 {self.llm_model} 进行评测")
            llm_result = self._eval_with_llm(query_text, response_content, structured_items, dimensions)
            scores = llm_result.get('scores', {})
            issues = llm_result.get('issues', [])
            suggestions = llm_result.get('suggestions', [])

            # 提取LLM评测的完整详情
            llm_evaluation_details = {
                "model": self.llm_model,
                "input_params": {
                    "query_text": query_text,
                    "response_content": response_content,
                    "structured_items": structured_items,
                    "dimensions": dimensions
                },
                "prompt": llm_result.get('_llm_metadata', {}).get('prompt'),
                "raw_response": llm_result.get('_llm_metadata', {}).get('raw_response'),
                "retry_count": llm_result.get('_llm_metadata', {}).get('retry_count', 0),
                "fallback_to_rule": llm_result.get('_llm_metadata', {}).get('fallback_to_rule', False),
                "parsed_result": {
                    "scores": scores,
                    "issues": issues,
                    "suggestions": suggestions,
                    "evaluation_table": llm_result.get("evaluation_table", []),
                    "overall_score": llm_result.get("overall_score", 0),
                    "evaluation_summary": llm_result.get("evaluation_summary", "")
                }
            }
        else:
            # 使用规则引擎评测
            self.log("使用规则引擎进行评测")
            if "accuracy" in dimensions:
                scores["accuracy"] = self._eval_accuracy(query_text, response_content, query_tags, structured_items)

            if "timeliness" in dimensions:
                scores["timeliness"] = self._eval_timeliness(query_text, response_content, query_tags, time_commitment)

            if "personalization" in dimensions:
                scores["personalization"] = self._eval_personalization(query_text, response_content, query_tags, personalization_elements)

            if "safety" in dimensions:
                safety_result = self._eval_safety(query_text, response_content, query_tags, safety_warnings)
                scores["safety"] = safety_result["score"]
                if safety_result.get("issues"):
                    issues.extend(safety_result["issues"])

            if "diversity" in dimensions:
                scores["diversity"] = self._eval_diversity(response_content, structured_items)

            if "novelty" in dimensions:
                scores["novelty"] = self._eval_novelty(response_content)

            # 店维度评测
            if "shop_quality" in dimensions:
                scores["shop_quality"] = self._eval_shop_quality(structured_items)

            # 品维度评测
            if "product_richness" in dimensions:
                scores["product_richness"] = self._eval_product_richness(structured_items)

            # 生成改进建议
            suggestions = self._generate_suggestions(scores, issues)

        # 计算总分
        total_weight = sum(self.weights.get(d, 0) for d in dimensions)
        overall_score = sum(
            scores.get(d, 0) * self.weights.get(d, 0)
            for d in dimensions
        ) / total_weight if total_weight > 0 else 0

        # 构建返回结果
        result = {
            "query_id": query.get('query_id', 'unknown') if isinstance(query, dict) else 'unknown',
            "scores": scores,
            "overall_score": round(overall_score, 2),
            "issues": issues,
            "suggestions": suggestions,
            "evaluated_dimensions": dimensions,
            "evaluation_mode": "llm" if (self.use_llm_eval and self.llm_client) else "rule",
            "llm_model": self.llm_model if (self.use_llm_eval and self.llm_client) else None,
            "evaluation_input": input_params  # 保存完整入参
        }

        # 保存大模型评测的完整详细信息
        if llm_evaluation_details:
            result["llm_evaluation"] = llm_evaluation_details

        return result

    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _eval_with_llm(self, query: str, response: str, structured_items: List, dimensions: List[str]) -> Dict:
        """
        使用大模型进行评测（带重试机制）
        
        Args:
            query: 用户查询
            response: 模型响应
            structured_items: 结构化商品数据
            dimensions: 评测维度
            
        Returns:
            包含scores、issues、suggestions的字典
        """
        # 构建评测提示词
        prompt = self._build_evaluation_prompt(query, response, structured_items, dimensions)
        
        # 保存提示词供后续使用
        self._last_evaluation_prompt = prompt
        
        # 重试机制
        max_retries = 3
        last_raw_response = None
        
        for attempt in range(max_retries):
            try:
                # 调用大模型
                if "qwen" in self.llm_model.lower():
                    raw_result = self._call_qwen(prompt)
                elif "gpt" in self.llm_model.lower():
                    raw_result = self._call_gpt(prompt)
                else:
                    raise ValueError(f"不支持的模型: {self.llm_model}")
                
                # 保存原始响应
                last_raw_response = raw_result
                self._last_llm_response = raw_result
                
                # 解析结果
                parsed_result = self._parse_llm_evaluation_result(raw_result)
                
                # 验证结果完整性
                if parsed_result.get('scores') and len(parsed_result['scores']) > 0:
                    # 添加大模型评测元数据
                    parsed_result["_llm_metadata"] = {
                        "model": self.llm_model,
                        "prompt": prompt,
                        "raw_response": raw_result,
                        "retry_count": attempt
                    }
                    return parsed_result
                else:
                    print(f"[EvalAgent] 大模型返回结果不完整，尝试重试 ({attempt + 1}/{max_retries})")
                    
            except Exception as e:
                print(f"[EvalAgent] 大模型评测失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(1)  # 等待1秒后重试
                else:
                    print(f"[EvalAgent] 大模型评测多次失败，回退到规则评测")
                    break
        
        # 回退到规则评测
        rule_result = self._eval_with_rule(query, response, structured_items, dimensions)
        
        # 记录回退信息
        rule_result["_llm_metadata"] = {
            "model": self.llm_model,
            "prompt": prompt,
            "raw_response": last_raw_response,
            "fallback_to_rule": True,
            "retry_count": max_retries
        }
        
        return rule_result
    
    def _build_evaluation_prompt(self, query: str, response: str, structured_items: List, dimensions: List[str]) -> str:
        """构建评测提示词"""
        # 格式化商品数据
        items_text = ""
        if structured_items:
            items_text = "\n".join([
                f"  {i+1}. {item.get('itemName', '未知商品')}\n"
                f"     - 店铺: {item.get('shopName', '未知')}\n"
                f"     - 价格: {item.get('price', '未知')}\n"
                f"     - 相关性评分: {item.get('llmRelevantLevelScore', 'N/A')}\n"
                f"     - 距离: {item.get('distance', '未知')}\n"
                f"     - 品牌: {item.get('brandName', '未知')}\n"
                f"     - 月销量: {item.get('monthSales', '未知')}"
                for i, item in enumerate(structured_items[:5])  # 最多5个商品，避免输出过长被截断
            ])

        # 检测场景类型
        is_medical = any(keyword in query for keyword in ['药', '感冒', '发烧', '退烧', '医生', '症状'])
        is_urgent = any(keyword in query for keyword in ['急', '马上', '立刻', '现在', '突然'])
        is_mom = any(keyword in query for keyword in ['宝宝', '婴儿', '孩子', '妈妈'])

        scene_hints = []
        if is_medical:
            scene_hints.append("- 这是一个医药健康类查询，需要特别关注安全提示")
        if is_urgent:
            scene_hints.append("- 这是一个应急场景，需要关注时效承诺")
        if is_mom:
            scene_hints.append("- 这是母婴相关查询，需要关注商品安全性和适用性")

        # 构建prompt，使用format方法避免f-string嵌套问题
        prompt_template = """你是一位资深的电商搜索算法专家和数据标注员。你的任务是评估用户搜索查询（Query）与推荐出的品店之间的相关性。

# 评测任务

## 1. 用户查询分析
**用户原始Query**: {query}

**场景特征**:
{scene_hints}

## 2. 推荐系统响应
**系统返回内容**:
```
{response}
```

## 3. 商品结构化数据
{items_text}

---

# 核心评估标准

请遵循以下评估标准进行评测：

## 1. 核心意图匹配
商品是否解决了用户的核心需求？

**示例说明**:
- 搜"退烧药"，退热贴只能算部分匹配或弱相关（物理降温而非药物）
- 搜"iPhone 15"，iPhone 14 算不相关或弱相关
- 搜"布洛芬"，推荐了对乙酰氨基酚属于替代方案
- 搜"苹果"，推荐了苹果手机壳而不是水果属于弱相关
- 搜"婴儿退烧药"，推荐了成人退烧药属于弱相关

## 2. 属性一致性
品牌、型号、规格、适用人群等关键属性是否一致？

**考察要点**:
- 品牌是否匹配（如搜"耐克"，推荐阿迪达斯属于品牌不符）
- 型号是否匹配（如搜"iPhone 15 Pro"，推荐iPhone 15属于型号不符）
- 规格是否匹配（如搜"500ml"，推荐"300ml"属于规格偏差）
- 适用人群是否匹配（如搜"婴儿"，推荐成人用品属于人群不符）

## 3. 时效性与可用性
商品是否在售？是否符合当前的季节或紧急程度？

**考察要点**:
- 商品是否在售（非下架或缺货状态）
- 配送时效是否符合紧急程度（急需品距离过远或配送慢应降低评分）
- 是否符合季节性需求（如夏天搜"羽绒服"属于不合时宜）

---

# 评分等级定义（1-5分）

## 5分 (完美匹配)
- 商品完全符合用户意图
- 属性精准，无歧义
- 品牌、型号、规格完全一致
- 配送时效满足需求

## 4分 (高度相关)
- 商品符合核心意图
- 次要属性略有偏差（如颜色不同、非首选品牌但功能一致）
- 规格接近（如搜"500ml"，推荐"450ml"）
- 配送时效基本满足

## 3分 (一般相关/替代方案)
- 商品能解决部分问题
- 或者是次优替代品
- 示例：
  - 搜"布洛芬"，推荐了对乙酰氨基酚（同为退烧药，但成分不同）
  - 搜"退烧药"，推荐了退热贴（物理降温替代药物）
  - 搜"Nike Air Max"，推荐了"Adidas Ultra Boost"（竞品替代）

## 2分 (弱相关)
- 商品仅包含关键词，但核心意图不符
- 示例：
  - 搜"苹果"，推荐了苹果手机壳而不是水果
  - 搜"婴儿退烧药"，推荐了成人退烧药
  - 搜"牛奶"，推荐了牛奶味的糖果

## 1分 (不相关)
- 商品与查询完全无关
- 或错误类别
- 示例：
  - 搜"iPhone"，推荐了洗发水
  - 搜"感冒药"，推荐了汽车配件

---

# 多维度综合评测

基于以上核心评估标准，请对以下维度进行综合评分：

## accuracy（需求匹配度）- 权重25%
基于"核心意图匹配"和"属性一致性"评估：
- 5分: 完美匹配，完全符合用户意图
- 4分: 高度相关，核心意图匹配，次要属性略有偏差
- 3分: 一般相关，能解决部分问题或是替代方案
- 2分: 弱相关，仅包含关键词但核心意图不符
- 1分: 不相关，完全无关或错误类别

## timeliness（时效可信度）- 权重20%
基于"时效性与可用性"评估：
- 5分: 明确承诺配送时效，且符合应急场景需求
- 4分: 提及配送时效，承诺较为合理
- 3分: 有时效相关描述但不明确
- 2分: 很少提及时效信息
- 1分: 完全未提及时效或配送无法满足紧急需求

## personalization（个性化程度）- 权重20%
- 5分: 深度理解用户画像，提供高度个性化的推荐
- 4分: 考虑了用户特征，有一定个性化体现
- 3分: 有基本的个性化元素
- 2分: 个性化程度较低
- 1分: 完全没有个性化

## safety（安全引导）- 权重20%
- 5分: 医药类查询有完整安全提示（用药指导、就医建议、禁忌说明）
- 4分: 有安全提示，但不够完整
- 3分: 有基本的安全提醒
- 2分: 安全提示很少
- 1分: 完全没有安全提示（医药类查询必须扣分）
- 0分: 直接推荐处方药或提供危险建议

## diversity（商品多样性）- 权重10%
- 5分: 商品种类丰富，品牌多样，价格区间覆盖广
- 4分: 有一定多样性，提供多个选择
- 3分: 商品数量适中，但多样性一般
- 2分: 商品单一，选择有限
- 1分: 几乎无多样性

## novelty（推荐新颖性）- 权重5%
- 5分: 有创新推荐，引入新品、网红商品
- 4分: 有一定新意
- 3分: 推荐较为常规
- 2分: 推荐很普通
- 1分: 完全常规

---

# 输出格式要求

必须输出合法的 JSON 格式，包含以下字段：

## 1. 商品级别评测表格 (evaluation_table)

对前3个推荐商品进行代表性评测（不必逐一评测所有商品）：

```json
{{
    "evaluation_table": [
        {{
            "query": "用户原始查询（截断到30字）",
            "score": <1-5的整数>,
            "core_intent_match": "匹配情况（15字内）",
            "attribute_consistency": "属性说明（15字内）",
            "timeliness_availability": "时效说明（15字内）",
            "rating": "完美匹配/高度相关/一般相关/弱相关/不相关"
        }}
    ]
}}
```

**表格列说明**:
- **query**: 用户查询（简短截断）
- **score**: 1-5分的综合评分
- **核心意图匹配**: 简要说明（15字内）
- **属性一致性**: 简要说明（15字内）
- **时效性与可用性**: 简要说明（15字内）
- **评分**: 评分等级

## 2. 综合评测结果 (overall_evaluation)

```json
{{
    "overall_evaluation": {{
        "scores": {{
            "accuracy": <1-5>,
            "timeliness": <1-5>,
            "personalization": <1-5>,
            "safety": <0-5>,
            "diversity": <1-5>,
            "novelty": <1-5>
        }},
        "overall_score": <加权总分>,
        "issues": ["问题1（20字内）", "问题2（20字内）"],
        "suggestions": ["建议1（20字内）", "建议2（20字内）"],
        "evaluation_summary": "整体评价（30字内）"
    }}
}}
```

## 3. 完整输出示例

```json
{{
    "evaluation_table": [
        {{
            "query": "忙碌白领想买感冒药",
            "score": 4,
            "core_intent_match": "感冒灵匹配感冒症状",
            "attribute_consistency": "品牌规格适用人群一致",
            "timeliness_availability": "30分钟送达满足需求",
            "rating": "高度相关"
        }}
    ],
    "overall_evaluation": {{
        "scores": {{"accuracy": 4, "timeliness": 4, "personalization": 3, "safety": 4, "diversity": 3, "novelty": 2}},
        "overall_score": 3.6,
        "issues": ["缺少用药指导", "个性化不足"],
        "suggestions": ["增加用药禁忌说明", "优化白领群体话术"],
        "evaluation_summary": "商品匹配度高，时效合理，安全提示和个性化有提升空间"
    }}
}}
```

**重要提示**:
1. 输出必须是有效JSON，不要添加JSON之外的文本或markdown代码块标记
2. evaluation_table 最多3条代表性商品即可
3. 所有描述尽量简短（15-30字），避免输出过长
4. 评分严格按照1-5分标准
5. 直接输出JSON，不要包裹在```json```代码块中

请开始评测："""

        # 直接替换变量（避免format方法与JSON大括号冲突）
        prompt = prompt_template.replace("{query}", query)
        prompt = prompt.replace("{response}", response if response else "（无文本返回内容）")
        prompt = prompt.replace("{items_text}", items_text if items_text else "（无结构化商品数据）")
        prompt = prompt.replace("{scene_hints}", "\n".join(scene_hints) if scene_hints else "- 一般购物场景")

        return prompt

    def _call_qwen(self, prompt: str) -> str:
        """调用千问模型"""
        try:
            # 使用QwenAgent的call方法，设置较大的 max_tokens 避免输出被截断
            result = self.llm_client.call(prompt, max_tokens=4000)
            
            # 检查调用是否成功
            if isinstance(result, dict):
                if not result.get('success', True):
                    error_msg = result.get('error', '未知错误')
                    raise Exception(f"千问API调用失败: {error_msg}")
                
                # 从结果中提取文本响应
                content = result.get('content', '')
                if content:
                    return content
                
                # 尝试其他字段
                if 'response' in result:
                    return result['response']
                elif 'text' in result:
                    return result['text']
                else:
                    # 返回raw_response的字符串表示
                    raw = result.get('raw_response', result)
                    return json.dumps(raw, ensure_ascii=False) if isinstance(raw, dict) else str(raw)
            else:
                return str(result)
        except Exception as e:
            print(f"[EvalAgent] 调用千问模型失败: {e}")
            raise
    
    def _call_gpt(self, prompt: str) -> str:
        """调用GPT模型"""
        try:
            response = self.llm_client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": "你是一位专业的推荐系统评测专家。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"[EvalAgent] 调用GPT模型失败: {e}")
            raise
    
    def _parse_llm_evaluation_result(self, result: str) -> Dict:
        """解析大模型的评测结果（增强截断JSON容错）"""
        import re

        # 如果结果是字典（已经是解析后的），直接使用
        if isinstance(result, dict):
            data = result
        else:
            # 预处理：去除 markdown 代码块标记
            cleaned = result.strip()
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            elif cleaned.startswith('```'):
                cleaned = cleaned[3:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            data = None

            # 尝试1：直接解析
            try:
                data = json.loads(cleaned)
            except json.JSONDecodeError:
                pass

            # 尝试2：提取最外层 JSON 对象
            if data is None:
                json_match = re.search(r'\{[\s\S]*\}', cleaned)
                if json_match:
                    try:
                        data = json.loads(json_match.group())
                    except json.JSONDecodeError:
                        pass

            # 尝试3：修复截断的 JSON（逐步裁剪尾部找到合法 JSON 子串）
            if data is None:
                # 尝试补全截断的 JSON
                for suffix in ['}}}', '}}', '}', ']}}}', ']}}', ']}', '"]}}}', '"]}', '"]}}']:
                    try:
                        data = json.loads(cleaned + suffix)
                        self.log(f"通过补全 '{suffix}' 修复了截断的JSON")
                        break
                    except json.JSONDecodeError:
                        continue

            # 尝试4：只提取 overall_evaluation 部分
            if data is None:
                oe_match = re.search(r'"overall_evaluation"\s*:\s*(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})', cleaned)
                if oe_match:
                    try:
                        oe_data = json.loads(oe_match.group(1))
                        data = {"overall_evaluation": oe_data}
                        self.log("从截断JSON中成功提取 overall_evaluation")
                    except json.JSONDecodeError:
                        pass

            # 尝试5：用正则直接提取 scores
            if data is None:
                scores = {}
                for dim in ['accuracy', 'timeliness', 'personalization', 'safety', 'diversity', 'novelty']:
                    score_match = re.search(rf'"{dim}"\s*:\s*(\d+)', cleaned)
                    if score_match:
                        scores[dim] = int(score_match.group(1))
                if scores:
                    self.log(f"通过正则从截断JSON中提取了 {len(scores)} 个维度分数")
                    # 提取 issues 和 suggestions
                    issues = re.findall(r'"issues"\s*:\s*\[(.*?)\]', cleaned, re.DOTALL)
                    suggestions = re.findall(r'"suggestions"\s*:\s*\[(.*?)\]', cleaned, re.DOTALL)
                    issue_list = re.findall(r'"([^"]+)"', issues[0]) if issues else []
                    suggestion_list = re.findall(r'"([^"]+)"', suggestions[0]) if suggestions else []
                    summary_match = re.search(r'"evaluation_summary"\s*:\s*"([^"]*)"', cleaned)
                    summary = summary_match.group(1) if summary_match else ""
                    return {
                        "scores": scores,
                        "issues": issue_list,
                        "suggestions": suggestion_list,
                        "evaluation_table": [],
                        "overall_score": 0,
                        "evaluation_summary": summary
                    }

            if data is None:
                self.log(f"无法解析大模型输出: {result[:200]}...")
                return {"scores": {}, "issues": [], "suggestions": []}

        # 支持新的表格格式
        if "evaluation_table" in data or "overall_evaluation" in data:
            overall = data.get("overall_evaluation", {})
            table = data.get("evaluation_table", [])

            return {
                "scores": overall.get("scores", {}),
                "issues": overall.get("issues", []),
                "suggestions": overall.get("suggestions", []),
                "evaluation_table": table,
                "overall_score": overall.get("overall_score", 0),
                "evaluation_summary": overall.get("evaluation_summary", "")
            }
        else:
            # 兼容旧格式
            return {
                "scores": data.get("scores", {}),
                "issues": data.get("issues", []),
                "suggestions": data.get("suggestions", [])
            }
    
    def _eval_with_rule(self, query: str, response: str, structured_items: List, dimensions: List[str]) -> Dict:
        """使用规则引擎评测（作为回退）"""
        scores = {}
        issues = []
        
        if "accuracy" in dimensions:
            scores["accuracy"] = self._eval_accuracy(query, response, [], structured_items)
        
        if "timeliness" in dimensions:
            scores["timeliness"] = self._eval_timeliness(query, response, [], "")
        
        if "personalization" in dimensions:
            scores["personalization"] = self._eval_personalization(query, response, [], [])
        
        if "safety" in dimensions:
            safety_result = self._eval_safety(query, response, [], [])
            scores["safety"] = safety_result["score"]
            issues.extend(safety_result.get("issues", []))
        
        if "diversity" in dimensions:
            scores["diversity"] = self._eval_diversity(response, structured_items)
        
        if "novelty" in dimensions:
            scores["novelty"] = self._eval_novelty(response)
        
        suggestions = self._generate_suggestions(scores, issues)
        
        return {"scores": scores, "issues": issues, "suggestions": suggestions}
    
    def _eval_accuracy(self, query: str, response: str, tags: List[str], structured_items: List = None) -> float:
        """评估推荐准确性"""
        score = 3.0  # 基础分
        
        # 如果有结构化数据，优先使用
        if structured_items and len(structured_items) > 0:
            # 推荐商品数量
            if len(structured_items) >= 3:
                score += 1.0
            elif len(structured_items) >= 1:
                score += 0.5
            
            # 检查商品相关性评分
            avg_score = sum(item.get('llmRelevantLevelScore', 0) for item in structured_items) / len(structured_items)
            if avg_score >= 4:
                score += 1.0
            elif avg_score >= 3:
                score += 0.5
        else:
            # 使用文本内容评测
            if any(word in response for word in ["推荐", "建议", "可以", "适合"]):
                score += 0.5
            
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
    
    def _eval_timeliness(self, query: str, response: str, tags: List[str], time_commitment: str = None) -> float:
        """评估时效感知"""
        score = 3.0
        
        # 检查是否是应急场景
        is_urgent = any(tag in tags for tag in ["S1", "应急", "急"])
        
        # 如果有提取的时效承诺，优先使用
        if time_commitment:
            if is_urgent:
                score = 5.0  # 应急场景有时效承诺
            else:
                score = 4.0
        elif is_urgent:
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
    
    def _eval_personalization(self, query: str, response: str, tags: List[str], personalization_elements: List = None) -> float:
        """评估个性化程度"""
        score = 3.0
        
        # 如果有提取的个性化元素，优先使用
        if personalization_elements and len(personalization_elements) > 0:
            score += min(2.0, len(personalization_elements) * 0.5)
        else:
            # 使用文本内容评测
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
    
    def _eval_safety(self, query: str, response: str, tags: List[str], safety_warnings: List = None) -> Dict:
        """评估安全合规"""
        score = 5.0
        issues = []
        
        # 检查是否是医药场景
        is_medical = any(tag in tags for tag in ["C5", "医药", "药"])
        
        if is_medical:
            # 如果有提取的安全警告，优先使用
            if safety_warnings is not None:
                if len(safety_warnings) == 0:
                    score = 2.0
                    issues.append("医药品类缺少安全提示")
            else:
                # 使用文本内容检查
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
    
    def _eval_diversity(self, response: str, structured_items: List = None) -> float:
        """评估推荐多样性"""
        score = 3.0
        
        # 优先使用结构化商品数量
        if structured_items is not None:
            item_count = len(structured_items)
            if item_count >= 5:
                score = 5.0
            elif item_count >= 3:
                score = 4.5
            elif item_count >= 2:
                score = 4.0
            elif item_count >= 1:
                score = 3.0
            else:
                score = 2.0
        else:
            # 使用文本内容评测
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
    
    def _eval_shop_quality(self, structured_items: List) -> float:
        """
        评估店铺质量（店维度）
        考察指标：配送距离、配送时效、品牌集中度、店铺评分
        """
        if not structured_items:
            return 2.0  # 没有数据
        
        score = 3.0  # 基础分
        
        # 按店铺分组
        shop_groups = {}
        for item in structured_items:
            shop = item.get('shopName', '')
            if shop:
                if shop not in shop_groups:
                    shop_groups[shop] = {
                        'distance': item.get('distance', ''),
                        'rating': item.get('rating', ''),
                        'brandName': item.get('brandName', ''),
                        'items': []
                    }
                shop_groups[shop]['items'].append(item)
        
        shop_count = len(shop_groups)
        if shop_count == 0:
            return 2.0
        
        # 1. 配送距离评分（平均）
        distances = []
        for shop_data in shop_groups.values():
            d = shop_data.get('distance', '')
            if d:
                try:
                    distances.append(float(str(d).replace('m', '')))
                except:
                    pass
        
        if distances:
            avg_distance = sum(distances) / len(distances)
            if avg_distance <= 1000:
                score += 1.0  # 1km内加分
            elif avg_distance <= 2000:
                score += 0.5
            elif avg_distance > 5000:
                score -= 0.5  # 超过5km扣分
        
        # 2. 配送时效（从 distance 推断，近=快）
        if distances:
            avg_distance = sum(distances) / len(distances)
            if avg_distance <= 1500:
                score += 0.5  # 近距离暗示快配送
        
        # 3. 品牌集中度（同一店铺下品牌多样性）
        brand_entropy = 0
        total_items = len(structured_items)
        for shop_data in shop_groups.values():
            shop_items = shop_data['items']
            p = len(shop_items) / total_items
            if p > 0:
                brand_entropy -= p * (1 if len(set(i.get('brandName', '') for i in shop_items if i.get('brandName'))) > 0 else 0.5)
        
        if brand_entropy > 0.3:
            score += 0.5  # 品牌多样性好
        
        # 4. 店铺评分
        ratings = []
        for shop_data in shop_groups.values():
            r = shop_data.get('rating', '')
            if r:
                try:
                    ratings.append(float(r))
                except:
                    pass
        
        if ratings:
            avg_rating = sum(ratings) / len(ratings)
            if avg_rating >= 4.5:
                score += 1.0
            elif avg_rating >= 4.0:
                score += 0.5
            elif avg_rating < 3.5:
                score -= 0.5
        
        return max(1.0, min(5.0, score))
    
    def _eval_product_richness(self, structured_items: List) -> float:
        """
        评估商品丰富性（品维度）
        考察指标：商品相关性、商品丰富性（数量+多样性）
        """
        if not structured_items:
            return 2.0
        
        score = 3.0  # 基础分
        
        # 1. 商品数量
        item_count = len(structured_items)
        if item_count >= 10:
            score += 1.5
        elif item_count >= 5:
            score += 1.0
        elif item_count >= 3:
            score += 0.5
        elif item_count <= 1:
            score -= 0.5
        
        # 2. 相关性评分分布
        relevance_scores = []
        for item in structured_items:
            s = item.get('llmRelevantLevelScore', '')
            if s:
                try:
                    relevance_scores.append(float(s))
                except:
                    pass
        
        if relevance_scores:
            avg_relevance = sum(relevance_scores) / len(relevance_scores)
            if avg_relevance >= 4:
                score += 1.0
            elif avg_relevance >= 3:
                score += 0.5
            elif avg_relevance < 2:
                score -= 0.5
        
        # 3. 品类多样性（不同商品名称数量）
        unique_items = set(item.get('itemName', '') for item in structured_items)
        unique_count = len(unique_items)
        if unique_count >= 8:
            score += 0.5
        elif unique_count >= 5:
            score += 0.3
        
        # 4. 品牌多样性
        unique_brands = set(item.get('brandName', '') for item in structured_items if item.get('brandName'))
        if len(unique_brands) >= 3:
            score += 0.5
        elif len(unique_brands) >= 1:
            score += 0.3
        
        # 5. 店铺多样性
        unique_shops = set(item.get('shopName', '') for item in structured_items)
        if len(unique_shops) >= 3:
            score += 0.5
        elif len(unique_shops) >= 2:
            score += 0.3
        
        return max(1.0, min(5.0, score))
    
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
                elif dimension == "shop_quality":
                    suggestions.append("优化店铺质量：优先推荐距离近、评分高、时效快的店铺")
                elif dimension == "product_richness":
                    suggestions.append("丰富商品选择：增加商品数量和品类多样性，提升相关性")
        
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
