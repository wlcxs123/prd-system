# 问卷数据管理系统设计文档

## 概述

本设计文档基于问卷数据管理系统的需求，提供了完整的技术实现方案。系统采用前后端分离架构，支持多种问题类型，提供安全的用户认证和完善的数据管理功能。

## 架构

### 系统架构图

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端问卷页面   │    │   管理后台界面   │    │   登录认证页面   │
│   (HTML/JS)     │    │   (HTML/JS)     │    │   (HTML/JS)     │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │      Flask 后端服务       │
                    │   - API 路由处理          │
                    │   - 数据验证             │
                    │   - 会话管理             │
                    │   - 权限控制             │
                    └─────────────┬─────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │      SQLite 数据库        │
                    │   - 问卷数据表           │
                    │   - 用户认证表           │
                    │   - 系统日志表           │
                    └───────────────────────────┘
```

### 技术栈

- **前端**: HTML5, CSS3, JavaScript (ES6+)
- **后端**: Python Flask
- **数据库**: SQLite (可扩展为 PostgreSQL/MySQL)
- **认证**: Flask-Session + 密码哈希
- **API**: RESTful API 设计
- **部署**: 本地开发环境，支持容器化部署

## 组件和接口

### 1. 数据模型设计

#### 1.1 问卷数据表 (questionnaires)

```sql
CREATE TABLE questionnaires (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,                    -- 问卷类型
    name TEXT,                            -- 填写人姓名
    grade TEXT,                           -- 年级
    submission_date DATE,                 -- 填写日期
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data TEXT NOT NULL                    -- JSON格式的完整问卷数据
);
```

#### 1.2 用户认证表 (users)

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'admin',            -- 用户角色
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

#### 1.3 操作日志表 (operation_logs)

```sql
CREATE TABLE operation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    operation TEXT NOT NULL,              -- 操作类型
    target_id INTEGER,                    -- 操作目标ID
    details TEXT,                         -- 操作详情
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

### 2. 标准化数据结构

#### 2.1 问卷提交数据格式

```json
{
    "type": "questionnaire_type",
    "basic_info": {
        "name": "学生姓名",
        "grade": "年级",
        "submission_date": "2024-01-15"
    },
    "questions": [
        {
            "id": 1,
            "type": "multiple_choice",
            "question": "问题文本",
            "options": [
                {"value": 0, "text": "选项A"},
                {"value": 1, "text": "选项B"}
            ],
            "selected": [0],
            "can_speak": true
        },
        {
            "id": 2,
            "type": "text_input",
            "question": "填空题问题",
            "answer": "用户填写的答案"
        }
    ],
    "statistics": {
        "total_score": 85,
        "completion_rate": 100,
        "submission_time": "2024-01-15T10:30:00Z"
    }
}
```

### 3. API 接口设计

#### 3.1 认证相关接口

```python
# 登录
POST /api/auth/login
{
    "username": "admin",
    "password": "password"
}

# 登出
POST /api/auth/logout

# 检查登录状态
GET /api/auth/status
```

#### 3.2 问卷数据接口

```python
# 提交问卷数据
POST /api/questionnaires
Content-Type: application/json
{
    "type": "questionnaire_type",
    "basic_info": {...},
    "questions": [...],
    "statistics": {...}
}

# 获取问卷列表
GET /api/questionnaires?page=1&limit=20&search=keyword

# 获取单个问卷详情
GET /api/questionnaires/{id}

# 更新问卷数据
PUT /api/questionnaires/{id}

# 删除问卷
DELETE /api/questionnaires/{id}

# 批量删除问卷
DELETE /api/questionnaires/batch
{
    "ids": [1, 2, 3, 4, 5]
}
```

#### 3.3 管理功能接口

```python
# 获取统计数据
GET /api/admin/statistics

# 导出数据
GET /api/admin/export?format=csv&ids=1,2,3

# 获取操作日志
GET /api/admin/logs?page=1&limit=50
```

## 数据验证策略

### 1. 前端验证

```javascript
// 数据结构验证函数
function validateQuestionnaireData(data) {
    const errors = [];
    
    // 验证基本信息
    if (!data.basic_info?.name?.trim()) {
        errors.push("姓名不能为空");
    }
    
    if (!data.basic_info?.grade?.trim()) {
        errors.push("年级不能为空");
    }
    
    // 验证问题答案
    data.questions?.forEach((question, index) => {
        if (question.type === 'multiple_choice') {
            if (!question.selected || question.selected.length === 0) {
                errors.push(`第${index + 1}题未选择答案`);
            }
        } else if (question.type === 'text_input') {
            if (!question.answer?.trim()) {
                errors.push(`第${index + 1}题答案不能为空`);
            }
        }
    });
    
    return errors;
}
```

### 2. 后端验证

```python
from marshmallow import Schema, fields, validate, ValidationError

class BasicInfoSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    grade = fields.Str(required=True, validate=validate.Length(min=1, max=20))
    submission_date = fields.Date(required=True)

class QuestionSchema(Schema):
    id = fields.Int(required=True)
    type = fields.Str(required=True, validate=validate.OneOf(['multiple_choice', 'text_input']))
    question = fields.Str(required=True, validate=validate.Length(min=1, max=500))
    
class QuestionnaireSchema(Schema):
    type = fields.Str(required=True)
    basic_info = fields.Nested(BasicInfoSchema, required=True)
    questions = fields.List(fields.Nested(QuestionSchema), required=True)
```

