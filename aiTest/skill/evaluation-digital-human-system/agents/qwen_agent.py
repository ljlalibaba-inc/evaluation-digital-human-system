#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
千问调用 Agent
支持两种模式:
1. DashScope API (推荐，稳定，需要API Key)
2. qwen-chat-client HTTP API (复用内部接口，需要认证，支持流式调用)
"""

import json
import os
import time
import uuid
import urllib.parse
from datetime import datetime
from typing import Dict, Optional, Any, List, Callable
import requests
from .base_agent import BaseAgent


class QwenAgent(BaseAgent):
    """
    千问大模型调用Agent
    支持DashScope API和qwen-chat-client两种调用方式
    支持流式调用和自动获取认证参数
    """



    def __init__(self, config: Dict = None):
        super().__init__("QwenAgent", config or {})

        # 检测使用哪种API
        self.api_mode = self.config.get('api_mode', "qwen_chat")
        
        if self.api_mode == "dashscope":
            # DashScope API配置
            self.api_key = self.config.get('api_key') or os.getenv("DASHSCOPE_API_KEY")
            self.base_url = "https://dashscope.aliyuncs.com/api/v1"
            self.model = self.config.get('model', "qwen-turbo")
        else:
            # qwen-chat-client HTTP API配置
            self.use_production = self.config.get('use_production', True)
            self.base_url = "https://chat2.qianwen.com" if self.use_production else "https://pre-chat2-ea.qianwen.com"
            self.model = self.config.get('model', "quark-235b")
            
            # 认证参数 - 优先从环境变量读取，其次从配置读取，最后使用默认值
            self.x_sign = self.config.get('x_sign') or os.getenv('QWEN_X_SIGN', 'iz0pIe007xAAhdhFW3Y7oQLitN2Z5dhF3bdww0DmIdi53khXzKFrhumMuWwBQEFIMOXjXqMfFYw7NxwxiHScAgpyDufoQJYV6GXYRd')
            self.wpk_reqid = self.config.get('wpk_reqid') or os.getenv('QWEN_WPK_REQID', 'f8b4f1e218b441838175b5510b027531')
            
            # 其他必要的认证参数（从curl提取）
            self.app_key = self.config.get('app_key', '34400722')
            self.app_ver = self.config.get('app_ver', '5.1.20')
            self.bx_version = self.config.get('bx_version', '6.7.250903')
            self.pv = self.config.get('pv', '6.3')
            self.device_id = self.config.get('device_id', 'aR89N69/QVoDACshFdu81cwp')
            self.wpk_bid = self.config.get('wpk_bid', 'a3ucabr5-b1ayd2v5')
            self.umt = self.config.get('umt', 'GbkBIU5LPDMclhKdkFmQ3ooDsbe1rNye')
            self.mini_wua = self.config.get('mini_wua', 'iJwSsM5z3%2Fcjk%2F0ZcSAriWpK5HuNIonUh7GloLEnqa9%2F0qkK3cbSUa4Ff3G49%2FcSQ7qQuDatYTEDK5Fok3wiF8rvGxqi66yei8dz8ZmPCNsgHjNc1BIYOl4aeVX3C6MOkYllBTTfpn6U2K9SKzoYpUExnETOAN5gFi9h%2FTIbWG5yb%2BY2%2FAe6HYOo8')
            self.sgext = self.config.get('sgext', 'JBPsc06U%2B5ANtjcaQDLrNnPZQ91Q2UraUN5Fz1DdRNtF3kfUS9pDz0PcQdpD3EPcQ9xD3EPcQ9xQ3FDcUNxDz0PcQ9xQ3FDdUN1Q3VDdUN1Q3VDcUNxD3EPcUN4XjVDfUNRQ31CWHbsqz1PMQo1TzFPcUNUs3V7dXrMSs17dVdxV3EOzEbNK3F7dXtxe3F7cXt5e3lXdVdxV3FXdXtxe3UTbQ9lA3UffRMFCskLbRNxG30LYQNst3FXcVdwsiCy5JaIhukKiK7kfpU6zFbNAwUPBQ8FDwUHeLN1AszKLMq0yrTKtMq0yrTKtMq0yrTKtMq0yrTKtMq0s3UWzQ7NCjyzVQ8pDykPKQdwS3VXeStgSykKIStpVwULKXtlDykvfVdxV3UKzQoks3F7cLN5As0rcVcFCwkPcQ9xV3FXcVdxV3kHKQ8pDykPKQ8pB3izeR7NCwUPBQsFDwUPBQ8FDwUPBQ8FDs0HULK1B3Be8JalOsw%3D%3D')
            
            # 登录配置 - 用于自动获取认证参数
            self.login_config = self.config.get('login_config', {})
            self.auto_refresh_auth = self.config.get('auto_refresh_auth', False)
        
        self.timeout = self.config.get('timeout', 60)
        self.stream = self.config.get('stream', False)  # 是否使用流式调用

    def _ensure_auth_params(self) -> bool:
        """
        确保认证参数可用
        
        Returns:
            bool: 认证参数是否可用
        """
        if self.api_mode == "dashscope":
            return True
            
        # 使用写死的默认认证参数（从curl提取的最新值）
        if not self.x_sign:
            self.x_sign = 'iz0pIe007xAALA79Sn0WiQ8LY1n%2BTA78DW%2FfCpZf92Fhbk7hJ5i9NPDx%2F9W7t8zphxqBwMuvpct9tsqQXs1KqK%2B4qFwO7A78DuwO%2FA'
        if not self.wpk_reqid:
            self.wpk_reqid = '8791d3864f7f4f80bb43790352518b86'
            
        return bool(self.x_sign and self.wpk_reqid)
    
    def _fetch_auth_params(self) -> None:
        """
        通过登录接口获取认证参数 (x-sign 和 wpk_reqid)
        
        需要配置 login_config:
        {
            "login_url": "https://xxx.com/login",
            "login_type": "password|token|cookie",
            "credentials": {
                "username": "xxx",
                "password": "xxx"
                // 或
                "token": "xxx"
                // 或
                "cookies": "xxx"
            },
            "x_sign_path": "data.x_sign",  # 响应中x-sign的字段路径
            "wpk_reqid_path": "data.wpk_reqid"  # 响应中wpk_reqid的字段路径
        }
        """
        if not self.login_config:
            raise ValueError("未配置login_config，无法自动获取认证参数")
            
        login_url = self.login_config.get('login_url')
        login_type = self.login_config.get('login_type', 'password')
        credentials = self.login_config.get('credentials', {})
        
        if not login_url:
            raise ValueError("login_config中未配置login_url")
            
        # 构建登录请求
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        
        if login_type == 'password':
            payload = {
                "username": credentials.get('username'),
                "password": credentials.get('password')
            }
        elif login_type == 'token':
            headers["Authorization"] = f"Bearer {credentials.get('token')}"
            payload = {}
        elif login_type == 'cookie':
            headers["Cookie"] = credentials.get('cookies')
            payload = {}
        else:
            raise ValueError(f"不支持的登录类型: {login_type}")
            
        # 发送登录请求
        response = requests.post(
            login_url,
            headers=headers,
            json=payload if payload else None,
            timeout=self.timeout
        )
        response.raise_for_status()
        
        result = response.json()
        
        # 从响应中提取认证参数
        x_sign_path = self.login_config.get('x_sign_path', 'data.x_sign')
        wpk_reqid_path = self.login_config.get('wpk_reqid_path', 'data.wpk_reqid')
        
        self.x_sign = self._extract_nested_value(result, x_sign_path)
        self.wpk_reqid = self._extract_nested_value(result, wpk_reqid_path)
        
        if not self.x_sign or not self.wpk_reqid:
            raise ValueError(f"无法从登录响应中提取认证参数: x_sign={self.x_sign}, wpk_reqid={self.wpk_reqid}")
            
        self.log(f"成功获取认证参数: x_sign={self.x_sign[:20]}..., wpk_reqid={self.wpk_reqid}")
        
        # 更新配置
        self.config['x_sign'] = self.x_sign
        self.config['wpk_reqid'] = self.wpk_reqid
    
    def _extract_nested_value(self, data: Dict, path: str) -> Optional[str]:
        """从嵌套字典中提取值"""
        keys = path.split('.')
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current

    def call(
        self,
        query_text: str,
        system_prompt: Optional[str] = None,
        stream_callback: Optional[Callable[[str], None]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        调用千问API（支持流式）

        Args:
            query_text: 用户Query
            system_prompt: 系统提示词（可选）
            stream_callback: 流式回调函数，接收每个chunk的内容（可选）


        Returns:
            API响应结果（包含完整请求信息）
        """
        start_time = time.time()
        
        # 确保认证参数可用
        if not self._ensure_auth_params():
            return {
                "success": False,
                "error": "认证参数不可用，请配置x_sign和wpk_reqid，或启用auto_refresh_auth并提供login_config",
                "response_time_ms": 0,
                "content": "",
                "request_info": None
            }



        # 构建请求信息（用于保存完整请求）
        request_info = {
            "api_mode": self.api_mode,
            "base_url": self.base_url,
            "model": self.model,
            "query_text": query_text,
            "system_prompt": system_prompt,

            "timestamp": datetime.now().isoformat()
        }

        try:
            if self.api_mode == "dashscope":
                # 使用DashScope API
                request_info["url"] = f"{self.base_url}/services/aigc/text-generation/generation"
                request_info["headers"] = {
                    "Authorization": f"Bearer {self.api_key[:20]}..." if self.api_key else None,
                    "Content-Type": "application/json"
                }
                
                if self.stream or stream_callback:
                    result = self._call_dashscope_stream(query_text, system_prompt, stream_callback, **kwargs)
                else:
                    result = self._call_dashscope(query_text, system_prompt, **kwargs)
                    request_info["request_body"] = result.get("_request_body")
                    # 移除内部使用的字段
                    if "_request_body" in result:
                        del result["_request_body"]
            else:
                # 使用qwen-chat-client HTTP API
                request_data = self._build_request(query_text, system_prompt, **kwargs)

                # 获取实际使用的完整URL和headers
                actual_url, actual_headers = self._get_request_url_and_headers(request_data)

                # 记录完整请求信息
                request_info["url"] = actual_url
                request_info["headers"] = actual_headers
                request_info["request_body"] = request_data

                if self.stream or stream_callback:
                    result = self._execute_request_stream(request_data, stream_callback)
                else:
                    response = self._execute_request(request_data)
                    # 从流式响应中提取文本内容
                    content = self._extract_content_from_sse(response)
                    result = {
                        "success": True,
                        "content": content,
                        "raw_response": response
                    }

            response_time = int((time.time() - start_time) * 1000)
            result["response_time_ms"] = response_time
            result["request_info"] = request_info
            return result

        except requests.exceptions.RequestException as e:
            response_time = int((time.time() - start_time) * 1000)
            return {
                "success": False,
                "error": f"请求失败: {str(e)}",
                "response_time_ms": response_time,
                "content": "",
                "request_info": request_info
            }
        except Exception as e:
            response_time = int((time.time() - start_time) * 1000)
            return {
                "success": False,
                "error": str(e),
                "response_time_ms": response_time,
                "content": "",
                "request_info": request_info
            }

    def _call_dashscope(
        self,
        query_text: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """调用DashScope API（同步）"""
        
        if not self.api_key:
            raise ValueError("DashScope API Key未设置，请设置DASHSCOPE_API_KEY环境变量或在配置中传入api_key")
        
        url = f"{self.base_url}/services/aigc/text-generation/generation"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 构建消息
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": query_text})
        
        payload = {
            "model": kwargs.get('model', self.model),
            "input": {
                "messages": messages
            },
            "parameters": {
                "result_format": "message",
                "max_tokens": kwargs.get('max_tokens', 1500),
                "temperature": kwargs.get('temperature', 0.7),
                "top_p": kwargs.get('top_p', 0.9)
            }
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
        response.raise_for_status()
        
        result = response.json()
        
        # 提取生成的文本
        if "output" in result and "choices" in result["output"]:
            content = result["output"]["choices"][0]["message"]["content"]
        else:
            content = str(result)
        
        return {
            "success": True,
            "content": content,
            "raw_response": result
        }
    
    def _call_dashscope_stream(
        self,
        query_text: str,
        system_prompt: Optional[str] = None,
        stream_callback: Optional[Callable[[str], None]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """调用DashScope API（流式）"""
        
        if not self.api_key:
            raise ValueError("DashScope API Key未设置")
        
        url = f"{self.base_url}/services/aigc/text-generation/generation"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 构建消息
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": query_text})
        
        payload = {
            "model": kwargs.get('model', self.model),
            "input": {
                "messages": messages
            },
            "parameters": {
                "result_format": "message",
                "max_tokens": kwargs.get('max_tokens', 1500),
                "temperature": kwargs.get('temperature', 0.7),
                "top_p": kwargs.get('top_p', 0.9)
            }
        }
        
        full_content = []
        
        response = requests.post(
            url, 
            headers=headers, 
            json=payload, 
            timeout=self.timeout,
            stream=True
        )
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data:'):
                    try:
                        data = json.loads(line[5:])
                        if "output" in data and "choices" in data["output"]:
                            content = data["output"]["choices"][0]["message"].get("content", "")
                            if content:
                                full_content.append(content)
                                if stream_callback:
                                    stream_callback(content)
                    except json.JSONDecodeError:
                        pass
        
        return {
            "success": True,
            "content": "".join(full_content),
            "raw_response": None
        }

    def _build_request(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """构建请求（完全复用qwen-chat-client的curl参数结构）"""

        # 生成ID
        session_id = kwargs.get('session_id') or str(uuid.uuid4()).replace("-", "")
        req_id = kwargs.get('req_id') or f"AI_SEARCH_DEBUG_{str(uuid.uuid4()).replace('-', '')}"
        timestamp = int(time.time() * 1000)

        # 构建消息
        messages = []

        # 添加用户消息（与参考格式一致，不包含role字段）
        messages.append({
            "content": message,
            "mime_type": "text/plain",
            "meta_data": {
                "is_default_query": "0",
                "ori_query": message,
                "paa_pass_through": {}
            }
        })

        # 构建请求体（完全按照curl中的JSON结构）
        # 使用当前时间戳（毫秒）
        current_timestamp = int(time.time() * 1000)
        current_timestamp_str = str(current_timestamp)

        request_data = {
            "req_id": req_id,
            "prefetch_req_id": None,
            "session_id": session_id,
            "res_id": None,
            "scene": "chat",
            "sub_scene": "chat",
            "scene_param": "retry",
            "agent_id": None,
            "from": "kkframenew",
            "display_ext": "",
            "deep_search": 0,
            "grade": "",
            "timestamp": current_timestamp,
            "messages": messages,
            "ai_tool_scene": "",
            "u_supplement": "",
            "chat_client": "native",
            "messages_merge": True,
            "protocol_version": "v2",
            "transfer_memory_info": "",
            "topic_id": "d88f1cdf509244edb61331aafce617c2",
            "session_type": 0,
            "bucket": {"ef_shangou": "on"},
            "cms_test_data_ids": "",
            "incremental_strategy": 0,
            "original_session_id": None,
            "original_req_id": None,
            "client_tm": current_timestamp_str,
            "update_timestamp": current_timestamp_str,
            "model": kwargs.get('model', self.model),
            "biz_data": '{"origin_entrance":"chat_common","gen_doc_card":true,"long_text_enable":true}',
            "amap_location": "120.01557240711386,30.28562512138549",
            "address": "浙江省杭州市余杭区高教路靠近阿里巴巴西溪园区C区"
        }

        return request_data

    def _get_request_url_and_headers(self, request_data: Dict) -> tuple:
        """获取实际请求的完整URL和Headers（用于记录）"""
        # 完整URL（必须包含所有查询参数，否则403）
        # 参数值已经URL编码，直接拼接
        url = ('https://chat2.qianwen.com/api/v1/chat/debug?'
               'bi=997&'
               'biz_id=ai_qwen&'
               'ca=OjXvwEAmhObgWE%2bCJAgwJDjBgZD5yoo3FC8o74edvw34rpR7oIE%2fMWPzBapYlEXU%2bMAzlD%2bR7RTDLqc6uSr1ZfD%2bdREG9G2%2b75%2bZBKsEaZ6ZQIeLWKlCK5liwKE2yEBo7TrHRP2hNgDqyPPrQu25xvODi2%2f3LCGu2Wqz%2fj4%2bKfjsSiEa1ybh%2fGq1YPWpNXror%2fP9sRo5M88u6pxa%2f1keXHRkV16ZGCit69d4%2bF7XMVNeeGWjifM6k9Tps0daM5of3l2vxvMyUSvovaOAJNo8%2bR9vindKJqD5BZyCmT2SxzVChbylHygT51urqzjs5BsWt11S51HqofEq7MWWJi5Z7kazMFiaOd3Un7BfXqYjKZDebixQNh%2fSyBvBkoExGQG55WMtlb8mYBa%2frn3Ehd92Z7XAb03rMFbdr7vEVfrlxJUmO8ZozlPilooZ8OY2o%2fT6Fys%3d&'
               'chat_client=native&'
               'fr=iphone&'
               'gi=bTkwBTw0WBlp%2boTnF4tQcpQ2nmwgK%2fdMeUVd7CP6%2fTbXw%2f0%3d&'
               'kp=OjWpxqqVPrU4xtxg8MwCwOlH4KZcior8CpU%2bglFYCcibHqnVfQHcweIs4EhE3hPy%2bhI%2fZwqxN0Z%2bGCDDD7sUoo8or5AQDctUtW9IFDlt5AnHY7fjYKBP%2beuQ48xx9m%2b7l812tbDPGmtSHsSHecohR5IH3h37J1YYj2w4TXEPGEiL3w%3d%3d&'
               'kps_wg=OjWpxqqVPrU4xtxg8MwCwOlH4KZcior8CpU%2BglFYCcibHqnVfQHcweIs4EhE3hPy%2BhI%2FZwqxN0Z%2BGCDDD7sUoo8or5AQDctUtW9IFDlt5AnHY7fjYKBP%2BeuQ48xx9m%2B7l812tbDPGmtSHsSHecohR5IH3h37J1YYj2w4TXEPGEiL3w%3D%3D&'
               'mt=hJgBrDFLPKqi2RKdhpsJD02d%2bfQ8Dvsy&'
               'nn=OjU%3d&'
               'nonce=8F17E301EA0B47D49A41AFFC9402F416&'
               'pc=OjWqjjPaD70yY5oZssOhlyr1Rmz5HOs4nHuWrfs%2f1PRTJ5PgK9VAcVOgkE2jNSxSk5DW1V2oidb0pc%2btpl%2fB%2b0o0&'
               'pf=200&'
               'pr=qwen&'
               'protocol_version=v2&'
               'sign_type=2&'
               'sign_wg=OjVrGodG0ntsfU%2F3i5OF3O4bwoR7YVvkDapJ5bdOAuvtnO%2FkjqaTKNh7YlmYZ5wU%2Fp4%3D&'
               'sv=love&'
               'timestamp=1776249008771&'
               'uc_param_str=utmtpcsnnnvebipfdnprfrsvcgbcxsginxodcakp&'
               'ut=OjVYKtlbZZA5iyQSSCcDlU63XpANlvc%2bEZwULg2Ms%2bJAbw%3d%3d&'
               'vcode=1776249008769&'
               've=6.6.0.2780&'
               'sign=3a353d01e56bae37f20c7953090c9c545814fd46b62a')

        # 构建请求头
        headers = {
            'sec-ch-ua-platform': 'macOS',
            'X-Appkey': '34400722',
            'X-Wpk-Reqid': 'f8b4f1e218b441838175b5510b027531',
            'X-Pv': '6.3',
            'sec-ch-ua': '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
            'X-Umt': 'GbkBIU5LPDMclhKdkFmQ3ooDsbe1rNye',
            'sec-ch-ua-mobile': '?0',
            'X-App-Ver': '5.1.20',
            'X-Bx-Version': '6.7.250903',
            'Accept': 'application/json, text/event-stream, text/event-stream',
            'X-Mini-Wua': 'iJwSsM5z3%2Fcjk%2F0ZcSAriWpK5HuNIonUh7GloLEnqa9%2F0qkK3cbSUa4Ff3G49%2FcSQ7qQuDatYTEDK5Fok3wiF8rvGxqi66yei8dz8ZmPCNsgHjNc1BIYOl4aeVX3C6MOkYllBTTfpn6U2K9SKzoYpUExnETOAN5gFi9h%2FTIbWG5yb%2BY2%2FAe6HYOo8',
            'Content-Type': 'application/json',
            'X-Deviceid': 'aR89N69/QVoDACshFdu81cwp',
            'X-Utdid': 'aR89N69/QVoDACshFdu81cwp',
            'Cache-Control': 'no-store',
            'Referer': 'https://pre-aisearch-debug.alibaba-inc.com/qwen-chat-scene/prod?req_id=AI_SEARCH_DEBUG_f8256028-d68d-43e4-901c-ba7442166b3e',
            'Accept-Language': 'zh-Hans-CN;q=1',
            'X-T': '1766659025',
            'X-Ttid': 'qwen@qwen_ios_5.1.20',
            'X-Wpk-Traceid': 'd9cf28b282c6431ebe411022ffc98dcf',
            'X-Sign': 'iz0pIe007xAAhdhFW3Y7oQLitN2Z5dhF3bdww0DmIdi53khXzKFrhumMuWwBQEFIMOXjXqMfFYw7NxwxiHScAgpyDufoQJYV6GXYRd',
            'X-Wpk-Bid': 'a3ucabr5-b1ayd2v5',
            'X-Sgext': 'JBPsc06U%2B5ANtjcaQDLrNnPZQ91Q2UraUN5Fz1DdRNtF3kfUS9pDz0PcQdpD3EPcQ9xD3EPcQ9xQ3FDcUNxDz0PcQ9xQ3FDdUN1Q3VDdUN1Q3VDcUNxD3EPcUN4XjVDfUNRQ31CWHbsqz1PMQo1TzFPcUNUs3V7dXrMSs17dVdxV3EOzEbNK3F7dXtxe3F7cXt5e3lXdVdxV3FXdXtxe3UTbQ9lA3UffRMFCskLbRNxG30LYQNst3FXcVdwsiCy5JaIhukKiK7kfpU6zFbNAwUPBQ8FDwUHeLN1AszKLMq0yrTKtMq0yrTKtMq0yrTKtMq0yrTKtMq0s3UWzQ7NCjyzVQ8pDykPKQdwS3VXeStgSykKIStpVwULKXtlDykvfVdxV3UKzQoks3F7cLN5As0rcVcFCwkPcQ9xV3FXcVdxV3kHKQ8pDykPKQ8pB3izeR7NCwUPBQsFDwUPBQ8FDwUPBQ8FDs0HULK1B3Be8JalOsw%3D%3D',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36'
        }

        return url, headers

    def _execute_request(self, request_data: Dict) -> Dict:
        """执行HTTP请求（同步）- 完全按照curl参数设定"""

        # 获取完整URL和Headers
        url, headers = self._get_request_url_and_headers(request_data)

        # 发送POST请求（流式读取）
        response = requests.post(
            url,
            headers=headers,
            json=request_data,
            timeout=self.timeout,
            stream=True
        )
        response.raise_for_status()

        # 读取流式响应内容
        full_content = []
        for line in response.iter_lines():
            if line:
                line_text = line.decode('utf-8')
                if line_text.startswith('data:'):
                    try:
                        data = json.loads(line_text[5:])
                        if data and 'content' in str(data):
                            full_content.append(line_text[5:])
                    except:
                        pass
        
        return {"content": "\n".join(full_content), "raw_lines": full_content}
    
    def _execute_request_stream(
        self, 
        request_data: Dict,
        stream_callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """执行HTTP请求（流式）"""
        
        url = f"{self.base_url}/api/v2/chat"
        
        # 构建请求头
        headers = self._build_headers(request_data['req_id'])
        headers["Accept"] = "text/event-stream"
        
        full_content = []
        
        response = requests.post(
            url,
            headers=headers,
            json=request_data,
            timeout=self.timeout,
            stream=True
        )
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data:'):
                    try:
                        data = json.loads(line[5:])
                        content = self._extract_content_from_stream(data)
                        if content:
                            full_content.append(content)
                            if stream_callback:
                                stream_callback(content)
                    except json.JSONDecodeError:
                        pass
        
        return {
            "success": True,
            "content": "".join(full_content),
            "raw_response": None
        }
    
    def _build_headers(self, req_id: str) -> Dict[str, str]:
        """构建请求头"""
        return {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "Cache-Control": "no-store",
            "X-Appkey": self.app_key,
            "X-App-Ver": self.app_ver,
            "X-Bx-Version": self.bx_version,
            "X-Pv": self.pv,
            "X-Deviceid": self.device_id,
            "X-Utdid": self.device_id,
            "X-Wpk-Bid": self.wpk_bid,
            "X-Umt": self.umt,
            "X-Mini-Wua": self.mini_wua,
            "X-Sgext": self.sgext,
            "X-Sign": self.x_sign or "",
            "X-Wpk-Reqid": self.wpk_reqid or "",
            "X-T": str(int(time.time())),
            "X-Ttid": "qwen@qwen_ios_5.1.20",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
            "Referer": f"https://pre-aisearch-debug.alibaba-inc.com/qwen-chat-scene/prod?req_id={req_id}"
        }

    def _extract_content(self, response: Dict) -> str:
        """从响应中提取内容"""
        content_parts = []

        if "data" in response and "messages" in response["data"]:
            for msg in response["data"]["messages"]:
                mime_type = msg.get("mime_type", "")
                if mime_type == "text/plain" and msg.get("content"):
                    content_parts.append(msg["content"])

        return "".join(content_parts)
    
    def _extract_content_from_sse(self, response: Dict) -> str:
        """从SSE流式响应中提取文本内容"""
        content_parts = []
        raw_lines = response.get("raw_lines", [])
        
        for line in raw_lines:
            try:
                data = json.loads(line)
                if "data" in data and "messages" in data["data"]:
                    for msg in data["data"]["messages"]:
                        if msg.get("mime_type") == "text/plain" and msg.get("content"):
                            content_parts.append(msg["content"])
            except:
                pass
        
        return "".join(content_parts)
    
    def _extract_content_from_stream(self, data: Dict) -> str:
        """从流式响应中提取内容"""
        content_parts = []
        
        if "data" in data and "messages" in data["data"]:
            for msg in data["data"]["messages"]:
                mime_type = msg.get("mime_type", "")
                if mime_type == "text/plain" and msg.get("content"):
                    content_parts.append(msg["content"])
        
        return "".join(content_parts)

    def execute(self, input_data: Dict) -> Dict:
        """执行调用任务"""
        return self.call(
            query_text=input_data.get('query_text', ''),
            system_prompt=input_data.get('system_prompt'),
            model=input_data.get('model')
        )
