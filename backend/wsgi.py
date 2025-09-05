"""
WSGI 入口文件 - 用于生产环境部署
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler

# 添加应用目录到 Python 路径
sys.path.insert(0, os.path.dirname(__file__))

from app import app
from config_production import ProductionConfig

def create_app():
    """创建生产环境应用实例"""
    
    # 设置生产环境
    os.environ.setdefault('FLASK_ENV', 'production')
    
    # 验证生产环境配置
    try:
        ProductionConfig.validate_config()
    except ValueError as e:
        print(f"配置验证失败: {e}")
        sys.exit(1)
    
    # 应用生产环境配置
    app.config.from_object(ProductionConfig)
    
    # 设置生产环境日志
    setup_logging(app)
    
    # 初始化数据库
    from app import init_db
    init_db()
    
    app.logger.info("问卷数据管理系统启动 - 生产环境")
    
    return app

def setup_logging(app):
    """设置生产环境日志"""
    
    # 创建日志目录
    log_dir = os.path.dirname(app.config['LOG_FILE'])
    os.makedirs(log_dir, exist_ok=True)
    
    # 设置日志级别
    log_level = getattr(logging, app.config['LOG_LEVEL'].upper(), logging.INFO)
    
    # 创建文件处理器 - 轮转日志
    file_handler = RotatingFileHandler(
        app.config['LOG_FILE'],
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10
    )
    
    # 设置日志格式
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s [%(name)s] %(message)s'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    
    # 添加到应用日志器
    app.logger.addHandler(file_handler)
    app.logger.setLevel(log_level)
    
    # 设置 Werkzeug 日志
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.addHandler(file_handler)
    werkzeug_logger.setLevel(log_level)
    
    # 禁用控制台日志（生产环境）
    app.logger.propagate = False

# 创建应用实例
application = create_app()

if __name__ == "__main__":
    # 开发模式运行
    application.run(host='0.0.0.0', port=5000, debug=False)