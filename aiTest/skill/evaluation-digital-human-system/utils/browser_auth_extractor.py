#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
浏览器认证参数提取工具
帮助用户从浏览器请求头中提取 x-sign 和 wpk_reqid 等认证参数

使用方法:
1. 打开浏览器开发者工具 (F12)
2. 访问千问聊天页面并发送一条消息
3. 在 Network 面板中找到 /api/v2/chat 请求
4. 复制请求头中的以下参数值
5. 粘贴到本工具或保存到配置文件
"""

import json
import re
from typing import Dict, Optional


class BrowserAuthExtractor:
    """从浏览器请求头中提取认证参数"""
    
    # 需要提取的关键参数
    REQUIRED_HEADERS = [
        'x-sign',
        'x-wpk-reqid',
        'x-appkey',
        'x-app-ver',
        'x-bx-version',
        'x-pv',
        'x-deviceid',
        'x-wpk-bid',
        'x-umt',
        'x-mini-wua',
        'x-sgext'
    ]
    
    @classmethod
    def extract_from_curl(cls, curl_command: str) -> Dict[str, str]:
        """
        从 curl 命令中提取认证参数
        
        Args:
            curl_command: 浏览器开发者工具复制的 curl 命令
            
        Returns:
            提取的认证参数字典
        """
        config = {}
        
        # 提取 headers
        header_pattern = r"-H '([^:]+): ([^']+)'"
        headers = dict(re.findall(header_pattern, curl_command))
        
        # 映射到配置
        mapping = {
            'x-sign': 'x_sign',
            'x-wpk-reqid': 'wpk_reqid',
            'x-appkey': 'app_key',
            'x-app-ver': 'app_ver',
            'x-bx-version': 'bx_version',
            'x-pv': 'pv',
            'x-deviceid': 'device_id',
            'x-wpk-bid': 'wpk_bid',
            'x-umt': 'umt',
            'x-mini-wua': 'mini_wua',
            'x-sgext': 'sgext'
        }
        
        for header_key, config_key in mapping.items():
            if header_key in headers:
                config[config_key] = headers[header_key]
        
        return config
    
    @classmethod
    def extract_from_raw_headers(cls, raw_headers: str) -> Dict[str, str]:
        """
        从原始请求头字符串中提取认证参数
        
        Args:
            raw_headers: 浏览器开发者工具中复制的请求头
            
        Returns:
            提取的认证参数字典
        """
        config = {}
        
        # 解析每一行
        for line in raw_headers.strip().split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                # 映射到配置键
                mapping = {
                    'x-sign': 'x_sign',
                    'x-wpk-reqid': 'wpk_reqid',
                    'x-appkey': 'app_key',
                    'x-app-ver': 'app_ver',
                    'x-bx-version': 'bx_version',
                    'x-pv': 'pv',
                    'x-deviceid': 'device_id',
                    'x-wpk-bid': 'wpk_bid',
                    'x-umt': 'umt',
                    'x-mini-wua': 'mini_wua',
                    'x-sgext': 'sgext'
                }
                
                if key in mapping:
                    config[mapping[key]] = value
        
        return config
    
    @classmethod
    def generate_config(cls, auth_params: Dict[str, str], api_mode: str = 'qwen_chat') -> Dict:
        """
        生成完整的配置字典
        
        Args:
            auth_params: 提取的认证参数
            api_mode: API模式
            
        Returns:
            完整的配置字典
        """
        config = {
            'api_mode': api_mode,
            'stream': True,  # 默认启用流式
            'model': 'quark-235b',
            **auth_params
        }
        
        return config
    
    @classmethod
    def save_config(cls, config: Dict, filepath: str = './config/qwen_auth_config.json'):
        """保存配置到文件"""
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 配置已保存: {filepath}")
    
    @classmethod
    def print_extraction_guide(cls):
        """打印提取指南"""
        guide = """
╔════════════════════════════════════════════════════════════════╗
║           浏览器认证参数提取指南                                ║
╚════════════════════════════════════════════════════════════════╝

【步骤】

