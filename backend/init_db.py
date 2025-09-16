#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建数据库表结构和初始数据
"""

import sqlite3
import os
import bcrypt
from datetime import datetime

# 数据库文件路径
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'questionnaires.db')

def check_table_structure():
    """检查并更新表结构"""
    print("正在检查数据库表结构...")
    
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        
        # 检查问卷表是否存在以及结构
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='questionnaires'")
        if cursor.fetchone():
            # 表存在，检查列结构
            cursor.execute("PRAGMA table_info(questionnaires)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # 检查是否需要添加新列
            if 'gender' not in columns:
                print("正在添加 gender 列...")
                cursor.execute("ALTER TABLE questionnaires ADD COLUMN gender TEXT")
            
            if 'birthdate' not in columns:
                print("正在添加 birthdate 列...")
                cursor.execute("ALTER TABLE questionnaires ADD COLUMN birthdate TEXT")
            
            if 'grade' not in columns:
                print("正在添加 grade 列...")
                cursor.execute("ALTER TABLE questionnaires ADD COLUMN grade TEXT")
            
            if 'school' not in columns:
                print("正在添加 school 列...")
                cursor.execute("ALTER TABLE questionnaires ADD COLUMN school TEXT")
            
            if 'teacher' not in columns:
                print("正在添加 teacher 列...")
                cursor.execute("ALTER TABLE questionnaires ADD COLUMN teacher TEXT")
            
            if 'parent_phone' not in columns:
                print("正在添加 parent_phone 列...")
                cursor.execute("ALTER TABLE questionnaires ADD COLUMN parent_phone TEXT")
            
            if 'parent_wechat' not in columns:
                print("正在添加 parent_wechat 列...")
                cursor.execute("ALTER TABLE questionnaires ADD COLUMN parent_wechat TEXT")
            
            if 'parent_email' not in columns:
                print("正在添加 parent_email 列...")
                cursor.execute("ALTER TABLE questionnaires ADD COLUMN parent_email TEXT")
            
            if 'submission_date' not in columns:
                print("正在添加 submission_date 列...")
                cursor.execute("ALTER TABLE questionnaires ADD COLUMN submission_date DATE")
            
            if 'updated_at' not in columns:
                print("正在添加 updated_at 列...")
                cursor.execute("ALTER TABLE questionnaires ADD COLUMN updated_at TIMESTAMP")
            
            # 添加新的字段
            if 'school_name' not in columns:
                print("正在添加 school_name 列...")
                cursor.execute("ALTER TABLE questionnaires ADD COLUMN school_name TEXT")
            
            if 'admission_date' not in columns:
                print("正在添加 admission_date 列...")
                cursor.execute("ALTER TABLE questionnaires ADD COLUMN admission_date DATE")
            
            if 'address' not in columns:
                print("正在添加 address 列...")
                cursor.execute("ALTER TABLE questionnaires ADD COLUMN address TEXT")
            
            if 'filler_name' not in columns:
                print("正在添加 filler_name 列...")
                cursor.execute("ALTER TABLE questionnaires ADD COLUMN filler_name TEXT")
            
            if 'fill_date' not in columns:
                print("正在添加 fill_date 列...")
                cursor.execute("ALTER TABLE questionnaires ADD COLUMN fill_date DATE")
            
            # 迁移旧数据格式
            if 'birthdate' in columns:
                print("正在迁移旧数据格式...")
                cursor.execute("UPDATE questionnaires SET grade = birthdate WHERE grade IS NULL AND birthdate IS NOT NULL")
                cursor.execute("UPDATE questionnaires SET submission_date = DATE(created_at) WHERE submission_date IS NULL")
                cursor.execute("UPDATE questionnaires SET updated_at = created_at WHERE updated_at IS NULL")
        
        conn.commit()

def create_tables():
    """创建数据库表结构"""
    print("正在创建数据库表...")
    
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        
        # 创建问卷数据表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS questionnaires (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            name TEXT,
            gender TEXT,
            birthdate TEXT,
            grade TEXT,
            school TEXT,
            teacher TEXT,
            parent_phone TEXT,
            parent_wechat TEXT,
            parent_email TEXT,
            submission_date DATE,
            school_name TEXT,
            admission_date DATE,
            address TEXT,
            filler_name TEXT,
            fill_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data TEXT NOT NULL
        )
        ''')
        print("✓ 问卷数据表创建完成")
        
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
        print("✓ 用户认证表创建完成")
        
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
        print("✓ 操作日志表创建完成")
        
        conn.commit()

def create_default_admin():
    """创建默认管理员用户"""
    print("正在创建默认管理员用户...")
    
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        
        # 检查是否已存在管理员用户
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
        if cursor.fetchone()[0] > 0:
            print("✓ 管理员用户已存在，跳过创建")
            return
        
        # 创建默认管理员用户
        # 默认用户名: admin, 密码: admin123
        password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
        cursor.execute(
            "INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
            ('admin', password_hash.decode('utf-8'), 'admin', datetime.now().isoformat())
        )
        conn.commit()
        print("✓ 默认管理员用户创建完成")
        print("  用户名: admin")
        print("  密码: admin123")
        print("  请在生产环境中修改默认密码！")

def create_indexes():
    """创建数据库索引以提高查询性能"""
    print("正在创建数据库索引...")
    
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        
        # 为问卷表创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_questionnaires_type ON questionnaires(type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_questionnaires_name ON questionnaires(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_questionnaires_created_at ON questionnaires(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_questionnaires_submission_date ON questionnaires(submission_date)")
        
        # 为用户表创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
        
        # 为操作日志表创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_operation_logs_user_id ON operation_logs(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_operation_logs_created_at ON operation_logs(created_at)")
        
        conn.commit()
        print("✓ 数据库索引创建完成")

def verify_database():
    """验证数据库结构"""
    print("正在验证数据库结构...")
    
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['questionnaires', 'users', 'operation_logs']
        for table in expected_tables:
            if table in tables:
                print(f"✓ 表 '{table}' 存在")
            else:
                print(f"✗ 表 '{table}' 不存在")
                return False
        
        # 检查管理员用户
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
        admin_count = cursor.fetchone()[0]
        if admin_count > 0:
            print(f"✓ 找到 {admin_count} 个管理员用户")
        else:
            print("✗ 未找到管理员用户")
            return False
        
        return True

def main():
    """主函数"""
    print("=" * 50)
    print("问卷数据管理系统 - 数据库初始化")
    print("=" * 50)
    
    try:
        # 检查并更新表结构
        check_table_structure()
        
        # 创建数据库表
        create_tables()
        
        # 创建默认管理员用户
        create_default_admin()
        
        # 创建索引
        create_indexes()
        
        # 验证数据库
        if verify_database():
            print("\n" + "=" * 50)
            print("✓ 数据库初始化完成！")
            print("=" * 50)
            print(f"数据库文件位置: {DATABASE_PATH}")
            print("现在可以启动 Flask 应用程序了")
        else:
            print("\n" + "=" * 50)
            print("✗ 数据库验证失败！")
            print("=" * 50)
            
    except Exception as e:
        print(f"\n✗ 数据库初始化失败: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())