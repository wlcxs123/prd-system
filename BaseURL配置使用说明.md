# BaseURL动态配置使用说明

## 概述

本项目已实现服务器端动态配置baseUrl的功能，无需在前端硬编码不同环境的URL，而是通过服务器端API动态获取配置信息。

## 工作原理

### 1. 服务器端配置

服务器端根据环境变量自动判断当前运行环境：

```python
# 在 app.py 中
def get_base_url():
    """根据环境动态获取baseUrl"""
    if app.config.get('DEBUG', False) or config_name == 'development':
        # 开发环境使用相对路径（空字符串）
        return ''
    else:
        # 生产环境使用完整URL
        server_name = os.environ.get('SERVER_NAME', '115.190.103.114')
        port = os.environ.get('PORT', '8081')
        return f'http://{server_name}:{port}'
```

### 2. 配置API

新增了 `/api/config` 端点，返回前端需要的配置信息：

```json
{
    "baseUrl": "",  // 开发环境为空，生产环境为完整URL
    "environment": "development",
    "debug": true
}
```

### 3. 前端动态加载

前端config.js文件现在包含初始化方法：

```javascript
const CONFIG = {
    BASE_URL: '',  // 将在初始化时从服务器获取
    
    // 初始化配置 - 从服务器获取baseUrl
    init: async function() {
        const response = await fetch(this.TEMP_BASE_URL + '/api/config');
        const config = await response.json();
        this.BASE_URL = config.baseUrl;
        this.ENVIRONMENT = config.environment;
        this.DEBUG = config.debug;
    }
};
```

## 环境差异

### 开发环境
- **baseUrl**: `""` (空字符串，使用相对路径)
- **API调用**: `fetch('/api/submit')` 
- **静态资源**: `src="config.js"`

### 生产环境
- **baseUrl**: `"http://115.190.103.114:8081"`
- **API调用**: `fetch('http://115.190.103.114:8081/api/submit')`
- **静态资源**: `src="/config.js"`

## 使用方法

### 1. 页面集成

在HTML页面中添加配置加载逻辑：

```html
<script>
// 环境检测和配置加载
(function() {
    var isLocal = location.hostname === 'localhost' || location.hostname === '127.0.0.1' || location.hostname === '';
    var configPath = isLocal ? 'config.js' : '/config.js';
    var script = document.createElement('script');
    script.src = configPath;
    script.onload = async function() {
        try {
            await CONFIG.init();
            console.log('CONFIG initialized successfully');
            // 触发配置初始化完成事件
            window.dispatchEvent(new CustomEvent('configReady'));
        } catch (error) {
            console.error('Failed to initialize CONFIG:', error);
            window.dispatchEvent(new CustomEvent('configReady'));
        }
    };
    document.head.appendChild(script);
})();
</script>
```

### 2. 等待配置加载

在需要使用CONFIG的脚本中，监听配置就绪事件：

```javascript
// 等待CONFIG初始化完成
window.addEventListener('configReady', function() {
    // 现在可以安全使用CONFIG对象
    console.log('Base URL:', CONFIG.BASE_URL);
    
    // 加载其他依赖CONFIG的脚本
    var script = document.createElement('script');
    script.src = '/backend/static/js/questionnaire-helper.js';
    document.head.appendChild(script);
});
```

### 3. API调用

使用CONFIG对象的辅助方法进行API调用：

```javascript
// 正确的API调用方式
const apiUrl = CONFIG.getApiUrl('/api/submit');
fetch(apiUrl, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
});
```

## 环境变量配置

### 开发环境
```bash
FLASK_ENV=development
DEBUG=True
```

### 生产环境
```bash
FLASK_ENV=production
SERVER_NAME=115.190.103.114
PORT=8081
DEBUG=False
```

## 测试验证

可以访问测试页面验证配置是否正确：
- 开发环境: `http://localhost:8081/test_baseurl.html`
- 生产环境: `http://115.190.103.114:8081/test_baseurl.html`

测试页面会显示：
1. 当前环境信息
2. 配置加载结果
3. API调用测试
4. 路径解析测试

## 优势

1. **统一代码**: 同一套代码可以在不同环境运行
2. **动态配置**: 服务器端控制baseUrl，无需前端硬编码
3. **环境自适应**: 自动检测环境并应用相应配置
4. **易于部署**: 部署时无需修改前端代码
5. **配置集中**: 所有环境配置集中在服务器端管理

## 注意事项

1. 确保 `/api/config` 端点在所有环境中都可访问
2. 前端代码必须等待CONFIG初始化完成后再使用
3. 生产环境需要正确设置SERVER_NAME和PORT环境变量
4. 开发环境和生产环境的静态资源路径不同（相对路径 vs 绝对路径）

## 故障排除

### 问题1: CONFIG未定义
**原因**: config.js文件加载失败或初始化未完成
**解决**: 检查文件路径，确保监听configReady事件

### 问题2: API调用失败
**原因**: baseUrl配置错误或服务器未启动
**解决**: 检查服务器状态和环境变量配置

### 问题3: 静态资源404
**原因**: 开发环境和生产环境路径差异
**解决**: 确保环境检测逻辑正确，使用相应的路径格式