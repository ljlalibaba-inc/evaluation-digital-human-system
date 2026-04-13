/**
 * 千问认证参数提取 Bookmarklet
 * 
 * 使用方法:
 * 1. 创建一个新的浏览器书签
 * 2. 将以下代码复制到书签的 URL/地址栏
 * 3. 访问千问聊天页面 (https://chat2.qianwen.com)
 * 4. 点击书签，即可复制认证参数
 * 
 * 注意: 需要在发送一条消息后使用，确保有 /api/v2/chat 请求
 */

javascript:(function(){
    // 查找最近的 chat 请求
    const requests = performance.getEntriesByType('resource')
        .filter(r => r.name.includes('/api/v2/chat'));
    
    if (requests.length === 0) {
        alert('未找到 /api/v2/chat 请求，请先发送一条消息');
        return;
    }
    
    // 获取最新的请求
    const latestRequest = requests[requests.length - 1];
    
    // 尝试从浏览器缓存或拦截器中获取请求头
    // 注意: 由于浏览器安全限制，无法直接获取请求头
    // 这里提供手动复制指导
    
    const guide = `
╔════════════════════════════════════════════════════════╗
║  认证参数提取指导                                      ║
╚════════════════════════════════════════════════════════╝

检测到 ${requests.length} 个 chat 请求

由于浏览器安全限制，无法自动获取请求头。
请按以下步骤手动复制:

1. 按 F12 打开开发者工具
2. 切换到 Network (网络) 面板
3. 找到 /api/v2/chat 请求 (已高亮)
4. 点击请求，查看 Headers
5. 复制以下字段:
   - x-sign
   - x-wpk-reqid
   - x-appkey
   - x-deviceid

快捷方式:
- 右键点击请求 → Copy → Copy as cURL
- 或使用 Copy all request headers
    `;
    
    console.log('%c' + guide, 'color: #00ff00; font-size: 14px;');
    alert(guide);
    
    // 尝试高亮相关请求 (在控制台)
    console.log('%c最近的 chat 请求:', 'color: #ff9900; font-size: 16px; font-weight: bold;');
    requests.forEach((req, i) => {
        console.log(`${i + 1}. ${req.name}`);
        console.log('   时间:', new Date(req.startTime).toLocaleString());
        console.log('   时长:', req.duration.toFixed(2), 'ms');
    });
})();
