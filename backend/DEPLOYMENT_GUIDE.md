# 问卷数据管理系统部署指南

## 概述

本指南详细说明了如何在生产环境中部署问卷数据管理系统。系统支持多种部署方式，包括传统服务器部署、Docker 容器化部署和云平台部署。

## 系统要求

### 最低硬件要求

- **CPU**: 2 核心
- **内存**: 2GB RAM
- **存储**: 10GB 可用磁盘空间
- **网络**: 稳定的互联网连接

### 推荐硬件配置

- **CPU**: 4 核心或更多
- **内存**: 4GB RAM 或更多
- **存储**: 50GB SSD
- **网络**: 100Mbps 带宽

### 软件要求

- **操作系统**: Ubuntu 20.04 LTS 或更高版本 / CentOS 8 或更高版本
- **Python**: 3.8 或更高版本
- **数据库**: SQLite 3.x（默认）或 PostgreSQL 12+
- **Web 服务器**: Nginx 1.18+ 或 Apache 2.4+
- **进程管理**: Systemd 或 Supervisor

## 部署方式

### 方式一：自动化部署脚本（推荐）

#### 1. 准备部署环境

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 下载部署脚本
wget https://your-domain.com/deploy.sh
chmod +x deploy.sh

# 设置环境变量
export ADMIN_PASSWORD="your_secure_password"
export SERVER_NAME="your-domain.com"
export CORS_ORIGINS="https://your-domain.com"
```

#### 2. 运行部署脚本

```bash
sudo ./deploy.sh
```

部署脚本将自动完成以下操作：
- 安装系统依赖
- 创建应用用户和目录
- 设置 Python 虚拟环境
- 配置数据库
- 设置 Systemd 服务
- 配置 Nginx 反向代理
- 设置日志轮转和备份

#### 3. 验证部署

```bash
# 检查服务状态
sudo systemctl status questionnaire-system

# 检查健康状态
curl http://localhost/health

# 查看日志
sudo journalctl -u questionnaire-system -f
```

### 方式二：手动部署

#### 1. 创建应用用户

```bash
sudo useradd --system --shell /bin/bash --home-dir /opt/questionnaire-system --create-home www-data
```

#### 2. 安装系统依赖

```bash
sudo apt install -y python3 python3-pip python3-venv nginx supervisor sqlite3
```

#### 3. 部署应用代码

```bash
# 创建应用目录
sudo mkdir -p /opt/questionnaire-system/current
sudo chown -R www-data:www-data /opt/questionnaire-system

# 复制应用文件
sudo cp -r . /opt/questionnaire-system/current/
sudo chown -R www-data:www-data /opt/questionnaire-system/current
```

#### 4. 设置 Python 环境

```bash
# 切换到应用用户
sudo -u www-data bash

# 创建虚拟环境
cd /opt/questionnaire-system
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r current/requirements_production.txt
```

#### 5. 配置环境变量

```bash
# 创建环境配置文件
sudo tee /opt/questionnaire-system/.env << EOF
FLASK_ENV=production
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
DATABASE_PATH=/var/lib/questionnaire-system/questionnaires.db
SESSION_FILE_DIR=/var/lib/questionnaire-system/sessions
LOG_FILE=/var/log/questionnaire-system/app.log
BACKUP_PATH=/var/lib/questionnaire-system/backups
BACKUP_ENABLED=true
WORKERS=4
PORT=5000
EOF

sudo chown www-data:www-data /opt/questionnaire-system/.env
sudo chmod 600 /opt/questionnaire-system/.env
```

#### 6. 初始化数据库

```bash
# 创建数据目录
sudo mkdir -p /var/lib/questionnaire-system
sudo chown -R www-data:www-data /var/lib/questionnaire-system

# 运行数据库迁移
sudo -u www-data bash -c "
    cd /opt/questionnaire-system/current
    source ../venv/bin/activate
    export DATABASE_PATH=/var/lib/questionnaire-system/questionnaires.db
    python migrate_db.py
    python migrate_db.py --create-admin --admin-username admin --admin-password 'your_password'
