#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成增强版HTML评测报告 - 包含完整的综合评测结果、发现问题和改进建议
"""

import json
from datetime import datetime

def generate_enhanced_report(eval_file):
    """生成增强版HTML报告"""

    # 读取评测结果
    with open(eval_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    evaluations = data.get('evaluations', [])

    # 生成HTML
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>数字人评测报告 - 增强版</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', sans-serif;
            background: #f5f7fa;
            color: #333;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            font-size: 32px;
            margin-bottom: 10px;
        }}
        .header .meta {{
            opacity: 0.9;
            font-size: 14px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            text-align: center;
        }}
        .stat-card .number {{
            font-size: 36px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        .stat-card .label {{
            color: #666;
            font-size: 14px;
        }}
        .section {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        }}
        .section h2 {{
            color: #333;
            font-size: 20px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        .eval-card {{
            border: 1px solid #e8e8e8;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            background: #fafafa;
        }}
        .eval-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 1px solid #e8e8e8;
        }}
        .eval-id {{
            font-weight: bold;
            color: #667eea;
            font-size: 16px;
        }}
        .eval-score {{
            font-size: 28px;
            font-weight: bold;
            padding: 5px 15px;
            border-radius: 20px;
            color: white;
        }}
        .score-excellent {{ background: #52c41a; }}
        .score-good {{ background: #73d13d; }}
        .score-average {{ background: #faad14; }}
        .score-poor {{ background: #ff4d4f; }}
        .overall-info {{
            background: #e6f7ff;
            border: 1px solid #91d5ff;
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
        }}
        .overall-info h3 {{
            color: #1890ff;
            margin-bottom: 15px;
            font-size: 16px;
        }}
        .overall-info p {{
            margin-bottom: 10px;
            line-height: 1.8;
        }}
        .scores-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin: 15px 0;
        }}
        .score-item {{
            background: white;
            padding: 10px;
            border-radius: 6px;
            text-align: center;
            border: 1px solid #d9d9d9;
        }}
        .score-item .dim {{
            font-size: 12px;
            color: #666;
            margin-bottom: 5px;
        }}
        .score-item .val {{
            font-size: 20px;
            font-weight: bold;
            color: #333;
        }}
        .issues {{
            background: #fff2f0;
            border: 1px solid #ffccc7;
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
        }}
        .suggestions {{
            background: #f6ffed;
            border: 1px solid #b7eb8f;
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
        }}
        .issues h4 {{
            color: #cf1322;
            margin-bottom: 15px;
            font-size: 16px;
        }}
        .suggestions h4 {{
            color: #389e0d;
            margin-bottom: 15px;
            font-size: 16px;
        }}
        .issues ul, .suggestions ul {{
            margin-left: 20px;
        }}
        .issues li {{
            color: #cf1322;
            margin-bottom: 8px;
            line-height: 1.6;
        }}
        .suggestions li {{
            color: #389e0d;
            margin-bottom: 8px;
            line-height: 1.6;
        }}
        .table-section {{
            margin-top: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            font-size: 14px;
        }}
        th {{
            background: #667eea;
            color: white;
            padding: 12px 10px;
            text-align: left;
            font-weight: 600;
        }}
        td {{
            padding: 12px 10px;
            border-bottom: 1px solid #e8e8e8;
            vertical-align: top;
        }}
        tr:hover {{
            background: #f5f7fa;
        }}
        .text-cell {{
            max-width: 300px;
            line-height: 1.6;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>数字人评测报告 - 增强版</h1>
            <div class="meta">
                执行ID: {data.get('execution_id', 'unknown')} | 保存时间: {data.get('saved_at', 'unknown')}
            </div>
        </div>

        <div class="summary">
            <div class="stat-card">
                <div class="number">{len(evaluations)}</div>
                <div class="label">总评测数</div>
            </div>
            <div class="stat-card">
                <div class="number">{sum(1 for e in evaluations if e.get('overall_score', 0) >= 4.0)}</div>
                <div class="label">通过数 (≥4.0)</div>
            </div>
            <div class="stat-card">
                <div class="number">{round(sum(e.get('overall_score', 0) for e in evaluations) / len(evaluations), 2) if evaluations else 0}</div>
                <div class="label">平均分</div>
            </div>
        </div>
'''

    # 添加每个评测的详细信息
    for i, eval_item in enumerate(evaluations):
        query_id = eval_item.get('query_id', f'unknown_{i}')
        overall_score = eval_item.get('overall_score', 0)
        scores = eval_item.get('scores', {})
        
        # 从 llm_evaluation 获取详细信息
        llm_eval = eval_item.get('llm_evaluation', {})
        parsed = llm_eval.get('parsed_result', {})
        table = parsed.get('evaluation_table', [])
        evaluation_summary = parsed.get('evaluation_summary', '')
        issues = parsed.get('issues', [])
        suggestions = parsed.get('suggestions', [])
        
        # 确定分数等级
        if overall_score >= 4.5:
            score_class = 'score-excellent'
        elif overall_score >= 4.0:
            score_class = 'score-good'
        elif overall_score >= 3.0:
            score_class = 'score-average'
        else:
            score_class = 'score-poor'

        html += f'''
        <div class="section">
            <div class="eval-card">
                <div class="eval-header">
                    <span class="eval-id">评测项 {i+1}: {query_id}</span>
                    <span class="eval-score {score_class}">{overall_score:.2f}</span>
                </div>

                <!-- 综合评测结果 -->
                <div class="overall-info">
                    <h3>📊 综合评测结果</h3>
                    <p><strong>评价摘要：</strong>{evaluation_summary}</p>
                    
                    <div class="scores-grid">
'''
        # 添加各维度分数
        for dim, score in scores.items():
            html += f'''
                        <div class="score-item">
                            <div class="dim">{dim}</div>
                            <div class="val">{score}</div>
                        </div>
'''
        
        html += '''
                    </div>
                </div>
'''

        # 添加发现问题
        if issues:
            html += f'''
                <div class="issues">
                    <h4>⚠️ 发现问题 ({len(issues)}个)</h4>
                    <ul>
'''
            for issue in issues:
                html += f'<li>{issue}</li>'
            html += '''
                    </ul>
                </div>
'''

        # 添加改进建议
        if suggestions:
            html += f'''
                <div class="suggestions">
                    <h4>💡 改进建议 ({len(suggestions)}条)</h4>
                    <ul>
'''
            for suggestion in suggestions:
                html += f'<li>{suggestion}</li>'
            html += '''
                    </ul>
                </div>
'''

        # 添加表格数据
        if table:
            html += '''
                <div class="table-section">
                    <h3>📋 商品级别评测表格</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Query</th>
                                <th>Score</th>
                                <th>核心意图匹配</th>
                                <th>属性一致性</th>
                                <th>时效性与可用性</th>
                                <th>Rating</th>
                            </tr>
                        </thead>
                        <tbody>
'''
            for row in table:
                html += f'''
                            <tr>
                                <td class="text-cell">{row.get('query', '')}</td>
                                <td>{row.get('score', 0)}</td>
                                <td class="text-cell">{row.get('core_intent_match', '')}</td>
                                <td class="text-cell">{row.get('attribute_consistency', '')}</td>
                                <td class="text-cell">{row.get('timeliness_availability', '')}</td>
                                <td>{row.get('rating', '')}</td>
                            </tr>
'''
            html += '''
                        </tbody>
                    </table>
                </div>
'''

        html += '''
            </div>
        </div>
'''

    html += '''
    </div>
</body>
</html>
'''

    # 保存HTML文件
    output_file = eval_file.replace('.json', '_enhanced.html').replace('results/', '')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✓ 增强版HTML报告已生成: {output_file}")
    print(f"✓ 文件大小: {len(html)} 字符")
    return output_file

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        eval_file = sys.argv[1]
    else:
        # 使用最新的完整评测结果
        eval_file = "./results/evaluation_results_exec_20260416_205321_327fac.json"

    output = generate_enhanced_report(eval_file)
    print(f"\n报告文件: {output}")
