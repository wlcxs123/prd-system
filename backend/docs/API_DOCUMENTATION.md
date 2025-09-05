# 问卷数据管理系统 API 接口文档

## 概述

本文档详细描述了问卷数据管理系统的所有 API 接口，包括请求格式、响应格式、错误处理和使用示例。

### 基本信息

- **基础 URL**: `http://your-domain.com/api`
- **API 版本**: v1.0
- **数据格式**: JSON
- **字符编码**: UTF-8
- **认证方式**: Session-based Authentication

### 通用响应格式

所有 API 接口都遵循统一的响应格式：

```json
{
    "success": true,
    "data": {},
    "message": "操作成功",
    "timestamp": "2024-01-15T10:30:00Z"
}
```

错误响应格式：

```json
{
    "success": false,
    "error": {
        "code": "ERROR_CODE",
        "message": "错误描述",
        "details": ["详细错误信息"]
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

## 认证接口

### 用户登录

**接口地址**: `POST /auth/login`

**描述**: 用户登录系统，获取会话权限

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
    "message": "登录成功",
    "user": {
        "id": 1,
        "username": "admin",
        "role": "admin"
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

**错误响应**:
```json
{
    "success": false,
    "error": {
        "code": "AUTH_FAILED",
        "message": "用户名或密码错误"
    }
}
```

### 用户登出

**接口地址**: `POST /auth/logout`

**描述**: 用户登出系统，清除会话

**请求参数**: 无

**响应示例**:
```json
{
    "success": true,
    "message": "登出成功",
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### 检查登录状态

**接口地址**: `GET /auth/status`

**描述**: 检查当前用户的登录状态

**请求参数**: 无

**响应示例**:
```json
{
    "success": true,
    "authenticated": true,
    "user": {
        "id": 1,
        "username": "admin",
        "role": "admin"
    },
    "session_info": {
        "remaining_time": 3600,
        "last_activity": "2024-01-15T10:30:00Z",
        "expires_at": "2024-01-15T11:30:00Z"
    }
}
```

### 刷新会话

**接口地址**: `POST /auth/refresh`

**描述**: 刷新用户会话，延长有效期

**权限要求**: 需要登录

**请求参数**: 无

**响应示例**:
```json
{
    "success": true,
    "message": "会话已刷新",
    "session_info": {
        "remaining_time": 7200,
        "last_activity": "2024-01-15T10:30:00Z",
        "expires_at": "2024-01-15T12:30:00Z"
    }
}
```

## 问卷数据接口

### 提交问卷数据

**接口地址**: `POST /questionnaires`

**描述**: 提交新的问卷数据

**请求参数**:
```json
{
    "type": "小学生交流评定表",
    "basic_info": {
        "name": "张三",
        "grade": "三年级",
        "submission_date": "2024-01-15"
    },
    "questions": [
        {
            "id": 1,
            "type": "multiple_choice",
            "question": "你喜欢和同学交流吗？",
            "options": [
                {"value": 0, "text": "非常喜欢"},
                {"value": 1, "text": "比较喜欢"},
                {"value": 2, "text": "一般"},
                {"value": 3, "text": "不太喜欢"}
            ],
            "selected": [0],
            "can_speak": true
        },
        {
            "id": 2,
            "type": "text_input",
            "question": "请描述你最喜欢的交流方式",
            "answer": "面对面交流"
        }
    ],
    "statistics": {
        "total_score": 85,
        "completion_rate": 100
    }
}
```

**响应示例**:
```json
{
    "success": true,
    "id": 123,
    "message": "问卷提交成功",
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### 获取问卷列表

**接口地址**: `GET /questionnaires`

**描述**: 获取问卷数据列表，支持分页和筛选

**权限要求**: 需要登录

**请求参数**:
- `page` (int, 可选): 页码，默认为 1
- `limit` (int, 可选): 每页数量，默认为 20，最大 100
- `search` (string, 可选): 搜索关键词
- `type` (string, 可选): 问卷类型筛选
- `grade` (string, 可选): 年级筛选
- `date_from` (string, 可选): 开始日期 (YYYY-MM-DD)
- `date_to` (string, 可选): 结束日期 (YYYY-MM-DD)
- `sort_by` (string, 可选): 排序字段，默认为 created_at
- `sort_order` (string, 可选): 排序方向，asc 或 desc，默认为 desc

**请求示例**:
```
GET /questionnaires?page=1&limit=20&search=张三&type=小学生交流评定表&sort_by=created_at&sort_order=desc
```

**响应示例**:
```json
{
    "success": true,
    "data": [
        {
            "id": 123,
            "type": "小学生交流评定表",
            "name": "张三",
            "grade": "三年级",
            "submission_date": "2024-01-15",
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z",
            "data": {
                // 完整的问卷数据
            }
        }
    ],
    "pagination": {
        "page": 1,
        "limit": 20,
        "total": 150,
        "pages": 8,
        "has_next": true,
        "has_prev": false
    },
    "filters": {
        "search": "张三",
        "type": "小学生交流评定表",
        "grade": "",
        "date_from": "",
        "date_to": "",
        "sort_by": "created_at",
        "sort_order": "desc"
    }
}
```

### 获取单个问卷详情

**接口地址**: `GET /questionnaires/{id}`

**描述**: 获取指定 ID 的问卷详细信息

**权限要求**: 需要登录

**路径参数**:
- `id` (int): 问卷 ID

**响应示例**:
```json
{
    "success": true,
    "data": {
        "id": 123,
        "type": "小学生交流评定表",
        "name": "张三",
        "grade": "三年级",
        "submission_date": "2024-01-15",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z",
        "data": {
            "type": "小学生交流评定表",
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
            }
        }
    }
}
```

### 更新问卷数据

**接口地址**: `PUT /questionnaires/{id}`

**描述**: 更新指定 ID 的问卷数据

**权限要求**: 需要管理员权限

**路径参数**:
- `id` (int): 问卷 ID

**请求参数**: 与提交问卷数据相同的格式

**响应示例**:
```json
{
    "success": true,
    "message": "问卷更新成功",
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### 删除问卷

**接口地址**: `DELETE /questionnaires/{id}`

**描述**: 删除指定 ID 的问卷

**权限要求**: 需要管理员权限

**路径参数**:
- `id` (int): 问卷 ID

**响应示例**:
```json
{
    "success": true,
    "message": "问卷删除成功",
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### 批量删除问卷

**接口地址**: `DELETE /questionnaires/batch`

**描述**: 批量删除多个问卷

**权限要求**: 需要管理员权限

**请求参数**:
```json
{
    "ids": [123, 124, 125, 126]
}
```

**响应示例**:
```json
{
    "success": true,
    "message": "批量删除完成",
    "deleted_count": 4,
    "failed_count": 0,
    "failed_ids": [],
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### 获取筛选选项

**接口地址**: `GET /questionnaires/filters`

**描述**: 获取可用的筛选选项

**权限要求**: 需要登录

**响应示例**:
```json
{
    "success": true,
    "data": {
        "types": [
            "小学生交流评定表",
            "家长访谈表",
            "青少年访谈表格"
        ],
        "grades": [
            "一年级",
            "二年级",
            "三年级",
            "四年级",
            "五年级",
            "六年级"
        ],
        "date_range": {
            "min": "2024-01-01",
            "max": "2024-01-15"
        },
        "sort_options": [
            {"value": "id", "text": "ID"},
            {"value": "name", "text": "姓名"},
            {"value": "type", "text": "类型"},
            {"value": "grade", "text": "年级"},
            {"value": "created_at", "text": "创建时间"},
            {"value": "submission_date", "text": "提交日期"}
        ]
    }
}
```

## 数据导出接口

### 导出单个问卷

**接口地址**: `GET /questionnaires/{id}/export`

**描述**: 导出指定问卷的数据

**权限要求**: 需要登录

**路径参数**:
- `id` (int): 问卷 ID

**查询参数**:
- `format` (string): 导出格式，支持 csv、excel、pdf

**响应**: 直接返回文件下载

### 批量导出问卷

**接口地址**: `POST /admin/export`

**描述**: 批量导出问卷数据

**权限要求**: 需要管理员权限

**请求参数**:
```json
{
    "format": "excel",
    "ids": [123, 124, 125],
    "include_fields": ["basic_info", "questions", "statistics"],
    "filename": "questionnaires_export"
}
```

**响应**: 直接返回文件下载

## 管理员接口

### 获取系统统计

**接口地址**: `GET /admin/statistics`

**描述**: 获取系统统计信息

**权限要求**: 需要管理员权限

**响应示例**:
```json
{
    "success": true,
    "data": {
        "total_questionnaires": 1500,
        "today_submissions": 25,
        "week_submissions": 180,
        "month_submissions": 750,
        "questionnaire_types": {
            "小学生交流评定表": 800,
            "家长访谈表": 400,
            "青少年访谈表格": 300
        },
        "grade_distribution": {
            "一年级": 200,
            "二年级": 250,
            "三年级": 300,
            "四年级": 280,
            "五年级": 270,
            "六年级": 200
        },
        "submission_trend": [
            {"date": "2024-01-01", "count": 15},
            {"date": "2024-01-02", "count": 20},
            // ... 更多数据
        ]
    }
}
```

### 获取操作日志

**接口地址**: `GET /admin/logs`

**描述**: 获取系统操作日志

**权限要求**: 需要管理员权限

**查询参数**:
- `page` (int, 可选): 页码，默认为 1
- `limit` (int, 可选): 每页数量，默认为 50
- `user_id` (int, 可选): 用户 ID 筛选
- `operation` (string, 可选): 操作类型筛选
- `date_from` (string, 可选): 开始日期
- `date_to` (string, 可选): 结束日期

**响应示例**:
```json
{
    "success": true,
    "data": [
        {
            "id": 1001,
            "user_id": 1,
            "username": "admin",
            "operation": "DELETE_QUESTIONNAIRE",
            "target_id": 123,
            "details": "删除问卷: 张三 - 小学生交流评定表",
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0...",
            "created_at": "2024-01-15T10:30:00Z"
        }
    ],
    "pagination": {
        "page": 1,
        "limit": 50,
        "total": 2500,
        "pages": 50,
        "has_next": true,
        "has_prev": false
    }
}
```

### 获取系统状态

**接口地址**: `GET /admin/system/status`

**描述**: 获取系统运行状态和监控信息

**权限要求**: 需要管理员权限

**响应示例**:
```json
{
    "success": true,
    "data": {
        "system_info": {
            "platform": "linux",
            "python_version": "3.9.7",
            "pid": 12345,
            "working_directory": "/opt/questionnaire-system",
            "start_time": "2024-01-15T08:00:00Z",
            "uptime_seconds": 9000
        },
        "app_config": {
            "debug": false,
            "testing": false,
            "database_path": "/var/lib/questionnaire-system/questionnaires.db",
            "session_timeout": "2:00:00"
        },
        "database_stats": {
            "file_size": 10485760,
            "tables": {
                "questionnaires": {
                    "count": 1500,
                    "latest_record": "2024-01-15T10:30:00Z"
                },
                "users": {
                    "count": 5
                },
                "operation_logs": {
                    "count": 2500,
                    "latest_record": "2024-01-15T10:30:00Z"
                }
            }
        },
        "recent_errors": [
            "2024-01-15 10:25:00 - ERROR - Database connection timeout",
            "2024-01-15 09:15:00 - WARNING - High memory usage detected"
        ],
        "alerts": [
            {
                "type": "high_memory",
                "message": "内存使用率较高: 85%",
                "severity": "warning",
                "timestamp": "2024-01-15T10:20:00Z"
            }
        ]
    }
}
```

## 健康检查接口

### 系统健康检查

**接口地址**: `GET /health`

**描述**: 检查系统健康状态，用于负载均衡器和监控系统

**权限要求**: 无

**响应示例**:
```json
{
    "status": "healthy",
    "timestamp": "2024-01-15T10:30:00Z",
    "uptime": 9000,
    "checks": {
        "database": {
            "healthy": true,
            "records_count": 1500,
            "database_size": 10485760,
            "response_time": 0.05
        },
        "disk": {
            "healthy": true,
            "status": "ok",
            "free_space": 50000000000,
            "total_space": 100000000000,
            "free_percent": 50.0
        },
        "memory": {
            "healthy": true,
            "status": "ok",
            "used_percent": 65.5,
            "available": 2147483648,
            "total": 4294967296
        }
    }
}
```

### 系统指标

**接口地址**: `GET /metrics`

**描述**: 获取详细的系统性能指标

**权限要求**: 无

**响应示例**:
```json
{
    "timestamp": "2024-01-15T10:30:00Z",
    "uptime": 9000,
    "cpu": {
        "percent": 25.5,
        "count": 4
    },
    "memory": {
        "total": 4294967296,
        "available": 2147483648,
        "percent": 65.5,
        "used": 2147483648
    },
    "disk": {
        "total": 100000000000,
        "used": 50000000000,
        "free": 50000000000,
        "percent": 50.0
    },
    "network": {
        "bytes_sent": 1048576000,
        "bytes_recv": 2097152000,
        "packets_sent": 1000000,
        "packets_recv": 1500000
    },
    "process": {
        "pid": 12345,
        "cpu_percent": 15.2,
        "memory_percent": 8.5,
        "memory_info": {
            "rss": 134217728,
            "vms": 268435456
        },
        "num_threads": 8,
        "create_time": 1705305600.0
    }
}
```

## 错误代码

### HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权访问 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 409 | 资源冲突 |
| 422 | 数据验证失败 |
| 500 | 服务器内部错误 |
| 503 | 服务不可用 |

### 业务错误代码

| 错误代码 | 说明 |
|----------|------|
| AUTH_REQUIRED | 需要登录 |
| AUTH_FAILED | 认证失败 |
| PERMISSION_DENIED | 权限不足 |
| SESSION_EXPIRED | 会话过期 |
| SESSION_INVALID | 会话无效 |
| VALIDATION_ERROR | 数据验证失败 |
| NOT_FOUND | 资源不存在 |
| DUPLICATE_RESOURCE | 资源重复 |
| SERVER_ERROR | 服务器错误 |
| DATABASE_ERROR | 数据库错误 |
| FILE_ERROR | 文件操作错误 |

## 使用示例

### JavaScript 示例

```javascript
// 登录
async function login(username, password) {
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
            credentials: 'include' // 包含 cookies
        });
        
        const result = await response.json();
        
        if (result.success) {
            console.log('登录成功:', result.user);
            return result.user;
        } else {
            console.error('登录失败:', result.error.message);
            throw new Error(result.error.message);
        }
    } catch (error) {
        console.error('请求失败:', error);
        throw error;
    }
}

// 获取问卷列表
async function getQuestionnaires(page = 1, limit = 20, search = '') {
    try {
        const params = new URLSearchParams({
            page: page.toString(),
            limit: limit.toString(),
            search: search
        });
        
        const response = await fetch(`/api/questionnaires?${params}`, {
            credentials: 'include'
        });
        
        const result = await response.json();
        
        if (result.success) {
            return result.data;
        } else {
            throw new Error(result.error.message);
        }
    } catch (error) {
        console.error('获取问卷列表失败:', error);
        throw error;
    }
}

// 提交问卷数据
async function submitQuestionnaire(questionnaireData) {
    try {
        const response = await fetch('/api/questionnaires', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(questionnaireData),
            credentials: 'include'
        });
        
        const result = await response.json();
        
        if (result.success) {
            console.log('问卷提交成功，ID:', result.id);
            return result.id;
        } else {
            throw new Error(result.error.message);
        }
    } catch (error) {
        console.error('问卷提交失败:', error);
        throw error;
    }
}

// 删除问卷
async function deleteQuestionnaire(id) {
    try {
        const response = await fetch(`/api/questionnaires/${id}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        
        const result = await response.json();
        
        if (result.success) {
            console.log('问卷删除成功');
            return true;
        } else {
            throw new Error(result.error.message);
        }
    } catch (error) {
        console.error('问卷删除失败:', error);
        throw error;
    }
}

