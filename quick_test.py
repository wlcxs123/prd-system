#!/usr/bin/env python3
"""
问卷系统快速测试脚本
一键测试系统的基本功能
"""

import requests
import json
import sqlite3
import os
import sys
import time
from datetime import datetime

# 配置
BASE_URL = "http://localhost:5000"
TEST_DB = "backend/questionnaires.db"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def check_server_running():
    """检查服务器是否运行"""
    try:
        response = requests.get(BASE_URL, timeout=5)
        return True
    except requests.exceptions.RequestException:
        return False

def test_database():
    """测试数据库连接和结构"""
    print_info("测试数据库...")
    
    if not os.path.exists(TEST_DB):
        print_error("数据库文件不存在")
        return False
    
    try:
        with sqlite3.connect(TEST_DB) as conn:
            cursor = conn.cursor()
            
            # 检查表是否存在
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = ['questionnaires', 'users', 'operation_logs']
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                print_error(f"缺少数据表: {missing_tables}")
                return False
            
            # 检查管理员用户
            cursor.execute("SELECT COUNT(*) FROM users WHERE username='admin'")
            admin_count = cursor.fetchone()[0]
            
            if admin_count == 0:
                print_error("默认管理员用户不存在")
                return False
            
            print_success("数据库结构正常")
            return True
            
    except Exception as e:
        print_error(f"数据库测试失败: {e}")
        return False

def test_login():
    """测试登录功能"""
    print_info("测试登录功能...")
    
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print_success("登录功能正常")
                return response.cookies
            else:
                print_error(f"登录失败: {data.get('message', '未知错误')}")
                return None
        else:
            print_error(f"登录请求失败: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print_error(f"登录测试失败: {e}")
        return None

def test_submit_questionnaire():
    """测试问卷提交"""
    print_info("测试问卷提交...")
    
    test_data = {
        "type": "test_questionnaire",
        "basic_info": {
            "name": "测试用户",
            "grade": "三年级",
            "submission_date": datetime.now().strftime("%Y-%m-%d")
        },
        "questions": [
            {
                "id": 1,
                "type": "multiple_choice",
                "question": "这是一个测试问题",
                "options": [
                    {"value": 0, "text": "选项A"},
                    {"value": 1, "text": "选项B"}
                ],
                "selected": [1],
                "can_speak": True
            },
            {
                "id": 2,
                "type": "text_input",
                "question": "请输入你的想法",
                "answer": "这是测试答案",
                "input_type": "text"
            }
        ]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/submit", json=test_data, timeout=10)
        
        if response.status_code == 201:
            data = response.json()
            if data.get('success'):
                print_success("问卷提交功能正常")
                return data.get('questionnaire_id')
            else:
                print_error(f"问卷提交失败: {data.get('message', '未知错误')}")
                return None
        else:
            print_error(f"问卷提交请求失败: HTTP {response.status_code}")
            print_error(f"响应内容: {response.text}")
            return None
            
    except Exception as e:
        print_error(f"问卷提交测试失败: {e}")
        return None

def test_get_questionnaires(cookies):
    """测试获取问卷列表"""
    print_info("测试获取问卷列表...")
    
    if not cookies:
        print_warning("跳过问卷列表测试（需要登录）")
        return False
    
    try:
        response = requests.get(f"{BASE_URL}/api/questionnaires", cookies=cookies, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                questionnaire_count = len(data.get('data', []))
                print_success(f"获取问卷列表正常 (共{questionnaire_count}条记录)")
                return True
            else:
                print_error(f"获取问卷列表失败: {data.get('message', '未知错误')}")
                return False
        else:
            print_error(f"获取问卷列表请求失败: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"获取问卷列表测试失败: {e}")
        return False

def test_validation():
    """测试数据验证"""
    print_info("测试数据验证...")
    
    # 测试无效数据
    invalid_data = {
        "type": "test_questionnaire",
        "basic_info": {
            "name": "",  # 空姓名
            "grade": "无效年级",
            "submission_date": "invalid-date"
        },
        "questions": []
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/submit", json=invalid_data, timeout=10)
        
        if response.status_code == 400:
            data = response.json()
            if not data.get('success') and 'errors' in data:
                print_success("数据验证功能正常")
                return True
            else:
                print_error("数据验证响应格式不正确")
                return False
        else:
            print_error(f"数据验证测试失败: 应该返回400错误，实际返回{response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"数据验证测试失败: {e}")
        return False

def test_static_files():
    """测试静态文件访问"""
    print_info("测试静态文件访问...")
    
    static_files = [
        "/static/css/login.css",
        "/static/js/login.js"
    ]
    
    success_count = 0
    for file_path in static_files:
        try:
            response = requests.get(f"{BASE_URL}{file_path}", timeout=5)
            if response.status_code == 200:
                success_count += 1
            else:
                print_warning(f"静态文件 {file_path} 访问失败: HTTP {response.status_code}")
        except Exception as e:
            print_warning(f"静态文件 {file_path} 访问异常: {e}")
    
    if success_count > 0:
        print_success(f"静态文件访问正常 ({success_count}/{len(static_files)})")
        return True
    else:
        print_error("所有静态文件访问失败")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("🚀 问卷数据管理系统 - 快速测试")
    print("=" * 60)
    
    # 检查服务器是否运行
    if not check_server_running():
        print_error("服务器未运行！请先启动后端服务:")
        print("  cd backend")
        print("  python app.py")
        return False
    
    print_success("服务器运行正常")
    
    # 运行测试
    tests = []
    
    # 1. 数据库测试
    tests.append(("数据库", test_database()))
    
    # 2. 登录测试
    cookies = test_login()
    tests.append(("登录功能", cookies is not None))
    
    # 3. 问卷提交测试
    questionnaire_id = test_submit_questionnaire()
    tests.append(("问卷提交", questionnaire_id is not None))
    
    # 4. 问卷查询测试
    tests.append(("问卷查询", test_get_questionnaires(cookies)))
    
    # 5. 数据验证测试
    tests.append(("数据验证", test_validation()))
    
    # 6. 静态文件测试
    tests.append(("静态文件", test_static_files()))
    
    # 统计结果
    passed_tests = sum(1 for _, result in tests if result)
    total_tests = len(tests)
    
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    for test_name, result in tests:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:12} : {status}")
    
    print("-" * 60)
    print(f"总计: {passed_tests}/{total_tests} 通过")
    
    if passed_tests == total_tests:
        print_success("🎉 所有测试通过！系统运行正常")
        
        print("\n📋 下一步可以测试:")
        print("1. 在浏览器中访问: http://localhost:5000")
        print("2. 使用管理员账户登录: admin / admin123")
        print("3. 测试问卷页面提交功能")
        print("4. 在管理页面查看和导出数据")
        
        return True
    else:
        print_error(f"❌ {total_tests - passed_tests} 个测试失败")
        print("\n🔧 故障排查建议:")
        print("1. 检查后端服务是否正常启动")
        print("2. 检查数据库是否正确初始化")
        print("3. 检查依赖包是否完整安装")
        print("4. 查看控制台错误信息")
        
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print_error(f"测试执行异常: {e}")
        sys.exit(1)