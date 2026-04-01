#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Query Generator FastAPI Server
基于 query-gen skill 的高性能 RESTful API

安装依赖:
    pip install fastapi uvicorn pydantic

运行方式:
    python api_fastapi.py
    或
    uvicorn api_fastapi:app --reload --port 5000
"""

import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# 添加 skill 路径
skill_path = Path(__file__).parent / "python"
sys.path.insert(0, str(skill_path))

from query_generator import QueryGenerator, GeneratedQuery

# 初始化生成器
generator = QueryGenerator()

# 尝试导入 FastAPI
try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("FastAPI not installed. Please run: pip install fastapi uvicorn")
    sys.exit(1)

# 创建 FastAPI 应用
app = FastAPI(
    title="Query Generator API",
    description="基于用户人设自动生成搜索 Query 的 API 服务",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ 数据模型 ============

class GenerateRequest(BaseModel):
    """生成 Query 请求模型"""
    persona: str = Field(default="新手焦虑型妈妈", description="用户人设名称")
    scene: str = Field(default="医药健康", description="场景名称")
    count: int = Field(default=1, ge=1, le=100, description="生成数量 (1-100)")

    class Config:
        json_schema_extra = {
            "example": {
                "persona": "新手焦虑型妈妈",
                "scene": "医药健康",
                "count": 5
            }
        }


class MultiPersonaRequest(BaseModel):
    """多人群生成 Query 请求模型"""
    personas: List[str] = Field(..., description="用户人设名称列表")
    scene: str = Field(default="医药健康", description="场景名称")
    count_per_persona: int = Field(default=5, ge=1, le=50, description="每人生成数量")

    class Config:
        json_schema_extra = {
            "example": {
                "personas": ["新手焦虑型妈妈", "价格敏感型妈妈"],
                "scene": "医药健康",
                "count_per_persona": 5
            }
        }


class QueryResponse(BaseModel):
    """Query 响应模型"""
    query: str
    persona: str
    scene: str
    intent: str
    complexity: str
    emotion_level: str
    expected_focus: List[str]
    context: Optional[Dict[str, Any]] = None


class GenerateResponse(BaseModel):
    """生成响应模型"""
    success: bool
    data: List[QueryResponse]
    persona: str
    scene: str
    count: int


# ============ API 端点 ============

@app.get("/", tags=["文档"])
async def root():
    """API 根路径 - 返回基本信息"""
    return {
        "service": "Query Generator API",
        "version": "2.0.0",
        "docs": "/docs",
        "endpoints": {
            "personas": "/personas",
            "scenes": "/scenes",
            "generate": "/generate"
        }
    }


@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "query-gen-api",
        "version": "2.0.0"
    }


@app.get("/personas", response_model=Dict[str, Any], tags=["元数据"])
async def get_personas():
    """获取所有支持的用户人设"""
    personas = generator.get_all_persona_names()
    return {
        "success": True,
        "data": personas,
        "count": len(personas),
        "descriptions": {
            "新手焦虑型妈妈": "0-1岁宝宝，第一胎，谨慎焦虑",
            "效率实用型妈妈": "职场妈妈，时间碎片化，追求效率",
            "品质追求型妈妈": "经济条件好，注重品质和体验",
            "价格敏感型妈妈": "精打细算，关注性价比",
            "社交分享型妈妈": "爱新鲜事物，爱分享，跟风",
            "谨慎保守型老人": "60岁+，数字素养低，害怕被骗",
            "求助依赖型老人": "不熟悉操作，习惯求助",
            "潮流探索型 Z 世代": "18-25岁，追新潮，注重体验"
        }
    }


@app.get("/scenes", response_model=Dict[str, Any], tags=["元数据"])
async def get_scenes():
    """获取所有支持的场景"""
    scenes = generator.get_all_scene_names()
    return {
        "success": True,
        "data": scenes,
        "count": len(scenes)
    }


@app.get("/generate", response_model=GenerateResponse, tags=["生成"])
async def generate_get(
    persona: str = Query(default="新手焦虑型妈妈", description="用户人设名称"),
    scene: str = Query(default="医药健康", description="场景名称"),
    count: int = Query(default=1, ge=1, le=100, description="生成数量")
):
    """生成 Query (GET 方式)"""
    try:
        queries = generator.generate_batch(persona, scene, count)
        return {
            "success": True,
            "data": [q.to_dict() for q in queries],
            "persona": persona,
            "scene": scene,
            "count": len(queries)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate", response_model=GenerateResponse, tags=["生成"])
async def generate_post(request: GenerateRequest):
    """生成 Query (POST 方式)"""
    try:
        queries = generator.generate_batch(
            request.persona, request.scene, request.count
        )
        return {
            "success": True,
            "data": [q.to_dict() for q in queries],
            "persona": request.persona,
            "scene": request.scene,
            "count": len(queries)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate/multi", tags=["生成"])
async def generate_multi(request: MultiPersonaRequest):
    """多人群对比生成 Query"""
    try:
        results = generator.generate_multi_persona(
            request.personas, request.scene, request.count_per_persona
        )
        return {
            "success": True,
            "data": {
                persona: [q.to_dict() for q in queries]
                for persona, queries in results.items()
            },
            "scene": request.scene,
            "count_per_persona": request.count_per_persona
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ 主程序 ============

if __name__ == "__main__":
    import uvicorn
    import argparse

    parser = argparse.ArgumentParser(description="Query Generator FastAPI Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host (default: 0.0.0.0)")
    parser.add_argument("--port", "-p", type=int, default=5000, help="Port (default: 5000)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    args = parser.parse_args()

    print("=" * 60)
    print("Query Generator FastAPI Server")
    print("=" * 60)
    print(f"Server: http://{args.host}:{args.port}")
    print(f"Docs:   http://{args.host}:{args.port}/docs")
    print(f"Redoc:  http://{args.host}:{args.port}/redoc")
    print("=" * 60)
    print("Press Ctrl+C to stop")
    print("=" * 60)

    uvicorn.run(
        "api_fastapi:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )
