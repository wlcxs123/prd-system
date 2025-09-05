#!/bin/bash

# 问卷数据管理系统部署脚本
# 用于生产环境部署

set -e  # 遇到错误立即退出

# 配置变量
APP_NAME="questionnaire-system"
APP_DIR="/opt/${APP_NAME}"
USER="www-data"
GROUP="www-data"
PYTHON_VERSION="3.9"
VENV_DIR="${APP_DIR}/venv"
LOG_DIR="/var/log/${APP_NAME}"
DATA_DIR="/var/lib/${APP_NAME}"
BACKUP_DIR="${DATA_DIR}/backups"
NGINX_AVAILABLE="/etc/nginx/sites-available"
NGINX_ENABLED="/etc/nginx/sites-enabled"
SYSTEMD_DIR="/etc/systemd/system"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否为 root 用户
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "此脚本需要 root 权限运行"
        exit 1
    fi
}

# 检查系统要求
check_requirements() {
    log_info "检查系统要求..."
    
    # 检查操作系统
    if ! command -v apt-get &> /dev/null; then
        log_error "此脚本仅支持基于 Debian/Ubuntu 的系统"
        exit 1
    fi
    
    # 检查 Python 版本
    if ! command -v python3 &> /dev/null; then
        log_error "未找到 Python 3"
        exit 1
    fi
    
    # 检查磁盘空间（至少需要 1GB）
    available_space=$(df / | awk 'NR==2 {print $4}')
    if [[ $available_space -lt 1048576 ]]; then
        log_error "磁盘空间不足，至少需要 1GB 可用空间"
        exit 1
    fi
    
    log_info "系统要求检查通过"
}

# 安装系统依赖
install_dependencies() {
    log_info "安装系统依赖..."
    
    apt-get update
    apt-get install -y \
        python3 \
        python3-pip \
        python3-venv \
        nginx \
        supervisor \
        sqlite3 \
        curl \
        wget \
        unzip \
        logrotate \
        cron
    
    log_info "系统依赖安装完成"
}

# 创建用户和目录
setup_user_and_directories() {
    log_info "创建用户和目录..."
    
    # 创建应用用户（如果不存在）
    if ! id "$USER" &>/dev/null; then
        useradd --system --shell /bin/bash --home-dir "$APP_DIR" --create-home "$USER"
        log_info "创建用户: $USER"
    fi
    
    # 创建必要目录
    mkdir -p "$APP_DIR"
    mkdir -p "$LOG_DIR"
    mkdir -p "$DATA_DIR"
    mkdir -p "$BACKUP_DIR"
    mkdir -p "${DATA_DIR}/sessions"
    
    # 设置目录权限
    chown -R "$USER:$GROUP" "$APP_DIR"
    chown -R "$USER:$GROUP" "$LOG_DIR"
    chown -R "$USER:$GROUP" "$DATA_DIR"
    
    chmod 755 "$APP_DIR"
    chmod 755 "$LOG_DIR"
    chmod 750 "$DATA_DIR"
    chmod 750 "$BACKUP_DIR"
    
    log_info "用户和目录设置完成"
}

# 部署应用代码
deploy_application() {
    log_info "部署应用代码..."
    
    # 如果存在旧版本，先备份
    if [[ -d "${APP_DIR}/current" ]]; then
        log_info "备份当前版本..."
        mv "${APP_DIR}/current" "${APP_DIR}/backup_$(date +%Y%m%d_%H%M%S)"
    fi
    
    # 创建新的应用目录
    mkdir -p "${APP_DIR}/current"
    
    # 复制应用文件（假设当前目录包含应用代码）
    cp -r . "${APP_DIR}/current/"
    
    # 设置权限
    chown -R "$USER:$GROUP" "${APP_DIR}/current"
    
    log_info "应用代码部署完成"
}

# 设置 Python 虚拟环境
setup_python_environment() {
    log_info "设置 Python 虚拟环境..."
    
    # 创建虚拟环境
    sudo -u "$USER" python3 -m venv "$VENV_DIR"
    
    # 激活虚拟环境并安装依赖
    sudo -u "$USER" bash -c "
        source '$VENV_DIR/bin/activate'
        pip install --upgrade pip
        pip install -r '${APP_DIR}/current/requirements_production.txt'
    "
    
    log_info "Python 环境设置完成"
}