"
```

#### 7. 配置 Systemd 服务

```bash
# 创建服务文件
sudo tee /etc/systemd/system/questionnaire-system.service << EOF
[Unit]
Description=问卷数据管理系统
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/opt/questionnaire-system/current
Environment=PATH=/opt/questionnaire-system/venv/bin
EnvironmentFile=/opt/questionnaire-system/.env
ExecStart=/opt/questionnaire-system/venv/bin/gunicorn --config gunicorn.conf.py wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 启用并启动服务
sudo systemctl daemon-reload
sudo systemctl enable questionnaire-system
sudo systemctl start questionnaire-system
```

#### 8. 配置 Nginx

```bash
# 创建 Nginx 配置
sudo tee /etc/nginx/sites-available/questionnaire-system << EOF
server {
    listen 80;
    server_name your-domain.com;
    
    location /static/ {
        alias /opt/questionnaire-system/current/static/;
        expires 1y;
    }
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# 启用站点
sudo ln -s /etc/nginx/sites-available/questionnaire-system /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 方式三：Docker 部署

#### 1. 创建 Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# 复制应用文件
COPY requirements_production.txt .
RUN pip install --no-cache-dir -r requirements_production.txt

COPY . .

# 创建数据目录
RUN mkdir -p /app/data /app/logs /app/backups

# 设置权限
RUN useradd --system --shell /bin/bash app && \
    chown -R app:app /app

USER app

# 初始化数据库
RUN python migrate_db.py --db-path /app/data/questionnaires.db

EXPOSE 5000

CMD ["gunicorn", "--config", "gunicorn.conf.py", "wsgi:application"]
```

#### 2. 创建 docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=your-secret-key
      - DATABASE_PATH=/app/data/questionnaires.db
      - LOG_FILE=/app/logs/app.log
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./backups:/app/backups
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped
```

#### 3. 部署命令

```bash
# 构建并启动容器
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 配置说明

### 环境变量配置

| 变量名 | 说明 | 默认值 | 必需 |
|--------|------|--------|------|
| `SECRET_KEY` | Flask 密钥 | - | 是 |
| `DATABASE_PATH` | 数据库文件路径 | `/app/data/questionnaires.db` | 否 |
| `LOG_FILE` | 日志文件路径 | `/app/logs/app.log` | 否 |
| `BACKUP_ENABLED` | 是否启用自动备份 | `true` | 否 |
| `BACKUP_INTERVAL_HOURS` | 备份间隔（小时） | `24` | 否 |
| `WORKERS` | Gunicorn 工作进程数 | `4` | 否 |
| `PORT` | 应用端口 | `5000` | 否 |

### 数据库配置

#### SQLite（默认）
- 文件路径：`/var/lib/questionnaire-system/questionnaires.db`
- 自动创建和迁移
- 适合中小型部署

#### PostgreSQL（可选）
```bash
# 安装 PostgreSQL 支持
pip install psycopg2-binary

# 环境变量配置
export DATABASE_URL="postgresql://user:password@localhost/questionnaire_db"
```

### SSL/HTTPS 配置

#### 使用 Let's Encrypt

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取 SSL 证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加：0 12 * * * /usr/bin/certbot renew --quiet
```

#### 手动 SSL 配置

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    # SSL 配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # 其他配置...
}
```

## 监控和维护

### 系统监控

#### 健康检查
```bash
# 检查应用健康状态
curl http://localhost/health

# 检查系统指标
curl http://localhost/metrics
```

#### 日志监控
```bash
# 查看应用日志
sudo journalctl -u questionnaire-system -f

# 查看 Nginx 日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 备份和恢复

#### 自动备份
```bash
# 启用自动备份定时器
sudo systemctl enable questionnaire-system-backup.timer
sudo systemctl start questionnaire-system-backup.timer

# 查看备份状态
sudo systemctl status questionnaire-system-backup.timer
```

#### 手动备份
```bash
# 创建备份
cd /opt/questionnaire-system/current
python backup_system.py --backup

# 恢复备份
python backup_system.py --restore /path/to/backup
```

