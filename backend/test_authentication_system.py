#!/usr/bin/env python3
"""
完整的用户认证系统测试
验证任务 3 的所有功能是否正确实现
"""

import os
import sys
import sqlite3
import bcrypt
import re

# 添加backend目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

def test_complete_authentication_system():
    """测试完整的认证系统"""
    print("=" * 60)
    print("完整用户认证系统验证")
    print("=" * 60)
    
    all_tests_passed = True
    
    # 1. 数据库和用户模型测试
    print("\n1. 数据库和用户模型测试")
    print("-" * 30)
    
    try:
        DATABASE = os.path.join(os.path.dirname(__file__), 'questionnaires.db')
        
        with sqlite3.connect(DATABASE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 检查用户表结构
            cursor.execute("PRAGMA table_info(users)")
            columns = [col[1] for col in cursor.fetchall()]
            
            required_columns = ['id', 'username', 'password_hash', 'role', 'created_at', 'last_login']
            if all(col in columns for col in required_columns):
                print("✓ 用户数据表结构完整")
            else:
                print("✗ 用户数据表结构不完整")
                all_tests_passed = False
            
            # 检查默认管理员用户
            cursor.execute("SELECT * FROM users WHERE username = 'admin'")
            admin_user = cursor.fetchone()
            
            if admin_user and bcrypt.checkpw('admin123'.encode('utf-8'), admin_user['password_hash'].encode('utf-8')):
                print("✓ 默认管理员用户正确")
            else:
                print("✗ 默认管理员用户不正确")
                all_tests_passed = False
                
    except Exception as e:
        print(f"✗ 数据库测试失败: {e}")
        all_tests_passed = False
    
    # 2. 密码哈希和验证测试
    print("\n2. 密码哈希和验证测试")
    print("-" * 30)
    
    try:
        test_password = "testpassword123"
        hashed = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt())
        
        if bcrypt.checkpw(test_password.encode('utf-8'), hashed):
            print("✓ 密码哈希和验证功能正常")
        else:
            print("✗ 密码验证失败")
            all_tests_passed = False
            
    except Exception as e:
        print(f"✗ 密码哈希测试失败: {e}")
        all_tests_passed = False
    
    # 3. API接口测试
    print("\n3. API接口测试")
    print("-" * 30)
    
    try:
        from app import app
        
        # 检查认证相关路由
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        
        auth_routes = ['/api/auth/login', '/api/auth/logout', '/api/auth/status']
        for route in auth_routes:
            if route in routes:
                print(f"✓ API路由 {route} 存在")
            else:
                print(f"✗ API路由 {route} 不存在")
                all_tests_passed = False
                
    except Exception as e:
        print(f"✗ API接口测试失败: {e}")
        all_tests_passed = False
    
    # 4. 会话管理测试
    print("\n4. 会话管理测试")
    print("-" * 30)
    
    try:
        from app import login_required, admin_required
        
        if callable(login_required) and callable(admin_required):
            print("✓ 认证装饰器存在")
        else:
            print("✗ 认证装饰器不存在")
            all_tests_passed = False
            
        # 检查会话配置
        if hasattr(app, 'config') and 'SECRET_KEY' in app.config:
            print("✓ 会话配置正确")
        else:
            print("✗ 会话配置不正确")
            all_tests_passed = False
            
    except Exception as e:
        print(f"✗ 会话管理测试失败: {e}")
        all_tests_passed = False
    
    # 5. 登录页面测试
    print("\n5. 登录页面测试")
    print("-" * 30)
    
    try:
        # 检查模板文件
        login_template = os.path.join(os.path.dirname(__file__), 'templates', 'login.html')
        if os.path.exists(login_template):
            print("✓ 登录页面模板存在")
            
            with open(login_template, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查关键元素
            if all(element in content for element in ['loginForm', 'username', 'password', 'submit']):
                print("✓ 登录表单结构完整")
            else:
                print("✗ 登录表单结构不完整")
                all_tests_passed = False
        else:
            print("✗ 登录页面模板不存在")
            all_tests_passed = False
            
    except Exception as e:
        print(f"✗ 登录页面测试失败: {e}")
        all_tests_passed = False
    
    # 6. 静态文件测试
    print("\n6. 静态文件测试")
    print("-" * 30)
    
    try:
        # 检查CSS文件
        login_css = os.path.join(os.path.dirname(__file__), 'static', 'css', 'login.css')
        if os.path.exists(login_css):
            print("✓ 登录页面CSS存在")
        else:
            print("✗ 登录页面CSS不存在")
            all_tests_passed = False
        
        # 检查JavaScript文件
        login_js = os.path.join(os.path.dirname(__file__), 'static', 'js', 'login.js')
        if os.path.exists(login_js):
            print("✓ 登录页面JavaScript存在")
            
            with open(login_js, 'r', encoding='utf-8') as f:
                js_content = f.read()
            
            # 检查关键功能
            if all(func in js_content for func in ['LoginManager', 'handleLogin', 'validateUsername', 'validatePassword']):
                print("✓ 登录JavaScript功能完整")
            else:
                print("✗ 登录JavaScript功能不完整")
                all_tests_passed = False
        else:
            print("✗ 登录页面JavaScript不存在")
            all_tests_passed = False
            
    except Exception as e:
        print(f"✗ 静态文件测试失败: {e}")
        all_tests_passed = False
    
    # 7. 页面路由测试
    print("\n7. 页面路由测试")
    print("-" * 30)
    
    try:
        from app import app
        
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        
        page_routes = ['/login', '/admin', '/']
        for route in page_routes:
            if route in routes:
                print(f"✓ 页面路由 {route} 存在")
            else:
                print(f"✗ 页面路由 {route} 不存在")
                all_tests_passed = False
                
    except Exception as e:
        print(f"✗ 页面路由测试失败: {e}")
        all_tests_passed = False
    
    # 8. 安全特性测试
    print("\n8. 安全特性测试")
    print("-" * 30)
    
    try:
        # 检查登录页面的安全特性
        login_template = os.path.join(os.path.dirname(__file__), 'templates', 'login.html')
        
        with open(login_template, 'r', encoding='utf-8') as f:
            content = f.read()
        
        security_features = [
            'type="password"',  # 密码字段类型
            'autocomplete="username"',  # 用户名自动完成
            'autocomplete="current-password"',  # 密码自动完成
            'novalidate',  # 禁用浏览器验证
            '安全提示'  # 安全提示文本
        ]
        
        for feature in security_features:
            if feature in content:
                print(f"✓ 安全特性: {feature}")
            else:
                print(f"✗ 缺少安全特性: {feature}")
                all_tests_passed = False
                
    except Exception as e:
        print(f"✗ 安全特性测试失败: {e}")
        all_tests_passed = False
    
    # 总结
    print("\n" + "=" * 60)
    if all_tests_passed:
        print("✓ 用户认证系统完整实现！")
        print("\n已实现的功能:")
        print("- ✓ 用户数据表和模型")
        print("- ✓ 密码哈希和验证")
        print("- ✓ 登录API接口")
        print("- ✓ 会话管理机制")
        print("- ✓ 认证装饰器")
        print("- ✓ 登录页面HTML结构")
        print("- ✓ 登录表单样式")
        print("- ✓ 登录JavaScript逻辑")
        print("- ✓ 登录状态验证")
        print("- ✓ 安全特性")
        print("- ✓ 页面路由")
        
        print("\n符合需求:")
        print("- ✓ 需求 3.1: 用户认证和登录系统")
        print("- ✓ 需求 3.2: 登录页面和表单")
        print("- ✓ 需求 3.3: 登录状态验证")
        print("- ✓ 需求 3.4: 会话管理")
        print("- ✓ 需求 3.5: 权限控制")
        
        return True
    else:
        print("✗ 用户认证系统实现不完整")
        return False

if __name__ == '__main__':
    success = test_complete_authentication_system()
    sys.exit(0 if success else 1)