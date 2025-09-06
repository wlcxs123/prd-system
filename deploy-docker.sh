#!/bin/bash

# 问卷数据管理系统 Docker 部署脚本
# 使用方法: ./deploy-docker.sh [环境]
# 环境选项: dev, staging, prod

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    log_info "检查系统依赖..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    log_success "依赖检查完成"
}

# 设置环境变量
setup_environment() {
    local env=${1:-prod}
    
    log_info "设置 ${env} 环境变量..."
    
    # 检查 .env 文件
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            log_warning ".env 文件不存在，从 .env.example 复制"
            cp .env.example .env
            log_warning "请编辑 .env 文件并设置正确的配置值"
        else
            log_error ".env.example 文件不存在"
            exit 1
        fi
    fi
    
    # 生成随机密钥（如果需要）
    if grep -q "your-super-secret-key-change-this-in-production" .env; then
        log_info "生成随机 SECRET_KEY..."
        SECRET_KEY=$(openssl rand -hex 32)
        sed -i "s/your-super-secret-key-change-this-in-production/${SECRET_KEY}/g" .env
    fi
    
    log_success "环境变量设置完成"
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    
    mkdir -p ssl
    mkdir -p data/backups
    mkdir -p logs
    
    log_success "目录创建完成"
}

# 生成自签名SSL证书（用于测试）
generate_ssl_cert() {
    if [ ! -f "ssl/cert.pem" ] || [ ! -f "ssl/key.pem" ]; then
        log_info "生成自签名 SSL 证书（仅用于测试）..."
        
        openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem \
            -days 365 -nodes -subj "/C=CN/ST=State/L=City/O=Organization/CN=localhost"
        
        log_warning "已生成自签名证书，生产环境请使用正式证书"
    fi
}

# 构建镜像
build_image() {
    log_info "构建 Docker 镜像..."
    
    docker-compose build --no-cache
    
    log_success "镜像构建完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    docker-compose up -d
    
    log_success "服务启动完成"
}

# 等待服务就绪
wait_for_services() {
    log_info "等待服务就绪..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost/health &> /dev/null; then
            log_success "服务已就绪"
            return 0
        fi
        
        log_info "等待服务启动... ($attempt/$max_attempts)"
        sleep 10
        ((attempt++))
    done
    
    log_error "服务启动超时"
    return 1
}

# 显示服务状态
show_status() {
    log_info "服务状态:"
    docker-compose ps
    
    echo
    log_info "服务日志:"
    docker-compose logs --tail=20
    
    echo
    log_info "访问地址:"
    echo "  HTTP:  http://localhost"
    echo "  HTTPS: https://localhost"
    echo "  管理后台: http://localhost/admin"
}

# 停止服务
stop_services() {
    log_info "停止服务..."
    docker-compose down
    log_success "服务已停止"
}

# 清理资源
cleanup() {
    log_info "清理 Docker 资源..."
    docker-compose down -v --rmi all
    docker system prune -f
    log_success "清理完成"
}

# 备份数据
backup_data() {
    log_info "备份数据..."
    
    local backup_dir="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # 备份数据库
    docker-compose exec -T app sqlite3 /app/data/questionnaires.db ".backup /app/backups/db_backup.db"
    docker cp "$(docker-compose ps -q app):/app/backups/db_backup.db" "$backup_dir/"
    
    # 备份配置文件
    cp .env "$backup_dir/"
    
    log_success "数据备份完成: $backup_dir"
}

# 恢复数据
restore_data() {
    local backup_file=$1
    
    if [ -z "$backup_file" ]; then
        log_error "请指定备份文件路径"
        exit 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        log_error "备份文件不存在: $backup_file"
        exit 1
    fi
    
    log_info "恢复数据: $backup_file"
    
    docker cp "$backup_file" "$(docker-compose ps -q app):/app/data/questionnaires.db"
    docker-compose restart app
    
    log_success "数据恢复完成"
}

# 显示帮助信息
show_help() {
    echo "问卷数据管理系统 Docker 部署脚本"
    echo
    echo "使用方法:"
    echo "  $0 [命令] [选项]"
    echo
    echo "命令:"
    echo "  deploy [env]    部署系统 (env: dev|staging|prod, 默认: prod)"
    echo "  start           启动服务"
    echo "  stop            停止服务"
    echo "  restart         重启服务"
    echo "  status          显示服务状态"
    echo "  logs            显示服务日志"
    echo "  backup          备份数据"
    echo "  restore <file>  恢复数据"
    echo "  cleanup         清理 Docker 资源"
    echo "  help            显示帮助信息"
    echo
    echo "示例:"
    echo "  $0 deploy prod    # 部署生产环境"
    echo "  $0 start          # 启动服务"
    echo "  $0 backup         # 备份数据"
}

# 主函数
main() {
    local command=${1:-deploy}
    local env=${2:-prod}
    
    case $command in
        "deploy")
            check_dependencies
            setup_environment $env
            create_directories
            generate_ssl_cert
            build_image
            start_services
            wait_for_services
            show_status
            ;;
        "start")
            start_services
            wait_for_services
            show_status
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            stop_services
            start_services
            wait_for_services
            show_status
            ;;
        "status")
            show_status
            ;;
        "logs")
            docker-compose logs -f
            ;;
        "backup")
            backup_data
            ;;
        "restore")
            restore_data $2
            ;;
        "cleanup")
            cleanup
            ;;
        "help")
            show_help
            ;;
        *)
            log_error "未知命令: $command"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"