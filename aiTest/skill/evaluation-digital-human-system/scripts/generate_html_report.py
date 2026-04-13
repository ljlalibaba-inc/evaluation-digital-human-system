#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大模型数字人评测报告HTML生成器
生成美观的HTML格式报告
"""

import json
from typing import Dict, List, Any
from datetime import datetime


class HTMLReportGenerator:
    """HTML报告生成器"""
    
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
    
    def _get_score_color(self, score: float) -> str:
        """根据分数获取颜色"""
        if score >= 4.5:
            return "#52c41a"  # 绿色-优秀
        elif score >= 4.0:
            return "#1890ff"  # 蓝色-良好
        elif score >= 3.5:
            return "#faad14"  # 橙色-一般
        else:
            return "#f5222d"  # 红色-需改进
    
    def _get_score_level(self, score: float) -> str:
        """根据分数获取等级"""
        if score >= 4.5:
            return "优秀"
        elif score >= 4.0:
            return "良好"
        elif score >= 3.5:
            return "一般"
        else:
            return "需改进"
    
    def generate_html(self) -> str:
        """生成完整HTML报告"""
        summary = self.data.get('execution_summary', {})
        results = self.data.get('detailed_results', [])
        
        # 统计数据
        total_cases = summary.get('results_summary', {}).get('total_evaluated', 0)
        avg_score = summary.get('results_summary', {}).get('average_score', 0)
        pass_count = summary.get('results_summary', {}).get('pass_count', 0)
        pass_rate = (pass_count / total_cases * 100) if total_cases > 0 else 0
        
        # 涉及的人群
        personas = set()
        for result in results:
            query_id = result.get('query_id', '')
            persona = self._get_persona_by_query_id(query_id)
            personas.add(persona)
        
        persona_names = [self.PERSONA_NAMES.get(p, p) for p in personas]
        
        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>大模型数字人评测报告</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 32px;
            margin-bottom: 10px;
            font-weight: 600;
        }}
        
        .header .subtitle {{
            font-size: 16px;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .summary-section {{
            background: #f8f9fa;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
        }}
        
        .summary-title {{
            font-size: 20px;
            color: #333;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
        }}
        
        .summary-title::before {{
            content: "";
            width: 4px;
            height: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin-right: 10px;
            border-radius: 2px;
        }}
        
        .summary-text {{
            font-size: 16px;
            line-height: 1.8;
            color: #555;
        }}
        
        .summary-text strong {{
            color: #667eea;
            font-size: 18px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .stat-card {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-value {{
            font-size: 36px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            font-size: 14px;
            color: #888;
        }}
        
        .detail-section {{
            margin-top: 30px;
        }}
        
        .detail-title {{
            font-size: 20px;
            color: #333;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
        }}
        
        .detail-title::before {{
            content: "";
            width: 4px;
            height: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin-right: 10px;
            border-radius: 2px;
        }}
        
        .table-container {{
            overflow-x: auto;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
        }}
        
        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 500;
            font-size: 14px;
        }}
        
        td {{
            padding: 15px;
            border-bottom: 1px solid #eee;
            font-size: 14px;
            color: #555;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        tr:last-child td {{
            border-bottom: none;
        }}
        
        .persona-tag {{
            display: inline-block;
            padding: 4px 12px;
            background: #e6f7ff;
            color: #1890ff;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
        }}
        
        .scenario-tag {{
            display: inline-block;
            padding: 4px 12px;
            background: #f6ffed;
            color: #52c41a;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
        }}
        
        .category-tag {{
            display: inline-block;
            padding: 4px 12px;
            background: #fff7e6;
            color: #fa8c16;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
        }}
        
        .score-badge {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 6px 12px;
            border-radius: 20px;
            font-weight: 500;
            font-size: 13px;
        }}
        
        .score-excellent {{
            background: #f6ffed;
            color: #52c41a;
        }}
        
        .score-good {{
            background: #e6f7ff;
            color: #1890ff;
        }}
        
        .score-warning {{
            background: #fffbe6;
            color: #faad14;
        }}
        
        .score-danger {{
            background: #fff1f0;
            color: #f5222d;
        }}
        
        .test-case {{
            max-width: 400px;
            line-height: 1.6;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px 40px;
            text-align: center;
            color: #888;
            font-size: 12px;
            border-top: 1px solid #eee;
        }}
        
        .legend {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 20px;
            flex-wrap: wrap;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
            color: #666;
        }}
        
        .legend-icon {{
            width: 16px;
            height: 16px;
            border-radius: 50%;
        }}
        
        .info-section {{
            background: #e6f7ff;
            border-left: 4px solid #1890ff;
            padding: 20px;
            margin-top: 30px;
            border-radius: 0 8px 8px 0;
        }}
        
        .info-title {{
            font-size: 16px;
            color: #1890ff;
            margin-bottom: 10px;
            font-weight: 500;
        }}
        
        .info-list {{
            list-style: none;
            color: #555;
            font-size: 14px;
            line-height: 2;
        }}
        
        .info-list li::before {{
            content: "•";
            color: #1890ff;
            font-weight: bold;
            margin-right: 8px;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 24px;
            }}
            
            .content {{
                padding: 20px;
            }}
            
            .stats-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
            
            th, td {{
                padding: 10px;
                font-size: 12px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 大模型数字人评测报告</h1>
            <div class="subtitle">搜推大模型测评数字人系统 | {datetime.now().strftime('%Y年%m月%d日')}</div>
        </div>
        
        <div class="content">
            <!-- 总结部分 -->
            <div class="summary-section">
                <div class="summary-title">📊 报告总结</div>
                <div class="summary-text">
                    本次评测涉及 <strong>{len(personas)}</strong> 个数字人（{', '.join(persona_names)}），
                    共进行了 <strong>{total_cases}</strong> 个测试用例，
                    整体结果 <strong style="color: {self._get_score_color(avg_score)}">{self._get_score_level(avg_score)}</strong>
                    （平均分 {avg_score:.2f}/5.0，通过率 {pass_rate:.1f}%）。
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">{len(personas)}</div>
                        <div class="stat-label">数字人</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{total_cases}</div>
                        <div class="stat-label">测试用例</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" style="color: {self._get_score_color(avg_score)}">{avg_score:.2f}</div>
                        <div class="stat-label">平均分</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" style="color: {self._get_score_color(pass_rate/20)}">{pass_rate:.1f}%</div>
                        <div class="stat-label">通过率</div>
                    </div>
                </div>
            </div>
            
            <!-- 明细部分 -->
            <div class="detail-section">
                <div class="detail-title">📋 评测明细</div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th style="width: 15%">人设</th>
                                <th style="width: 12%">场景</th>
                                <th style="width: 12%">品类</th>
                                <th style="width: 46%">测试用例</th>
                                <th style="width: 15%">评测结果</th>
                            </tr>
                        </thead>
                        <tbody>
                            {self._generate_table_rows(results)}
                        </tbody>
                    </table>
                </div>
                
                <div class="legend">
                    <div class="legend-item">
                        <div class="legend-icon" style="background: #52c41a;"></div>
                        <span>优秀 (≥4.5分)</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-icon" style="background: #1890ff;"></div>
                        <span>良好 (4.0-4.5分)</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-icon" style="background: #faad14;"></div>
                        <span>一般 (3.5-4.0分)</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-icon" style="background: #f5222d;"></div>
                        <span>需改进 (<3.5分)</span>
                    </div>
                </div>
            </div>
            
            <!-- 说明部分 -->
            <div class="info-section">
                <div class="info-title">ℹ️ 评测说明</div>
                <ul class="info-list">
                    <li><strong>评分标准</strong>：5分制，4分及以上为通过</li>
                    <li><strong>评测维度</strong>：准确性、时效性、个性化、安全性</li>
                    <li><strong>数字人模型</strong>：基于用户画像(P) × 场景(S) × 品类(C)三维模型</li>
                    <li><strong>评测模型</strong>：{summary.get('task_config', {}).get('target_model', 'unknown')}</li>
                </ul>
            </div>
        </div>
        
        <div class="footer">
            <p>搜推大模型测评数字人系统 | 报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>'''
        return html
    
    def _generate_table_rows(self, results: List[Dict]) -> str:
        """生成表格行"""
        rows = []
        
        for result in results:
            query_id = result.get('query_id', '')
            
            # 获取信息
            persona = self._get_persona_by_query_id(query_id)
            persona_name = self.PERSONA_NAMES.get(persona, persona)
            
            scenario = self._get_scenario_by_query_id(query_id)
            scenario_name = self.SCENARIO_NAMES.get(scenario, scenario)
            
            category = self._get_category_by_query_id(query_id)
            category_name = self.CATEGORY_NAMES.get(category, category)
            
            test_case = self._get_test_case_by_query_id(query_id)
            
            # 评测结果
            overall = result.get('overall_score', 0)
            issues = result.get('issues', [])
            
            # 确定样式
            if overall >= 4.5:
                score_class = "score-excellent"
                icon = "✓"
            elif overall >= 4.0:
                score_class = "score-good"
                icon = "✓"
            elif overall >= 3.5:
                score_class = "score-warning"
                icon = "⚠️"
            else:
                score_class = "score-danger"
                icon = "✗"
            
            if issues:
                result_text = f"{overall:.2f}分 {icon} {issues[0][:20]}"
            else:
                result_text = f"{overall:.2f}分 {icon}"
            
            row = f'''<tr>
    <td><span class="persona-tag">{persona_name}</span></td>
    <td><span class="scenario-tag">{scenario_name}</span></td>
    <td><span class="category-tag">{category_name}</span></td>
    <td><div class="test-case">{test_case}</div></td>
    <td><span class="score-badge {score_class}">{result_text}</span></td>
</tr>'''
            rows.append(row)
        
        return '\n'.join(rows)
    
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
        test_cases = {
            "Q001": "我是互联网公司的产品经理，经常加班到深夜，现在突然头痛得厉害，家里没有止痛药了",
            "Q017": "我是新手妈妈，宝宝突然发烧到39度，家里没有退热贴了，急需购买",
            "Q056": "我是加班族，颈椎最近很不舒服，想买一个颈椎按摩仪",
        }
        return test_cases.get(query_id, f"测试用例 {query_id}")


def main():
    """主函数"""
    report_file = "/Users/linjie/Documents/workspace/aiTest/skill/evaluation-digital-human-system/report_exec_20260409_180004_d9ce66.json"
    
    print("=" * 80)
    print("大模型数字人评测报告HTML生成器")
    print("=" * 80)
    print()
    
    # 生成HTML
    generator = HTMLReportGenerator(report_file)
    html = generator.generate_html()
    
    # 保存文件
    output_file = "/Users/linjie/Documents/workspace/aiTest/skill/evaluation-digital-human-system/评测报告.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✓ HTML报告已生成: {output_file}")
    print(f"✓ 文件大小: {len(html)} 字符")
    print()
    print("=" * 80)
    print("提示: 请用浏览器打开HTML文件查看报告")
    print("=" * 80)


if __name__ == "__main__":
    main()
