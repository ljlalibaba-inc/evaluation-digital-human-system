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
        
        # 涉及的人群（从testcases获取实际的persona）
        testcases = full_results.get('testcases', [])
        tc_map = {tc['query_id']: tc for tc in testcases}
        
        personas = set()
        for result in results:
            query_id = result.get('query_id', '')
            tc = tc_map.get(query_id, {})
            # 从testcase获取persona名称（格式：P1_忙碌的年轻白领）
            persona_full = tc.get('persona', '')
            if persona_full and '_' in persona_full:
                # 提取中文名称部分
                persona_name = persona_full.split('_', 1)[1]
            else:
                # 回退到旧逻辑
                persona_code = self._get_persona_by_query_id(query_id)
                persona_name = self.PERSONA_NAMES.get(persona_code, persona_code)
            personas.add(persona_name)
        
        persona_names = sorted(list(personas))
        
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
            max-height: 600px;
            overflow-y: auto;
            white-space: normal;
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
            <!-- 核心结论 -->
            <div class="section" style="margin-bottom: 32px;">
                <div class="section-title" style="font-size: 18px; margin-bottom: 16px;">📊 核心结论</div>
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
            </div>
            
            <!-- 整体评测结果 -->
            {self._generate_overall_evaluation_table(results)}
            
            <!-- 测评记录 -->
            <div class="section" style="margin-bottom: 24px;">
                <div class="section-title" style="font-size: 18px; margin-bottom: 16px;">📝 测评记录</div>
                
                <!-- 人设筛选 -->
                <div class="category-tabs">
                    <div class="tab active">全部</div>
                    {''.join([f'<div class="tab">{name}</div>' for name in persona_names])}
                </div>
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
            // 更新测试用例数量（第二个stat-value）
            const statValues = document.querySelectorAll('.stat-value');
            if (statValues.length >= 2) {{
                statValues[1].textContent = visibleCards.length;
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
            
            # 获取解析结果（从parsedResponse中获取完整数据）
            parsed_info = {}
            response_text = ""
            if i < len(parsed_results):
                parsed = parsed_results[i]
                if isinstance(parsed, dict):
                    parsed_response = parsed.get('parsedResponse')
                    if parsed_response and isinstance(parsed_response, dict):
                        response_text = parsed_response.get('original_response', '')
                        # structured_items 和其他数据在 parsedResponse.data 中
                        data = parsed_response.get('data', {})
                        if data and isinstance(data, dict):
                            parsed_info = data
            
            # 如果parsed_results中没有，尝试从responses获取
            if not response_text and i < len(responses):
                resp = responses[i]
                if isinstance(resp, dict):
                    response_data = resp.get('response', {})
                    if isinstance(response_data, dict):
                        response_text = response_data.get('content', str(response_data))
                    else:
                        response_text = str(response_data)
            
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
                
                <!-- 1. 测评用例 -->
                <div class="section">
                    <div class="section-title">① 测评用例</div>
                    <div class="section-content test-case">
                        {query_info['test_case']}
                    </div>
                </div>
                
                <!-- 2. 千问返回 -->
                <div class="section">
                    <div class="section-title">② 千问返回</div>
                    <div class="section-content qwen-response">
                        {self._generate_structured_items(parsed_info) if parsed_info.get('structured_items') else (response_text if response_text else "（无响应内容）")}
                    </div>
                </div>
                
                <!-- 3. 解析详情 -->
                <div class="collapsible">
                    <div class="collapsible-header">
                        <span>③ 解析详情（点击展开）</span>
                        <span class="arrow">▶</span>
                    </div>
                    <div class="collapsible-content">
                        <div style="font-size: 13px; color: #666;">
                            {self._generate_recommended_products_display(parsed_info)}
                            <p><strong>时效承诺：</strong>{parsed_info.get('time_commitment', '无')}</p>
                            <p><strong>个性化元素：</strong>{', '.join(parsed_info.get('personalization_elements', [])) if parsed_info.get('personalization_elements') else '无'}</p>
                            <p><strong>安全提示：</strong>{', '.join(parsed_info.get('safety_warnings', [])) if parsed_info.get('safety_warnings') else '无'}</p>
                        </div>
                    </div>
                </div>
                
                <!-- 4. 测评结果 -->
                <div class="section" style="margin-top: 20px;">
                    <div class="section-title">④ 测评结果</div>
                    <div style="font-size: 12px; color: #666; margin-bottom: 8px;">
                        {self._generate_evaluation_mode_badge(result if isinstance(result, dict) else {})}
                    </div>
                    <div class="score-dimensions">
                        {self._generate_dimension_scores(scores)}
                    </div>
                    <!-- 维度评测明细 -->
                    <div style="margin-top: 16px;">
                        {self._generate_dimension_details(scores, issues, parsed_info)}
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
    
    def _generate_structured_items(self, parsed_info: Dict) -> str:
        """生成结构化商品表格展示"""
        items = parsed_info.get('structured_items', [])
        if not items:
            return "（无结构化数据）"
        
        # 按 recommendType 分组
        groups = {}
        for item in items:
            rec_type = item.get('recommendType', '') or '其他'
            if rec_type not in groups:
                groups[rec_type] = []
            groups[rec_type].append(item)
        
        # 推荐类型名称映射
        type_names = {
            'PRODUCT': '📦 商品推荐',
            'NEW_SHOP': '🏪 新店推荐',
            'SHOP': '🏪 店铺推荐',
            'CATEGORY': '📂 品类推荐',
            'BRAND': '🏷️ 品牌推荐',
            '其他': '📋 其他推荐'
        }
        
        # 计算总数据量：店卡按店铺数量算，品卡按商品数量算
        total_count = 0
        for rec_type, type_items in groups.items():
            if rec_type in ('NEW_SHOP', 'SHOP'):
                # 按店铺去重计算
                shop_names = set()
                for item in type_items:
                    shop = item.get('shopName', '')
                    if shop:
                        shop_names.add(shop)
                total_count += len(shop_names)
            else:
                total_count += len(type_items)
        
        html_parts = []
        html_parts.append(f'<div style="font-size: 13px; color: #666; margin-bottom: 12px;">共 <strong style="color: #1890ff;">{total_count}</strong> 条推荐数据</div>')
        
        # 表格样式
        table_style = '''
            <style>
                .item-table {{
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 13px;
                    margin-bottom: 16px;
                    border: 2px solid #999 !important;
                }}
                .item-table th {{
                    background: #fafafa;
                    padding: 10px 12px;
                    border: 2px solid #999 !important;
                    font-weight: 600;
                    color: #333;
                    text-align: left;
                    white-space: nowrap;
                }}
                .item-table td {{
                    padding: 10px 12px;
                    border: 2px solid #999 !important;
                    color: #666;
                }}
                .item-table tbody tr:hover {{
                    background: #f5f5f5;
                }}
                .item-table .price {{
                    color: #f5222d;
                    font-weight: 600;
                }}
                .item-table .shop-group {{
                    background: #f0f5ff;
                    font-weight: 600;
                    color: #1890ff;
                }}
                .item-table .product-row {{
                    background: #ffffff;
                }}
            </style>
        '''
        html_parts.append(table_style)
        
        for rec_type, type_items in groups.items():
            type_name = type_names.get(rec_type, rec_type)
            
            # 计算该类型的数量：店卡按店铺数量算，品卡按商品数量算
            if rec_type in ('NEW_SHOP', 'SHOP'):
                shop_names = set()
                for item in type_items:
                    shop = item.get('shopName', '')
                    if shop:
                        shop_names.add(shop)
                type_count = len(shop_names)
                count_label = f'{type_count}家'
            else:
                type_count = len(type_items)
                count_label = f'{type_count}条'
            
            html_parts.append(f'<div style="font-size: 14px; font-weight: 600; color: #333; margin-bottom: 8px;">{type_name} ({count_label})</div>')
            
            # NEW_SHOP 或 SHOP 类型：按店铺聚合展示
            if rec_type in ('NEW_SHOP', 'SHOP'):
                html_parts.append(self._generate_shop_aggregated_table(type_items))
            # 其他类型（如 PRODUCT 品卡）：直接展示，不聚合
            else:
                html_parts.append(self._generate_flat_table(type_items))
        
        return '\n'.join(html_parts)
    
    def _generate_shop_aggregated_table(self, items: list) -> str:
        """生成按店铺聚合的表格"""
        # 按店铺分组
        shop_groups = {}
        for item in items:
            shop = item.get('shopName', '') or '未知店铺'
            if shop not in shop_groups:
                shop_groups[shop] = {
                    'shop_info': item,
                    'products': []
                }
            shop_groups[shop]['products'].append(item)
        
        html_parts = []
        html_parts.append('<table class="item-table">')
        html_parts.append('<thead><tr>')
        html_parts.append('<th>序号</th>')
        html_parts.append('<th>店铺名称</th>')
        html_parts.append('<th>距离(m)</th>')
        html_parts.append('<th>店铺评分</th>')
        html_parts.append('<th>商品数量</th>')
        html_parts.append('<th>商品名称</th>')
        html_parts.append('<th>价格(元)</th>')
        html_parts.append('<th>相关性评分</th>')
        html_parts.append('</tr></thead>')
        html_parts.append('<tbody>')
        
        shop_index = 1
        for shop_name, shop_data in shop_groups.items():
            products = shop_data['products']
            shop_info = shop_data['shop_info']
            
            # 计算商品名称、价格、相关性评分的HTML（每行一个商品）
            product_names_html = ''
            product_prices_html = ''
            product_scores_html = ''
            
            for p in products:
                name = p.get('itemName', '') or '-'
                price = p.get('price', '')
                score = p.get('llmRelevantLevelScore', '')
                
                if product_names_html:
                    product_names_html += '<br>'
                    product_prices_html += '<br>'
                    product_scores_html += '<br>'
                
                product_names_html += name
                product_prices_html += f'<span class="price">¥{price}</span>' if price else '-'
                product_scores_html += str(score) if score else '-'
            
            html_parts.append('<tr class="shop-group">')
            html_parts.append(f'<td>{shop_index}</td>')
            html_parts.append(f'<td style="font-weight: 600;">{shop_name}</td>')
            
            distance = shop_info.get('distance', '')
            html_parts.append(f'<td>{distance + "m" if distance else "-"}</td>')
            
            rating = shop_info.get('rating', '')
            html_parts.append(f'<td>{rating if rating else "-"}</td>')
            
            html_parts.append(f'<td>{len(products)}</td>')
            
            html_parts.append(f'<td style="max-width: 300px; word-break: break-word;">{product_names_html}</td>')
            html_parts.append(f'<td>{product_prices_html}</td>')
            html_parts.append(f'<td>{product_scores_html}</td>')
            html_parts.append('</tr>')
            shop_index += 1
        
        html_parts.append('</tbody>')
        html_parts.append('</table>')
        return '\n'.join(html_parts)
    
    def _generate_flat_table(self, items: list) -> str:
        """生成普通扁平表格（不聚合）"""
        html_parts = []
        html_parts.append('<table class="item-table">')
        html_parts.append('<thead><tr>')
        html_parts.append('<th>序号</th>')
        html_parts.append('<th>商品名称</th>')
        html_parts.append('<th>价格(元)</th>')
        html_parts.append('<th>品牌</th>')
        html_parts.append('<th>店铺</th>')
        html_parts.append('<th>距离(m)</th>')
        html_parts.append('<th>评分</th>')
        html_parts.append('<th>相关性评分</th>')
        html_parts.append('</tr></thead>')
        html_parts.append('<tbody>')
        
        for i, item in enumerate(items, 1):
            html_parts.append('<tr class="product-row">')
            
            # 序号
            html_parts.append(f'<td>{i}</td>')
            
            # 商品名称
            name = item.get('itemName', '') or '-'
            html_parts.append(f'<td style="max-width: 300px; word-break: break-word;">{name}</td>')
            
            # 价格
            price = item.get('price', '')
            if price:
                html_parts.append(f'<td class="price">¥{price}</td>')
            else:
                html_parts.append('<td>-</td>')
            
            # 品牌
            brand = item.get('brandName', '') or '-'
            html_parts.append(f'<td>{brand}</td>')
            
            # 店铺
            shop = item.get('shopName', '') or '-'
            html_parts.append(f'<td>{shop}</td>')
            
            # 距离
            distance = item.get('distance', '')
            if distance:
                html_parts.append(f'<td>{distance}m</td>')
            else:
                html_parts.append('<td>-</td>')
            
            # 评分
            rating = item.get('rating', '')
            if rating:
                html_parts.append(f'<td>{rating}</td>')
            else:
                html_parts.append('<td>-</td>')
            
            # 相关性评分
            score = item.get('llmRelevantLevelScore', '')
            if score:
                html_parts.append(f'<td>{score}</td>')
            else:
                html_parts.append('<td>-</td>')
            
            html_parts.append('</tr>')
        
        html_parts.append('</tbody>')
        html_parts.append('</table>')
        return '\n'.join(html_parts)
    
    def _generate_recommended_products_display(self, parsed_info: Dict) -> str:
        """生成推荐商品展示（区分店卡和品卡）"""
        structured_items = parsed_info.get('structured_items', [])
        if not structured_items:
            return '<p><strong>推荐商品：</strong>无</p>'
        
        html_parts = []
        
        # 按 recommendType 分组
        shop_items = []  # 店卡（SHOP, NEW_SHOP）
        product_items = []  # 品卡（PRODUCT 等）
        
        for item in structured_items:
            rec_type = item.get('recommendType', '')
            if rec_type in ('SHOP', 'NEW_SHOP'):
                shop_items.append(item)
            else:
                product_items.append(item)
        
        # 店卡：按店铺聚合
        if shop_items:
            shop_groups = {}
            for item in shop_items:
                shop = item.get('shopName', '') or '未知店铺'
                if shop not in shop_groups:
                    shop_groups[shop] = []
                shop_groups[shop].append(item)
            
            html_parts.append('<p><strong>推荐商品（店卡）：</strong></p>')
            html_parts.append('<div style="margin-left: 12px; margin-bottom: 8px;">')
            
            for shop_name, items in shop_groups.items():
                html_parts.append(f'<div style="margin-bottom: 6px;">')
                html_parts.append(f'<div style="font-weight: 600; color: #1890ff;">🏪 {shop_name}</div>')
                html_parts.append('<div style="margin-left: 16px; font-size: 12px; color: #666;">')
                product_names = []
                for p in items[:5]:  # 最多显示5个商品
                    name = p.get('itemName', '')
                    price = p.get('price', '')
                    if name:
                        product_names.append(f'{name}{" (¥" + str(price) + ")" if price else ""}')
                html_parts.append(', '.join(product_names))
                if len(items) > 5:
                    html_parts.append(f' ...等{len(items)}个商品')
                html_parts.append('</div></div>')
            
            html_parts.append('</div>')
        
        # 品卡：直接展示
        if product_items:
            html_parts.append('<p><strong>推荐商品（品卡）：</strong></p>')
            html_parts.append('<div style="margin-left: 12px; margin-bottom: 8px;">')
            product_names = []
            for p in product_items[:5]:  # 最多显示5个
                name = p.get('itemName', '')
                price = p.get('price', '')
                if name:
                    product_names.append(f'{name}{" (¥" + str(price) + ")" if price else ""}')
            html_parts.append(', '.join(product_names))
            if len(product_items) > 5:
                html_parts.append(f' ...等{len(product_items)}个商品')
            html_parts.append('</div>')
        
        return '\n'.join(html_parts) if html_parts else '<p><strong>推荐商品：</strong>无</p>'
    
    def _generate_evaluation_mode_badge(self, result: Dict) -> str:
        """生成评测模式标签"""
        eval_mode = result.get('evaluation_mode', 'rule')
        llm_model = result.get('llm_model', '')
        
        if eval_mode == 'llm' and llm_model:
            return f'<span style="background: #e6f7ff; color: #1890ff; padding: 2px 8px; border-radius: 4px; font-size: 11px;">🤖 大模型评测 ({llm_model})</span>'
        else:
            return f'<span style="background: #f6ffed; color: #52c41a; padding: 2px 8px; border-radius: 4px; font-size: 11px;">📋 规则评测</span>'
    
    def _generate_dimension_scores(self, scores: Dict) -> str:
        """生成维度评分"""
        dimensions = [
            ('accuracy', '准确性'),
            ('timeliness', '时效性'),
            ('personalization', '个性化'),
            ('safety', '安全性'),
            ('diversity', '多样性'),
            ('novelty', '新颖性'),
            ('shop_quality', '店铺质量'),
            ('product_richness', '商品丰富性')
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
    
    def _generate_dimension_details(self, scores: Dict, issues: List, parsed_info: Dict) -> str:
        """生成维度评测明细（表格形式）- 三列：测评维度、指标、值"""
        html_parts = []
        html_parts.append('<div style="font-size: 13px;">')
        html_parts.append('<div style="font-weight: 600; color: #333; margin-bottom: 12px;">📋 评测明细</div>')
        
        # 表格样式
        detail_table_style = '''
            <style>
                .detail-table {
                    width: 100%;
                    border-collapse: collapse !important;
                    font-size: 12px;
                    margin-bottom: 12px;
                    border: 2px solid #999 !important;
                }
                .detail-table th {
                    background: #fafafa;
                    padding: 8px 10px;
                    border: 2px solid #999 !important;
                    font-weight: 600;
                    color: #333;
                    text-align: left;
                }
                .detail-table td {
                    padding: 8px 10px;
                    border: 2px solid #999 !important;
                    color: #666;
                }
                .detail-table tbody tr:hover {
                    background: #e6f7ff !important;
                }
                .detail-table .dimension-cell {
                    font-weight: 600;
                    background: #f0f5ff;
                    vertical-align: top;
                }
                .detail-table .score-cell {
                    color: #1890ff;
                    font-weight: 500;
                }
            </style>
        '''
        html_parts.append(detail_table_style)
        
        structured_items = parsed_info.get('structured_items', [])
        time_commitment = parsed_info.get('time_commitment', '')
        personalization_elements = parsed_info.get('personalization_elements', [])
        safety_warnings = parsed_info.get('safety_warnings', [])
        
        # 开始统一表格
        html_parts.append('<table class="detail-table">')
        html_parts.append('<thead><tr><th style="width: 15%;">测评维度</th><th style="width: 35%;">指标</th><th style="width: 50%;">值</th></tr></thead>')
        html_parts.append('<tbody>')
        
        # 1. 准确性
        accuracy = scores.get('accuracy', 0)
        if structured_items:
            avg_relevance = sum(i.get('llmRelevantLevelScore', 0) for i in structured_items) / len(structured_items)
            unique_items = len(set(i.get('itemName', '') for i in structured_items))
            html_parts.append(f'<tr><td class="dimension-cell" rowspan="3">准确性<br><span class="score-cell">{accuracy:.1f}/5.0</span></td><td>推荐商品数量</td><td>{len(structured_items)}个</td></tr>')
            html_parts.append(f'<tr><td>平均相关性评分</td><td>{avg_relevance:.1f}/5.0</td></tr>')
            html_parts.append(f'<tr><td>不同商品数</td><td>{unique_items}个</td></tr>')
        else:
            html_parts.append(f'<tr><td class="dimension-cell">准确性<br><span class="score-cell">{accuracy:.1f}/5.0</span></td><td>-</td><td>无数据</td></tr>')
        
        # 2. 时效性
        timeliness = scores.get('timeliness', 0)
        if structured_items:
            distances = [float(str(i.get('distance', '0')).replace('m', '')) for i in structured_items if i.get('distance')]
            if distances:
                row_count = 4 if distances else 1
                html_parts.append(f'<tr><td class="dimension-cell" rowspan="{row_count}">时效性<br><span class="score-cell">{timeliness:.1f}/5.0</span></td><td>时效承诺</td><td>{time_commitment or "无"}</td></tr>')
                avg_distance = sum(distances) / len(distances)
                min_distance = min(distances)
                max_distance = max(distances)
                html_parts.append(f'<tr><td>平均距离</td><td>{avg_distance:.0f}m</td></tr>')
                html_parts.append(f'<tr><td>最近距离</td><td>{min_distance:.0f}m</td></tr>')
                html_parts.append(f'<tr><td>最远距离</td><td>{max_distance:.0f}m</td></tr>')
            else:
                html_parts.append(f'<tr><td class="dimension-cell">时效性<br><span class="score-cell">{timeliness:.1f}/5.0</span></td><td>时效承诺</td><td>{time_commitment or "无"}</td></tr>')
        else:
            html_parts.append(f'<tr><td class="dimension-cell">时效性<br><span class="score-cell">{timeliness:.1f}/5.0</span></td><td>时效承诺</td><td>{time_commitment or "无"}</td></tr>')
        
        # 3. 个性化
        personalization = scores.get('personalization', 0)
        if structured_items:
            shop_count = len(set(i.get('shopName', '') for i in structured_items))
            html_parts.append(f'<tr><td class="dimension-cell" rowspan="2">个性化<br><span class="score-cell">{personalization:.1f}/5.0</span></td><td>个性化元素</td><td>{", ".join(personalization_elements) if personalization_elements else "无"}</td></tr>')
            html_parts.append(f'<tr><td>涉及店铺数</td><td>{shop_count}家</td></tr>')
        else:
            html_parts.append(f'<tr><td class="dimension-cell">个性化<br><span class="score-cell">{personalization:.1f}/5.0</span></td><td>个性化元素</td><td>{", ".join(personalization_elements) if personalization_elements else "无"}</td></tr>')
        
        # 4. 安全性
        safety = scores.get('safety', 0)
        issue_count = len(issues)
        row_count = 2 if issues else 1
        html_parts.append(f'<tr><td class="dimension-cell" rowspan="{row_count}">安全性<br><span class="score-cell">{safety:.1f}/5.0</span></td><td>安全提示</td><td>{", ".join(safety_warnings) if safety_warnings else "无"}</td></tr>')
        if issues:
            html_parts.append(f'<tr><td><span style="color: #f5222d;">发现问题</span></td><td><span style="color: #f5222d;">{"; ".join(issues)}</span></td></tr>')
        
        # 5. 多样性
        diversity = scores.get('diversity', 0)
        if structured_items:
            unique_shops = len(set(i.get('shopName', '') for i in structured_items))
            unique_brands = len(set(i.get('brandName', '') for i in structured_items if i.get('brandName')))
            unique_items_count = len(set(i.get('itemName', '') for i in structured_items))
            rec_types = {}
            for i in structured_items:
                rt = i.get('recommendType', '') or '其他'
                rec_types[rt] = rec_types.get(rt, 0) + 1
            type_str = ', '.join(f'{k}: {v}个' for k, v in rec_types.items())
            
            html_parts.append(f'<tr><td class="dimension-cell" rowspan="5">多样性<br><span class="score-cell">{diversity:.1f}/5.0</span></td><td>商品总数</td><td>{len(structured_items)}个</td></tr>')
            html_parts.append(f'<tr><td>不同商品数</td><td>{unique_items_count}个</td></tr>')
            html_parts.append(f'<tr><td>店铺数量</td><td>{unique_shops}家</td></tr>')
            html_parts.append(f'<tr><td>品牌数量</td><td>{unique_brands}个</td></tr>')
            html_parts.append(f'<tr><td>推荐类型分布</td><td>{type_str}</td></tr>')
        else:
            html_parts.append(f'<tr><td class="dimension-cell">多样性<br><span class="score-cell">{diversity:.1f}/5.0</span></td><td>-</td><td>无数据</td></tr>')
        
        # 6. 新颖性
        novelty = scores.get('novelty', 0)
        html_parts.append(f'<tr><td class="dimension-cell">新颖性<br><span class="score-cell">{novelty:.1f}/5.0</span></td><td>新颖性评分</td><td>{novelty:.1f}/5.0</td></tr>')
        
        # 7. 店铺质量
        shop_quality = scores.get('shop_quality', 0)
        if structured_items:
            shop_groups = {}
            for item in structured_items:
                shop = item.get('shopName', '')
                if shop:
                    if shop not in shop_groups:
                        shop_groups[shop] = {'distance': 0, 'rating': 0, 'items': []}
                    shop_groups[shop]['items'].append(item)
                    if item.get('distance'):
                        try:
                            shop_groups[shop]['distance'] = float(str(item.get('distance', '0')).replace('m', ''))
                        except:
                            pass
                    if item.get('rating'):
                        try:
                            shop_groups[shop]['rating'] = float(item.get('rating', 0))
                        except:
                            pass
            
            row_count = len(shop_groups) if shop_groups else 1
            html_parts.append(f'<tr><td class="dimension-cell" rowspan="{row_count}">店铺质量<br><span class="score-cell">{shop_quality:.1f}/5.0</span></td>')
            if shop_groups:
                first = True
                for shop_name, shop_data in shop_groups.items():
                    if not first:
                        html_parts.append('<tr>')
                    distance_str = f'{shop_data["distance"]:.0f}m' if shop_data["distance"] else '-'
                    rating_str = f'{shop_data["rating"]:.1f}' if shop_data["rating"] else '-'
                    html_parts.append(f'<td>{shop_name}</td><td>距离: {distance_str}, 评分: {rating_str}, 商品数: {len(shop_data["items"])}个</td></tr>')
                    first = False
            else:
                html_parts.append('<td>-</td><td>无店铺数据</td></tr>')
        else:
            html_parts.append(f'<tr><td class="dimension-cell">店铺质量<br><span class="score-cell">{shop_quality:.1f}/5.0</span></td><td>-</td><td>无数据</td></tr>')
        
        # 8. 商品丰富性
        product_richness = scores.get('product_richness', 0)
        if structured_items:
            unique_items = len(set(i.get('itemName', '') for i in structured_items))
            unique_brands = len(set(i.get('brandName', '') for i in structured_items if i.get('brandName')))
            unique_shops = len(set(i.get('shopName', '') for i in structured_items))
            avg_relevance = sum(i.get('llmRelevantLevelScore', 0) for i in structured_items) / len(structured_items)
            
            html_parts.append(f'<tr><td class="dimension-cell" rowspan="5">商品丰富性<br><span class="score-cell">{product_richness:.1f}/5.0</span></td><td>商品总数</td><td>{len(structured_items)}个</td></tr>')
            html_parts.append(f'<tr><td>不同商品数</td><td>{unique_items}个</td></tr>')
            html_parts.append(f'<tr><td>品牌数</td><td>{unique_brands}个</td></tr>')
            html_parts.append(f'<tr><td>店铺数</td><td>{unique_shops}家</td></tr>')
            html_parts.append(f'<tr><td>平均相关性</td><td>{avg_relevance:.1f}/5.0</td></tr>')
        else:
            html_parts.append(f'<tr><td class="dimension-cell">商品丰富性<br><span class="score-cell">{product_richness:.1f}/5.0</span></td><td>-</td><td>无数据</td></tr>')
        
        html_parts.append('</tbody></table>')
        html_parts.append('</div>')
        return '\n'.join(html_parts)
    
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

    def _generate_overall_evaluation_table(self, results: List[Dict]) -> str:
        """生成整体评测结果表"""
        # 计算各维度平均分
        dimension_scores = {d: [] for d in ['accuracy', 'timeliness', 'personalization', 'safety', 'diversity', 'novelty', 'shop_quality', 'product_richness']}
        all_issues = []
        
        for result in results:
            scores = result.get('scores', {})
            for dim, score in scores.items():
                if dim in dimension_scores:
                    dimension_scores[dim].append(score)
            all_issues.extend(result.get('issues', []))
        
        # 计算平均分
        dim_avg = {}
        for dim, scores in dimension_scores.items():
            if scores:
                dim_avg[dim] = sum(scores) / len(scores)
        
        # 维度名称映射
        dim_names = {
            'accuracy': '需求匹配度',
            'timeliness': '时效可信度',
            'personalization': '个性化程度',
            'safety': '安全引导',
            'diversity': '商品多样性',
            'novelty': '推荐新颖性',
            'shop_quality': '店铺质量',
            'product_richness': '商品丰富性'
        }
        
        # 生成评语
        def get_comment(dim, score):
            comments = {
                'accuracy': {
                    (0, 2): '严重混淆药品与辅材，需求理解偏差大',
                    (2, 3): '部分匹配需求，但存在偏差',
                    (3, 4): '基本满足需求，少数不匹配',
                    (4, 5): '精准匹配用户需求'
                },
                'timeliness': {
                    (0, 2): '时效承诺缺失或不可信',
                    (2, 3): '距离近但缺乏实时预测',
                    (3, 4): '时效信息较完整',
                    (4, 5): '时效预测准确可信'
                },
                'personalization': {
                    (0, 2): '缺乏个性化元素',
                    (2, 3): '个性化程度有限',
                    (3, 4): '有一定个性化考量',
                    (4, 5): '高度个性化推荐'
                },
                'safety': {
                    (0, 2): '无用药警示，存在误导风险',
                    (2, 3): '安全提示不足',
                    (3, 4): '基本安全提示到位',
                    (4, 5): '完善的安全引导'
                },
                'diversity': {
                    (0, 2): '商品类型单一',
                    (2, 3): '多样性有限',
                    (3, 4): '品类较丰富',
                    (4, 5): '高度多样化推荐'
                },
                'novelty': {
                    (0, 2): '缺乏新意',
                    (2, 3): '新颖性一般',
                    (3, 4): '有一定创新',
                    (4, 5): '推荐新颖独特'
                },
                'shop_quality': {
                    (0, 2): '店铺质量差',
                    (2, 3): '店铺质量一般',
                    (3, 4): '店铺质量良好',
                    (4, 5): '优质店铺推荐'
                },
                'product_richness': {
                    (0, 2): '商品丰富度不足',
                    (2, 3): '商品选择有限',
                    (3, 4): '商品较丰富',
                    (4, 5): '商品高度丰富'
                }
            }
            
            dim_comments = comments.get(dim, {})
            for (low, high), comment in dim_comments.items():
                if low <= score < high:
                    return comment
            return '表现一般'
        
        # 生成星星评分
        def get_stars(score):
            full_stars = int(score)
            half_star = 1 if score - full_stars >= 0.5 else 0
            empty_stars = 5 - full_stars - half_star
            stars = '⭐' * full_stars
            if half_star:
                stars += '✨'
            stars += '☆' * empty_stars
            return f'{stars}（{score:.1f}/5）'
        
        # 构建表格HTML
        html_parts = []
        html_parts.append('<div class="section" style="margin-bottom: 32px;">')
        html_parts.append('<div class="section-title" style="font-size: 18px; margin-bottom: 16px;">📋 整体评测结果</div>')
        html_parts.append('<table class="detail-table" style="font-size: 14px;">')
        html_parts.append('<thead><tr><th style="width: 20%;">维度</th><th style="width: 30%;">得分</th><th style="width: 50%;">评语</th></tr></thead>')
        html_parts.append('<tbody>')
        
        # 按优先级显示维度
        priority_dims = ['accuracy', 'safety', 'timeliness', 'personalization', 'diversity', 'novelty']
        for dim in priority_dims:
            if dim in dim_avg:
                score = dim_avg[dim]
                name = dim_names.get(dim, dim)
                stars = get_stars(score)
                comment = get_comment(dim, score)
                html_parts.append(f'<tr><td><strong>{name}</strong></td><td>{stars}</td><td>{comment}</td></tr>')
        
        html_parts.append('</tbody></table>')
        html_parts.append('</div>')
        
        return '\n'.join(html_parts)

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
    import sys
    import os
    
    # 支持命令行参数指定报告文件
    if len(sys.argv) > 1:
        report_file = sys.argv[1]
    else:
        # 默认使用最新的报告文件
        report_file = "/Users/linjie/Documents/workspace/aiTest/skill/evaluation-digital-human-system/report_exec_20260416_100206_2ea604.json"
    
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
