# 问卷数据管理系统故障排除指南

## 目录

1. [常见问题快速诊断](#常见问题快速诊断)
2. [系统启动问题](#系统启动问题)
3. [登录和认证问题](#登录和认证问题)
4. [数据库相关问题](#数据库相关问题)
5. [性能问题](#性能问题)
6. [网络和连接问题](#网络和连接问题)
7. [文件和权限问题](#文件和权限问题)
8. [数据导出问题](#数据导出问题)
9. [监控和日志问题](#监控和日志问题)
10. [部署和配置问题](#部署和配置问题)
11. [错误代码参考](#错误代码参考)
12. [诊断工具和命令](#诊断工具和命令)

## 常见问题快速诊断

### 问题分类决策树

```
系统无法访问？
├─ 是 → 检查服务状态 → [系统启动问题](#系统启动问题)
└─ 否 → 能否登录？
    ├─ 否 → [登录和认证问题](#登录和认证问题)
    └─ 是 → 功能正常？
        ├─ 否 → 哪个功能异常？
        │   ├─ 数据查询 → [数据库相关问题](#数据库相关问题)
        │   ├─ 页面加载慢 → [性能问题](#性能问题)
        │   ├─ 数据导出 → [数据导出问题](#数据导出问题)
        │   └─ 其他 → 查看具体错误信息
        └─ 是 → 系统正常运行
```

### 快速检查清单

在深入诊断之前，请先完成以下快速检查：

- [ ] 服务器是否正常运行？
- [ ] 网络连接是否正常？
- [ ] 系统服务是否启动？
- [ ] 磁盘空间是否充足？
- [ ] 内存使用是否正常？
- [ ] 数据库文件是否存在？
- [ ] 日志文件是否有错误信息？

## 系统启动问题

### 问题 1: 系统服务无法启动

**症状**：
- 执行 `systemctl start questionnaire-system` 失败
- 服务状态显示为 `failed` 或 `inactive`

**诊断步骤**：

1. **检查服务状态**
```bash
sudo systemctl status questionnaire-system
```

2. **查看详细日志**
```bash
sudo journalctl -u questionnaire-system -n 50
```

3. **检查配置文件**
```bash
# 检查服务配置文件
sudo cat /etc/systemd/system/questionnaire-system.service

# 检查应用配置文件
sudo cat /opt/questionnaire-system/.env
```

**常见原因和解决方法**：

| 原因 | 解决方法 |
|------|----------|
| 配置文件语法错误 | 检查并修正配置文件语法 |
| 环境变量缺失 | 补充必需的环境变量 |
| 文件权限问题 | 修正文件和目录权限 |
| 端口被占用 | 更改端口或停止占用进程 |
| Python 虚拟环境问题 | 重新创建虚拟环境 |

**解决示例**：

```bash
# 修正文件权限
sudo chown -R www-data:www-data /opt/questionnaire-system
sudo chmod 755 /opt/questionnaire-system

# 检查端口占用
sudo netstat -tlnp | grep :5000

# 重新加载 systemd 配置
sudo systemctl daemon-reload
sudo systemctl restart questionnaire-system
```

### 问题 2: Gunicorn 进程异常退出

**症状**：
- 服务启动后立即退出
- 日志显示 Gunicorn 相关错误

**诊断步骤**：

1. **手动启动 Gunicorn**
```bash
cd /opt/questionnaire-system/current
sudo -u www-data bash -c "
    source ../venv/bin/activate
    gunicorn --config gunicorn.conf.py wsgi:application
"
```

2. **检查 Gunicorn 配置**
```bash
cat /opt/questionnaire-system/current/gunicorn.conf.py
```

**常见解决方法**：

```bash
# 检查 Python 模块是否正确安装
sudo -u www-data bash -c "
    cd /opt/questionnaire-system/current
    source ../venv/bin/activate
    python -c 'import app; print(\"Import successful\")'
"

# 更新 Gunicorn 配置
sudo nano /opt/questionnaire-system/current/gunicorn.conf.py

# 减少工作进程数（如果内存不足）
# 在配置文件中设置: workers = 2
```

### 问题 3: 数据库初始化失败

**症状**：
- 应用启动时报数据库相关错误
- 数据库文件不存在或损坏

**解决步骤**：

```bash
# 检查数据库文件
ls -la /var/lib/questionnaire-system/questionnaires.db

# 重新初始化数据库
cd /opt/questionnaire-system/current
sudo -u www-data bash -c "
    source ../venv/bin/activate
    export DATABASE_PATH=/var/lib/questionnaire-system/questionnaires.db
    python migrate_db.py
"

# 创建管理员用户
sudo -u www-data bash -c "
    cd /opt/questionnaire-system/current
    source ../venv/bin/activate
    export DATABASE_PATH=/var/lib/questionnaire-system/questionnaires.db
    python migrate_db.py --create-admin --admin-username admin --admin-password 'new_password'
"
```

## 登录和认证问题

### 问题 1: 无法登录系统

**症状**：
- 输入正确用户名密码后仍无法登录
- 登录页面显示"用户名或密码错误"

**诊断步骤**：

1. **检查用户是否存在**
```bash
cd /opt/questionnaire-system/current
sudo -u www-data bash -c "
    source ../venv/bin/activate
    export DATABASE_PATH=/var/lib/questionnaire-system/questionnaires.db
    sqlite3 \$DATABASE_PATH 'SELECT * FROM users;'
"
```

2. **检查会话配置**
```bash
# 检查会话目录权限
ls -la /var/lib/questionnaire-system/sessions/

# 检查会话配置
grep -i session /opt/questionnaire-system/.env
```

**解决方法**：

```bash
# 重置管理员密码
cd /opt/questionnaire-system/current
sudo -u www-data bash -c "
    source ../venv/bin/activate
    export DATABASE_PATH=/var/lib/questionnaire-system/questionnaires.db
    python -c \"
import sqlite3
import bcrypt

# 连接数据库
conn = sqlite3.connect('/var/lib/questionnaire-system/questionnaires.db')
cursor = conn.cursor()

# 生成新密码哈希
new_password = 'admin123'
password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

# 更新密码
cursor.execute('UPDATE users SET password_hash = ? WHERE username = ?', 
               (password_hash.decode('utf-8'), 'admin'))
conn.commit()
conn.close()

print('密码重置完成')
\"
"
```

### 问题 2: 会话频繁过期

**症状**：
- 用户需要频繁重新登录
- 会话时间比预期短

**解决方法**：

```bash
# 检查会话配置
grep PERMANENT_SESSION_LIFETIME /opt/questionnaire-system/.env

# 延长会话时间（修改环境变量）
sudo nano /opt/questionnaire-system/.env
# 添加或修改：SESSION_TIMEOUT=7200  # 2小时

# 重启服务
sudo systemctl restart questionnaire-system
```

### 问题 3: 会话存储问题

**症状**：
- 登录后立即被登出
- 多个用户会话冲突

**解决方法**：

```bash
# 清理会话文件
sudo rm -rf /var/lib/questionnaire-system/sessions/*

# 检查会话目录权限
sudo chown -R www-data:www-data /var/lib/questionnaire-system/sessions
sudo chmod 750 /var/lib/questionnaire-system/sessions

# 重启服务
sudo systemctl restart questionnaire-system
```

## 数据库相关问题

### 问题 1: 数据库连接失败

**症状**：
- 页面显示数据库连接错误
- 无法查询或保存数据

**诊断步骤**：

```bash
# 检查数据库文件
ls -la /var/lib/questionnaire-system/questionnaires.db

# 测试数据库连接
sqlite3 /var/lib/questionnaire-system/questionnaires.db ".tables"

# 检查数据库完整性
sqlite3 /var/lib/questionnaire-system/questionnaires.db "PRAGMA integrity_check;"
```

**解决方法**：

```bash
# 修复数据库权限
sudo chown www-data:www-data /var/lib/questionnaire-system/questionnaires.db
sudo chmod 664 /var/lib/questionnaire-system/questionnaires.db

# 如果数据库损坏，从备份恢复
sudo cp /var/lib/questionnaire-system/backups/latest_backup.db /var/lib/questionnaire-system/questionnaires.db

# 重建数据库索引
sqlite3 /var/lib/questionnaire-system/questionnaires.db "REINDEX;"
```

### 问题 2: 数据库锁定

**症状**：
- 操作时出现"database is locked"错误
- 数据保存失败

**解决方法**：

```bash
# 查找占用数据库的进程
sudo lsof /var/lib/questionnaire-system/questionnaires.db

# 重启应用服务
sudo systemctl restart questionnaire-system

# 如果问题持续，检查是否有僵尸连接
ps aux | grep questionnaire
```

### 问题 3: 数据库空间不足

**症状**：
- 无法插入新数据
- 磁盘空间警告

**解决方法**：

```bash
# 检查磁盘空间
df -h /var/lib/questionnaire-system/

# 清理数据库
sqlite3 /var/lib/questionnaire-system/questionnaires.db "VACUUM;"

# 清理旧的操作日志
sqlite3 /var/lib/questionnaire-system/questionnaires.db "
DELETE FROM operation_logs 
WHERE created_at < datetime('now', '-30 days');
"

# 创建备份并清理
cd /opt/questionnaire-system/current
python backup_system.py --backup
python backup_system.py --cleanup
```

## 性能问题

### 问题 1: 页面加载缓慢

**症状**：
- 管理后台加载时间超过 10 秒
- 问卷列表显示缓慢

**诊断步骤**：

```bash
# 检查系统资源使用
top
free -h
df -h

# 检查数据库大小和记录数
sqlite3 /var/lib/questionnaire-system/questionnaires.db "
SELECT 
    'questionnaires' as table_name, 
    COUNT(*) as record_count 
FROM questionnaires
UNION ALL
SELECT 
    'operation_logs' as table_name, 
    COUNT(*) as record_count 
FROM operation_logs;
"
```

**优化方法**：

```bash
# 1. 数据库优化
sqlite3 /var/lib/questionnaire-system/questionnaires.db "
-- 创建索引
CREATE INDEX IF NOT EXISTS idx_questionnaires_created_at ON questionnaires(created_at);
CREATE INDEX IF NOT EXISTS idx_questionnaires_type ON questionnaires(type);
CREATE INDEX IF NOT EXISTS idx_questionnaires_name ON questionnaires(name);

-- 分析表统计信息
ANALYZE;
"

# 2. 调整 Gunicorn 配置
sudo nano /opt/questionnaire-system/current/gunicorn.conf.py
# 增加工作进程数：workers = 4
# 调整超时时间：timeout = 60

# 3. 启用 Nginx 缓存
sudo nano /etc/nginx/sites-available/questionnaire-system
# 添加缓存配置
```

### 问题 2: 内存使用过高

**症状**：
- 系统内存使用率超过 90%
- 应用响应变慢或崩溃

**解决方法**：

```bash
# 检查内存使用详情
ps aux --sort=-%mem | head -10

# 减少 Gunicorn 工作进程
sudo nano /opt/questionnaire-system/current/gunicorn.conf.py
# 设置：workers = 2

# 重启服务
sudo systemctl restart questionnaire-system

# 添加 swap 空间（临时解决）
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 问题 3: CPU 使用率过高

**症状**：
- CPU 使用率持续超过 80%
- 系统响应缓慢

**诊断和解决**：

```bash
# 查看 CPU 使用情况
htop

# 检查是否有死循环或异常进程
ps aux --sort=-%cpu | head -10

# 查看应用日志中的异常
sudo journalctl -u questionnaire-system -f

# 临时限制 CPU 使用
sudo systemctl edit questionnaire-system
# 添加：
# [Service]
# CPUQuota=50%
```

## 网络和连接问题

### 问题 1: 无法访问系统

**症状**：
- 浏览器显示"无法连接到服务器"
- 网络超时错误

**诊断步骤**：

```bash
# 检查服务是否监听端口
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :5000

# 检查防火墙状态
sudo ufw status

# 测试本地连接
curl -I http://localhost/health
curl -I http://localhost:5000/health
```

**解决方法**：

```bash
# 检查 Nginx 状态
sudo systemctl status nginx

# 重启 Nginx
sudo systemctl restart nginx

# 检查 Nginx 配置
sudo nginx -t

# 开放防火墙端口
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### 问题 2: CORS 跨域问题

**症状**：
- 浏览器控制台显示 CORS 错误
- 前端无法调用 API

**解决方法**：

```bash
# 检查 CORS 配置
grep -i cors /opt/questionnaire-system/current/app.py

# 更新 CORS 设置
sudo nano /opt/questionnaire-system/.env
# 添加：CORS_ORIGINS=https://your-domain.com,http://localhost:3000

# 重启服务
sudo systemctl restart questionnaire-system
```

### 问题 3: SSL/HTTPS 问题

**症状**：
- HTTPS 连接失败
- SSL 证书错误

**解决方法**：

```bash
# 检查 SSL 证书
sudo certbot certificates

# 更新证书
sudo certbot renew

# 检查 Nginx SSL 配置
sudo nginx -t

# 强制 HTTPS 重定向
sudo nano /etc/nginx/sites-available/questionnaire-system
# 添加重定向规则
```

## 文件和权限问题

### 问题 1: 文件权限错误

**症状**：
- 应用无法读写文件
- 权限被拒绝错误

**解决方法**：

```bash
# 修正应用目录权限
sudo chown -R www-data:www-data /opt/questionnaire-system
sudo chmod -R 755 /opt/questionnaire-system

# 修正数据目录权限
sudo chown -R www-data:www-data /var/lib/questionnaire-system
sudo chmod -R 750 /var/lib/questionnaire-system

# 修正日志目录权限
sudo chown -R www-data:www-data /var/log/questionnaire-system
sudo chmod -R 755 /var/log/questionnaire-system

# 设置特殊权限
sudo chmod 600 /opt/questionnaire-system/.env
sudo chmod 664 /var/lib/questionnaire-system/questionnaires.db
```

### 问题 2: 磁盘空间不足

**症状**：
- 无法创建新文件
- 系统运行缓慢

**解决方法**：

```bash
# 检查磁盘使用情况
df -h
du -sh /var/lib/questionnaire-system/*
du -sh /var/log/questionnaire-system/*

# 清理日志文件
sudo journalctl --vacuum-time=7d
sudo find /var/log -name "*.log" -mtime +30 -delete

# 清理旧备份
sudo find /var/lib/questionnaire-system/backups -name "*.tar.gz" -mtime +30 -delete

# 清理临时文件
sudo rm -rf /tmp/*
sudo rm -rf /var/tmp/*
```

## 数据导出问题

### 问题 1: 导出功能失败

**症状**：
- 点击导出按钮无响应
- 导出文件损坏或为空

**诊断步骤**：

```bash
# 检查导出相关日志
sudo journalctl -u questionnaire-system | grep -i export

# 测试导出功能
curl -X GET "http://localhost/api/questionnaires/1/export?format=csv" \
     -H "Cookie: session=your_session_cookie"

# 检查临时目录权限
ls -la /tmp/
```

**解决方法**：

```bash
# 安装缺失的依赖
cd /opt/questionnaire-system/current
sudo -u www-data bash -c "
    source ../venv/bin/activate
    pip install openpyxl reportlab
"

# 创建临时目录
sudo mkdir -p /tmp/questionnaire-exports
sudo chown www-data:www-data /tmp/questionnaire-exports

# 重启服务
sudo systemctl restart questionnaire-system
```

### 问题 2: 大文件导出超时

**症状**：
- 导出大量数据时超时
- 浏览器显示请求超时

**解决方法**：

```bash
# 增加 Nginx 超时设置
sudo nano /etc/nginx/sites-available/questionnaire-system
# 添加：
# proxy_read_timeout 300;
# proxy_connect_timeout 300;
# proxy_send_timeout 300;

# 增加 Gunicorn 超时设置
sudo nano /opt/questionnaire-system/current/gunicorn.conf.py
# 设置：timeout = 300

# 重启服务
sudo systemctl restart nginx
sudo systemctl restart questionnaire-system
```

## 监控和日志问题

### 问题 1: 日志文件过大

**症状**：
- 日志文件占用大量磁盘空间
- 系统性能下降

**解决方法**：

```bash
# 配置日志轮转
sudo nano /etc/logrotate.d/questionnaire-system
# 内容：
# /var/log/questionnaire-system/*.log {
#     daily
#     missingok
#     rotate 30
#     compress
#     delaycompress
#     notifempty
#     create 644 www-data www-data
# }

# 手动执行日志轮转
sudo logrotate -f /etc/logrotate.d/questionnaire-system

# 清理旧日志
sudo find /var/log/questionnaire-system -name "*.log.*" -mtime +30 -delete
```

### 问题 2: 监控数据异常

**症状**：
- 健康检查失败
- 监控指标不准确

**解决方法**：

```bash
# 检查监控端点
curl http://localhost/health
curl http://localhost/metrics

# 重启监控服务
sudo systemctl restart questionnaire-system

# 检查系统资源
free -h
df -h
ps aux --sort=-%mem | head -5
```

## 部署和配置问题

### 问题 1: 环境变量配置错误

**症状**：
- 应用启动时配置相关错误
- 功能异常

**解决方法**：

```bash
# 检查环境变量文件
sudo cat /opt/questionnaire-system/.env

# 验证必需的环境变量
cd /opt/questionnaire-system/current
sudo -u www-data bash -c "
    source ../venv/bin/activate
    python -c \"
import os
from config_production import ProductionConfig

try:
    ProductionConfig.validate_config()
    print('配置验证通过')
except Exception as e:
    print(f'配置验证失败: {e}')
\"
"

# 重新生成密钥
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
sudo sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" /opt/questionnaire-system/.env
```

### 问题 2: 依赖包版本冲突

**症状**：
- 导入模块失败
- 功能异常

**解决方法**：

```bash
# 重新创建虚拟环境
cd /opt/questionnaire-system
sudo rm -rf venv
sudo -u www-data python3 -m venv venv

# 重新安装依赖
sudo -u www-data bash -c "
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r current/requirements_production.txt
"

# 验证安装
sudo -u www-data bash -c "
    source venv/bin/activate
    pip list
    python -c 'import flask, sqlite3, bcrypt; print(\"Dependencies OK\")'
"
```

## 错误代码参考

### HTTP 状态码

| 状态码 | 含义 | 常见原因 | 解决方法 |
|--------|------|----------|----------|
| 400 | 请求错误 | 参数格式错误 | 检查请求参数格式 |
| 401 | 未授权 | 未登录或会话过期 | 重新登录 |
| 403 | 权限不足 | 用户权限不够 | 检查用户权限 |
| 404 | 资源不存在 | URL 错误或资源被删除 | 检查 URL 和资源状态 |
| 500 | 服务器错误 | 应用内部错误 | 查看应用日志 |
| 502 | 网关错误 | 后端服务不可用 | 检查应用服务状态 |
| 503 | 服务不可用 | 系统维护或过载 | 检查系统资源 |

### 应用错误代码

| 错误代码 | 说明 | 解决方法 |
|----------|------|----------|
| AUTH_REQUIRED | 需要登录 | 重新登录系统 |
| AUTH_FAILED | 认证失败 | 检查用户名密码 |
| SESSION_EXPIRED | 会话过期 | 重新登录 |
| VALIDATION_ERROR | 数据验证失败 | 检查数据格式 |
| DATABASE_ERROR | 数据库错误 | 检查数据库状态 |
| PERMISSION_DENIED | 权限不足 | 联系管理员 |
| FILE_ERROR | 文件操作错误 | 检查文件权限 |
| NETWORK_ERROR | 网络错误 | 检查网络连接 |

## 诊断工具和命令

### 系统状态检查

```bash
#!/bin/bash
# 系统健康检查脚本

echo "=== 问卷数据管理系统健康检查 ==="
echo "检查时间: $(date)"
echo

# 检查服务状态
echo "1. 服务状态检查"
systemctl is-active questionnaire-system && echo "✓ 应用服务正常" || echo "✗ 应用服务异常"
systemctl is-active nginx && echo "✓ Nginx 服务正常" || echo "✗ Nginx 服务异常"
echo

# 检查端口监听
echo "2. 端口监听检查"
netstat -tlnp | grep :80 > /dev/null && echo "✓ 端口 80 正常监听" || echo "✗ 端口 80 未监听"
netstat -tlnp | grep :5000 > /dev/null && echo "✓ 端口 5000 正常监听" || echo "✗ 端口 5000 未监听"
echo

# 检查磁盘空间
echo "3. 磁盘空间检查"
df -h | grep -E "(/$|/var)" | while read line; do
    usage=$(echo $line | awk '{print $5}' | sed 's/%//')
    if [ $usage -gt 80 ]; then
        echo "✗ 磁盘使用率过高: $line"
    else
        echo "✓ 磁盘空间正常: $line"
    fi
done
echo

# 检查内存使用
echo "4. 内存使用检查"
memory_usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100}')
if [ $memory_usage -gt 80 ]; then
    echo "✗ 内存使用率过高: ${memory_usage}%"
else
    echo "✓ 内存使用正常: ${memory_usage}%"
fi
echo

# 检查数据库
echo "5. 数据库检查"
if [ -f "/var/lib/questionnaire-system/questionnaires.db" ]; then
    echo "✓ 数据库文件存在"
    sqlite3 /var/lib/questionnaire-system/questionnaires.db "SELECT COUNT(*) FROM questionnaires;" > /dev/null 2>&1 && \
        echo "✓ 数据库连接正常" || echo "✗ 数据库连接异常"
else
    echo "✗ 数据库文件不存在"
fi
echo

# 检查应用健康
echo "6. 应用健康检查"
curl -s -f http://localhost/health > /dev/null && echo "✓ 应用健康检查通过" || echo "✗ 应用健康检查失败"
echo

echo "=== 检查完成 ==="
```

### 日志分析脚本

```bash
#!/bin/bash
# 日志分析脚本

echo "=== 问卷数据管理系统日志分析 ==="
echo "分析时间: $(date)"
echo

# 分析应用日志
echo "1. 应用日志分析（最近1小时）"
journalctl -u questionnaire-system --since "1 hour ago" --no-pager | \
    grep -E "(ERROR|CRITICAL)" | tail -10
echo

# 分析 Nginx 错误日志
echo "2. Nginx 错误日志分析"
if [ -f "/var/log/nginx/error.log" ]; then
    tail -20 /var/log/nginx/error.log | grep -E "(error|crit)"
else
    echo "Nginx 错误日志文件不存在"
fi
echo

# 分析系统日志
echo "3. 系统日志分析"
journalctl --since "1 hour ago" --no-pager | \
    grep -E "(questionnaire|nginx)" | \
    grep -E "(error|fail|crit)" | tail -10
echo

echo "=== 分析完成 ==="
```

### 性能监控脚本

```bash
#!/bin/bash
# 性能监控脚本

echo "=== 系统性能监控 ==="
echo "监控时间: $(date)"
echo

# CPU 使用率
echo "1. CPU 使用率"
top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//'
echo

# 内存使用情况
echo "2. 内存使用情况"
free -h
echo

# 磁盘 I/O
echo "3. 磁盘 I/O"
iostat -x 1 1 | grep -E "(Device|sda|nvme)"
echo

# 网络连接
echo "4. 网络连接统计"
netstat -an | awk '/^tcp/ {print $6}' | sort | uniq -c | sort -nr
echo

# 进程资源使用
echo "5. 进程资源使用 Top 10"
ps aux --sort=-%cpu | head -11
echo

echo "=== 监控完成 ==="
```

## 联系技术支持

如果按照本指南仍无法解决问题，请联系技术支持团队：

### 联系方式
- **邮箱**: support@example.com
- **电话**: 400-xxx-xxxx
- **在线支持**: 工作日 9:00-18:00

### 提供信息
在联系技术支持时，请提供以下信息：

1. **问题描述**
   - 具体的错误现象
   - 错误发生的时间
   - 重现步骤

2. **系统信息**
   - 操作系统版本
   - 应用版本
   - 部署方式

3. **日志信息**
   - 相关错误日志
   - 系统日志片段
   - 配置文件内容

4. **环境信息**
   - 服务器配置
   - 网络环境
   - 用户数量

### 紧急情况处理

对于以下紧急情况，请立即联系技术支持：

- 系统完全无法访问
- 数据丢失或损坏
- 安全漏洞或攻击
- 大规模用户无法使用

技术支持团队将在收到紧急情况报告后 2 小时内响应，并提供临时解决方案。

---

**文档版本**: v1.0  
**最后更新**: 2024-01-15  
**适用版本**: 问卷数据管理系统 v1.0+