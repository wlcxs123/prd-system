# 统一错误处理系统使用指南

## 概述

本系统实现了统一的前后端错误处理机制，提供了标准化的错误响应格式、用户友好的错误提示、自动重试机制和网络错误处理功能。

## 系统组件

### 1. 后端错误处理 (`backend/error_handlers.py`)

#### 主要功能
- 标准化错误响应格式
- 错误代码和消息映射
- 自动错误日志记录
- 全局异常处理

#### 错误代码
```python
# 验证错误
VALIDATION_ERROR = 'VALIDATION_ERROR'
REQUIRED_FIELD_MISSING = 'REQUIRED_FIELD_MISSING'
INVALID_FORMAT = 'INVALID_FORMAT'

# 认证和授权错误
AUTH_REQUIRED = 'AUTH_REQUIRED'
AUTH_ERROR = 'AUTH_ERROR'
SESSION_EXPIRED = 'SESSION_EXPIRED'
PERMISSION_DENIED = 'PERMISSION_DENIED'

# 资源错误
NOT_FOUND = 'NOT_FOUND'
RESOURCE_EXISTS = 'RESOURCE_EXISTS'

# 服务器错误
SERVER_ERROR = 'SERVER_ERROR'
DATABASE_ERROR = 'DATABASE_ERROR'
NETWORK_ERROR = 'NETWORK_ERROR'
```

#### 使用方法
```python
from error_handlers import validation_error, auth_error, server_error

# 在视图函数中使用
@app.route('/api/example', methods=['POST'])
def example_endpoint():
    try:
        data = request.json
        if not data:
            return jsonify(*validation_error(['请求数据不能为空']))
        
        # 业务逻辑...
        
    except Exception as e:
        return jsonify(*server_error('操作失败', str(e)))
```

### 2. 前端错误处理 (`backend/static/js/error-handler.js`)

#### 主要功能
- 统一的错误提示界面
- 自动重试机制
- 网络请求封装
- 全局错误捕获

#### 基本使用
```javascript
// 显示不同类型的提示
errorHandler.showError('操作失败', '详细错误信息');
errorHandler.showSuccess('操作成功');
errorHandler.showWarning('注意事项');
errorHandler.showInfo('提示信息');

// 带重试功能的错误提示
errorHandler.showError('网络错误', '连接失败', 'error', {
    retry: () => retryFunction()
});

// 带详情的错误提示
errorHandler.showError('验证失败', '数据格式不正确', 'error', {
    details: ['姓名不能为空', '年级必须选择']
});
```

#### 网络请求
```javascript
// 使用封装的请求方法（自动处理错误和重试）
const response = await errorHandler.post('/api/questionnaires', data);
const response = await errorHandler.get('/api/questionnaires');
const response = await errorHandler.put('/api/questionnaires/1', data);
const response = await errorHandler.delete('/api/questionnaires/1');

// 处理API响应错误
try {
    const response = await fetch('/api/example');
    if (!response.ok) {
        await errorHandler.handleApiError(response);
    }
} catch (error) {
    errorHandler.showError('网络错误', error.message);
}
```

### 3. 问卷辅助工具 (`backend/static/js/questionnaire-helper.js`)

#### 主要功能
- 问卷数据验证
- 统一提交接口
- 自动保存功能
- 数据格式标准化

#### 使用方法
```javascript
// 验证问卷数据
const errors = questionnaireHelper.validateQuestionnaire(data);
if (errors.length > 0) {
    errorHandler.showError('验证失败', '请检查输入', 'error', {
        details: errors
    });
}

// 提交问卷
const result = await questionnaireHelper.submitQuestionnaire(data, {
    showLoading: true,
    onSuccess: (result) => {
        questionnaireHelper.showSuccessPage(result.id);
    }
});

// 启用自动保存
const cleanup = questionnaireHelper.enableAutoSave(data, 30000); // 30秒间隔

// 恢复自动保存的数据
const savedData = questionnaireHelper.restoreAutoSavedData();
```

## 集成指南

### 1. 在现有HTML页面中集成

#### 步骤1：引入脚本文件
```html
<head>
    <!-- 引入错误处理组件 -->
    <script src="backend/static/js/error-handler.js"></script>
    <script src="backend/static/js/questionnaire-helper.js"></script>
</head>
```

