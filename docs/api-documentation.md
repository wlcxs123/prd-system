# 问卷数据管理系统 API 接口文档

## 概述

本文档描述了问卷数据管理系统的 RESTful API 接口。所有 API 接口都遵循统一的请求和响应格式，支持 JSON 数据交换。

## 基础信息

- **Base URL**: `http://localhost:5000/api`
- **Content-Type**: `application/json`
- **字符编码**: UTF-8
- **API 版本**: v1.0

## 认证机制

系统使用基于 Session 的认证机制。除了登录接口外，所有其他接口都需要先登录获取有效会话。

### 认证流程
1. 调用登录接口获取会话
2. 后续请求会自动携带会话信息
3. 会话过期后需要重新登录

## 通用响应格式

### 成功响应
```json
{
    "success": true,
    "data": {
        // 具体的响应数据
    },
    "message": "操作成功",
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### 错误响应
```json
{
    "success": false,
    "error": {
        "code": "ERROR_CODE",
        "message": "错误描述",
        "details": [
            "具体错误信息1",
            "具体错误信息2"
        ]
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

## 错误代码

| 错误代码 | HTTP状态码 | 描述 |
|---------|-----------|------|
| VALIDATION_ERROR | 400 | 数据验证失败 |
| UNAUTHORIZED | 401 | 未登录或会话过期 |
| FORBIDDEN | 403 | 权限不足 |
| NOT_FOUND | 404 | 资源不存在 |
| CONFLICT | 409 | 数据冲突 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |

## API 接口详情

### 1. 认证接口

#### 1.1 用户登录

**接口地址**: `POST /auth/login`

**请求参数**:
```json
{
    "username": "admin",
    "password": "password123"
}
```

**响应示例**:
```json
{
    "success": true,
    "data": {
        "user_id": 1,
        "username": "admin",
        "role": "admin",
        "last_login": "2024-01-15T10:30:00Z"
    },
    "message": "登录成功"
}
```

#### 1.2 用户登出

**接口地址**: `POST /auth/logout`

**请求参数**: 无

**响应示例**:
```json
{
    "success": true,
    "message": "登出成功"
}
```

#### 1.3 检查登录状态

**接口地址**: `GET /auth/status`

**请求参数**: 无

**响应示例**:
```json
{
    "success": true,
    "data": {
        "logged_in": true,
        "user_id": 1,
        "username": "admin",
        "role": "admin"
    }
}
```

### 2. 问卷数据接口

#### 2.1 提交问卷数据

**接口地址**: `POST /questionnaires`

**请求参数**:
```json
{
    "type": "primary_communication_scale",
    "basic_info": {
        "name": "张三",
        "grade": "三年级",
        "submission_date": "2024-01-15"
    },
    "questions": [
        {
            "id": 1,
            "type": "multiple_choice",
            "question": "你在学校里会主动和老师说话吗？",
            "options": [
                {"value": 0, "text": "从不"},
                {"value": 1, "text": "很少"},
                {"value": 2, "text": "有时"},
                {"value": 3, "text": "经常"}
            ],
            "selected": [2],
            "can_speak": true
        },
        {
            "id": 2,
            "type": "text_input",
            "question": "请描述你最喜欢的活动",
            "answer": "我喜欢画画和读书"
        }
    ],
    "statistics": {
        "total_score": 85,
        "completion_rate": 100,
        "submission_time": "2024-01-15T10:30:00Z"
    }
}
```

**响应示例**:
```json
{
    "success": true,
    "data": {
        "id": 123,
        "message": "问卷提交成功"
    }
}
```

#### 2.2 获取问卷列表

**接口地址**: `GET /questionnaires`

**查询参数**:
- `page`: 页码（默认: 1）
- `limit`: 每页数量（默认: 20）
- `search`: 搜索关键词
- `type`: 问卷类型筛选
- `start_date`: 开始日期
- `end_date`: 结束日期

**请求示例**:
```
GET /questionnaires?page=1&limit=10&search=张三&type=primary_communication_scale
```

**响应示例**:
```json
{
    "success": true,
    "data": {
        "questionnaires": [
            {
                "id": 123,
                "type": "primary_communication_scale",
                "name": "张三",
                "grade": "三年级",
                "submission_date": "2024-01-15",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        ],
        "pagination": {
            "current_page": 1,
            "total_pages": 5,
            "total_count": 100,
            "per_page": 20
        }
    }
}
```

#### 2.3 获取单个问卷详情

**接口地址**: `GET /questionnaires/{id}`

**路径参数**:
- `id`: 问卷ID

**响应示例**:
```json
{
    "success": true,
    "data": {
        "id": 123,
        "type": "primary_communication_scale",
        "basic_info": {
            "name": "张三",
            "grade": "三年级",
            "submission_date": "2024-01-15"
        },
        "questions": [
            // 完整的问题和答案数据
        ],
        "statistics": {
            "total_score": 85,
            "completion_rate": 100
        },
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
    }
}
```

#### 2.4 更新问卷数据

**接口地址**: `PUT /questionnaires/{id}`

**路径参数**:
- `id`: 问卷ID

**请求参数**: 与提交问卷数据相同的格式

**响应示例**:
```json
{
    "success": true,
    "data": {
        "id": 123,
        "message": "问卷更新成功"
    }
}
```

#### 2.5 删除问卷

**接口地址**: `DELETE /questionnaires/{id}`

**路径参数**:
- `id`: 问卷ID

**响应示例**:
```json
{
    "success": true,
    "message": "问卷删除成功"
}
```

#### 2.6 批量删除问卷

**接口地址**: `DELETE /questionnaires/batch`

**请求参数**:
```json
{
    "ids": [1, 2, 3, 4, 5]
}
```

**响应示例**:
```json
{
    "success": true,
    "data": {
        "deleted_count": 5,
        "failed_ids": []
    },
    "message": "批量删除成功"
}
```

### 3. 管理功能接口

#### 3.1 获取统计数据

**接口地址**: `GET /admin/statistics`

**响应示例**:
```json
{
    "success": true,
    "data": {
        "total_questionnaires": 1250,
        "today_count": 15,
        "week_count": 89,
        "month_count": 342,
        "type_distribution": {
            "primary_communication_scale": 450,
            "parent_interview": 380,
            "student_report": 420
        },
        "submission_trend": [
            {"date": "2024-01-01", "count": 12},
            {"date": "2024-01-02", "count": 18}
        ]
    }
}
```

#### 3.2 数据导出

**接口地址**: `GET /admin/export`

**查询参数**:
- `format`: 导出格式（csv, excel, pdf）
- `ids`: 要导出的问卷ID列表（逗号分隔）
- `start_date`: 开始日期
- `end_date`: 结束日期
- `type`: 问卷类型

**请求示例**:
```
GET /admin/export?format=excel&ids=1,2,3&type=primary_communication_scale
```

**响应示例**:
```json
{
    "success": true,
    "data": {
        "download_url": "/downloads/export_20240115_143022.xlsx",
        "filename": "questionnaire_export_20240115_143022.xlsx",
        "file_size": 2048576,
        "record_count": 100
    }
}
```

#### 3.3 获取操作日志

**接口地址**: `GET /admin/logs`

**查询参数**:
- `page`: 页码（默认: 1）
- `limit`: 每页数量（默认: 50）
- `operation`: 操作类型筛选
- `user_id`: 用户ID筛选
- `start_date`: 开始日期
- `end_date`: 结束日期

**响应示例**:
```json
{
    "success": true,
    "data": {
        "logs": [
            {
                "id": 1001,
                "user_id": 1,
                "username": "admin",
                "operation": "DELETE_QUESTIONNAIRE",
                "target_id": 123,
                "details": "删除问卷: 张三的小学生交流评定表",
                "created_at": "2024-01-15T10:30:00Z"
            }
        ],
        "pagination": {
            "current_page": 1,
            "total_pages": 10,
            "total_count": 500,
            "per_page": 50
        }
    }
}
```

### 4. 系统监控接口

#### 4.1 系统健康检查

**接口地址**: `GET /system/health`

**响应示例**:
```json
{
    "success": true,
    "data": {
        "status": "healthy",
        "database": {
            "status": "connected",
            "response_time": 15
        },
        "disk_space": {
            "total": "100GB",
            "used": "45GB",
            "available": "55GB",
            "usage_percent": 45
        },
        "memory": {
            "total": "8GB",
            "used": "3.2GB",
            "available": "4.8GB",
            "usage_percent": 40
        }
    }
}
```

#### 4.2 获取系统信息

**接口地址**: `GET /system/info`

**响应示例**:
```json
{
    "success": true,
    "data": {
        "version": "1.0.0",
        "build_date": "2024-01-15",
        "python_version": "3.9.7",
        "flask_version": "2.3.3",
        "database_version": "SQLite 3.39.4",
        "uptime": "5 days, 12 hours, 30 minutes"
    }
}
```

## 数据验证规则

### 问卷数据验证
- `type`: 必填，字符串类型
- `basic_info.name`: 必填，1-50个字符
- `basic_info.grade`: 必填，1-20个字符
- `basic_info.submission_date`: 必填，日期格式 YYYY-MM-DD
- `questions`: 必填，数组类型，至少包含一个问题
- `questions[].type`: 必填，枚举值：multiple_choice, text_input
- `questions[].question`: 必填，1-500个字符

### 选择题验证
- `options`: 必填，数组类型
- `selected`: 必填，数组类型，包含选中的选项索引

### 填空题验证
- `answer`: 必填，字符串类型，不能为空

## 使用示例

### JavaScript 示例

```javascript
// 登录
async function login(username, password) {
    const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    });
    
    const result = await response.json();
    if (result.success) {
        console.log('登录成功:', result.data);
    } else {
        console.error('登录失败:', result.error.message);
    }
}

// 提交问卷
async function submitQuestionnaire(data) {
    const response = await fetch('/api/questionnaires', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });
    
    const result = await response.json();
    if (result.success) {
        console.log('提交成功:', result.data);
    } else {
        console.error('提交失败:', result.error.message);
    }
}

// 获取问卷列表
async function getQuestionnaires(page = 1, limit = 20) {
    const response = await fetch(`/api/questionnaires?page=${page}&limit=${limit}`);
    const result = await response.json();
    
    if (result.success) {
        return result.data;
    } else {
        throw new Error(result.error.message);
    }
}
```

### Python 示例

```python
import requests
import json

class QuestionnaireAPI:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
    
    def login(self, username, password):
        """用户登录"""
        url = f"{self.base_url}/auth/login"
        data = {"username": username, "password": password}
        
        response = self.session.post(url, json=data)
        result = response.json()
        
        if result['success']:
            print("登录成功")
            return result['data']
        else:
            raise Exception(f"登录失败: {result['error']['message']}")
    
    def submit_questionnaire(self, questionnaire_data):
        """提交问卷"""
        url = f"{self.base_url}/questionnaires"
        
        response = self.session.post(url, json=questionnaire_data)
        result = response.json()
        
        if result['success']:
            return result['data']
        else:
            raise Exception(f"提交失败: {result['error']['message']}")
    
    def get_questionnaires(self, page=1, limit=20, **filters):
        """获取问卷列表"""
        url = f"{self.base_url}/questionnaires"
        params = {"page": page, "limit": limit, **filters}
        
        response = self.session.get(url, params=params)
        result = response.json()
        
        if result['success']:
            return result['data']
        else:
            raise Exception(f"获取失败: {result['error']['message']}")

# 使用示例
api = QuestionnaireAPI("http://localhost:5000/api")
api.login("admin", "password123")

# 提交问卷
questionnaire_data = {
    "type": "primary_communication_scale",
    "basic_info": {
        "name": "张三",
        "grade": "三年级",
        "submission_date": "2024-01-15"
    },
    "questions": [
        # 问题数据...
    ]
}

result = api.submit_questionnaire(questionnaire_data)
print(f"问卷ID: {result['id']}")
```

## 版本更新记录

### v1.0.0 (2024-01-15)
- 初始版本发布
- 实现基础的问卷数据管理功能
- 支持用户认证和权限控制
- 提供完整的 CRUD 接口

---

*本文档最后更新时间: 2024年1月15日*