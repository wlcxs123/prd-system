@echo off
echo ========================================
echo 📤 上传问卷管理系统到 GitHub
echo ========================================
echo.

echo 🔧 初始化 Git 仓库...
git init

echo.
echo 🔗 添加远程仓库...
git remote add origin https://github.com/wlcxs123/prd-system.git

echo.
echo 📁 添加所有文件到暂存区...
git add .

echo.
echo 💾 提交代码...
git commit -m "Initial commit: 问卷数据管理系统完整版

✅ 功能特性:
- 完整的问卷管理系统 (CRUD操作)
- 多格式数据导出 (CSV, Excel, PDF)  
- 用户认证和权限管理
- 响应式管理员界面
- 详细的问卷数据显示格式
- 调试和测试工具

🔧 技术栈:
- Backend: Python Flask + SQLite
- Frontend: HTML5 + CSS3 + JavaScript
- 数据处理: Pandas, ReportLab
- 认证: Flask Session

📊 支持的问卷类型:
- 小学生交流评定表
- SM维持因素清单
- 其他自定义问卷类型

🎨 界面优化:
- 问题序号 + 完整问题文本
- 所有答案选项显示 (0-4分制)
- 选中答案高亮显示
- 评分统计和数据分析"

echo.
echo 🚀 推送到 GitHub...
git push -u origin main

echo.
echo ========================================
echo ✅ 上传完成！
echo 📍 仓库地址: https://github.com/wlcxs123/prd-system
echo ========================================
echo.

pause