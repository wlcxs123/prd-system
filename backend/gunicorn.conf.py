"""
Gunicorn 配置文件
"""

import os
import multiprocessing

# 服务器配置
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"
workers = int(os.environ.get('WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2

# 进程配置
preload_app = True
daemon = False
user = os.environ.get('USER', 'www-data')
group = os.environ.get('GROUP', 'www-data')
pidfile = '/tmp/gunicorn.pid'

# 日志配置
accesslog = os.environ.get('ACCESS_LOG', '/app/logs/access.log')
errorlog = os.environ.get('ERROR_LOG', '/app/logs/error.log')
loglevel = os.environ.get('LOG_LEVEL', 'info').lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 安全配置
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# 性能配置
worker_tmp_dir = '/dev/shm'  # 使用内存文件系统提高性能

def when_ready(server):
    """服务器启动完成时的回调"""
    server.log.info("问卷数据管理系统已启动")

def worker_int(worker):
    """工作进程中断时的回调"""
    worker.log.info("工作进程 %s 正在关闭", worker.pid)

def on_exit(server):
    """服务器退出时的回调"""
    server.log.info("问卷数据管理系统已关闭")