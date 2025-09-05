# 问卷数据管理系统 - 本地手动测试指南

## 1. 环境准备

### 1.1 检查Python环境
```bash
# 检查Python版本（需要3.8+）
python --version

# 检查pip
pip --version
```

### 1.2 创建虚拟环境
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 1.3 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

### 1.4 初始化数据库
```bash
python init_db.py
```

## 2. 启动系统

### 2.1 启动后端服务
```bash
cd backend
python app.py
```

服务启动后会显示：
```
* Running on http://127.0.0.1:5000
* Debug mode: on
```

### 2.2 验证服务状态
在浏览器中访问：http://localhost:5000

应该看到系统首页或登录页面。

## 3. 功能测试

### 3.1 用户认证测试

#### 登录功能测试
1. 访问：http://localhost:5000/login
2. 使用默认管理员账户：
   - 用户名：`admin`
   - 密码：`admin123`
3. 点击登录，应该跳转到管理页面

#### API登录测试
使用curl或Postman测试：
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

预期响应：
```json
{
  "success": true,
  "message": "登录成功",
  "user": {
    "username": "admin",
    "role": "admin"
  }
}
```

### 3.2 问卷提交测试

#### 通过API提交问卷
```bash
curl -X POST http://localhost:5000/api/submit \
  -H "Content-Type: application/json" \
  -d '{
    "type": "test_questionnaire",
    "basic_info": {
      "name": "张三",
      "grade": "三年级",
      "submission_date": "2024-01-15"
    },
    "questions": [
      {
        "id": 1,
        "type": "multiple_choice",
        "question": "你喜欢什么颜色？",
        "options": [
          {"value": 0, "text": "红色"},
          {"value": 1, "text": "蓝色"}
        ],
        "selected": [1],
        "can_speak": true
      }
    ]
  }'
```

预期响应：
```json
{
  "success": true,
  "message": "问卷提交成功",
  "questionnaire_id": 1
}
```

#### 通过HTML页面提交
1. 访问问卷页面（如：Frankfurt Scale of Selective Mutism.html）
2. 点击"开始填写"
3. 填写基本信息：
   - 儿童姓名：测试儿童
   - 家长/监护人：测试家长
   - 日期：选择当前日期
4. 完成A部分（快速筛查）：
   - 至少回答5个问题
   - 选择"是"或"否"
5. 点击"下一步：B"
6. 完成B部分（说话情况评分）：
   - 在学校/公共/家庭三个场景中选择评分
   - 0=无问题，1=轻度限制，2=偶尔，3=几乎从不，4=完全不说
7. 点击"提交到系统"按钮
8. 检查提交结果：
   - 成功：显示"✅ 数据提交成功！问卷ID: xxx"
   - 失败：显示具体错误信息

### 3.3 数据查询测试

#### 获取问卷列表
需要先登录，然后：
```bash
curl -X GET http://localhost:5000/api/questionnaires \
  -H "Cookie: session=your_session_cookie"
```

或在浏览器中登录后访问：http://localhost:5000/admin

#### 查看单个问卷详情
```bash
curl -X GET http://localhost:5000/api/questionnaires/1 \
  -H "Cookie: session=your_session_cookie"
```

### 3.4 数据导出测试

在管理页面中：
1. 选择要导出的问卷
2. 选择导出格式（CSV、Excel、PDF）
3. 点击导出按钮
4. 检查下载的文件是否正确

## 4. 数据库测试

### 4.1 直接查看数据库
```bash
sqlite3 backend/questionnaires.db

# 查看所有表
.tables

# 查看问卷数据
SELECT * FROM questionnaires;

# 查看用户数据
SELECT * FROM users;

# 退出
.quit
```

### 4.2 数据完整性检查
```bash
cd backend
python -c "
import sqlite3
conn = sqlite3.connect('questionnaires.db')
cursor = conn.cursor()
cursor.execute('PRAGMA integrity_check')
print(cursor.fetchone()[0])
conn.close()
"
```

## 5. 错误处理测试

### 5.1 测试无效数据提交
```bash
curl -X POST http://localhost:5000/api/submit \
  -H "Content-Type: application/json" \
  -d '{
    "type": "test_questionnaire",
    "basic_info": {
      "name": "",
      "grade": "无效年级"
    },
    "questions": []
  }'
```

应该返回验证错误信息。

### 5.2 测试未授权访问
```bash
curl -X GET http://localhost:5000/api/questionnaires
```

应该返回401未授权错误。

### 5.3 测试不存在的资源
```bash
curl -X GET http://localhost:5000/api/questionnaires/999
```

应该返回404未找到错误。

## 6. 性能测试

### 6.1 批量数据提交测试
运行测试脚本：
```bash
cd backend
python test_api_simple.py
```

### 6.2 并发访问测试
可以使用Apache Bench (ab) 工具：
```bash
# 安装ab工具（如果没有）
# Ubuntu: sudo apt-get install apache2-utils
# Mac: brew install httpie

# 测试并发访问
ab -n 100 -c 10 http://localhost:5000/
```

## 7. 日志检查

### 7.1 查看应用日志
```bash
# 如果有日志文件
tail -f backend/logs/app.log

# 或查看控制台输出
```

### 7.2 查看错误日志
检查是否有Python异常或错误信息。

## 8. 浏览器测试

### 8.1 功能测试
1. 打开浏览器开发者工具（F12）
2. 访问各个页面
3. 检查Console是否有JavaScript错误
4. 检查Network标签页的请求响应

### 8.2 兼容性测试
在不同浏览器中测试：
- Chrome
- Firefox
- Safari
- Edge

### 8.3 响应式测试
测试不同屏幕尺寸下的显示效果。

## 9. 自动化测试脚本

### 9.1 运行现有测试
```bash
cd backend

# 运行简单API测试
python test_api_simple.py

# 运行登录测试
python test_login_simple.py

# 运行综合测试
python test_all_comprehensive.py
```

### 9.2 测试Frankfurt Scale提交功能
```bash
# 测试Frankfurt Scale问卷提交
python test_frankfurt_submit.py
```

### 9.3 创建自定义测试脚本
可以参考现有的测试文件创建自己的测试脚本。

## 10. 常见问题排查

### 10.1 服务无法启动
- 检查端口5000是否被占用
- 检查Python依赖是否完整安装
- 检查数据库文件是否存在

### 10.2 数据库错误
- 重新初始化数据库：`rm questionnaires.db && python init_db.py`
- 检查文件权限

### 10.3 前端页面错误
- 检查浏览器控制台错误信息
- 确认后端API正常响应
- 检查CORS配置

### 10.4 认证问题
- 确认用户名密码正确
- 检查会话配置
- 清除浏览器缓存和Cookie

## 11. 测试检查清单

### 基础功能
- [ ] 系统启动正常
- [ ] 数据库连接正常
- [ ] 登录功能正常
- [ ] 问卷提交功能正常
- [ ] Frankfurt Scale提交功能正常
- [ ] 数据查询功能正常
- [ ] 数据导出功能正常

### 错误处理
- [ ] 无效数据验证正常
- [ ] 未授权访问拒绝正常
- [ ] 404错误处理正常
- [ ] 服务器错误处理正常

### 性能
- [ ] 页面加载速度正常
- [ ] 大量数据处理正常
- [ ] 并发访问处理正常

### 安全
- [ ] 密码加密存储
- [ ] 会话管理安全
- [ ] 输入数据验证
- [ ] SQL注入防护

通过以上测试步骤，你可以全面验证问卷数据管理系统的各项功能是否正常工作。