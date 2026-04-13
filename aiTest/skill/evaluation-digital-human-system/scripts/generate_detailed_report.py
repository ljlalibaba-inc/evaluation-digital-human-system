#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细评测报告生成器
包含人设、场景、品类全部分类，展示千问完整返回内容
"""

import json
from typing import Dict, List, Any
from datetime import datetime


class DetailedReportGenerator:
    """详细报告生成器"""
    
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
            return "#52c41a"
        elif score >= 4.0:
            return "#1890ff"
        elif score >= 3.5:
            return "#faad14"
        else:
            return "#f5222d"
    
    def generate_html(self) -> str:
        """生成完整HTML报告"""
        summary = self.data.get('execution_summary', {})
        results = self.data.get('detailed_results', [])
        
        # 获取完整的响应数据
        full_results = self.data.get('results', {})
        responses = full_results.get('responses', [])
        parsed_results = full_results.get('parsed', [])
        
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
    <title>大模型数字人详细评测报告</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: #f5f7fa;
            min-height: 100vh;
            padding: 20px;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{ font-size: 32px; margin-bottom: 10px; font-weight: 600; }}
        .header .subtitle {{ font-size: 16px; opacity: 0.9; }}
        
        .content {{ padding: 40px; }}
        
        /* 统计卡片 */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .stat-card {{
            background: white;
            border-radius: 12px;
            padding: 24px;
            text-align: center;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            border: 1px solid #e8e8e8;
        }}
        
        .stat-value {{
            font-size: 36px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 8px;
        }}
        
        .stat-label {{ font-size: 14px; color: #888; }}
        
        /* 分类标签 */
        .category-tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            flex-wrap: wrap;
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 20px;
        }}
        
        .tab {{
            padding: 10px 20px;
            background: #f5f5f5;
            border-radius: 20px;
            font-size: 14px;
            color: #666;
            cursor: pointer;
            transition: all 0.3s;
        }}
        
        .tab:hover, .tab.active {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        /* 详情卡片 */
        .detail-card {{
            background: white;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            border: 1px solid #e8e8e8;
        }}
        
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 16px;
            border-bottom: 2px solid #f0f0f0;
        }}
        
        .card-title {{
            font-size: 18px;
            font-weight: 600;
            color: #333;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .card-score {{
            font-size: 24px;
            font-weight: bold;
            padding: 8px 16px;
            border-radius: 20px;
            color: white;
        }}
        
        /* 标签 */
        .tag {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
            margin-right: 8px;
        }}
        
        .tag-persona {{ background: #e6f7ff; color: #1890ff; }}
        .tag-scenario {{ background: #f6ffed; color: #52c41a; }}
        .tag-category {{ background: #fff7e6; color: #fa8c16; }}
        .tag-priority {{ background: #fff1f0; color: #f5222d; }}
        
        /* 内容区块 */
        .section {{
            margin-bottom: 20px;
        }}
        
        .section-title {{
            font-size: 14px;
            font-weight: 600;
            color: #666;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .section-content {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 16px;
            font-size: 14px;
            line-height: 1.8;
            color: #333;
            border-left: 4px solid #667eea;
        }}
        
        .qwen-response {{
            background: #f6ffed;
            border-left-color: #52c41a;
            max-height: 300px;
            overflow-y: auto;
            white-space: pre-wrap;
        }}
        
        .test-case {{
            background: #e6f7ff;
            border-left-color: #1890ff;
        }}
        
        .evaluation-result {{
            background: #fff7e6;
            border-left-color: #faad14;
        }}
        
        /* 评分维度 */
        .score-dimensions {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 12px;
            margin-top: 16px;
        }}
        
        .dimension-item {{
            background: #f5f5f5;
            padding: 12px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .dimension-name {{ font-size: 12px; color: #888; margin-bottom: 4px; }}
        .dimension-score {{ font-size: 18px; font-weight: bold; color: #333; }}
        
        /* 问题提示 */
        .issue-alert {{
            background: #fff1f0;
            border: 1px solid #ffa39e;
            border-radius: 8px;
            padding: 12px 16px;
            margin-top: 16px;
            color: #cf1322;
            font-size: 14px;
        }}
        
        .issue-alert::before {{
            content: "⚠️ ";
            margin-right: 8px;
        }}
        
        /* 表格 */
        .summary-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            font-size: 14px;
        }}
        
        .summary-table th {{
            background: #fafafa;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #666;
            border-bottom: 2px solid #e8e8e8;
        }}
        
        .summary-table td {{
            padding: 12px;
            border-bottom: 1px solid #e8e8e8;
        }}
        
        .summary-table tr:hover {{
            background: #fafafa;
        }}
        
        /* 折叠面板 */
        .collapsible {{
            background: #f8f9fa;
            border-radius: 8px;
            margin-top: 12px;
        }}
        
        .collapsible-header {{
            padding: 12px 16px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: 500;
            color: #666;
        }}
        
        .collapsible-content {{
            padding: 16px;
            display: none;
            border-top: 1px solid #e8e8e8;
        }}
        
        .collapsible-content.active {{
            display: block;
        }}
        
        .footer {{
            background: #fafafa;
            padding: 20px 40px;
            text-align: center;
            color: #888;
            font-size: 12px;
            border-top: 1px solid #e8e8e8;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{ font-size: 24px; }}
            .content {{ padding: 20px; }}
            .stats-grid {{ grid-template-columns: repeat(2, 1fr); }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 大模型数字人详细评测报告</h1>
            <div class="subtitle">搜推大模型测评数字人系统 | {datetime.now().strftime('%Y年%m月%d日 %H:%M')}</div>
        </div>
        
        <div class="content">
            <!-- 统计概览 -->
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{len(personas)}</div>
                    <div class="stat-label">数字人设</div>
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
                    <div class="stat-value">{pass_rate:.1f}%</div>
                    <div class="stat-label">通过率</div>
                </div>
            </div>
            
            <!-- 涉及人群 -->
            <div class="category-tabs">
                <div class="tab active">全部</div>
                {''.join([f'<div class="tab">{name}</div>' for name in persona_names])}
            </div>
            
            <!-- 详细评测记录 -->
            <h2 style="margin-bottom: 24px; color: #333;">📋 详细评测记录</h2>
            
            {self._generate_detail_cards(results, responses, parsed_results)}
            
            <!-- 改进建议汇总 -->
            <div class="detail-card" style="margin-top: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                <div class="card-header" style="border-bottom-color: rgba(255,255,255,0.3);">
                    <div class="card-title" style="color: white;">💡 改进建议汇总</div>
                </div>
                {self._generate_improvement_summary(results)}
            </div>
            
            <!-- 汇总表格 -->
            <div class="detail-card" style="margin-top: 40px;">
                <div class="card-header">
                    <div class="card-title">📊 评测汇总表</div>
                </div>
                <table class="summary-table">
                    <thead>
                        <tr>
                            <th>Query ID</th>
                            <th>人设</th>
                            <th>场景</th>
                            <th>品类</th>
                            <th>总分</th>
                            <th>状态</th>
                        </tr>
                    </thead>
                    <tbody>
                        {self._generate_summary_rows(results)}
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="footer">
            <p>搜推大模型测评数字人系统 | 报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
    
    <script>
        // 折叠面板交互
        document.querySelectorAll('.collapsible-header').forEach(header => {{
            header.addEventListener('click', function() {{
                const content = this.nextElementSibling;
                content.classList.toggle('active');
                const arrow = this.querySelector('.arrow');
                if (arrow) {{
                    arrow.textContent = content.classList.contains('active') ? '▼' : '▶';
                }}
            }});
        }});
        
        // Tab切换功能
        const tabs = document.querySelectorAll('.tab');
        const cards = document.querySelectorAll('.detail-card[data-persona]');
        
        tabs.forEach(tab => {{
            tab.addEventListener('click', function() {{
                // 移除所有active状态
                tabs.forEach(t => t.classList.remove('active'));
                this.classList.add('active');
                
                const filter = this.textContent.trim();
                
                // 过滤卡片
                cards.forEach(card => {{
                    if (filter === '全部') {{
                        card.style.display = 'block';
                    }} else {{
                        const persona = card.getAttribute('data-persona');
                        if (persona && persona.includes(filter)) {{
                            card.style.display = 'block';
                        }} else {{
                            card.style.display = 'none';
                        }}
                    }}
                }});
                
                // 更新统计
                updateStats();
            }});
        }});
        
        // 更新统计信息
        function updateStats() {{
            const visibleCards = document.querySelectorAll('.detail-card[data-persona]:not([style*="none"])');
            const totalCount = document.querySelector('.stat-value');
            if (totalCount) {{
                totalCount.textContent = visibleCards.length;
            }}
        }}
    </script>
</body>
</html>'''
        return html
    
    def _generate_detail_cards(self, results: List[Dict], responses: List[Dict], parsed_results: List[Dict]) -> str:
        """生成详细卡片"""
        cards = []
        
        # 获取测试用例数据
        full_results = self.data.get('results', {})
        testcases = full_results.get('testcases', [])
        
        for i, result in enumerate(results):
            query_id = result.get('query_id', '')
            
            # 获取Query信息
            query_info = self._get_query_info(query_id, testcases)
            
            # 获取响应内容
            response_text = ""
            if i < len(responses):
                resp = responses[i]
                if isinstance(resp, dict):
                    response_data = resp.get('response', {})
                    if isinstance(response_data, dict):
                        response_text = response_data.get('content', str(response_data))
                    else:
                        response_text = str(response_data)
            
            # 获取解析结果
            parsed_info = {}
            if i < len(parsed_results):
                parsed = parsed_results[i]
                if isinstance(parsed, dict):
                    parsed_info = parsed.get('parsed', {})
            
            # 评分信息
            scores = result.get('scores', {})
            overall = result.get('overall_score', 0)
            issues = result.get('issues', [])
            
            # 确定状态
            if issues:
                status_icon = "⚠️"
                status_text = "发现问题"
            elif overall >= 4.0:
                status_icon = "✅"
                status_text = "通过"
            else:
                status_icon = "❌"
                status_text = "未通过"
            
            card = f'''
            <div class="detail-card" data-persona="{query_info['persona']}" data-scenario="{query_info['scenario']}" data-category="{query_info['category']}">
                <div class="card-header">
                    <div class="card-title">
                        <span>#{query_id}</span>
                        <span class="tag tag-persona">{query_info['persona']}</span>
                        <span class="tag tag-scenario">{query_info['scenario']}</span>
                        <span class="tag tag-category">{query_info['category']}</span>
                    </div>
                    <div class="card-score" style="background: {self._get_score_color(overall)}">
                        {overall:.2f}分
                    </div>
                </div>
                
                <!-- 测试用例 -->
                <div class="section">
                    <div class="section-title">📝 测试用例（用户输入）</div>
                    <div class="section-content test-case">
                        {query_info['test_case']}
                    </div>
                </div>
                
                <!-- 千问返回内容 -->
                <div class="section">
                    <div class="section-title">🤖 千问模型返回内容</div>
                    <div class="section-content qwen-response">
                        {response_text if response_text else "（无响应内容）"}
                    </div>
                </div>
                
                <!-- 解析结果 -->
                <div class="collapsible">
                    <div class="collapsible-header">
                        <span>🔍 解析详情（点击展开）</span>
                        <span class="arrow">▶</span>
                    </div>
                    <div class="collapsible-content">
                        <div style="font-size: 13px; color: #666;">
                            <p><strong>推荐商品：</strong>{', '.join(parsed_info.get('recommended_products', [])[:5]) if parsed_info.get('recommended_products') else '无'}</p>
                            <p><strong>时效承诺：</strong>{parsed_info.get('time_commitment', '无')}</p>
                            <p><strong>个性化元素：</strong>{', '.join(parsed_info.get('personalization_elements', [])) if parsed_info.get('personalization_elements') else '无'}</p>
                            <p><strong>安全提示：</strong>{', '.join(parsed_info.get('safety_warnings', [])) if parsed_info.get('safety_warnings') else '无'}</p>
                        </div>
                    </div>
                </div>
                
                <!-- 评测结果 -->
                <div class="section" style="margin-top: 20px;">
                    <div class="section-title">📊 多维度评测结果</div>
                    <div class="score-dimensions">
                        {self._generate_dimension_scores(scores)}
                    </div>
                </div>
                
                <!-- 问题提示 -->
                {f'<div class="issue-alert">{issues[0]}</div>' if issues else ''}
                
                <!-- 状态标签 -->
                <div style="margin-top: 16px; text-align: right;">
                    <span style="font-size: 14px; color: {self._get_score_color(overall)}; font-weight: 500;">
                        {status_icon} {status_text}
                    </span>
                </div>
            </div>'''
            cards.append(card)
        
        return '\n'.join(cards)
    
    def _generate_dimension_scores(self, scores: Dict) -> str:
        """生成维度评分"""
        dimensions = [
            ('accuracy', '准确性'),
            ('timeliness', '时效性'),
            ('personalization', '个性化'),
            ('safety', '安全性'),
            ('diversity', '多样性'),
            ('novelty', '新颖性')
        ]
        
        items = []
        for key, name in dimensions:
            score = scores.get(key, 0)
            color = self._get_score_color(score)
            items.append(f'''
                <div class="dimension-item">
                    <div class="dimension-name">{name}</div>
                    <div class="dimension-score" style="color: {color}">{score:.1f}</div>
                </div>
            ''')
        
        return '\n'.join(items)
    
    def _generate_summary_rows(self, results: List[Dict]) -> str:
        """生成汇总表格行"""
        rows = []
        
        # 获取测试用例数据
        full_results = self.data.get('results', {})
        testcases = full_results.get('testcases', [])
        
        for result in results:
            query_id = result.get('query_id', '')
            query_info = self._get_query_info(query_id, testcases)
            overall = result.get('overall_score', 0)
            issues = result.get('issues', [])
            
            status = "⚠️ 问题" if issues else ("✅ 通过" if overall >= 4.0 else "❌ 未通过")
            
            row = f'''<tr>
                <td>{query_id}</td>
                <td>{query_info['persona']}</td>
                <td>{query_info['scenario']}</td>
                <td>{query_info['category']}</td>
                <td style="color: {self._get_score_color(overall)}; font-weight: 600;">{overall:.2f}</td>
                <td>{status}</td>
            </tr>'''
            rows.append(row)
        return '\n'.join(rows)
    
    def _get_query_info(self, query_id: str, testcases: List[Dict] = None) -> Dict:
        """获取Query详细信息"""
        # 首先从testcases列表中查找实际的query_text
        query_text = None
        persona_code = None
        scenario_code = None
        category_code = None
        
        if testcases:
            for tc in testcases:
                if tc.get('query_id') == query_id:
                    query_text = tc.get('query_text', '')
                    persona_code = tc.get('persona_id', '')
                    scenario_code = tc.get('scenario_id', '')
                    category_code = tc.get('category_id', '')
                    break
        
        # 如果找到了query_text，直接使用
        if query_text:
            persona = self.PERSONA_NAMES.get(persona_code, persona_code)
            scenario = self.SCENARIO_NAMES.get(scenario_code, scenario_code)
            category = self.CATEGORY_NAMES.get(category_code, category_code)
            return {
                'persona': persona,
                'scenario': scenario,
                'category': category,
                'test_case': query_text
            }
        
        # 回退到旧逻辑（用于兼容旧数据）
        try:
            query_num = int(query_id.replace('Q', ''))
        except ValueError:
            query_num = 0
        
        # 测试用例文本（旧数据兼容）
        test_cases = {
            "Q001": "我是互联网公司的产品经理，经常加班到深夜，现在突然头痛得厉害，家里没有止痛药了，请推荐一款适合我的止痛药，要求30分钟内送到。",
            "Q017": "我是新手妈妈，宝宝突然发烧到39度，家里没有退热贴了，急需购买，多久能送到？",
            "Q056": "我是加班族，颈椎最近很不舒服，想买一个颈椎按摩仪，有什么推荐？",
        }
        
        # 人群映射
        if query_num in [1, 16, 28, 33, 44, 56, 62, 68, 79, 91]:
            persona = "P1"
        elif query_num in [2, 10, 17, 24, 32, 40, 46, 58, 64, 70]:
            persona = "P2"
        elif query_num in [6, 15, 20, 26, 31, 37, 43, 49, 55, 61]:
            persona = "P3"
        elif query_num in [5, 13, 18, 23, 29, 34, 39, 45, 51, 57]:
            persona = "P4"
        elif query_num in [8, 19, 25, 30, 35, 41, 47, 53, 59, 65]:
            persona = "P5"
        else:
            persona = "P6"
        
        # 场景映射
        if query_num in [1, 2, 3, 16, 17, 18]:
            scenario = "S1"
        elif query_num in [4, 5, 6, 15, 20, 22]:
            scenario = "S2"
        elif query_num in [7, 8, 9, 19, 35]:
            scenario = "S3"
        elif query_num in [10, 11, 12, 24, 26]:
            scenario = "S4"
        else:
            scenario = "S5"
        
        # 品类映射
        if query_num in [3, 5, 11, 14]:
            category = "C1"
        elif query_num in [4, 6, 15, 20]:
            category = "C2"
        elif query_num in [18, 26, 31, 37]:
            category = "C3"
        elif query_num in [2, 9, 10, 17]:
            category = "C4"
        elif query_num in [1, 16, 19, 30]:
            category = "C5"
        elif query_num in [7, 8, 12, 21]:
            category = "C6"
        elif query_num in [13, 14, 23, 25]:
            category = "C7"
        else:
            category = "C8"
        
        return {
            'persona': self.PERSONA_NAMES.get(persona, persona),
            'scenario': self.SCENARIO_NAMES.get(scenario, scenario),
            'category': self.CATEGORY_NAMES.get(category, category),
            'test_case': test_cases.get(query_id, f"测试用例 {query_id}")
        }
    
    def _get_persona_by_query_id(self, query_id: str) -> str:
        """根据Query ID获取人群"""
        query_num = int(query_id.replace('Q', ''))
        if query_num in [1, 16, 28, 33, 44, 56, 62, 68, 79, 91]:
            return "P1"
        elif query_num in [2, 10, 17, 24, 32, 40, 46, 58, 64, 70]:
            return "P2"
        elif query_num in [6, 15, 20, 26, 31, 37, 43, 49, 55, 61]:
            return "P3"
        elif query_num in [5, 13, 18, 23, 29, 34, 39, 45, 51, 57]:
            return "P4"
        elif query_num in [8, 19, 25, 30, 35, 41, 47, 53, 59, 65]:
            return "P5"
        else:
            return "P6"

    def _generate_improvement_summary(self, results: List[Dict]) -> str:
        """生成改进建议汇总"""
        # 收集所有问题和建议
        all_issues = []
        all_suggestions = []
        dimension_scores = {d: [] for d in ['accuracy', 'timeliness', 'personalization', 'safety', 'diversity', 'novelty']}
        
        for result in results:
            scores = result.get('scores', {})
            for dim, score in scores.items():
                if dim in dimension_scores:
                    dimension_scores[dim].append(score)
            
            all_issues.extend(result.get('issues', []))
            all_suggestions.extend(result.get('suggestions', []))
        
        # 计算各维度平均分
        dim_avg = {}
        for dim, scores in dimension_scores.items():
            if scores:
                dim_avg[dim] = sum(scores) / len(scores)
        
        # 找出薄弱维度
        weak_dimensions = []
        dim_names = {
            'accuracy': '准确性',
            'timeliness': '时效性',
            'personalization': '个性化',
            'safety': '安全性',
            'diversity': '多样性',
            'novelty': '新颖性'
        }
        
        for dim, avg in dim_avg.items():
            if avg < 4.0:
                weak_dimensions.append((dim_names.get(dim, dim), avg))
        
        weak_dimensions.sort(key=lambda x: x[1])
        
        # 统计问题类型
        issue_types = {}
        for issue in all_issues:
            if '安全' in issue or '医药' in issue:
                issue_types['安全问题'] = issue_types.get('安全问题', 0) + 1
            elif '时效' in issue or '时间' in issue:
                issue_types['时效问题'] = issue_types.get('时效问题', 0) + 1
            elif '个性化' in issue or '用户' in issue:
                issue_types['个性化问题'] = issue_types.get('个性化问题', 0) + 1
            else:
                issue_types['其他问题'] = issue_types.get('其他问题', 0) + 1
        
        # 生成HTML
        html_parts = []
        
        # 薄弱维度
        if weak_dimensions:
            html_parts.append('<div style="margin-bottom: 20px;">')
            html_parts.append('<h4 style="margin-bottom: 12px; opacity: 0.9;">📉 待提升维度</h4>')
            html_parts.append('<div style="display: flex; flex-wrap: wrap; gap: 10px;">')
            for dim_name, score in weak_dimensions:
                html_parts.append(f'<span style="background: rgba(255,255,255,0.2); padding: 6px 12px; border-radius: 16px; font-size: 13px;">{dim_name}: {score:.2f}分</span>')
            html_parts.append('</div></div>')
        
        # 问题统计
        if issue_types:
            html_parts.append('<div style="margin-bottom: 20px;">')
            html_parts.append('<h4 style="margin-bottom: 12px; opacity: 0.9;">⚠️ 问题分布</h4>')
            html_parts.append('<div style="display: flex; flex-wrap: wrap; gap: 10px;">')
            for issue_type, count in issue_types.items():
                html_parts.append(f'<span style="background: rgba(255,255,255,0.2); padding: 6px 12px; border-radius: 16px; font-size: 13px;">{issue_type}: {count}次</span>')
            html_parts.append('</div></div>')
        
        # 改进建议
        unique_suggestions = list(set(all_suggestions))[:5]  # 去重，最多5条
        if unique_suggestions:
            html_parts.append('<div>')
            html_parts.append('<h4 style="margin-bottom: 12px; opacity: 0.9;">🎯 重点改进方向</h4>')
            html_parts.append('<ul style="margin: 0; padding-left: 20px; line-height: 1.8;">')
            for suggestion in unique_suggestions:
                html_parts.append(f'<li style="margin-bottom: 6px;">{suggestion}</li>')
            html_parts.append('</ul></div>')
        
        if not html_parts:
            return '<p style="opacity: 0.9;">✅ 整体表现良好，暂无重大改进建议</p>'
        
        return '\n'.join(html_parts)


def main():
    """主函数"""
    report_file = "/Users/linjie/.qoderwork/skills/qwen-digital-human-evaluator/report_exec_20260409_203332_d952f9.json"
    
    print("=" * 80)
    print("详细评测报告HTML生成器")
    print("=" * 80)
    print()
    
    # 生成HTML
    generator = DetailedReportGenerator(report_file)
    html = generator.generate_html()
    
    # 保存文件
    output_file = "/Users/linjie/Documents/workspace/aiTest/skill/evaluation-digital-human-system/详细评测报告.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✓ 详细HTML报告已生成: {output_file}")
    print(f"✓ 文件大小: {len(html)} 字符")
    print()
    print("报告特点:")
    print("  - 展示人设、场景、品类全部分类")
    print("  - 展示完整千问返回内容")
    print("  - 展示多维度评测得分")
    print("  - 可折叠的解析详情")
    print("  - 汇总表格一目了然")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