// 批量删除问卷
async function batchDeleteQuestionnaires(ids) {
    try {
        const response = await fetch('/api/questionnaires/batch', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ ids }),
            credentials: 'include'
        });
        
        const result = await response.json();
        
        if (result.success) {
            console.log(`批量删除完成，成功删除 ${result.deleted_count} 个问卷`);
            return result;
        } else {
            throw new Error(result.error.message);
        }
    } catch (error) {
        console.error('批量删除失败:', error);
        throw error;
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
        data = {
            "username": username,
            "password": password
        }
        
        response = self.session.post(url, json=data)
        result = response.json()
        
        if result['success']:
            print(f"登录成功: {result['user']['username']}")
            return result['user']
        else:
            raise Exception(f"登录失败: {result['error']['message']}")
    
    def get_questionnaires(self, page=1, limit=20, search=''):
        """获取问卷列表"""
        url = f"{self.base_url}/questionnaires"
        params = {
            'page': page,
            'limit': limit,
            'search': search
        }
        
        response = self.session.get(url, params=params)
        result = response.json()
        
        if result['success']:
            return result['data'], result['pagination']
        else:
            raise Exception(f"获取问卷列表失败: {result['error']['message']}")
    
    def submit_questionnaire(self, questionnaire_data):
        """提交问卷数据"""
        url = f"{self.base_url}/questionnaires"
        
        response = self.session.post(url, json=questionnaire_data)
        result = response.json()
        
        if result['success']:
            print(f"问卷提交成功，ID: {result['id']}")
            return result['id']
        else:
            raise Exception(f"问卷提交失败: {result['error']['message']}")
    
    def delete_questionnaire(self, questionnaire_id):
        """删除问卷"""
        url = f"{self.base_url}/questionnaires/{questionnaire_id}"
        
        response = self.session.delete(url)
        result = response.json()
        
        if result['success']:
            print("问卷删除成功")
            return True
        else:
            raise Exception(f"问卷删除失败: {result['error']['message']}")
    
    def batch_delete_questionnaires(self, ids):
        """批量删除问卷"""
        url = f"{self.base_url}/questionnaires/batch"
        data = {"ids": ids}
        
        response = self.session.delete(url, json=data)
        result = response.json()
        
        if result['success']:
            print(f"批量删除完成，成功删除 {result['deleted_count']} 个问卷")
            return result
        else:
            raise Exception(f"批量删除失败: {result['error']['message']}")

# 使用示例
if __name__ == "__main__":
    api = QuestionnaireAPI("http://localhost:5000/api")
    
    # 登录
    user = api.login("admin", "password123")
    
    # 获取问卷列表
    questionnaires, pagination = api.get_questionnaires(page=1, limit=10)
    print(f"获取到 {len(questionnaires)} 个问卷")
    
    # 提交问卷数据
    questionnaire_data = {
        "type": "测试问卷",
        "basic_info": {
            "name": "测试用户",
            "grade": "三年级",
            "submission_date": "2024-01-15"
        },
        "questions": [
            {
                "id": 1,
                "type": "multiple_choice",
                "question": "测试问题",
                "options": [
                    {"value": 0, "text": "选项A"},
                    {"value": 1, "text": "选项B"}
                ],
                "selected": [0]
            }
        ]
    }
    
    questionnaire_id = api.submit_questionnaire(questionnaire_data)
    
    # 删除问卷
    api.delete_questionnaire(questionnaire_id)
```

## 版本更新

### v1.0 (2024-01-15)
- 初始版本发布
- 实现基本的 CRUD 操作
- 支持用户认证和权限管理
- 提供数据导出功能
- 实现系统监控接口

### 后续版本计划
- v1.1: 增加更多导出格式支持
- v1.2: 实现 WebSocket 实时通知
- v1.3: 添加 API 限流功能
- v2.0: 支持多租户架构

---

**注意事项**:
1. 所有需要认证的接口都需要先调用登录接口获取会话
2. 请求和响应都使用 UTF-8 编码
3. 时间格式统一使用 ISO 8601 标准
4. 文件上传限制为 16MB
5. API 调用频率限制为每分钟 1000 次

如有疑问或需要技术支持，请联系开发团队。