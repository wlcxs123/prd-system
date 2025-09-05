"""
Flask 应用配置文件
"""

import os
from datetime import timedelta

class Config:
    """基础配置类"""
    
    # 基本配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # 数据库配置
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'questionnaires.db')
    
    # 会话配置
    SESSION_PERMANENT = False
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)  # 1小时会话超时
    
    # 安全配置
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # 分页配置
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False
    
    # 生产环境使用环境变量中的密钥，如果没有则使用默认值（不推荐）
    SECRET_KEY = os.environ.get('SECRET_KEY', Config.SECRET_KEY)

class TestingConfig(Config):
    """测试环境配置"""
    DEBUG = True
    TESTING = True
    DATABASE_PATH = ':memory:'  # 使用内存数据库进行测试

# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}