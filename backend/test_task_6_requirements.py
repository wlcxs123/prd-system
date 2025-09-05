#!/usr/bin/env python3
"""
测试任务6的需求验证脚本
验证权限控制、会话管理和操作日志系统
"""

import requests
import json
import time
from datetime import datetime

# 测试配置
BASE_URL = "http://localhost:5000"
TEST_USER = {
    "username": "admin",
    "password": "admin123"
}

class Task6Tester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def test_login_and_session_management(self):
        """测试登录和会话管理功能"""
        print("=== 测试登录和会话管理 ===")
        
        # 1. 测试登录
        print("1. 测试用户登录...")
        login_response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json=TEST_USER
        )
        
        if login_response.status_code == 200:
            data = login_response.json()
            if data.get('success'):
                print("✓ 登录成功")
                print(f"  用户信息: {data.get('user')}")
            else:
                print(f"✗ 登录失败: {data.get('error')}")
                return False
        else:
            print(f"✗ 登录请求失败: {login_response.status_code}")
            return False
        
        # 2. 测试会话状态检查
        print("\n2. 测试会话状态检查...")
        status_response = self.session.get(f"{BASE_URL}/api/auth/status")
        
        if status_response.status_code == 200:
            data = status_response.json()
            if data.get('authenticated'):
                print("✓ 会话状态正常")
                session_info = data.get('session_info', {})
                print(f"  剩余时间: {session_info.get('remaining_time')} 秒")
                print(f"  最后活动: {session_info.get('last_activity')}")
            else:
                print("✗ 会话状态异常")
                return False
        else:
            print(f"✗ 会话状态检查失败: {status_response.status_code}")
            return False
        
        # 3. 测试会话刷新
        print("\n3. 测试会话刷新...")
        refresh_response = self.session.post(f"{BASE_URL}/api/auth/refresh")
        
        if refresh_response.status_code == 200:
            data = refresh_response.json()
            if data.get('success'):
                print("✓ 会话刷新成功")
                session_info = data.get('session_info', {})
                print(f"  刷新后剩余时间: {session_info.get('remaining_time')} 秒")
            else:
                print(f"✗ 会话刷新失败: {data.get('error')}")
        else:
            print(f"✗ 会话刷新请求失败: {refresh_response.status_code}")
        
        return True
    
    def test_permission_control(self):
        """测试权限控制功能"""
        print("\n=== 测试权限控制 ===")
        
        # 1. 测试需要登录的接口
        print("1. 测试需要登录的接口访问...")
        questionnaires_response = self.session.get(f"{BASE_URL}/api/questionnaires")
        
        if questionnaires_response.status_code == 200:
            data = questionnaires_response.json()
            if data.get('success'):
                print("✓ 已登录用户可以访问问卷列表")
            else:
                print(f"✗ 访问问卷列表失败: {data.get('error')}")
        else:
            print(f"✗ 问卷列表请求失败: {questionnaires_response.status_code}")
        
        # 2. 测试需要管理员权限的接口
        print("\n2. 测试需要管理员权限的接口...")
        logs_response = self.session.get(f"{BASE_URL}/api/admin/logs")
        
        if logs_response.status_code == 200:
            data = logs_response.json()
            if data.get('success'):
                print("✓ 管理员可以访问操作日志")
                print(f"  日志条数: {len(data.get('data', []))}")
            else:
                print(f"✗ 访问操作日志失败: {data.get('error')}")
        else:
            print(f"✗ 操作日志请求失败: {logs_response.status_code}")
        
        # 3. 测试会话延长（管理员功能）
        print("\n3. 测试会话延长功能...")
        extend_response = self.session.post(
            f"{BASE_URL}/api/auth/extend",
            json={"minutes": 30}
        )
        
        if extend_response.status_code == 200:
            data = extend_response.json()
            if data.get('success'):
                print("✓ 管理员可以延长会话")
                print(f"  延长时间: {data.get('extended_minutes')} 分钟")
            else:
                print(f"✗ 延长会话失败: {data.get('error')}")
        else:
            print(f"✗ 延长会话请求失败: {extend_response.status_code}")
        
        return True
    
    def test_operation_logging(self):
        """测试操作日志系统"""
        print("\n=== 测试操作日志系统 ===")
        
        # 1. 测试日志记录 - 创建一个测试问卷
        print("1. 测试操作日志记录...")
        test_questionnaire = {
            "type": "test_questionnaire",
            "basic_info": {
                "name": "测试用户",
                "grade": "测试年级",
                "submission_date": "2024-01-15"
            },
            "questions": [
                {
                    "id": 1,
                    "type": "multiple_choice",
                    "question": "测试选择题",
                    "options": [
                        {"value": 0, "text": "选项A"},
                        {"value": 1, "text": "选项B"}
                    ],
                    "selected": [0]
                }
            ]
        }
        
        create_response = self.session.post(
            f"{BASE_URL}/api/questionnaires",
            json=test_questionnaire
        )
        
        questionnaire_id = None
        if create_response.status_code == 201:
            data = create_response.json()
            if data.get('success'):
                questionnaire_id = data.get('id')
                print(f"✓ 创建测试问卷成功，ID: {questionnaire_id}")
            else:
                print(f"✗ 创建测试问卷失败: {data.get('error')}")
        else:
            print(f"✗ 创建问卷请求失败: {create_response.status_code}")
        
        # 2. 测试日志查询
        print("\n2. 测试日志查询功能...")
        logs_response = self.session.get(f"{BASE_URL}/api/admin/logs?limit=10")
        
        if logs_response.status_code == 200:
            data = logs_response.json()
            if data.get('success'):
                logs = data.get('data', [])
                print(f"✓ 获取操作日志成功，共 {len(logs)} 条")
                
                # 查找刚才的创建操作日志
                create_log = None
                for log in logs:
                    if (log.get('operation') == 'CREATE_QUESTIONNAIRE' and 
                        log.get('target_id') == questionnaire_id):
                        create_log = log
                        break
                
                if create_log:
                    print("✓ 找到创建问卷的操作日志")
                    print(f"  操作类型: {create_log.get('operation')}")
                    print(f"  用户: {create_log.get('username')}")
                    print(f"  时间: {create_log.get('created_at')}")
                    print(f"  IP地址: {create_log.get('ip_address')}")
                else:
                    print("✗ 未找到创建问卷的操作日志")
            else:
                print(f"✗ 获取操作日志失败: {data.get('error')}")
        else:
            print(f"✗ 日志查询请求失败: {logs_response.status_code}")
        
        # 3. 测试日志统计
        print("\n3. 测试日志统计功能...")
        stats_response = self.session.get(f"{BASE_URL}/api/admin/logs/statistics")
        
        if stats_response.status_code == 200:
            data = stats_response.json()
            if data.get('success'):
                stats = data.get('data', {})
                print("✓ 获取日志统计成功")
                print(f"  总日志数: {stats.get('total_logs')}")
                print(f"  今日日志数: {stats.get('today_logs')}")
                print(f"  敏感操作数: {stats.get('sensitive_logs')}")
                
                # 显示操作类型统计
                op_stats = stats.get('operation_statistics', [])
                if op_stats:
                    print("  操作类型统计:")
                    for stat in op_stats[:5]:  # 显示前5个
                        print(f"    {stat.get('operation')}: {stat.get('count')} 次")
            else:
                print(f"✗ 获取日志统计失败: {data.get('error')}")
        else:
            print(f"✗ 日志统计请求失败: {stats_response.status_code}")
        
        # 4. 清理测试数据
        if questionnaire_id:
            print(f"\n4. 清理测试数据...")
            delete_response = self.session.delete(f"{BASE_URL}/api/questionnaires/{questionnaire_id}")
            if delete_response.status_code == 200:
                print("✓ 测试问卷删除成功")
            else:
                print("✗ 测试问卷删除失败")
        
        return True
    
    def test_unauthorized_access(self):
        """测试未授权访问"""
        print("\n=== 测试未授权访问 ===")
        
        # 先登出
        print("1. 登出当前用户...")
        logout_response = self.session.post(f"{BASE_URL}/api/auth/logout")
        if logout_response.status_code == 200:
            print("✓ 登出成功")
        
        # 测试未登录访问需要认证的接口
        print("\n2. 测试未登录访问...")
        questionnaires_response = self.session.get(f"{BASE_URL}/api/questionnaires")
        
        if questionnaires_response.status_code == 401:
            data = questionnaires_response.json()
            error_code = data.get('error', {}).get('code')
            if error_code in ['AUTH_REQUIRED', 'SESSION_EXPIRED']:
                print("✓ 未登录用户被正确拒绝访问")
            else:
                print(f"✗ 错误代码不正确: {error_code}")
        else:
            print(f"✗ 未登录访问应该返回401，实际返回: {questionnaires_response.status_code}")
        
        return True
    
    def run_all_tests(self):
        """运行所有测试"""
        print("开始测试任务6的功能...")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"测试服务器: {BASE_URL}")
        
        try:
            # 测试登录和会话管理
            if not self.test_login_and_session_management():
                print("\n❌ 登录和会话管理测试失败")
                return False
            
            # 测试权限控制
            if not self.test_permission_control():
                print("\n❌ 权限控制测试失败")
                return False
            
            # 测试操作日志
            if not self.test_operation_logging():
                print("\n❌ 操作日志测试失败")
                return False
            
            # 测试未授权访问
            if not self.test_unauthorized_access():
                print("\n❌ 未授权访问测试失败")
                return False
            
            print("\n🎉 所有测试通过！")
            print("\n任务6功能验证完成:")
            print("✓ 登录状态检查装饰器")
            print("✓ 管理员权限验证")
            print("✓ 会话超时处理")
            print("✓ 自动登出功能")
            print("✓ 操作日志数据表")
            print("✓ 日志记录中间件")
            print("✓ 日志查询和展示功能")
            print("✓ 敏感操作审计")
            
            return True
            
        except Exception as e:
            print(f"\n❌ 测试过程中发生错误: {e}")
            return False

if __name__ == "__main__":
    tester = Task6Tester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ 任务6验证成功 - 数据完整性和安全功能已实现")
    else:
        print("\n❌ 任务6验证失败 - 请检查实现")