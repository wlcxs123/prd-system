#!/usr/bin/env python3
"""
数据库迁移脚本
用于生产环境数据库初始化和升级
"""

import os
import sys
import sqlite3
import json
import shutil
from datetime import datetime
import argparse

def backup_database(db_path, backup_dir):
    """备份数据库"""
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return None
    
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f'questionnaires_backup_{timestamp}.db')
    
    try:
        shutil.copy2(db_path, backup_path)
        print(f"数据库备份完成: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"数据库备份失败: {e}")
        return None

def get_db_version(db_path):
    """获取数据库版本"""
    if not os.path.exists(db_path):
        return 0
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # 检查是否存在版本表
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='db_version'
            """)
            
            if not cursor.fetchone():
                return 1  # 假设是第一个版本
            
            cursor.execute("SELECT version FROM db_version ORDER BY id DESC LIMIT 1")
            result = cursor.fetchone()
            return result[0] if result else 1
            
    except Exception as e:
        print(f"获取数据库版本失败: {e}")
        return 0

def create_version_table(conn):
    """创建版本表"""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS db_version (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version INTEGER NOT NULL,
            description TEXT,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

def apply_migration_v1(conn):
    """应用版本1迁移 - 初始数据库结构"""
    cursor = conn.cursor()
    
    print("应用迁移 v1: 创建初始数据库结构...")
    
    # 创建问卷数据表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questionnaires (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            name TEXT,
            grade TEXT,
            submission_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data TEXT NOT NULL
        )
    ''')
    
    # 创建用户认证表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'admin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # 创建操作日志表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS operation_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            operation TEXT NOT NULL,
            target_id INTEGER,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    print("v1 迁移完成")

def apply_migration_v2(conn):
    """应用版本2迁移 - 添加索引和性能优化"""
    cursor = conn.cursor()
    
    print("应用迁移 v2: 添加索引和性能优化...")
    
    # 为问卷表添加索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_questionnaires_type ON questionnaires(type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_questionnaires_name ON questionnaires(name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_questionnaires_grade ON questionnaires(grade)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_questionnaires_created_at ON questionnaires(created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_questionnaires_submission_date ON questionnaires(submission_date)")
    
    # 为操作日志表添加索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_operation_logs_user_id ON operation_logs(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_operation_logs_operation ON operation_logs(operation)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_operation_logs_created_at ON operation_logs(created_at)")
    
    # 为用户表添加索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_last_login ON users(last_login)")
    
    conn.commit()
    print("v2 迁移完成")

def apply_migration_v3(conn):
    """应用版本3迁移 - 添加系统配置表"""
    cursor = conn.cursor()
    
    print("应用迁移 v3: 添加系统配置表...")
    
    # 创建系统配置表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 插入默认配置
    default_configs = [
        ('system_name', '问卷数据管理系统', '系统名称'),
        ('max_file_size', '16777216', '最大文件上传大小（字节）'),
        ('session_timeout', '7200', '会话超时时间（秒）'),
        ('backup_enabled', 'true', '是否启用自动备份'),
        ('backup_interval', '86400', '备份间隔（秒）')
    ]
    
    for key, value, description in default_configs:
        cursor.execute("""
            INSERT OR IGNORE INTO system_config (key, value, description) 
            VALUES (?, ?, ?)
        """, (key, value, description))
    
    conn.commit()
    print("v3 迁移完成")

# 迁移函数映射
MIGRATIONS = {
    1: apply_migration_v1,
    2: apply_migration_v2,
    3: apply_migration_v3,
}

CURRENT_VERSION = max(MIGRATIONS.keys())

def migrate_database(db_path, target_version=None, backup_dir=None):
    """执行数据库迁移"""
    
    if target_version is None:
        target_version = CURRENT_VERSION
    
    # 获取当前版本
    current_version = get_db_version(db_path)
    print(f"当前数据库版本: {current_version}")
    print(f"目标版本: {target_version}")
    
    if current_version >= target_version:
        print("数据库已是最新版本，无需迁移")
        return True
    
    # 备份数据库
    if backup_dir and current_version > 0:
        backup_path = backup_database(db_path, backup_dir)
        if not backup_path:
            print("数据库备份失败，迁移中止")
            return False
    
    try:
        # 确保数据库目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        with sqlite3.connect(db_path) as conn:
            # 创建版本表
            create_version_table(conn)
            
            # 应用迁移
            for version in range(current_version + 1, target_version + 1):
                if version in MIGRATIONS:
                    print(f"应用迁移到版本 {version}...")
                    MIGRATIONS[version](conn)
                    
                    # 记录版本
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO db_version (version, description) VALUES (?, ?)",
                        (version, f"迁移到版本 {version}")
                    )
                    conn.commit()
                    print(f"版本 {version} 迁移完成")
                else:
                    print(f"警告: 未找到版本 {version} 的迁移脚本")
        
        print(f"数据库迁移完成，当前版本: {target_version}")
        return True
        
    except Exception as e:
        print(f"数据库迁移失败: {e}")
        return False

def create_admin_user(db_path, username, password):
    """创建管理员用户"""
    try:
        import bcrypt
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # 检查用户是否已存在
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                print(f"用户 {username} 已存在")
                return False
            
            # 创建用户
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, password_hash.decode('utf-8'), 'admin')
            )
            conn.commit()
            
            print(f"管理员用户 {username} 创建成功")
            return True
            
    except Exception as e:
        print(f"创建管理员用户失败: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='问卷数据管理系统数据库迁移工具')
    parser.add_argument('--db-path', default='questionnaires.db', help='数据库文件路径')
    parser.add_argument('--backup-dir', default='./backups', help='备份目录')
    parser.add_argument('--target-version', type=int, help='目标版本号')
    parser.add_argument('--create-admin', action='store_true', help='创建管理员用户')
    parser.add_argument('--admin-username', default='admin', help='管理员用户名')
    parser.add_argument('--admin-password', help='管理员密码')
    parser.add_argument('--check-version', action='store_true', help='检查数据库版本')
    
    args = parser.parse_args()
    
    if args.check_version:
        version = get_db_version(args.db_path)
        print(f"数据库版本: {version}")
        print(f"最新版本: {CURRENT_VERSION}")
        return
    
    if args.create_admin:
        if not args.admin_password:
            import getpass
            args.admin_password = getpass.getpass("请输入管理员密码: ")
        
        create_admin_user(args.db_path, args.admin_username, args.admin_password)
        return
    
    # 执行迁移
    success = migrate_database(args.db_path, args.target_version, args.backup_dir)
    
    if success:
        print("数据库迁移成功完成")
        sys.exit(0)
    else:
        print("数据库迁移失败")
        sys.exit(1)

if __name__ == '__main__':
    main()