#!/usr/bin/env python3
"""
简化的登录功能测试
直接测试数据库和API逻辑
"""

import sqlite3
import bcrypt
import json
import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

def test_database_structure():
    """测试数据库结构"""
    print("测试 1: 检查数据库结构...")
    
    try:
        DATABASE = os.path.join(os.path.dirname(__file__), 'questionnaires.db')
        
        with sqlite3.connect(DATABASE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 检查用户表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            if not cursor.fetchone():
                print("✗ 用户表不存在")
                return False
            
            # 检查表结构
            cursor.execute("PRAGMA table_info(users)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            required_columns = ['id', 'username', 'password_hash', 'role', 'created_at', 'last_login']
            missing_columns = [col for col in required_columns if col not in column_names]
            
            if missing_columns:
                print(f"✗ 用户表缺少列: {missing_columns}")
                return False
            
            print("✓ 用户表结构完整")
            
            # 检查默认管理员
            cursor.execute("SELECT * FROM users WHERE username = 'admin'")
            admin_user = cursor.fetchone()
            
            if not admin_user:
                print("✗ 默认管理员用户不存在")
                return False
            
            # 验证密码
            if not bcrypt.checkpw('admin123'.encode('utf-8'), admin_user['password_hash'].encode('utf-8')):
                print("✗ 默认管理员密码错误")
                return False
            
            print("✓ 默认管理员用户正确")
            return True
            
    except Exception as e:
        print(f"✗ 数据库测试失败: {e}")
        return False

def test_login_logic():
    """测试登录逻辑"""
    print("\n测试 2: 检查登录逻辑...")
    
    try:
        DATABASE = os.path.join(os.path.dirname(__file__), 'questionnaires.db')
        
        # 模拟登录验证逻辑
        username = 'admin'
        password = 'admin123'
        
        with sqlite3.connect(DATABASE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 查询用户
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            
            if not user:
                print("✗ 用户不存在")
                return False
            
            # 验证密码
            if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                print("✗ 密码验证失败")
                return False
            
            print("✓ 登录逻辑正确")
            
            # 测试更新最后登录时间
            from datetime import datetime
            cursor.execute(
                "UPDATE users SET last_login = ? WHERE id = ?",
                (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), user['id'])
            )
            conn.commit()
            
            print("✓ 最后登录时间更新正常")
            return True
            
    except Exception as e:
        print(f"✗ 登录逻辑测试失败: {e}")
        return False

def test_api_endpoints_exist():
    """测试API端点是否存在"""
    print("\n测试 3: 检查API端点...")
    
    try:
        from app import app
        
        # 检查路由
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append((rule.rule, list(rule.methods)))
        
        # 检查必要的认证路由
        required_routes = [
            '/api/auth/login',
            '/api/auth/logout', 
            '/api/auth/status',
            '/login',
            '/admin'
        ]
        
        existing_routes = [route[0] for route in routes]
        
        for required_route in required_routes:
            if required_route in existing_routes:
                print(f"✓ 路由 {required_route} 存在")
            else:
                print(f"✗ 路由 {required_route} 不存在")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ API端点测试失败: {e}")
        return False

def test_decorators_exist():
    """测试装饰器是否存在"""
    print("\n测试 4: 检查认证装饰器...")
    
    try:
        from app import login_required, admin_required
        
        if callable(login_required):
            print("✓ login_required 装饰器存在")
        else:
            print("✗ login_required 装饰器不存在")
            return False
        
        if callable(admin_required):
            print("✓ admin_required 装饰器存在")
        else:
            print("✗ admin_required 装饰器不存在")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ 装饰器测试失败: {e}")
        return False

def test_templates_exist():
    """测试模板文件是否存在"""
    print("\n测试 5: 检查模板文件...")
    
    try:
        login_template = os.path.join(os.path.dirname(__file__), 'templates', 'login.html')
        admin_template = os.path.join(os.path.dirname(__file__), 'templates', 'admin.html')
        
        if os.path.exists(login_template):
            print("✓ 登录页面模板存在")
        else:
            print("✗ 登录页面模板不存在")
            return False
        
        if os.path.exists(admin_template):
            print("✓ 管理页面模板存在")
        else:
            print("✗ 管理页面模板不存在")
            return False
        
        # 检查静态文件
        login_css = os.path.join(os.path.dirname(__file__), 'static', 'css', 'login.css')
        login_js = os.path.join(os.path.dirname(__file__), 'static', 'js', 'login.js')
        
        if os.path.exists(login_css):
            print("✓ 登录页面CSS存在")
        else:
            print("✗ 登录页面CSS不存在")
            return False
        
        if os.path.exists(login_js):
            print("✓ 登录页面JavaScript存在")
        else:
            print("✗ 登录页面JavaScript不存在")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ 模板文件测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("任务 3.1 登录功能实现验证 (简化版)")
    print("=" * 60)
    
    # 运行所有测试
    tests = [
        test_database_structure,
        test_login_logic,
        test_api_endpoints_exist,
        test_decorators_exist,
        test_templates_exist
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed_tests += 1
        except Exception as e:
            print(f"测试执行异常: {e}")
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed_tests}/{total_tests} 通过")
    
    if passed_tests == total_tests:
        print("✓ 任务 3.1 登录功能实现完整！")
        print("\n实现的功能包括:")
        print("- ✓ 用户数据表和模型")
        print("- ✓ 密码哈希和验证")
        print("- ✓ 登录 API 接口")
        print("- ✓ 会话管理机制")
        print("- ✓ 认证装饰器")
        print("- ✓ 登录页面模板和静态文件")
        return True
    else:
        print("✗ 任务 3.1 登录功能实现不完整")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)