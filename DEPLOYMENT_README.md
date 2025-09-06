# 问卷数据管理系统部署指南

## 概述

本文档提供了问卷数据管理系统的完整部署指南，包括 Docker 容器化部署、传统服务器部署和云平台部署等多种方式。

## 快速开始

### 使用 Docker 部署（推荐）

#### 前置要求

- Docker 20.10+ 
- Docker Compose 2.0+
- 2GB+ 可用内存
- 10GB+ 可用磁盘空间

#### 1. 克隆项目

```bash
git clone <repository-url>
cd prd-system
```

#### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置文件
nano .env
```

**重要配置项：**

```env
# 必须修改的配置
SECRET_KEY=your-super-secret-key-change-this-in-production
ADMIN_PASSWORD=your-admin-password
SERVER_NAME=your-domain.com
CORS_ORIGINS=https://your-domain.com

# 可选配置
LOG_LEVEL=INFO
BACKUP_ENABLED=true
BACKUP_INTERVAL_HOURS=24
```

#### 3. 部署系统

**Linux/macOS:**
```bash
# 使用部署脚本
chmod +x deploy-docker.sh
./deploy-docker.sh deploy prod
```

**Windows:**
```powershell
# 使用 PowerShell 脚本
.\deploy-docker.ps1 deploy prod
```

**手动部署:**
```bash
# 构建并启动服务
docker-compose up -d

# 检查服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

#### 4. 验证部署

```bash
# 健康检查
curl http://localhost/health

# 访问管理后台
open http://localhost/admin
```

## 详细部署选项

### 1. 生产环境部署

#### SSL/TLS 配置

1. **获取 SSL 证书**
   ```bash
   # 使用 Let's Encrypt
   certbot certonly --standalone -d your-domain.com
   
   # 复制证书到项目目录
   cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/cert.pem
   cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/key.pem
   ```

2. **配置自动续期**
   ```bash
   # 添加 crontab 任务
   echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -
   ```

#### 反向代理配置

如果使用外部 Nginx：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. 高可用部署

#### 负载均衡配置

```yaml
# docker-compose.ha.yml
version: '3.8'

services:
  app1:
    build: .
    environment:
      - INSTANCE_ID=app1
    volumes:
      - shared_data:/app/data
  
  app2:
    build: .
    environment:
      - INSTANCE_ID=app2
    volumes:
      - shared_data:/app/data
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx-ha.conf:/etc/nginx/nginx.conf
    depends_on:
      - app1
      - app2

volumes:
  shared_data:
    driver: local
```

#### 数据库集群

对于大规模部署，建议使用 PostgreSQL：

```yaml
  postgres-master:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=questionnaire
      - POSTGRES_USER=questionnaire
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_REPLICATION_MODE=master
      - POSTGRES_REPLICATION_USER=replicator
      - POSTGRES_REPLICATION_PASSWORD=${REPLICATION_PASSWORD}
    volumes:
      - postgres_master_data:/var/lib/postgresql/data
  
  postgres-slave:
    image: postgres:15-alpine
    environment:
      - POSTGRES_MASTER_SERVICE=postgres-master
      - POSTGRES_REPLICATION_MODE=slave
      - POSTGRES_REPLICATION_USER=replicator
      - POSTGRES_REPLICATION_PASSWORD=${REPLICATION_PASSWORD}
    volumes:
      - postgres_slave_data:/var/lib/postgresql/data
```

### 3. 云平台部署

#### AWS ECS 部署

1. **创建任务定义**
   ```json
   {
     "family": "questionnaire-system",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "512",
     "memory": "1024",
     "containerDefinitions": [
       {
         "name": "app",
         "image": "your-registry/questionnaire-system:latest",
         "portMappings": [
           {
             "containerPort": 5000,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {
             "name": "FLASK_ENV",
             "value": "production"
           }
         ],
         "secrets": [
           {
             "name": "SECRET_KEY",
             "valueFrom": "arn:aws:secretsmanager:region:account:secret:questionnaire/secret-key"
           }
         ]
       }
     ]
   }
   ```

2. **创建服务**
   ```bash
   aws ecs create-service \
     --cluster questionnaire-cluster \
     --service-name questionnaire-service \
     --task-definition questionnaire-system \
     --desired-count 2 \
     --launch-type FARGATE \
     --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}"
   ```

#### Kubernetes 部署

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: questionnaire-system
spec:
  replicas: 3
  selector:
    matchLabels:
      app: questionnaire-system
  template:
    metadata:
      labels:
        app: questionnaire-system
    spec:
      containers:
      - name: app
        image: your-registry/questionnaire-system:latest
        ports:
        - containerPort: 5000
        env:
        - name: FLASK_ENV
          value: "production"
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: questionnaire-secrets
              key: secret-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: questionnaire-service
spec:
  selector:
    app: questionnaire-system
  ports:
  - port: 80
    targetPort: 5000
  type: LoadBalancer
