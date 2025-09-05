"""
生产环境配置文件
"""

import os
from datetime import timedelta

class ProductionConfig:
    """生产环境配置"""
    
    # 基本配置
    DEBUG = False
    TESTING = False
    
    # 安全配置 - 必须从环境变量获取
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("生产环境必须设置 SECRET_KEY 环境变量")
    
    # 数据库配置
    DATABASE_PATH = os.environ.get('DATABASE_PATH', '/app/data/questionnaires.db')
    
    # 会话配置
    SESSION_PERMANENT = False
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)  # 生产环境2小时会话超时
    SESSION_FILE_DIR = os.environ.get('SESSION_FILE_DIR', '/app/sessions')
    
    # 安全配置
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # 分页配置
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', '/app/logs/app.log')
    
    # 性能配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB 最大请求大小
    
    # CORS 配置 - 生产环境更严格
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',') if os.environ.get('CORS_ORIGINS') else []
    
    # 监控配置
    ENABLE_MONITORING = os.environ.get('ENABLE_MONITORING', 'true').lower() == 'true'
    MONITORING_ENDPOINT = os.environ.get('MONITORING_ENDPOINT', '/health')
    
    # 备份配置
    BACKUP_ENABLED = os.environ.get('BACKUP_ENABLED', 'true').lower() == 'true'
    BACKUP_INTERVAL_HOURS = int(os.environ.get('BACKUP_INTERVAL_HOURS', '24'))
    BACKUP_RETENTION_DAYS = int(os.environ.get('BACKUP_RETENTION_DAYS', '30'))
    BACKUP_PATH = os.environ.get('BACKUP_PATH', '/app/backups')
    
    # 邮件配置（用于错误通知）
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
    
    # 速率限制配置
    RATELIMIT_ENABLED = os.environ.get('RATELIMIT_ENABLED', 'true').lower() == 'true'
    RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT', '100 per hour')
    
    @staticmethod
    def validate_config():
        """验证生产环境配置"""
        required_vars = ['SECRET_KEY']
        missing_vars = []
        
        for var in required_vars:
            if not os.environ.get(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"生产环境缺少必需的环境变量: {', '.join(missing_vars)}")
        
        # 验证数据库目录
        db_dir = os.path.dirname(ProductionConfig.DATABASE_PATH)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        # 验证会话目录
        if not os.path.exists(ProductionConfig.SESSION_FILE_DIR):
            os.makedirs(ProductionConfig.SESSION_FILE_DIR, exist_ok=True)
        
        # 验证日志目录
        log_dir = os.path.dirname(ProductionConfig.LOG_FILE)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # 验证备份目录
        if ProductionConfig.BACKUP_ENABLED and not os.path.exists(ProductionConfig.BACKUP_PATH):
            os.makedirs(ProductionConfig.BACKUP_PATH, exist_ok=True)
        
        return True

# 更新主配置文件的配置字典
config = {
    'development': 'config.DevelopmentConfig',
    'production': ProductionConfig,
    'testing': 'config.TestingConfig',
    'default': 'config.DevelopmentConfig'
}