#### 步骤2：替换现有的错误处理
```javascript
// 旧的错误处理方式
alert('❌ 保存失败：' + errorMessage);

// 新的错误处理方式
errorHandler.showError('保存失败', errorMessage, 'error', {
    details: errorDetails,
    retry: () => retrySubmission()
});
```

#### 步骤3：使用统一的提交方法
```javascript
// 旧的提交方式
try {
    const response = await fetch('/api/questionnaires', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    
    if (response.ok) {
        const result = await response.json();
        alert('提交成功');
    } else {
        alert('提交失败');
    }
} catch (error) {
    alert('网络错误');
}

// 新的提交方式
const result = await questionnaireHelper.submitQuestionnaire(data, {
    showLoading: true,
    onSuccess: (result) => {
        questionnaireHelper.showSuccessPage(result.id);
    }
});
```

### 2. 在Flask应用中集成

#### 步骤1：注册错误处理器
```python
from error_handlers import register_error_handlers

app = Flask(__name__)
register_error_handlers(app)
```

#### 步骤2：更新视图函数
```python
from error_handlers import validation_error, auth_error, server_error

@app.route('/api/example', methods=['POST'])
def example():
    try:
        # 验证数据
        if not request.json:
            return jsonify(*validation_error(['请求数据不能为空']))
        
        # 业务逻辑
        result = process_data(request.json)
        return jsonify({'success': True, 'data': result})
        
    except ValidationError as e:
        return jsonify(*validation_error(e.messages))
    except Exception as e:
        return jsonify(*server_error('处理失败', str(e)))
```

## 错误响应格式

### 标准错误响应结构
```json
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "用户友好的错误消息",
        "technical_message": "技术错误详情",
        "details": ["具体错误1", "具体错误2"],
        "request_id": "20241215123456-1234"
    },
    "timestamp": "2024-12-15T12:34:56.789Z",
    "retry_after": 30
}
```

### 成功响应结构
```json
{
    "success": true,
    "data": { /* 响应数据 */ },
    "message": "操作成功",
    "timestamp": "2024-12-15T12:34:56.789Z"
}
```

## 配置选项

### 前端配置
```javascript
// 在页面加载时配置错误处理器
errorHandler.retryAttempts = 3;        // 重试次数
errorHandler.retryDelay = 1000;        // 重试延迟（毫秒）
errorHandler.maxRetryDelay = 10000;    // 最大重试延迟
errorHandler.networkTimeout = 30000;   // 网络超时时间
```

### 后端配置
```python
# 在Flask配置中设置
app.config['ERROR_LOG_LEVEL'] = 'INFO'
app.config['ERROR_LOG_FILE'] = 'logs/error.log'
app.config['ENABLE_ERROR_DETAILS'] = True  # 开发环境显示详细错误
```

## 最佳实践

### 1. 错误消息设计
- 使用用户友好的语言
- 提供具体的解决建议
- 避免技术术语
- 支持多语言

### 2. 重试策略
- 只对可重试的错误启用重试
- 使用指数退避算法
- 设置合理的重试次数限制
- 提供手动重试选项

### 3. 日志记录
- 记录所有错误的详细信息
- 包含请求上下文信息
- 使用结构化日志格式
- 定期清理日志文件

### 4. 用户体验
- 提供清晰的错误提示
- 显示操作进度
- 支持错误详情查看
- 提供帮助和支持链接

## 示例文件

- `error_handling_demo.html` - 完整的功能演示
- `questionnaire_with_error_handling_example.html` - 问卷集成示例
- `backend/templates/admin.html` - 管理后台集成示例

## 故障排除

### 常见问题

1. **错误提示不显示**
   - 检查是否正确引入了 `error-handler.js`
   - 确认页面中存在错误容器元素
   - 检查浏览器控制台是否有JavaScript错误

2. **网络重试不工作**
   - 确认错误类型是否支持重试
   - 检查网络连接状态
   - 验证服务器端点是否正确

3. **错误日志不记录**
   - 检查日志目录权限
   - 确认日志配置是否正确
   - 验证错误处理器是否正确注册

### 调试技巧

1. 启用详细日志
2. 使用浏览器开发者工具
3. 检查网络请求和响应
4. 验证错误处理器配置

## 更新日志

### v1.0.0 (2024-12-15)
- 初始版本发布
- 实现统一错误处理系统
- 支持自动重试机制
- 提供用户友好的错误提示
- 集成问卷辅助工具