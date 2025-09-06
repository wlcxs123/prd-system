# 远程服务器自动部署脚本使用指南

## 概述

本脚本用于自动将项目部署到远程服务器，支持备份、回滚和健康检查功能。

## 服务器信息

- **服务器地址**: 115.190.103.114
- **用户名**: root
- **部署目录**: /usr/share/nginx-after
- **应用端口**: 8081

## 使用步骤

### 方法一：使用PowerShell脚本（推荐）

```powershell
# 英文版本（推荐，避免编码问题）
powershell -ExecutionPolicy Bypass -File deploy_en.ps1

# 中文版本（可能存在编码问题）
powershell -ExecutionPolicy Bypass -File deploy.ps1
```

### 方法二：使用批处理文件

```cmd
# 双击 deploy.bat 或在命令行执行：
deploy.bat
```

### 方法三：直接使用Python脚本

```bash
# 1. 安装依赖
pip install -r deploy_requirements.txt

# 2. 执行部署
python deploy_remote.py
```

### 确认部署

所有脚本都会提示确认，输入 `y` 或 `yes` 开始部署。

## 部署流程

1. **连接服务器** - 通过SSH连接到远程服务器
2. **创建备份** - 备份现有部署（如果存在）
3. **打包项目** - 创建项目压缩包（排除不必要文件）
4. **上传文件** - 将项目文件上传到服务器
5. **设置环境** - 安装依赖和设置权限
6. **启动服务** - 启动应用服务
7. **健康检查** - 验证服务是否正常运行

## 功能特性

### 自动备份
- 部署前自动创建备份
- 备份存储在 `/usr/share/nginx-after-backup/` 目录
- 备份文件名包含时间戳

### 智能回滚
- 部署失败时自动回滚到备份版本
- 保证服务的连续性

### 健康检查
- 检查端口监听状态
- 验证HTTP健康检查端点
- 确保服务正常运行

### 文件过滤
自动排除以下文件和目录：
- `__pycache__`、`*.pyc` - Python缓存文件
- `.git` - Git版本控制文件
- `.env` - 环境变量文件
- `venv`、`node_modules` - 依赖目录
- `*.log` - 日志文件
- `.DS_Store`、`Thumbs.db` - 系统文件

## 部署后验证

### 访问应用
```
http://115.190.103.114:8081
```

### 健康检查
```
http://115.190.103.114:8081/health
```

### 查看日志
```bash
ssh root@115.190.103.114
tail -f /usr/share/nginx-after/logs/app.log
```

## 故障排除

### 连接失败
- 检查服务器地址和端口
- 验证用户名和密码
- 确认网络连接

### 部署失败
- 查看 `deploy.log` 文件获取详细错误信息
- 检查服务器磁盘空间
- 验证权限设置

### 服务启动失败
- 检查Python环境和依赖
- 查看应用日志文件
- 验证端口是否被占用

## 手动操作

### 停止服务
```bash
ssh root@115.190.103.114
pkill -f 'python.*app.py'
```

### 启动服务
```bash
ssh root@115.190.103.114
cd /usr/share/nginx-after/backend
nohup python3 app.py > ../logs/app.log 2>&1 &
```

### 查看进程
```bash
ssh root@115.190.103.114
ps aux | grep 'python.*app.py'
```

## 安全注意事项

1. **密码安全**: 脚本中包含明文密码，请确保文件权限安全
2. **网络安全**: 建议使用SSH密钥认证替代密码认证
3. **备份管理**: 定期清理旧备份文件，避免磁盘空间不足

## 自定义配置

可以修改脚本中的配置参数：

```python
# 服务器配置
SERVER_CONFIG = {
    'hostname': '115.190.103.114',
    'username': 'root',
    'password': 'LKziTP2FWjbdv87AuUHJ',
    'port': 22,
    'deploy_dir': '/usr/share/nginx-after',
    'backup_dir': '/usr/share/nginx-after-backup'
}

# 项目配置
PROJECT_CONFIG = {
    'exclude_patterns': [
        # 添加需要排除的文件模式
    ]
}
```

## 支持

如遇问题，请检查：
1. `deploy.log` - 部署日志
2. `/usr/share/nginx-after/logs/app.log` - 应用日志
3. 服务器系统日志