# 部署验证清单

## 📋 部署文件检查

### ✅ 核心配置文件
- [x] `Dockerfile` - Docker容器配置
- [x] `docker-compose.yml` - 多容器编排配置
- [x] `nginx.conf` - 反向代理和负载均衡配置
- [x] `.env.example` - 环境变量模板

### ✅ 部署脚本
- [x] `deploy-docker.sh` - Linux/macOS部署脚本
- [x] `deploy-docker.ps1` - Windows PowerShell部署脚本

### ✅ CI/CD配置
- [x] `.github/workflows/deploy.yml` - GitHub Actions自动化部署

### ✅ 监控和健康检查
- [x] `backend/health_check.py` - 应用健康检查端点
- [x] `backend/wsgi.py` - 生产环境WSGI入口（已存在）
- [x] `backend/monitoring.py` - 性能监控（已存在）

### ✅ 文档
- [x] `DEPLOYMENT_README.md` - 详细部署指南
- [x] `backend/DEPLOYMENT_GUIDE.md` - 原有部署文档（已存在）

## 🔧 部署前准备

### 环境要求
1. **Docker环境**（推荐）
   - Docker Engine 20.10+
   - Docker Compose 2.0+

2. **传统部署**
   - Python 3.8+
   - Nginx 1.18+
   - PostgreSQL 12+ 或 SQLite

### 配置步骤
1. 复制 `.env.example` 为 `.env`
2. 修改环境变量配置
3. 生成SSL证书（生产环境）
4. 配置数据库连接

## 🚀 部署方式

### 方式一：Docker容器化部署（推荐）
```bash
# Linux/macOS
./deploy-docker.sh deploy

# Windows
.\deploy-docker.ps1 -Action deploy
```

### 方式二：传统服务器部署
参考 `backend/DEPLOYMENT_GUIDE.md`

### 方式三：CI/CD自动部署
推送代码到GitHub，自动触发部署流程

## 📊 部署验证

### 健康检查
- 访问 `/health` 端点验证应用状态
- 检查数据库连接
- 验证静态文件服务

### 性能监控
- 查看 `/metrics` 端点获取性能指标
- 监控系统资源使用情况
- 检查日志文件

## 🔒 安全配置

### 必须配置项
- [x] 更改默认密钥和密码
- [x] 配置HTTPS证书
- [x] 设置防火墙规则
- [x] 配置访问控制

### 可选配置项
- [ ] 配置WAF（Web应用防火墙）
- [ ] 设置监控告警
- [ ] 配置备份策略

## 📝 部署后操作

1. **验证部署**
   - 访问应用首页
   - 测试核心功能
   - 检查日志输出

2. **性能优化**
   - 调整worker进程数
   - 优化数据库连接池
   - 配置缓存策略

3. **监控设置**
   - 配置日志轮转
   - 设置告警阈值
   - 建立备份计划

## 🆘 故障排除

### 常见问题
1. **容器启动失败**
   - 检查Docker服务状态
   - 验证环境变量配置
   - 查看容器日志

2. **数据库连接错误**
   - 验证数据库服务状态
   - 检查连接字符串
   - 确认网络连通性

3. **静态文件404**
   - 检查Nginx配置
   - 验证文件路径
   - 确认权限设置

### 日志查看
```bash
# Docker部署
docker-compose logs -f app

# 传统部署
tail -f /var/log/questionnaire/app.log
```

## 📞 技术支持

如遇到部署问题，请参考：
1. `DEPLOYMENT_README.md` - 详细部署指南
2. `backend/DEPLOYMENT_GUIDE.md` - 原有部署文档
3. 项目日志文件
4. GitHub Issues

---

**部署状态**: ✅ 所有配置文件已创建并验证
**最后更新**: 2025年1月6日
**版本**: v1.0.0