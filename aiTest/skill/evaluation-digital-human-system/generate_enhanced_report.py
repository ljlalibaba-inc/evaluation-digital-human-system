#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成增强版HTML评测报告 - 调用详细报告生成器
包含人设/场景/品类分类、千问完整返回、结构化商品表格、8维度评测、折叠面板等
"""

import sys
import os
import glob

# 添加 scripts 目录到 path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from generate_detailed_report import DetailedReportGenerator


def find_latest_report():
    """查找最新的 report_exec_*.json 文件"""
    # 先找 report_exec_*.json（完整报告）
    files = glob.glob('./report_exec_*.json')
    if not files:
        files = glob.glob(os.path.join(os.path.dirname(__file__), 'report_exec_*.json'))
    files.sort(reverse=True)
    if files:
        return files[0]

    # 回退：找 results/evaluation_results_exec_*.json
    files = glob.glob('./results/evaluation_results_exec_*.json')
    files.sort(reverse=True)
    return files[0] if files else None


def generate_enhanced_report(eval_file):
    """生成增强版HTML报告"""
    print(f"读取报告文件: {eval_file}")

    # 使用详细报告生成器
    generator = DetailedReportGenerator(eval_file)
    html = generator.generate_html()

    # 输出文件名
    base_name = os.path.basename(eval_file).replace('.json', '')
    output_file = f"./{base_name}_enhanced.html"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"增强版HTML报告已生成: {output_file}")
    print(f"文件大小: {len(html)} 字符")
    return output_file


if __name__ == "__main__":
    if len(sys.argv) > 1:
        eval_file = sys.argv[1]
    else:
        eval_file = find_latest_report()

    if not eval_file:
        print("错误: 未找到报告文件")
        sys.exit(1)

    output = generate_enhanced_report(eval_file)
    print(f"\n报告文件: {output}")
