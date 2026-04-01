#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Query Generator HTTP API Server
基于 query-gen skill 的 RESTful API 封装
"""

import sys
import json
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote

# 添加 skill 路径
skill_path = Path(__file__).parent / "python"
sys.path.insert(0, str(skill_path))

from query_generator import QueryGenerator

# 初始化生成器
generator = QueryGenerator()


class QueryGenHandler(BaseHTTPRequestHandler):
    """HTTP 请求处理器"""

    def _set_headers(self, status_code=200, content_type="application/json"):
        """设置响应头"""
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _send_json(self, data, status_code=200):
        """发送 JSON 响应"""
        self._set_headers(status_code)
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _send_error(self, message, status_code=400):
        """发送错误响应"""
        self._send_json({"error": message, "success": False}, status_code)

    def do_OPTIONS(self):
        """处理 CORS 预检请求"""
        self._set_headers()

    def do_GET(self):
        """处理 GET 请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)

        # 获取所有人设
        if path == "/personas":
            personas = generator.get_all_persona_names()
            self._send_json({
                "success": True,
                "data": personas,
                "count": len(personas)
            })
            return

        # 获取所有场景
        if path == "/scenes":
            scenes = generator.get_all_scene_names()
            self._send_json({
                "success": True,
                "data": scenes,
                "count": len(scenes)
            })
            return

        # 生成 query (GET 方式)
        if path == "/generate":
            persona = unquote(query_params.get("persona", ["新手焦虑型妈妈"])[0])
            scene = unquote(query_params.get("scene", ["医药健康"])[0])
            count = int(query_params.get("count", ["1"])[0])

            try:
                queries = generator.generate_batch(persona, scene, count)
                self._send_json({
                    "success": True,
                    "data": [q.to_dict() for q in queries],
                    "persona": persona,
                    "scene": scene,
                    "count": len(queries)
                })
            except Exception as e:
                self._send_error(str(e), 500)
            return

        # 健康检查
        if path == "/health":
            self._send_json({
                "success": True,
                "status": "healthy",
                "service": "query-gen-api"
            })
            return

        # 首页/文档
        if path == "/" or path == "/docs":
            docs = {
                "service": "Query Generator API",
                "version": "2.0",
                "endpoints": {
                    "GET /personas": "获取所有人设列表",
                    "GET /scenes": "获取所有场景列表",
                    "GET /generate": "生成 query (参数: persona, scene, count)",
                    "POST /generate": "生成 query (JSON body)",
                    "GET /health": "健康检查",
                    "GET /docs": "API 文档"
                },
                "examples": {
                    "generate_single": "/generate?persona=新手焦虑型妈妈&scene=医药健康",
                    "generate_batch": "/generate?persona=新手焦虑型妈妈&scene=医药健康&count=10"
                }
            }
            self._send_json(docs)
            return

        self._send_error("Not Found", 404)

    def do_POST(self):
        """处理 POST 请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        # 读取请求体
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 0:
            body = self.rfile.read(content_length).decode("utf-8")
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                self._send_error("Invalid JSON", 400)
                return
        else:
            data = {}

        # 生成 query
        if path == "/generate":
            persona = data.get("persona", "新手焦虑型妈妈")
            scene = data.get("scene", "医药健康")
            count = data.get("count", 1)
            multi_personas = data.get("personas")  # 多人群模式

            try:
                if multi_personas:
                    # 多人群对比模式
                    results = generator.generate_multi_persona(
                        multi_personas, scene, count
                    )
                    self._send_json({
                        "success": True,
                        "data": {
                            persona: [q.to_dict() for q in queries]
                            for persona, queries in results.items()
                        },
                        "scene": scene,
                        "count_per_persona": count
                    })
                else:
                    # 单人设模式
                    queries = generator.generate_batch(persona, scene, count)
                    self._send_json({
                        "success": True,
                        "data": [q.to_dict() for q in queries],
                        "persona": persona,
                        "scene": scene,
                        "count": len(queries)
                    })
            except Exception as e:
                self._send_error(str(e), 500)
            return

        self._send_error("Not Found", 404)

    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"[{self.log_date_time_string()}] {args[0]}")


def run_server(port=5000):
    """启动服务器"""
    server_address = ("", port)
    httpd = HTTPServer(server_address, QueryGenHandler)
    print(f"=" * 60)
    print(f"Query Generator API Server")
    print(f"=" * 60)
    print(f"Server running at http://localhost:{port}")
    print(f"")
    print(f"API Endpoints:")
    print(f"  GET  http://localhost:{port}/personas")
    print(f"  GET  http://localhost:{port}/scenes")
    print(f"  GET  http://localhost:{port}/generate?persona=...&scene=...&count=...")
    print(f"  POST http://localhost:{port}/generate")
    print(f"  GET  http://localhost:{port}/health")
    print(f"  GET  http://localhost:{port}/docs")
    print(f"=" * 60)
    print(f"Press Ctrl+C to stop")
    print(f"=" * 60)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        httpd.shutdown()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Query Generator API Server")
    parser.add_argument("--port", "-p", type=int, default=5000,
                        help="Server port (default: 5000)")
    args = parser.parse_args()

    run_server(args.port)
