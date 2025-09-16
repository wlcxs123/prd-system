# 问卷数据管理系统 - 后端

这是问卷数据管理系统的后端服务，基于 Flask 框架开发。

## 功能特性

- 问卷数据收集和存储
- 用户认证和权限管理
- 数据验证和标准化
- RESTful API 接口
- 操作日志记录
- 批量操作支持

## 技术栈

- **框架**: Flask
- **数据库**: SQLite
- **认证**: bcrypt + Flask Session
- **数据验证**: Marshmallow
- **跨域支持**: Flask-CORS

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 初始化数据库

```bash
python init_db.py
```

这将创建必要的数据库表并创建默认管理员用户：
- 用户名: `admin`
- 密码: `admin123`

### 3. 启动服务器

```bash
python run.py
```

或者直接运行：

```bash
python app.py
```

服务器将在 `http://localhost:5000` 启动。

## 部署到云服务器

### 自动部署

项目根目录提供了自动部署脚本 `deploy_remote.py`，可以一键部署到云服务器：

```bash
# 1. 回到项目根目录
cd ..

# 2. 安装部署依赖
pip install -r deploy_requirements.txt

# 3. 执行部署
python deploy_remote.py
```

部署脚本会自动：
- 连接到云服务器 (115.190.103.114)
- 备份当前部署
- 上传最新代码
- 安装依赖并启动服务
- 进行健康检查

部署完成后可通过以下地址访问：
- 应用地址: http://115.190.103.114:8080
- 健康检查: http://115.190.103.114:8080/health

## 项目结构

```
backend/
├── app.py              # 主应用文件
├── config.py           # 配置文件
├── init_db.py          # 数据库初始化脚本
├── run.py              # 启动脚本
├── requirements.txt    # 依赖列表
├── questionnaires.db   # SQLite 数据库文件
├── static/             # 静态文件目录
├── templates/          # 模板文件目录
└── README.md           # 说明文档
```

## 数据库结构

### questionnaires 表
- `id`: 主键
- `type`: 问卷类型
- `name`: 填写人姓名
- `grade`: 年级
- `submission_date`: 填写日期
- `created_at`: 创建时间
- `updated_at`: 更新时间
- `data`: JSON格式的完整问卷数据

### users 表
- `id`: 主键
- `username`: 用户名
- `password_hash`: 密码哈希
- `role`: 用户角色
- `created_at`: 创建时间
- `last_login`: 最后登录时间

### operation_logs 表
- `id`: 主键
- `user_id`: 用户ID
- `operation`: 操作类型
- `target_id`: 操作目标ID
- `details`: 操作详情
- `created_at`: 操作时间

## API 接口

### 问卷数据接口

- `POST /api/submit` - 提交问卷数据
- `GET /api/questionnaires` - 获取问卷列表
- `GET /api/questionnaires/{id}` - 获取单个问卷详情
- `PUT /api/questionnaires/{id}` - 更新问卷数据
- `DELETE /api/questionnaires/{id}` - 删除问卷
- `DELETE /api/questionnaires/batch` - 批量删除问卷

### 管理接口

- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出
- `GET /api/auth/status` - 检查登录状态

## 环境变量

- `FLASK_ENV`: 运行环境 (development/production)
- `FLASK_HOST`: 服务器地址 (默认: 0.0.0.0)
- `FLASK_PORT`: 服务器端口 (默认: 5000)
- `SECRET_KEY`: Flask 密钥 (生产环境必须设置)

## 开发说明

### 数据验证

系统使用 `validate_questionnaire_data()` 函数验证提交的问卷数据：

```python
def validate_questionnaire_data(data):
    errors = []
    
    # 验证基本信息
    basic_info = data.get('basic_info', {})
    if not basic_info.get('name', '').strip():
        errors.append("姓名不能为空")
    
    # 验证问题答案
    questions = data.get('questions', [])
    for i, question in enumerate(questions):
        if question.get('type') == 'multiple_choice':
            if not question.get('selected'):
                errors.append(f"第{i + 1}题未选择答案")
    
    return errors
```

### 认证装饰器

使用装饰器保护需要认证的接口：

```python
@app.route('/api/admin/data')
@login_required
def get_admin_data():
    # 需要登录的接口
    pass

@app.route('/api/admin/settings')
@admin_required
def admin_settings():
    # 需要管理员权限的接口
    pass
```

### 操作日志

系统自动记录重要操作：

```python
log_operation('CREATE_QUESTIONNAIRE', questionnaire_id, '创建问卷')
log_operation('UPDATE_QUESTIONNAIRE', questionnaire_id, '更新问卷')
log_operation('DELETE_QUESTIONNAIRE', questionnaire_id, '删除问卷')
```

## 部署说明

### 开发环境

```bash
export FLASK_ENV=development
python run.py
```

### 生产环境

```bash
export FLASK_ENV=production
export SECRET_KEY=your-secret-key-here
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 故障排除

### 数据库问题

如果遇到数据库相关错误，可以重新初始化数据库：

```bash
rm questionnaires.db
python init_db.py
```

### 依赖问题

确保所有依赖都已正确安装：

```bash
pip install -r requirements.txt --upgrade
```

### 权限问题

确保应用有权限读写数据库文件和创建会话文件。

## 许可证

本项目仅供学习和研究使用。