# 配置数据库
setup_database() {
    log_info "配置数据库..."
    
    # 设置数据库路径
    DB_PATH="${DATA_DIR}/questionnaires.db"
    
    # 运行数据库迁移
    sudo -u "$USER" bash -c "
        cd '${APP_DIR}/current'
        source '$VENV_DIR/bin/activate'
        export DATABASE_PATH='$DB_PATH'
        python migrate_db.py
    "
    
    # 创建默认管理员用户
    if [[ -n "${ADMIN_PASSWORD:-}" ]]; then
        sudo -u "$USER" bash -c "
            cd '${APP_DIR}/current'
            source '$VENV_DIR/bin/activate'
            export DATABASE_PATH='$DB_PATH'
            python migrate_db.py --create-admin --admin-username admin --admin-password '$ADMIN_PASSWORD'
        "
    else
        log_warn "未设置 ADMIN_PASSWORD 环境变量，跳过管理员用户创建"
    fi
    
    log_info "数据库配置完成"
}

# 配置环境变量
setup_environment() {
    log_info "配置环境变量..."
    
    # 生成随机密钥
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    
    # 创建环境变量文件
    cat > "${APP_DIR}/.env" << EOF
# 生产环境配置
FLASK_ENV=production
SECRET_KEY=${SECRET_KEY}
DATABASE_PATH=${DATA_DIR}/questionnaires.db
SESSION_FILE_DIR=${DATA_DIR}/sessions
LOG_FILE=${LOG_DIR}/app.log
BACKUP_PATH=${BACKUP_DIR}
BACKUP_ENABLED=true
BACKUP_INTERVAL_HOURS=24
BACKUP_RETENTION_DAYS=30

# 监控配置
ENABLE_MONITORING=true
MONITORING_ENDPOINT=/health

# 性能配置
WORKERS=4
PORT=5000

# 安全配置
CORS_ORIGINS=${CORS_ORIGINS:-}
EOF
    
    # 设置文件权限
    chown "$USER:$GROUP" "${APP_DIR}/.env"
    chmod 600 "${APP_DIR}/.env"
    
    log_info "环境变量配置完成"
}

# 配置 Systemd 服务
setup_systemd_service() {
    log_info "配置 Systemd 服务..."
    
    cat > "${SYSTEMD_DIR}/${APP_NAME}.service" << EOF
[Unit]
Description=问卷数据管理系统
After=network.target

[Service]
Type=exec
User=${USER}
Group=${GROUP}
WorkingDirectory=${APP_DIR}/current
Environment=PATH=${VENV_DIR}/bin
EnvironmentFile=${APP_DIR}/.env
ExecStart=${VENV_DIR}/bin/gunicorn --config gunicorn.conf.py wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=${APP_NAME}

# 安全配置
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=${DATA_DIR} ${LOG_DIR}

[Install]
WantedBy=multi-user.target
EOF
    
    # 配置备份服务
    cat > "${SYSTEMD_DIR}/${APP_NAME}-backup.service" << EOF
[Unit]
Description=问卷数据管理系统自动备份
After=network.target

[Service]
Type=oneshot
User=${USER}
Group=${GROUP}
WorkingDirectory=${APP_DIR}/current
Environment=PATH=${VENV_DIR}/bin
EnvironmentFile=${APP_DIR}/.env
ExecStart=${VENV_DIR}/bin/python backup_system.py --backup
StandardOutput=journal
StandardError=journal
SyslogIdentifier=${APP_NAME}-backup
EOF
    
    # 配置备份定时器
    cat > "${SYSTEMD_DIR}/${APP_NAME}-backup.timer" << EOF
[Unit]
Description=问卷数据管理系统定时备份
Requires=${APP_NAME}-backup.service

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
EOF
    
    # 重新加载 systemd 配置
    systemctl daemon-reload
    
    log_info "Systemd 服务配置完成"
}

