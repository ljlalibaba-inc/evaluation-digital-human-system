#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大模型数字人评测报告生成器
生成格式化的评测报告
"""

import json
from typing import Dict, List, Any
from datetime import datetime


class EvaluationReportGenerator:
    """评测报告生成器"""
    
    # 数字人名称映射
    PERSONA_NAMES = {
        "P1": "忙碌的年轻白领",
        "P2": "新手妈妈",
        "P3": "大学生",
        "P4": "精致白领",
        "P5": "退休阿姨",
        "P6": "双职工家庭"
    }
    
    # 场景名称映射
    SCENARIO_NAMES = {
        "S1": "应急补给",
        "S2": "即时享受",
        "S3": "懒人便利",
        "S4": "计划性消费",
        "S5": "节日聚会"
    }
    
    # 品类名称映射
    CATEGORY_NAMES = {
        "C1": "生鲜果蔬",
        "C2": "休闲零售",
        "C3": "3C数码",
        "C4": "母婴用品",
        "C5": "医药健康",
        "C6": "日用百货",
        "C7": "鲜花礼品",
        "C8": "宠物用品"
    }
    
    def __init__(self, report_file: str):
        """初始化报告生成器"""
        with open(report_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
    
    def generate_summary(self) -> str:
        """生成报告总结"""
        summary = self.data.get('execution_summary', {})
        results = self.data.get('detailed_results', [])
        
        # 统计涉及的人数字
        personas = set()
        for result in results:
            query_id = result.get('query_id', '')
            # 从query_id或详细数据中提取人群信息
            if query_id.startswith('Q'):
                # 根据query_id映射到人群
                query_num = int(query_id.replace('Q', ''))
                if query_num in [1, 16, 28, 33, 44, 56, 62, 68, 79, 91]:
                    personas.add("P1")
                elif query_num in [2, 10, 17, 24, 32, 40, 46, 58, 64, 70, 81, 87, 93, 99]:
                    personas.add("P2")
                elif query_num in [6, 15, 20, 26, 31, 37, 43, 49, 55, 61, 67, 72, 78, 84, 90, 96]:
                    personas.add("P3")
                elif query_num in [5, 13, 18, 23, 29, 34, 39, 45, 51, 57, 63, 69, 75, 80, 86, 92, 98]:
                    personas.add("P4")
                elif query_num in [8, 19, 25, 30, 35, 41, 47, 53, 59, 65, 71, 76, 82, 88, 94, 100]:
                    personas.add("P5")
                elif query_num in [3, 9, 11, 14, 21, 27, 36, 42, 48, 54, 60, 66, 83, 89, 95]:
                    personas.add("P6")
        
        persona_names = [self.PERSONA_NAMES.get(p, p) for p in personas]
        persona_str = "、".join(persona_names) if len(persona_names) <= 3 else f"{len(persona_names)}类人群"
        
        # 统计用例数
        total_cases = summary.get('results_summary', {}).get('total_evaluated', 0)
        
        # 计算整体结果
        avg_score = summary.get('results_summary', {}).get('average_score', 0)
        pass_count = summary.get('results_summary', {}).get('pass_count', 0)
        pass_rate = (pass_count / total_cases * 100) if total_cases > 0 else 0
        
        # 整体评价
        if avg_score >= 4.5:
            overall = "优秀"
        elif avg_score >= 4.0:
            overall = "良好"
        elif avg_score >= 3.5:
            overall = "一般"
        else:
            overall = "需改进"
        
        return f"""## 报告总结

本次评测涉及 **{len(personas)}** 个数字人（{persona_str}），共进行了 **{total_cases}** 个测试用例，整体结果 **{overall}**（平均分 {avg_score:.2f}/5.0，通过率 {pass_rate:.1f}%）。

"""
    
    def generate_detail_table(self) -> str:
        """生成明细表格"""
        results = self.data.get('detailed_results', [])
        
        # 构建明细数据
        details = []
        for result in results:
            query_id = result.get('query_id', '')
            
            # 映射人群
            persona = self._get_persona_by_query_id(query_id)
            persona_name = self.PERSONA_NAMES.get(persona, persona)
            
            # 映射场景和品类
            scenario = self._get_scenario_by_query_id(query_id)
            category = self._get_category_by_query_id(query_id)
            
            # 获取测试用例文本
            test_case = self._get_test_case_by_query_id(query_id)
            
            # 评测结果
            scores = result.get('scores', {})
            overall = result.get('overall_score', 0)
            issues = result.get('issues', [])
            
            # 格式化评测结果
            if issues:
                eval_result = f"{overall:.2f}分 ⚠️ {issues[0]}"
            elif overall >= 4.0:
                eval_result = f"{overall:.2f}分 ✓"
            else:
                eval_result = f"{overall:.2f}分 ✗"
            
            details.append({
                'persona': persona_name,
                'scenario': '聚合' if not scenario else self.SCENARIO_NAMES.get(scenario, scenario),
                'category': self.CATEGORY_NAMES.get(category, category),
                'test_case': test_case[:60] + '...' if len(test_case) > 60 else test_case,
                'eval_result': eval_result
            })
        
        # 生成Markdown表格
        table = """## 评测明细