### 性能优化

#### 数据库优化
```bash
# 数据库清理和优化
sqlite3 /var/lib/questionnaire-system/questionnaires.db "VACUUM;"
sqlite3 /var/lib/questionnaire-system/questionnaires.db "ANALYZE;"
```

#### 缓存配置
```nginx
# Nginx 缓存配置
location /static/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}

location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 1M;
    add_header Cache-Control "public";
}
```

## 故障排除

### 常见问题

#### 1. 服务无法启动
```bash
# 检查服务状态
sudo systemctl status questionnaire-system

# 查看详细日志
sudo journalctl -u questionnaire-system -n 50

# 检查配置文件
sudo nginx -t
```

#### 2. 数据库连接失败
```bash
# 检查数据库文件权限
ls -la /var/lib/questionnaire-system/

# 检查数据库完整性
sqlite3 /var/lib/questionnaire-system/questionnaires.db "PRAGMA integrity_check;"
```

#### 3. 内存不足
```bash
# 检查内存使用
free -h
ps aux --sort=-%mem | head

# 调整 Gunicorn 工作进程数
# 编辑 /opt/questionnaire-system/.env
WORKERS=2
```

#### 4. 磁盘空间不足
```bash
# 检查磁盘使用
df -h

# 清理日志文件
sudo journalctl --vacuum-time=7d

# 清理旧备份
find /var/lib/questionnaire-system/backups -name "*.tar.gz" -mtime +30 -delete
```

### 日志分析

#### 应用日志位置
- 应用日志：`/var/log/questionnaire-system/app.log`
- Nginx 访问日志：`/var/log/nginx/access.log`
- Nginx 错误日志：`/var/log/nginx/error.log`
- 系统日志：`journalctl -u questionnaire-system`

#### 常见错误代码
- `500 Internal Server Error`：检查应用日志
- `502 Bad Gateway`：检查 Gunicorn 进程状态
- `503 Service Unavailable`：检查系统资源使用情况

## 安全配置

### 防火墙设置
```bash
# UFW 防火墙配置
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 安全加固
```bash
# 禁用不必要的服务
sudo systemctl disable apache2
sudo systemctl disable mysql

# 设置文件权限
sudo chmod 600 /opt/questionnaire-system/.env
sudo chmod 750 /var/lib/questionnaire-system

# 定期更新系统
sudo apt update && sudo apt upgrade -y
```

### 访问控制
```nginx
# IP 白名单（可选）
location /admin {
    allow 192.168.1.0/24;
    deny all;
    
    proxy_pass http://127.0.0.1:5000;
}
```

## 升级指南

### 应用升级
```bash
# 1. 备份当前版本
sudo systemctl stop questionnaire-system
sudo cp -r /opt/questionnaire-system/current /opt/questionnaire-system/backup_$(date +%Y%m%d)

# 2. 部署新版本
sudo cp -r /path/to/new/version/* /opt/questionnaire-system/current/

# 3. 更新依赖
sudo -u www-data bash -c "
    cd /opt/questionnaire-system
    source venv/bin/activate
    pip install -r current/requirements_production.txt
"

# 4. 运行数据库迁移
sudo -u www-data bash -c "
    cd /opt/questionnaire-system/current
    source ../venv/bin/activate
    python migrate_db.py
"

# 5. 重启服务
sudo systemctl start questionnaire-system
```

### 回滚操作
```bash
# 如果升级失败，回滚到备份版本
sudo systemctl stop questionnaire-system
sudo rm -rf /opt/questionnaire-system/current
sudo mv /opt/questionnaire-system/backup_YYYYMMDD /opt/questionnaire-system/current
sudo systemctl start questionnaire-system
```

## 联系支持

如果在部署过程中遇到问题，请：

1. 查看本文档的故障排除部分
2. 检查系统日志和应用日志
3. 确保系统满足最低要求
4. 联系技术支持团队

---

**注意**：本部署指南适用于生产环境。在部署前请确保已经在测试环境中验证了所有配置和功能。