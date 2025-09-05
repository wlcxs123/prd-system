#!/usr/bin/env python3
"""
测试问卷数据管理系统的API接口
验证任务4.1和4.2的实现
"""

import requests
import json
import sys
import time
from datetime import datetime

# 测试配置
BASE_URL = "http://localhost:5000"
TEST_USER = {"username": "admin", "password": "admin123"}

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        
    def login(self):
        """登录获取会话"""
        try:
            response = self.session.post(f"{BASE_URL}/api/auth/login", json=TEST_USER)
            if response.status_code == 200:
                print("✓ 登录成功")
                return True
            else:
                print(f"✗ 登录失败: {response.text}")
                return False
        except Exception as e:
            print(f"✗ 登录异常: {e}")
            return False
    
    def test_questionnaire_crud(self):
        """测试问卷CRUD接口"""
        print("\n=== 测试问卷CRUD接口 ===")
        
        # 测试数据
        test_questionnaire = {
            "type": "test_questionnaire",
            "basic_info": {
                "name": "测试学生",
                "grade": "三年级",
                "submission_date": "2024-01-15"
            },
            "questions": [
                {
                    "id": 1,
                    "type": "multiple_choice",
                    "question": "你喜欢什么颜色？",
                    "options": [
                        {"value": 0, "text": "红色"},
                        {"value": 1, "text": "蓝色"}
                    ],
                    "selected": [0]
                },
                {
                    "id": 2,
                    "type": "text_input",
                    "question": "你的爱好是什么？",
                    "answer": "阅读"
                }
            ]
        }
        
        # 1. 测试创建问卷 (POST /api/questionnaires)
        print("1. 测试创建问卷...")
        try:
            response = self.session.post(f"{BASE_URL}/api/questionnaires", json=test_questionnaire)
            if response.status_code == 201:
                data = response.json()
                questionnaire_id = data.get('id')
                print(f"✓ 创建问卷成功，ID: {questionnaire_id}")
            else:
                print(f"✗ 创建问卷失败: {response.text}")
                return None
        except Exception as e:
            print(f"✗ 创建问卷异常: {e}")
            return None
        
        # 2. 测试获取问卷列表 (GET /api/questionnaires)
        print("2. 测试获取问卷列表...")
        try:
            response = self.session.get(f"{BASE_URL}/api/questionnaires")
            if response.status_code == 200:
                data = response.json()
                print(f"✓ 获取问卷列表成功，共 {len(data.get('data', []))} 条记录")
            else:
                print(f"✗ 获取问卷列表失败: {response.text}")
        except Exception as e:
            print(f"✗ 获取问卷列表异常: {e}")
        
        # 3. 测试获取单个问卷 (GET /api/questionnaires/{id})
        print("3. 测试获取单个问卷...")
        try:
            response = self.session.get(f"{BASE_URL}/api/questionnaires/{questionnaire_id}")
            if response.status_code == 200:
                data = response.json()
                print(f"✓ 获取问卷详情成功，姓名: {data['data']['name']}")
            else:
                print(f"✗ 获取问卷详情失败: {response.text}")
        except Exception as e:
            print(f"✗ 获取问卷详情异常: {e}")
        
        # 4. 测试更新问卷 (PUT /api/questionnaires/{id})
        print("4. 测试更新问卷...")
        try:
            updated_questionnaire = test_questionnaire.copy()
            updated_questionnaire['basic_info']['name'] = "更新后的学生"
            
            response = self.session.put(f"{BASE_URL}/api/questionnaires/{questionnaire_id}", json=updated_questionnaire)
            if response.status_code == 200:
                print("✓ 更新问卷成功")
            else:
                print(f"✗ 更新问卷失败: {response.text}")
        except Exception as e:
            print(f"✗ 更新问卷异常: {e}")
        
        return questionnaire_id
    
    def test_batch_operations(self, questionnaire_id):
        """测试批量操作接口"""
        print("\n=== 测试批量操作接口 ===")
        
        # 创建更多测试数据
        test_ids = [questionnaire_id]
        
        for i in range(2, 4):
            test_data = {
                "type": "test_questionnaire",
                "basic_info": {
                    "name": f"测试学生{i}",
                    "grade": "三年级",
                    "submission_date": "2024-01-15"
                },
                "questions": [
                    {
                        "id": 1,
                        "type": "text_input",
                        "question": "测试问题",
                        "answer": f"测试答案{i}"
                    }
                ]
            }
            
            try:
                response = self.session.post(f"{BASE_URL}/api/questionnaires", json=test_data)
                if response.status_code == 201:
                    test_ids.append(response.json()['id'])
            except Exception as e:
                print(f"创建测试数据失败: {e}")
        
        print(f"创建了 {len(test_ids)} 条测试数据: {test_ids}")
        
        # 1. 测试批量导出 (POST /api/questionnaires/export)
        print("1. 测试批量导出...")
        try:
            export_data = {"ids": test_ids, "format": "json"}
            response = self.session.post(f"{BASE_URL}/api/questionnaires/export", json=export_data)
            if response.status_code == 200:
                print("✓ 批量导出成功 (JSON格式)")
            else:
                print(f"✗ 批量导出失败: {response.text}")
        except Exception as e:
            print(f"✗ 批量导出异常: {e}")
        
        # 测试CSV格式导出
        try:
            export_data = {"ids": test_ids, "format": "csv"}
            response = self.session.post(f"{BASE_URL}/api/questionnaires/export", json=export_data)
            if response.status_code == 200:
                print("✓ 批量导出成功 (CSV格式)")
            else:
                print(f"✗ 批量导出失败: {response.text}")
        except Exception as e:
            print(f"✗ 批量导出异常: {e}")
        
        # 2. 测试批量删除 (DELETE /api/questionnaires/batch)
        print("2. 测试批量删除...")
        try:
            delete_data = {"ids": test_ids[1:]}  # 保留第一个，删除其他的
            response = self.session.delete(f"{BASE_URL}/api/questionnaires/batch", json=delete_data)
            if response.status_code == 200:
                data = response.json()
                print(f"✓ 批量删除成功，删除了 {data.get('deleted_count', 0)} 条记录")
            else:
                print(f"✗ 批量删除失败: {response.text}")
        except Exception as e:
            print(f"✗ 批量删除异常: {e}")
        
        return test_ids[0]  # 返回剩余的ID
    
    def test_admin_apis(self):
        """测试管理接口"""
        print("\n=== 测试管理接口 ===")
        
        # 1. 测试统计数据接口
        print("1. 测试统计数据接口...")
        try:
            response = self.session.get(f"{BASE_URL}/api/admin/statistics")
            if response.status_code == 200:
                data = response.json()
                stats = data.get('data', {})
                print(f"✓ 获取统计数据成功，总问卷数: {stats.get('total_questionnaires', 0)}")
            else:
                print(f"✗ 获取统计数据失败: {response.text}")
        except Exception as e:
            print(f"✗ 获取统计数据异常: {e}")
        
        # 2. 测试操作日志接口
        print("2. 测试操作日志接口...")
        try:
            response = self.session.get(f"{BASE_URL}/api/admin/logs")
            if response.status_code == 200:
                data = response.json()
                logs = data.get('data', [])
                print(f"✓ 获取操作日志成功，共 {len(logs)} 条记录")
            else:
                print(f"✗ 获取操作日志失败: {response.text}")
        except Exception as e:
            print(f"✗ 获取操作日志异常: {e}")
    
    def test_single_delete(self, questionnaire_id):
        """测试单个删除"""
        print("\n=== 测试单个删除接口 ===")
        try:
            response = self.session.delete(f"{BASE_URL}/api/questionnaires/{questionnaire_id}")
            if response.status_code == 200:
                print("✓ 单个删除成功")
            else:
                print(f"✗ 单个删除失败: {response.text}")
        except Exception as e:
            print(f"✗ 单个删除异常: {e}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("开始测试问卷数据管理系统API接口...")
        print(f"测试时间: {datetime.now()}")
        
        # 登录
        if not self.login():
            print("登录失败，无法继续测试")
            return False
        
        # 测试CRUD接口
        questionnaire_id = self.test_questionnaire_crud()
        if not questionnaire_id:
            print("CRUD测试失败，无法继续")
            return False
        
        # 测试批量操作
        remaining_id = self.test_batch_operations(questionnaire_id)
        
        # 测试管理接口
        self.test_admin_apis()
        
        # 清理测试数据
        if remaining_id:
            self.test_single_delete(remaining_id)
        
        print("\n=== 测试完成 ===")
        return True

def main():
    """主函数"""
    print("问卷数据管理系统API测试工具")
    print("请确保Flask应用正在运行在 http://localhost:5000")
    
    # 等待用户确认
    input("按回车键开始测试...")
    
    tester = APITester()
    success = tester.run_all_tests()
    
    if success:
        print("✓ 所有测试完成")
        sys.exit(0)
    else:
        print("✗ 测试过程中出现错误")
        sys.exit(1)

if __name__ == "__main__":
    main()