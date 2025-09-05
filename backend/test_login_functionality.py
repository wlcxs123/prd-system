#!/usr/bin/env python3
"""
测试登录功能的完整性
验证任务 3.1 的所有要求是否已实现
"""

import sqlite3
import bcrypt
import json
import requests
import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

from app import app, get_db, init_db

def test_user_table_exists():
    """测试用户数据表是否存在"""
    print("测试 1: 检查用户数据表...")
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            result = cursor.fetchone()
            
            if result:
                print("✓ 用户数据表存在")
                
                # 检查表结构
                cursor.execute("PRAGMA table_info(users)")
                columns = cursor.fetchall()
                column_names = [col[1] for col in columns]
                
                required_columns = ['id', 'username', 'password_hash', 'role', 'created_at', 'last_login']
                missing_columns = [col for col in required_columns if col not in column_names]
                
                if not missing_columns:
                    print("✓ 用户表结构完整")
                    return True
                else:
                    print(f"✗ 用户表缺少列: {missing_columns}")
                    return False
            else:
                print("✗ 用户数据表不存在")
                return False
                
    except Exception as e:
        print(f"✗ 检查用户表失败: {e}")
        return False

def test_password_hashing():
    """测试密码哈希和验证功能"""
    print("\n测试 2: 检查密码哈希功能...")
    
    try:
        # 测试密码哈希
        test_password = "test123"
        password_hash = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt())
        
        # 测试密码验证
        is_valid = bcrypt.checkpw(test_password.encode('utf-8'), password_hash)
        
        if is_valid:
            print("✓ 密码哈希和验证功能正常")
            return True
        else:
            print("✗ 密码验证失败")
            return False
            
    except Exception as e:
        print(f"✗ 密码哈希测试失败: {e}")
        return False

def test_login_api():
    """测试登录API接口"""
    print("\n测试 3: 检查登录API接口...")
    
    try:
        with app.test_client() as client:
            # 测试有效登录
            response = client.post('/api/auth/login', 
                                 json={'username': 'admin', 'password': 'admin123'},
                                 content_type='application/json')
            
            if response.status_code == 200:
                data = response.get_json()
                if data.get('success'):
                    print("✓ 登录API接口正常工作")
                    
                    # 测试登录状态检查
                    with client.session_transaction() as sess:
                        if 'user_id' in sess:
                            print("✓ 会话管理正常")
                            return True
                        else:
                            print("✗ 会话未正确创建")
                            return False
                else:
                    print(f"✗ 登录失败: {data.get('error', {}).get('message', '未知错误')}")
                    return False
            else:
                print(f"✗ 登录API返回错误状态码: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"✗ 登录API测试失败: {e}")
        return False

def test_session_management():
    """测试会话管理机制"""
    print("\n测试 4: 检查会话管理...")
    
    try:
        with app.test_client() as client:
            # 先登录
            login_response = client.post('/api/auth/login', 
                                       json={'username': 'admin', 'password': 'admin123'},
                                       content_type='application/json')
            
            if login_response.status_code != 200:
                print("✗ 无法登录进行会话测试")
                return False
            
            # 测试登录状态检查
            status_response = client.get('/api/auth/status')
            if status_response.status_code == 200:
                status_data = status_response.get_json()
                if status_data.get('authenticated'):
                    print("✓ 登录状态检查正常")
                    
                    # 测试登出
                    logout_response = client.post('/api/auth/logout')
                    if logout_response.status_code == 200:
                        logout_data = logout_response.get_json()
                        if logout_data.get('success'):
                            print("✓ 登出功能正常")
                            
                            # 再次检查登录状态
                            status_response2 = client.get('/api/auth/status')
                            status_data2 = status_response2.get_json()
                            if not status_data2.get('authenticated'):
                                print("✓ 会话管理机制完整")
                                return True
                            else:
                                print("✗ 登出后会话未正确清除")
                                return False
                        else:
                            print("✗ 登出失败")
                            return False
                    else:
                        print("✗ 登出API错误")
                        return False
                else:
                    print("✗ 登录状态检查失败")
                    return False
            else:
                print("✗ 状态检查API错误")
                return False
                
    except Exception as e:
        print(f"✗ 会话管理测试失败: {e}")
        return False

def test_default_admin_user():
    """测试默认管理员用户是否存在"""
    print("\n测试 5: 检查默认管理员用户...")
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = 'admin'")
            admin_user = cursor.fetchone()
            
            if admin_user:
                print("✓ 默认管理员用户存在")
                
                # 验证密码哈希
                if bcrypt.checkpw('admin123'.encode('utf-8'), admin_user['password_hash'].encode('utf-8')):
                    print("✓ 默认密码正确")
                    
                    # 检查角色
                    if admin_user['role'] == 'admin':
                        print("✓ 管理员角色正确")
                        return True
                    else:
                        print(f"✗ 管理员角色错误: {admin_user['role']}")
                        return False
                else:
                    print("✗ 默认密码验证失败")
                    return False
            else:
                print("✗ 默认管理员用户不存在")
                return False
                
    except Exception as e:
        print(f"✗ 检查默认管理员用户失败: {e}")
        return False

def test_authentication_decorators():
    """测试认证装饰器"""
    print("\n测试 6: 检查认证装饰器...")
    
    try:
        with app.test_client() as client:
            # 测试未登录访问受保护的API
            response = client.get('/api/questionnaires')
            
            if response.status_code == 401:
                print("✓ 未登录访问受保护API被正确拒绝")
                
                # 登录后再次测试
                login_response = client.post('/api/auth/login', 
                                           json={'username': 'admin', 'password': 'admin123'},
                                           content_type='application/json')
                
                if login_response.status_code == 200:
                    # 再次访问受保护的API
                    response2 = client.get('/api/questionnaires')
                    
                    if response2.status_code == 200:
                        print("✓ 登录后可以访问受保护API")
                        return True
                    else:
                        print(f"✗ 登录后仍无法访问受保护API: {response2.status_code}")
                        return False
                else:
                    print("✗ 登录失败，无法测试认证装饰器")
                    return False
            else:
                print(f"✗ 未登录访问受保护API未被拒绝: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"✗ 认证装饰器测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("任务 3.1 登录功能实现验证")
    print("=" * 60)
    
    # 确保数据库已初始化
    try:
        init_db()
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        return False
    
    # 运行所有测试
    tests = [
        test_user_table_exists,
        test_password_hashing,
        test_login_api,
        test_session_management,
        test_default_admin_user,
        test_authentication_decorators
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
        print("- ✓ 默认管理员用户")
        return True
    else:
        print("✗ 任务 3.1 登录功能实现不完整")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)