| 人设 | 场景 | 品类 | 测试用例 | 评测结果 |
|------|------|------|----------|----------|
"""
        
        for d in details:
            table += f"| {d['persona']} | {d['scenario']} | {d['category']} | {d['test_case']} | {d['eval_result']} |\n"
        
        return table
    
    def _get_persona_by_query_id(self, query_id: str) -> str:
        """根据Query ID获取人群"""
        query_num = int(query_id.replace('Q', ''))
        
        if query_num in [1, 16, 28, 33, 44, 56, 62, 68, 79, 91]:
            return "P1"
        elif query_num in [2, 10, 17, 24, 32, 40, 46, 58, 64, 70, 81, 87, 93, 99]:
            return "P2"
        elif query_num in [6, 15, 20, 26, 31, 37, 43, 49, 55, 61, 67, 72, 78, 84, 90, 96]:
            return "P3"
        elif query_num in [5, 13, 18, 23, 29, 34, 39, 45, 51, 57, 63, 69, 75, 80, 86, 92, 98]:
            return "P4"
        elif query_num in [8, 19, 25, 30, 35, 41, 47, 53, 59, 65, 71, 76, 82, 88, 94, 100]:
            return "P5"
        else:
            return "P6"
    
    def _get_scenario_by_query_id(self, query_id: str) -> str:
        """根据Query ID获取场景"""
        query_num = int(query_id.replace('Q', ''))
        
        if query_num in [1, 2, 3, 16, 17, 18, 19, 21, 31, 33, 37, 44, 46, 47, 56, 62]:
            return "S1"
        elif query_num in [4, 5, 6, 15, 20, 22, 27, 28, 29, 38, 41, 47, 54, 68, 69, 73, 75, 79, 80]:
            return "S2"
        elif query_num in [7, 8, 9, 19, 35, 55]:
            return "S3"
        elif query_num in [10, 11, 12, 24, 26, 30, 32, 34, 36, 39, 40, 45, 48, 49, 51, 53, 57, 58, 60, 61, 63, 64, 65, 66, 67, 70, 82, 83, 87, 88, 89, 90, 93, 94, 95, 96, 97, 99, 100]:
            return "S4"
        else:
            return "S5"
    
    def _get_category_by_query_id(self, query_id: str) -> str:
        """根据Query ID获取品类"""
        query_num = int(query_id.replace('Q', ''))
        
        if query_num in [3, 5, 11, 14, 24, 27, 42, 47, 54, 81]:
            return "C1"
        elif query_num in [4, 6, 15, 20, 28, 29, 41, 51, 53, 54, 55, 59, 61, 73, 78, 79, 90]:
            return "C2"
        elif query_num in [18, 26, 31, 37, 44, 56, 62, 67, 86, 92, 95, 97]:
            return "C3"
        elif query_num in [2, 9, 10, 17, 24, 25, 32, 36, 40, 46, 48, 58, 60, 64, 66, 70, 81, 83, 87, 93, 99]:
            return "C4"
        elif query_num in [1, 16, 19, 30, 38, 56, 64, 68, 79, 82, 88, 91, 94, 97, 100]:
            return "C5"
        elif query_num in [7, 8, 12, 21, 23, 29, 35, 39, 44, 57, 63, 65, 69, 89, 96, 98]:
            return "C6"
        elif query_num in [13, 14, 23, 25, 43, 72, 75, 76]:
            return "C7"
        else:
            return "C8"
    
    def _get_test_case_by_query_id(self, query_id: str) -> str:
        """根据Query ID获取测试用例文本"""
        # 从数据集加载
        test_cases = {
            "Q001": "我是互联网公司的产品经理，经常加班到深夜，现在突然头痛得厉害，家里没有止痛药了",
            "Q017": "我是新手妈妈，宝宝突然发烧到39度，家里没有退热贴了，急需购买",
            "Q056": "我是加班族，颈椎最近很不舒服，想买一个颈椎按摩仪",
            "Q079": "我是加班族，有糖尿病，加班时饿了能吃什么",
        }
        return test_cases.get(query_id, f"测试用例 {query_id}")
    
    def generate_full_report(self) -> str:
        """生成完整报告"""
        report = f"""# 大模型数字人评测报告

**报告生成时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}

**评测模型**: {self.data.get('execution_summary', {}).get('task_config', {}).get('target_model', 'unknown')}

---

"""
        report += self.generate_summary()
        report += "\n---\n\n"
        report += self.generate_detail_table()
        report += """

---

## 评测说明

- **评分标准**: 5分制，4分及以上为通过
- **评测维度**: 准确性、时效性、个性化、安全性
- **数字人**: 基于用户画像(P) × 场景(S) × 品类(C)三维模型
- **⚠️**: 表示发现问题需要改进
- **✓**: 表示评测通过
- **✗**: 表示评测未通过

"""
        return report


def main():
    """主函数"""
    import sys
    
    # 使用最新的报告文件
    report_file = "/Users/linjie/Documents/workspace/aiTest/skill/evaluation-digital-human-system/report_exec_20260409_180004_d9ce66.json"
    
    print("=" * 80)
    print("大模型数字人评测报告生成器")
    print("=" * 80)
    print()
    
    # 生成报告
    generator = EvaluationReportGenerator(report_file)
    report = generator.generate_full_report()
    
    # 输出到控制台
    print(report)
    
    # 保存到文件
    output_file = "/Users/linjie/Documents/workspace/aiTest/skill/evaluation-digital-human-system/评测报告.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n报告已保存: {output_file}")
    print("=" * 80)


if __name__ == "__main__":
    main()