# 配置 Nginx
setup_nginx() {
    log_info "配置 Nginx..."
    
    # 获取服务器名称
    SERVER_NAME=${SERVER_NAME:-$(hostname -f)}
    
    cat > "${NGINX_AVAILABLE}/${APP_NAME}" << EOF
server {
    listen 80;
    server_name ${SERVER_NAME};
    
    # 安全头
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # 日志配置
    access_log ${LOG_DIR}/nginx_access.log;
    error_log ${LOG_DIR}/nginx_error.log;
    
    # 静态文件
    location /static/ {
        alias ${APP_DIR}/current/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # 健康检查
    location /health {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        access_log off;
    }
    
    # 应用代理
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # 超时配置
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
        
        # 缓冲配置
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
    
    # 限制文件上传大小
    client_max_body_size 16M;
}
EOF
    
    # 启用站点
    ln -sf "${NGINX_AVAILABLE}/${APP_NAME}" "${NGINX_ENABLED}/${APP_NAME}"
    
    # 测试 Nginx 配置
    nginx -t
    
    log_info "Nginx 配置完成"
}

# 配置日志轮转
setup_logrotate() {
    log_info "配置日志轮转..."
    
    cat > "/etc/logrotate.d/${APP_NAME}" << EOF
${LOG_DIR}/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 ${USER} ${GROUP}
    postrotate
        systemctl reload ${APP_NAME} > /dev/null 2>&1 || true
    endscript
}
EOF
    
    log_info "日志轮转配置完成"
}

# 配置防火墙
setup_firewall() {
    log_info "配置防火墙..."
    
    if command -v ufw &> /dev/null; then
        ufw allow 22/tcp   # SSH
        ufw allow 80/tcp   # HTTP
        ufw allow 443/tcp  # HTTPS
        ufw --force enable
        log_info "UFW 防火墙配置完成"
    else
        log_warn "未找到 UFW，跳过防火墙配置"
    fi
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    # 启用并启动应用服务
    systemctl enable "${APP_NAME}.service"
    systemctl start "${APP_NAME}.service"
    
    # 启用并启动备份定时器
    systemctl enable "${APP_NAME}-backup.timer"
    systemctl start "${APP_NAME}-backup.timer"
    
    # 重启 Nginx
    systemctl restart nginx
    
    # 检查服务状态
    sleep 5
    
    if systemctl is-active --quiet "${APP_NAME}.service"; then
        log_info "应用服务启动成功"
    else
        log_error "应用服务启动失败"
        systemctl status "${APP_NAME}.service"
        exit 1
    fi
    
    if systemctl is-active --quiet nginx; then
        log_info "Nginx 服务运行正常"
    else
        log_error "Nginx 服务异常"
        systemctl status nginx
        exit 1
    fi
    
    log_info "所有服务启动完成"
}

# 运行部署后测试
run_deployment_tests() {
    log_info "运行部署后测试..."
    
    # 测试健康检查端点
    if curl -f -s "http://localhost/health" > /dev/null; then
        log_info "健康检查端点测试通过"
    else
        log_error "健康检查端点测试失败"
        exit 1
    fi
    
    # 测试主页面
    if curl -f -s "http://localhost/" > /dev/null; then
        log_info "主页面测试通过"
    else
        log_warn "主页面测试失败，可能需要手动检查"
    fi
    
    log_info "部署后测试完成"
}

# 显示部署信息
show_deployment_info() {
    log_info "部署完成！"
    echo
    echo "=========================================="
    echo "问卷数据管理系统部署信息"
    echo "=========================================="
    echo "应用目录: ${APP_DIR}/current"
    echo "数据目录: ${DATA_DIR}"
    echo "日志目录: ${LOG_DIR}"
    echo "备份目录: ${BACKUP_DIR}"
    echo "访问地址: http://${SERVER_NAME:-$(hostname -f)}"
    echo "健康检查: http://${SERVER_NAME:-$(hostname -f)}/health"
    echo
    echo "服务管理命令:"
    echo "  启动服务: systemctl start ${APP_NAME}"
    echo "  停止服务: systemctl stop ${APP_NAME}"
    echo "  重启服务: systemctl restart ${APP_NAME}"
    echo "  查看状态: systemctl status ${APP_NAME}"
    echo "  查看日志: journalctl -u ${APP_NAME} -f"
    echo
    echo "数据库管理:"
    echo "  迁移数据库: cd ${APP_DIR}/current && python migrate_db.py"
    echo "  创建备份: cd ${APP_DIR}/current && python backup_system.py --backup"
    echo
    echo "默认管理员账户:"
    echo "  用户名: admin"
    echo "  密码: ${ADMIN_PASSWORD:-请手动创建}"
    echo "=========================================="
}

# 主函数
main() {
    log_info "开始部署问卷数据管理系统..."
    
    check_root
    check_requirements
    install_dependencies
    setup_user_and_directories
    deploy_application
    setup_python_environment
    setup_database
    setup_environment
    setup_systemd_service
    setup_nginx
    setup_logrotate
    setup_firewall
    start_services
    run_deployment_tests
    show_deployment_info
    
    log_info "部署完成！"
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi