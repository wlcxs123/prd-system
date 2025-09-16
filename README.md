# 问卷数据管理系统 (Questionnaire Management System)

一个基于 Flask 的问卷数据管理系统，支持多种问卷类型的创建、管理、查看和导出功能。

## 🌟 主要功能

### 📋 问卷管理
- **多种问卷类型支持**：小学生交流评定表、SM维持因素清单等
- **完整的CRUD操作**：创建、查看、编辑、删除问卷
- **智能数据验证**：确保数据完整性和准确性
- **分页和搜索**：高效的数据浏览和查找

### 👀 数据查看
- **详细问卷视图**：显示完整的问题、选项和答案
- **格式化显示**：
  - 序号 + 问题文本
  - 所有答案选项（0-4分制）
  - 高亮显示选择的答案
  - 评分统计和总结

### 📊 数据导出
- **多格式支持**：CSV、Excel、PDF
- **批量导出**：支持筛选条件的批量导出
- **自定义字段**：可选择导出的数据字段

### 🔐 用户管理
- **安全认证**：登录验证和会话管理
- **权限控制**：管理员和普通用户权限分离
- **操作日志**：记录所有重要操作

## 🚀 快速开始

### 环境要求
- Python 3.7+
- Flask 2.0+
- SQLite 3

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd questionnaire-management-system
```

2. **创建虚拟环境**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **安装依赖**
```bash
pip install -r backend/requirements.txt
```

4. **初始化数据库**
```bash
python backend/init_db.py
```

5. **启动服务**
```bash
python backend/app.py
```

6. **访问系统**
- 管理员界面: http://localhost:5000/admin
- 登录页面: http://localhost:5000/login
- 默认账号: admin/admin

## 🚀 云服务器部署

### 自动部署脚本

项目提供了自动化部署脚本 `deploy_remote.py`，可以一键部署到云服务器。

#### 使用方法

1. **安装部署依赖**
```bash
pip install -r deploy_requirements.txt
```

2. **执行部署脚本**
```bash
python deploy_remote.py
```

#### 部署配置

部署脚本会自动完成以下操作：
- 连接到远程服务器 (115.190.103.114)
- 创建当前部署的备份
- 上传项目文件到服务器
- 安装Python依赖
- 配置和启动服务
- 进行健康检查

#### 部署后访问
- 应用地址: http://115.190.103.114:8080
- 健康检查: http://115.190.103.114:8080/health
- 查看日志: `tail -f /usr/share/nginx-after/logs/app.log`

#### 注意事项
- 部署前请确保本地代码已提交并测试通过
- 部署过程中如遇错误，脚本会自动回滚到备份版本
- 部署脚本会排除敏感文件（如 .env、日志文件等）

## 📁 项目结构

```
questionnaire-management-system/
├── backend/                    # 后端代码
│   ├── app.py                 # 主应用文件
│   ├── templates/             # HTML模板
│   │   ├── admin.html         # 管理员界面
│   │   ├── login.html         # 登录页面
│   │   └── debug_admin.html   # 调试页面
│   ├── static/                # 静态资源
│   ├── requirements.txt       # Python依赖
│   └── init_db.py            # 数据库初始化
├── deploy_remote.py           # 云服务器自动部署脚本
├── deploy_requirements.txt    # 部署脚本依赖
├── 环境配置说明.md             # 环境配置文档
├── 小学生交流评定表.html        # 问卷表单
├── 可能的SM维持因素清单.html     # SM因素问卷
├── README.md                  # 项目说明
└── .gitignore                # Git忽略文件
```

## 🔧 核心功能

### 问卷数据结构
系统支持复杂的问卷数据结构：
```json
{
  "basic_info": {
    "name": "学生姓名",
    "gender": "性别",
    "age": "年龄",
    "grade": "年级"
  },
  "questions": [
    {
      "id": 0,
      "question": "问题文本",
      "options": [
        {"text": "选项文本", "value": 0}
      ],
      "selected": [0],
      "selected_texts": ["选择的文本"]
    }
  ]
}
```

### API 接口
- `GET /api/questionnaires` - 获取问卷列表
- `GET /api/questionnaires/{id}` - 获取问卷详情
- `POST /api/questionnaires` - 创建问卷
- `PUT /api/questionnaires/{id}` - 更新问卷
- `DELETE /api/questionnaires/{id}` - 删除问卷
- `GET /api/questionnaires/{id}/export` - 导出问卷

## 🎨 界面特性

### 管理员界面
- **现代化设计**：响应式布局，支持移动端
- **直观操作**：一键查看、编辑、导出、删除
- **实时搜索**：支持姓名、类型、年级等字段搜索
- **分页显示**：高效处理大量数据

### 问卷显示格式
- ✅ **选中答案高亮**：绿色背景 + 勾选标记
- 📝 **完整选项显示**：所有可选答案清晰展示
- 🔢 **序号标识**：问题按序号排列
- 📊 **统计信息**：总分、平均分、问题统计

## 🛠️ 开发工具

### 调试功能
- **调试页面**: `/debug` - API测试和数据结构分析
- **测试工具**: `/test-modal` - 模态框和渲染功能测试
- **控制台日志**: 详细的调试信息输出

### 数据验证
- **输入验证**：前端和后端双重验证
- **数据标准化**：自动格式化和清理数据
- **错误处理**：友好的错误提示和恢复机制

## 📈 系统监控

### 性能监控
- **响应时间统计**
- **数据库查询优化**
- **内存使用监控**

### 操作日志
- **用户操作记录**
- **系统事件日志**
- **错误日志追踪**

## 🔒 安全特性

- **会话管理**：安全的用户会话控制
- **权限验证**：基于角色的访问控制
- **数据保护**：SQL注入防护和XSS防护
- **输入过滤**：严格的数据验证和清理

## 📝 更新日志

### v1.0.0 (2025-09-03)
- ✅ 完整的问卷管理系统
- ✅ 多格式数据导出功能
- ✅ 用户认证和权限管理
- ✅ 响应式管理员界面
- ✅ 详细的问卷数据显示
- ✅ 调试和测试工具

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 创建 Issue
- 发送 Pull Request
- 邮件联系项目维护者

---

**注意**: 本系统仅用于教育和研究目的，请确保在使用时遵守相关的数据保护法规。