## 用户界面设计

### 1. 登录页面 (login.html)

```html
<!DOCTYPE html>
<html>
<head>
    <title>问卷管理系统 - 登录</title>
    <link rel="stylesheet" href="static/css/login.css">
</head>
<body>
    <div class="login-container">
        <div class="login-form">
            <h2>问卷管理系统</h2>
            <form id="loginForm">
                <div class="form-group">
                    <input type="text" id="username" placeholder="用户名" required>
                </div>
                <div class="form-group">
                    <input type="password" id="password" placeholder="密码" required>
                </div>
                <button type="submit">登录</button>
            </form>
        </div>
    </div>
</body>
</html>
```

### 2. 管理后台主页面 (admin.html)

```html
<!DOCTYPE html>
<html>
<head>
    <title>问卷管理系统</title>
    <link rel="stylesheet" href="static/css/admin.css">
</head>
<body>
    <div class="admin-container">
        <!-- 导航栏 -->
        <nav class="navbar">
            <div class="nav-brand">问卷管理系统</div>
            <div class="nav-menu">
                <a href="#dashboard">仪表板</a>
                <a href="#questionnaires">问卷管理</a>
                <a href="#logs">操作日志</a>
                <a href="#" onclick="logout()">退出</a>
            </div>
        </nav>
        
        <!-- 主内容区域 -->
        <main class="main-content">
            <!-- 统计卡片 -->
            <div class="stats-cards">
                <div class="stat-card">
                    <h3>总问卷数</h3>
                    <div class="stat-number" id="totalCount">0</div>
                </div>
                <div class="stat-card">
                    <h3>今日新增</h3>
                    <div class="stat-number" id="todayCount">0</div>
                </div>
            </div>
            
            <!-- 问卷列表 -->
            <div class="questionnaire-section">
                <div class="section-header">
                    <h2>问卷列表</h2>
                    <div class="toolbar">
                        <input type="text" id="searchInput" placeholder="搜索问卷...">
                        <button onclick="searchQuestionnaires()">搜索</button>
                        <button onclick="deleteSelected()" class="danger">批量删除</button>
                    </div>
                </div>
                
                <table class="questionnaire-table">
                    <thead>
                        <tr>
                            <th><input type="checkbox" id="selectAll"></th>
                            <th>ID</th>
                            <th>姓名</th>
                            <th>年级</th>
                            <th>提交时间</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody id="questionnaireList">
                        <!-- 动态加载数据 -->
                    </tbody>
                </table>
                
                <!-- 分页 -->
                <div class="pagination" id="pagination">
                    <!-- 动态生成分页按钮 -->
                </div>
            </div>
        </main>
    </div>
</body>
</html>
```

## 错误处理

### 1. API 错误响应格式

```json
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "数据验证失败",
        "details": [
            "姓名不能为空",
            "第3题未选择答案"
        ]
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### 2. 错误处理策略

```python
@app.errorhandler(ValidationError)
def handle_validation_error(e):
    return jsonify({
        'success': False,
        'error': {
            'code': 'VALIDATION_ERROR',
            'message': '数据验证失败',
            'details': e.messages
        },
        'timestamp': datetime.utcnow().isoformat()
    }), 400

@app.errorhandler(404)
def handle_not_found(e):
    return jsonify({
        'success': False,
        'error': {
            'code': 'NOT_FOUND',
            'message': '请求的资源不存在'
        }
    }), 404
```

## 安全考虑

### 1. 认证和授权

- 使用 Flask-Session 管理用户会话
- 密码使用 bcrypt 进行哈希存储
- 实现会话超时机制
- 所有管理接口需要登录验证

### 2. 数据安全

- SQL 注入防护（使用参数化查询）
- XSS 防护（输入输出过滤）
- CSRF 防护（使用 CSRF Token）
- 敏感操作需要二次确认

### 3. 访问控制

```python
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': '需要登录'}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_role') == 'admin':
            return jsonify({'error': '权限不足'}), 403
        return f(*args, **kwargs)
    return decorated_function
```

## 测试策略

### 1. 单元测试

- 数据验证函数测试
- API 接口测试
- 数据库操作测试

### 2. 集成测试

- 完整的问卷提交流程测试
- 用户登录认证流程测试
- 批量操作功能测试

### 3. 前端测试

- 表单验证测试
- AJAX 请求测试
- 用户交互测试

## 部署和运维

### 1. 开发环境

```bash
# 安装依赖
pip install flask flask-session bcrypt marshmallow

# 初始化数据库
python init_db.py

# 启动开发服务器
python app.py
```

### 2. 生产环境考虑

- 使用 Gunicorn 作为 WSGI 服务器
- 配置 Nginx 作为反向代理
- 数据库迁移到 PostgreSQL
- 实现日志轮转和监控
- 配置自动备份策略

### 3. 监控和维护

- 实现健康检查接口
- 配置错误日志收集
- 设置性能监控指标
- 定期数据备份验证