1. 打开浏览器，访问千问聊天页面 (https://chat2.qianwen.com)

2. 按 F12 打开开发者工具，切换到 Network (网络) 面板

3. 在页面上发送一条消息

4. 在 Network 面板中找到 /api/v2/chat 请求
   - 可以通过过滤器输入 "chat" 快速找到

5. 点击该请求，查看 Headers (请求头) 标签

6. 找到 Request Headers (请求头) 部分，复制以下字段的值:
   
   ✓ x-sign        (必需)
   ✓ x-wpk-reqid   (必需)
   ✓ x-appkey
   ✓ x-app-ver
   ✓ x-bx-version
   ✓ x-pv
   ✓ x-deviceid
   ✓ x-wpk-bid
   ✓ x-umt
   ✓ x-mini-wua
   ✓ x-sgext

7. 使用以下方式提取参数:

   方式A: 复制为 cURL
   - 右键点击请求 → Copy → Copy as cURL
   - 粘贴到本工具的 extract_from_curl() 方法

   方式B: 复制请求头
   - 在 Request Headers 区域右键 → Copy all
   - 粘贴到本工具的 extract_from_raw_headers() 方法

【示例代码】

    from utils.browser_auth_extractor import BrowserAuthExtractor
    
    # 方式A: 从 cURL 提取
    curl_cmd = """curl 'https://chat2.qianwen.com/api/v2/chat' \\
        -H 'x-sign: xxx' \\
        -H 'x-wpk-reqid: xxx' ..."""
    
    auth_params = BrowserAuthExtractor.extract_from_curl(curl_cmd)
    
    # 方式B: 从原始请求头提取
    raw_headers = """
    x-sign: xxx
    x-wpk-reqid: xxx
    ...
    """
    
    auth_params = BrowserAuthExtractor.extract_from_raw_headers(raw_headers)
    
    # 生成配置
    config = BrowserAuthExtractor.generate_config(auth_params)
    
    # 保存配置
    BrowserAuthExtractor.save_config(config)

【注意事项】

⚠️ 这些认证参数有过期时间，通常需要定期更新
⚠️ x-sign 和 x-wpk-reqid 是必需的，其他参数可以使用默认值
⚠️ 请勿将包含敏感信息的配置文件提交到版本控制

"""
        print(guide)


def interactive_extract():
    """交互式提取工具"""
    print("\n" + "="*60)
    print("  浏览器认证参数提取工具")
    print("="*60)
    
    print("\n请选择输入方式:")
    print("1. 粘贴 cURL 命令")
    print("2. 粘贴原始请求头")
    print("3. 查看提取指南")
    print("4. 退出")
    
    choice = input("\n请选择 (1-4): ").strip()
    
    if choice == '1':
        print("\n请粘贴 cURL 命令 (输入空行结束):")
        lines = []
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
        curl_cmd = '\n'.join(lines)
        
        auth_params = BrowserAuthExtractor.extract_from_curl(curl_cmd)
        
    elif choice == '2':
        print("\n请粘贴请求头 (输入空行结束):")
        lines = []
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
        raw_headers = '\n'.join(lines)
        
        auth_params = BrowserAuthExtractor.extract_from_raw_headers(raw_headers)
        
    elif choice == '3':
        BrowserAuthExtractor.print_extraction_guide()
        return
    elif choice == '4':
        return
    else:
        print("无效选择")
        return
    
    # 显示提取结果
    print("\n" + "="*60)
    print("  提取结果")
    print("="*60)
    
    if not auth_params:
        print("⚠️ 未提取到任何参数，请检查输入")
        return
    
    for key, value in auth_params.items():
        # 敏感信息部分隐藏
        if key in ['x_sign', 'wpk_reqid', 'umt']:
            display_value = value[:20] + '...' if len(value) > 20 else value
        else:
            display_value = value
        print(f"  {key}: {display_value}")
    
    # 生成配置
    config = BrowserAuthExtractor.generate_config(auth_params)
    
    print("\n" + "="*60)
    print("  生成的配置")
    print("="*60)
    print(json.dumps(config, ensure_ascii=False, indent=2))
    
    # 保存
    save = input("\n是否保存配置到文件? (y/n): ").strip().lower()
    if save == 'y':
        filepath = input("保存路径 (默认: ./config/qwen_auth_config.json): ").strip()
        if not filepath:
            filepath = './config/qwen_auth_config.json'
        BrowserAuthExtractor.save_config(config, filepath)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--guide':
        BrowserAuthExtractor.print_extraction_guide()
    else:
        interactive_extract()
