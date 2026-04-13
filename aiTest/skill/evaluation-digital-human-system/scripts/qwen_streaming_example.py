#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QwenAgent 流式调用配置示例
展示如何使用流式调用和自动获取认证参数
"""

# ==================== 配置示例 1: 流式调用（已有认证参数）====================
config_with_auth = {
    'api_mode': 'qwen_chat',  # 使用qwen-chat-client模式
    'stream': True,  # 启用流式调用
    'model': 'quark-235b',
    
    # 认证参数（已获取）
    'x_sign': 'your_x_sign_here',
    'wpk_reqid': 'your_wpk_reqid_here',
    
    # 其他请求头参数
    'app_key': 'your_app_key',
    'app_ver': '5.1.20',
    'device_id': 'your_device_id',
    'wpk_bid': 'your_wpk_bid',
}

# ==================== 配置示例 2: 流式调用（自动获取认证参数）====================
config_auto_auth = {
    'api_mode': 'qwen_chat',
    'stream': True,  # 启用流式调用
    'model': 'quark-235b',
    
    # 启用自动获取认证参数
    'auto_refresh_auth': True,
    
    # 登录配置 - 用于自动获取x-sign和wpk_reqid
    'login_config': {
        'login_url': 'https://your-login-api.com/login',
        'login_type': 'password',  # 支持: password, token, cookie
        'credentials': {
            'username': 'your_username',
            'password': 'your_password'
            # 或使用token:
            # 'token': 'your_token'
            # 或使用cookie:
            # 'cookies': 'your_cookies'
        },
        # 响应中字段路径（根据实际响应结构调整）
        'x_sign_path': 'data.x_sign',      # x-sign在响应中的路径
        'wpk_reqid_path': 'data.wpk_reqid' # wpk_reqid在响应中的路径
    },
    
    # 其他请求头参数
    'app_key': 'your_app_key',
    'app_ver': '5.1.20',
    'device_id': 'your_device_id',
    'wpk_bid': 'your_wpk_bid',
}

# ==================== 使用示例 ====================
def example_streaming_usage():
    """流式调用使用示例"""
    import sys
    sys.path.insert(0, '/Users/linjie/Documents/workspace/aiTest/skill/evaluation-digital-human-system')
    
    from agents.qwen_agent import QwenAgent
    
    # 初始化Agent
    agent = QwenAgent(config_auto_auth)
    
    # 定义流式回调函数
    def on_chunk(content: str):
        """接收每个流式chunk的回调"""
        print(content, end='', flush=True)
    
    # 调用（自动使用流式）
    result = agent.call(
        query_text="你好，请介绍一下自己",
        system_prompt="你是一个有帮助的助手",
        stream_callback=on_chunk  # 传入回调函数接收流式输出
    )
    
    print("\n\n完整响应:")
    print(result['content'])
    
    # 获取自动更新的认证参数（已保存到config中）
    print(f"\n当前x_sign: {agent.config.get('x_sign')[:30]}...")
    print(f"当前wpk_reqid: {agent.config.get('wpk_reqid')}")


# ==================== 在Master中使用 ====================
def example_master_config():
    """在MasterDigitalHuman中使用流式调用"""
    from master_digital_human import MasterDigitalHuman, TaskConfig
    
    # Master配置
    master_config = {
        'results_dir': './results',
        'qwen_config': {
            'api_mode': 'qwen_chat',
            'stream': True,  # 启用流式
            'auto_refresh_auth': True,
            'login_config': {
                'login_url': 'https://your-login-api.com/login',
                'login_type': 'password',
                'credentials': {
                    'username': 'your_username',
                    'password': 'your_password'
                },
                'x_sign_path': 'data.x_sign',
                'wpk_reqid_path': 'data.wpk_reqid'
            }
        }
    }
    
    master = MasterDigitalHuman(master_config)
    
    task_config = TaskConfig(
        name='流式调用测试',
        target_model='qwen-turbo',
        scope={...},
        cases_per_combination=2
    )
    
    execution = master.submit_task(task_config)


if __name__ == '__main__':
    print("配置示例文件")
    print("请根据实际登录接口修改login_config配置")
    print("\n主要配置项:")
    print("- stream: True  # 启用流式调用")
    print("- auto_refresh_auth: True  # 自动获取认证参数")
    print("- login_config: 登录接口配置")
    print("  - login_url: 登录接口地址")
    print("  - login_type: 登录类型 (password/token/cookie)")
    print("  - credentials: 认证信息")
    print("  - x_sign_path: x-sign字段路径")
    print("  - wpk_reqid_path: wpk_reqid字段路径")