```

## 运维管理

### 监控和日志

#### 1. 健康检查

```bash
# 基本健康检查
curl http://localhost/health

# 详细健康检查
curl http://localhost/health?detailed=true
```

#### 2. 日志管理

```bash
# 查看应用日志
docker-compose logs -f app

# 查看 Nginx 日志
docker-compose logs -f nginx

# 导出日志
docker-compose logs --no-color app > app.log
```

#### 3. 性能监控

访问监控仪表板：
```
http://localhost/admin/monitoring
```

### 备份和恢复

#### 1. 自动备份

系统默认每24小时自动备份数据库：

```bash
# 查看备份文件
ls -la data/backups/

# 手动触发备份
./deploy-docker.sh backup
```

#### 2. 手动备份

```bash
# 备份数据库
docker-compose exec app sqlite3 /app/data/questionnaires.db ".backup /app/backups/manual-$(date +%Y%m%d_%H%M%S).db"

# 备份整个数据目录
tar -czf backup-$(date +%Y%m%d_%H%M%S).tar.gz data/
```

#### 3. 数据恢复

```bash
# 恢复数据库
./deploy-docker.sh restore /path/to/backup.db

# 手动恢复
docker-compose stop app
docker cp backup.db $(docker-compose ps -q app):/app/data/questionnaires.db
docker-compose start app
```

### 更新和升级

#### 1. 滚动更新

```bash
# 拉取最新镜像
docker-compose pull

# 滚动更新
docker-compose up -d --no-deps app

# 验证更新
curl http://localhost/health
```

#### 2. 回滚

```bash
# 查看镜像历史
docker images your-registry/questionnaire-system

# 回滚到指定版本
docker-compose stop app
docker tag your-registry/questionnaire-system:previous your-registry/questionnaire-system:latest
docker-compose up -d app
```

### 安全配置

#### 1. 防火墙设置

```bash
# Ubuntu/Debian
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# CentOS/RHEL
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

#### 2. 系统加固

```bash
# 禁用 root 登录
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart sshd

# 设置自动安全更新
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

## 故障排除

### 常见问题

#### 1. 容器启动失败

```bash
# 查看容器状态
docker-compose ps

# 查看启动日志
docker-compose logs app

# 检查配置文件
docker-compose config
```

#### 2. 数据库连接问题

```bash
# 检查数据库文件权限
ls -la data/questionnaires.db

# 进入容器检查
docker-compose exec app bash
sqlite3 /app/data/questionnaires.db ".tables"
```

#### 3. 网络连接问题

```bash
# 检查端口占用
netstat -tlnp | grep :5000

# 检查防火墙
sudo ufw status

# 测试内部连接
docker-compose exec nginx curl http://app:5000/health
```

#### 4. 性能问题

```bash
# 检查系统资源
docker stats

# 检查磁盘空间
df -h

# 检查内存使用
free -h
```

### 日志分析

#### 应用日志位置

- 应用日志：`logs/app.log`
- Nginx 访问日志：`logs/nginx/access.log`
- Nginx 错误日志：`logs/nginx/error.log`
- 系统日志：`journalctl -u docker`

#### 常见错误码

- `500 Internal Server Error`：检查应用日志和数据库连接
- `502 Bad Gateway`：检查应用容器是否正常运行
- `503 Service Unavailable`：检查健康检查是否通过
- `404 Not Found`：检查路由配置和静态文件

## 性能优化

### 1. 应用优化

```python
# 启用 Gzip 压缩
app.config['COMPRESS_MIMETYPES'] = [
    'text/html', 'text/css', 'text/xml',
    'application/json', 'application/javascript'
]

# 设置缓存头
@app.after_request
def after_request(response):
    if request.endpoint == 'static':
        response.cache_control.max_age = 31536000  # 1年
    return response
```

### 2. 数据库优化

```sql
-- 创建索引
CREATE INDEX idx_questionnaires_created_at ON questionnaires(created_at);
CREATE INDEX idx_responses_questionnaire_id ON responses(questionnaire_id);

-- 定期清理
DELETE FROM responses WHERE created_at < datetime('now', '-1 year');
VACUUM;
```

### 3. 系统优化

```bash
# 调整内核参数
echo 'net.core.somaxconn = 65535' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_max_syn_backlog = 65535' >> /etc/sysctl.conf
sysctl -p

# 优化 Docker
echo '{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}' > /etc/docker/daemon.json
sudo systemctl restart docker
```

## 联系支持

如果遇到部署问题，请：

1. 查看本文档的故障排除部分
2. 检查 GitHub Issues
3. 提供详细的错误日志和环境信息
4. 联系技术支持团队

---

**注意：** 在生产环境部署前，请务必：
- 修改所有默认密码
- 配置 SSL/TLS 证书
- 设置防火墙规则
- 配置监控和告警
- 制定备份策略
- 进行安全审计