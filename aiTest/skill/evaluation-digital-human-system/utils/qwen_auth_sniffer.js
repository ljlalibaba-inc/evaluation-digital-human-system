/**
 * 千问认证参数拦截器
 * 将此代码粘贴到浏览器控制台使用
 * 
 * 使用方法:
 * 1. 访问 https://chat2.qianwen.com
 * 2. 按 F12 打开开发者工具，切换到 Console
 * 3. 粘贴此代码并回车
 * 4. 发送一条消息
 * 5. 认证参数会自动捕获并显示
 */

(function() {
    'use strict';
    
    // 存储捕获的配置
    const capturedConfigs = [];
    
    // 重写 fetch 以拦截请求
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        const [url, options] = args;
        
        // 检查是否是 chat 请求
        if (url.includes('/api/v2/chat') && options && options.headers) {
            const headers = options.headers;
            
            // 提取认证参数
            const config = {
                api_mode: 'qwen_chat',
                stream: true,
                model: 'quark-235b',
                x_sign: headers['x-sign'] || headers['X-Sign'],
                wpk_reqid: headers['x-wpk-reqid'] || headers['X-Wpk-Reqid'],
                app_key: headers['x-appkey'] || headers['X-Appkey'],
                app_ver: headers['x-app-ver'] || headers['X-App-Ver'],
                bx_version: headers['x-bx-version'] || headers['X-Bx-Version'],
                pv: headers['x-pv'] || headers['X-Pv'],
                device_id: headers['x-deviceid'] || headers['X-Deviceid'],
                wpk_bid: headers['x-wpk-bid'] || headers['X-Wpk-Bid'],
                umt: headers['x-umt'] || headers['X-Umt'],
                mini_wua: headers['x-mini-wua'] || headers['X-Mini-Wua'],
                sgext: headers['x-sgext'] || headers['X-Sgext'],
                captured_at: new Date().toISOString()
            };
            
            // 只保存有效的配置
            if (config.x_sign && config.wpk_reqid) {
                capturedConfigs.push(config);
                
                // 显示在控制台
                console.log('%c[认证参数已捕获]', 'color: #00ff00; font-size: 16px; font-weight: bold;');
                console.log('配置:', JSON.stringify(config, null, 2));
                
                // 复制到剪贴板
                navigator.clipboard.writeText(JSON.stringify(config, null, 2))
                    .then(() => {
                        console.log('%c[已复制到剪贴板]', 'color: #00ff00;');
                    })
                    .catch(err => {
                        console.log('复制失败，请手动复制上面的配置');
                    });
                
                // 显示提示
                showNotification('认证参数已捕获并复制到剪贴板！');
            }
        }
        
        return originalFetch.apply(this, args);
    };
    
    // 显示通知
    function showNotification(message) {
        const div = document.createElement('div');
        div.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 25px;
            border-radius: 8px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            font-size: 14px;
            font-weight: 500;
            z-index: 999999;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            animation: slideIn 0.3s ease;
        `;
        div.textContent = message;
        
        // 添加动画样式
        if (!document.getElementById('qwen-auth-sniffer-style')) {
            const style = document.createElement('style');
            style.id = 'qwen-auth-sniffer-style';
            style.textContent = `
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
            document.head.appendChild(style);
        }
        
        document.body.appendChild(div);
        
        setTimeout(() => {
            div.style.animation = 'slideIn 0.3s ease reverse';
            setTimeout(() => div.remove(), 300);
        }, 5000);
    }
    
    // 暴露全局方法
    window.qwenAuthSniffer = {
        getConfigs: () => capturedConfigs,
        getLatestConfig: () => capturedConfigs[capturedConfigs.length - 1] || null,
        exportConfig: () => {
            const config = capturedConfigs[capturedConfigs.length - 1];
            if (config) {
                const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `qwen_auth_config_${Date.now()}.json`;
                a.click();
                URL.revokeObjectURL(url);
            }
        },
        printGuide: () => {
            console.log(`
╔════════════════════════════════════════════════════════╗
║  千问认证参数拦截器已启动                              ║
╚════════════════════════════════════════════════════════╝

可用命令:
- qwenAuthSniffer.getConfigs()      获取所有捕获的配置
- qwenAuthSniffer.getLatestConfig() 获取最新的配置
- qwenAuthSniffer.exportConfig()    导出配置为JSON文件

使用方法:
1. 在页面上发送一条消息
2. 认证参数会自动捕获并复制到剪贴板
3. 使用上面的命令查看或导出配置
            `);
        }
    };
    
    console.log('%c千问认证参数拦截器已启动！', 'color: #00ff00; font-size: 18px; font-weight: bold;');
    console.log('发送一条消息，认证参数将自动捕获。');
    console.log('输入 qwenAuthSniffer.printGuide() 查看帮助');
    
})();
