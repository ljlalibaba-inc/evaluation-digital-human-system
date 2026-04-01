#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Query Generator CLI - 支持命令行参数调用的 Skill 示例
"""

import argparse
import json
import sys
from pathlib import Path

# 将项目路径添加到 sys.path
sys.path.insert(0, str(Path(__file__).parent))

from query_generator import QueryGenerator


def main():
    parser = argparse.ArgumentParser(
        description="基于数字人设自动生成搜索 Query",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 生成单个 Query
  python query_gen_cli.py --persona "新手焦虑型妈妈" --scene "医疗健康"

  # 批量生成 10 条
  python query_gen_cli.py --persona "新手焦虑型妈妈" --scene "医疗健康" --count 10

  # 多人群对比
  python query_gen_cli.py --multi --personas "新手焦虑型妈妈,谨慎保守型老人" --scene "医疗健康" --count 5

  # 列出所有人设和场景
  python query_gen_cli.py --list

  # 输出 JSON 格式
  python query_gen_cli.py --persona "新手焦虑型妈妈" --scene "医疗健康" --count 5 --format json
        """
    )

    # 主要参数
    parser.add_argument("--persona", "-p", type=str, help="人设名称")
    parser.add_argument("--scene", "-s", type=str, help="场景名称")
    parser.add_argument("--count", "-c", type=int, default=1, help="生成数量 (默认: 1)")
    parser.add_argument("--urgency", "-u", type=str, help="紧急程度 (可选)")

    # 多人群对比模式
    parser.add_argument("--multi", "-m", action="store_true", help="多人群对比模式")
    parser.add_argument("--personas", type=str, help="多个人设，用逗号分隔")

    # 输出格式
    parser.add_argument("--format", "-f", choices=["text", "json", "csv"], default="text",
                        help="输出格式 (默认: text)")
    parser.add_argument("--output", "-o", type=str, help="输出文件路径 (可选)")

    # 信息查询
    parser.add_argument("--list", "-l", action="store_true", help="列出所有人设和场景")
    parser.add_argument("--list-personas", action="store_true", help="列出所有人设")
    parser.add_argument("--list-scenes", action="store_true", help="列出所有场景")

    args = parser.parse_args()

    # 初始化生成器
    generator = QueryGenerator()

    # 处理信息查询
    if args.list or args.list_personas:
        print("=" * 60)
        print("支持的人设:")
        print("=" * 60)
        for persona in generator.get_all_persona_names():
            print(f"  - {persona}")
        print()

    if args.list or args.list_scenes:
        print("=" * 60)
        print("支持的场景:")
        print("=" * 60)
        for scene in generator.get_all_scene_names():
            print(f"  - {scene}")
        print()

    if args.list or args.list_personas or args.list_scenes:
        return

    # 验证参数
    if not args.multi and (not args.persona or not args.scene):
        parser.error("非多人群模式下，--persona 和 --scene 是必需的")

    if args.multi and (not args.personas or not args.scene):
        parser.error("多人群模式下，--personas 和 --scene 是必需的")

    # 生成 Query
    if args.multi:
        # 多人群对比模式
        persona_list = [p.strip() for p in args.personas.split(",")]
        results = generator.generate_multi_persona(
            persona_list, args.scene, args.count
        )
        output = format_multi_output(results, args.format)
    else:
        # 单人群批量生成
        queries = generator.generate_batch(args.persona, args.scene, args.count)
        output = format_batch_output(queries, args.format)

    # 输出结果
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"结果已保存到: {args.output}")
    else:
        print(output)


def format_batch_output(queries, format_type):
    """格式化批量输出"""
    if format_type == "json":
        data = [q.to_dict() for q in queries]
        return json.dumps(data, ensure_ascii=False, indent=2)

    elif format_type == "csv":
        lines = ["query,persona,scene,intent,complexity,emotion_level,expected_focus"]
        for q in queries:
            focus = "|".join(q.expected_focus)
            lines.append(f'"{q.query}",{q.persona},{q.scene},{q.intent},{q.complexity},{q.emotion_level},"{focus}"')
        return "\n".join(lines)

    else:  # text
        lines = ["=" * 60]
        lines.append(f"生成结果: {queries[0].persona} - {queries[0].scene}")
        lines.append("=" * 60)

        for i, q in enumerate(queries, 1):
            lines.append(f"\n【{i}】")
            lines.append(f"  Query: {q.query}")
            lines.append(f"  意图: {q.intent}")
            lines.append(f"  复杂度: {q.complexity}")
            lines.append(f"  情感强度: {q.emotion_level}")
            lines.append(f"  评测重点: {', '.join(q.expected_focus)}")

        lines.append("\n" + "=" * 60)
        return "\n".join(lines)


def format_multi_output(results, format_type):
    """格式化多人群输出"""
    if format_type == "json":
        data = {
            persona: [q.to_dict() for q in queries]
            for persona, queries in results.items()
        }
        return json.dumps(data, ensure_ascii=False, indent=2)

    elif format_type == "csv":
        lines = ["query,persona,scene,intent,complexity,emotion_level,expected_focus"]
        for persona, queries in results.items():
            for q in queries:
                focus = "|".join(q.expected_focus)
                lines.append(f'"{q.query}",{q.persona},{q.scene},{q.intent},{q.complexity},{q.emotion_level},"{focus}"')
        return "\n".join(lines)

    else:  # text
        lines = ["=" * 60]
        lines.append("多人群对比结果")
        lines.append("=" * 60)

        for persona, queries in results.items():
            lines.append(f"\n【{persona}】")
            for i, q in enumerate(queries, 1):
                lines.append(f"  {i}. {q.query}")

        lines.append("\n" + "=" * 60)
        return "\n".join(lines)


if __name__ == "__main__":
    main()
