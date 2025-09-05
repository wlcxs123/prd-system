#!/usr/bin/env python3
"""
带认证的更新问卷功能测试
"""

import requests
import json
from datetime import datetime

# 服务器配置
BASE_URL = "http://localhost:5000"

class TestSession:
    def __init__(self):
        self.session = requests.Session()
    
    def login(self, username="admin", password="admin123"):
        """登录系统"""
        print(f"正在登录用户: {username}")
        try:
            response = self.session.post(f"{BASE_URL}/api/auth/login", json={
                "username": username,
                "password": password
            })
            print(f"登录响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✅ 登录成功: {result.get('user', {}).get('username')}")
                    return True
                else:
                    print(f"❌ 登录失败: {result.get('message')}")
                    return False
            else:
                print(f"❌ 登录失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"登录时发生错误: {e}")
            return False
    
    def test_update_questionnaire(self):
        """测试更新问卷功能"""
        
        # 1. 先获取现有问卷列表
        print("\n1. 获取现有问卷列表...")
        try:
            response = self.session.get(f"{BASE_URL}/api/questionnaires")
            print(f"获取问卷列表状态码: {response.status_code}")
            
            if response.status_code != 200:
                print("无法获取问卷列表")
                return
                
            result = response.json()
            questionnaires = result.get('data', [])
            
            if not questionnaires:
                print("没有找到现有问卷，先创建一个测试问卷")
                questionnaire_id = self.create_test_questionnaire()
                if not questionnaire_id:
                    return
            else:
                # 选择第一个问卷进行更新测试
                questionnaire = questionnaires[0]
                questionnaire_id = questionnaire['id']
                print(f"选择问卷ID {questionnaire_id} 进行更新测试")
                print(f"原始问卷信息: {questionnaire['name']} - {questionnaire['type']}")
            
        except Exception as e:
            print(f"获取问卷列表时发生错误: {e}")
            return
        
        # 2. 获取问卷详细信息
        print(f"\n2. 获取问卷 {questionnaire_id} 的详细信息...")
        try:
            response = self.session.get(f"{BASE_URL}/api/questionnaires/{questionnaire_id}")
            print(f"获取详情状态码: {response.status_code}")
            
            if response.status_code != 200:
                print("无法获取问卷详情")
                return
                
            detail_result = response.json()
            if not detail_result.get('success'):
                print("获取问卷详情失败")
                return
                
            original_data = detail_result.get('data', {})
            print(f"原始数据获取成功")
            
        except Exception as e:
            print(f"获取问卷详情时发生错误: {e}")
            return
        
        # 3. 构建更新数据（基于原始数据进行小幅修改）
        print(f"\n3. 构建更新数据...")
        update_data = original_data.copy()
        
        # 修改基本信息
        if 'basic_info' in update_data:
            update_data['basic_info']['name'] = f"更新测试-{datetime.now().strftime('%H%M%S')}"
            update_data['basic_info']['submission_date'] = datetime.now().strftime('%Y-%m-%d')
        
        print(f"更新数据构建完成")
        
        # 4. 执行更新
        print(f"\n4. 执行更新问卷 {questionnaire_id}...")
        try:
            response = self.session.put(f"{BASE_URL}/api/questionnaires/{questionnaire_id}", json=update_data)
            print(f"更新响应状态码: {response.status_code}")
            print(f"更新响应内容: {response.text}")
            
            if response.status_code == 200:
                print("✅ 更新问卷成功")
            else:
                print("❌ 更新问卷失败")
                return
                
        except Exception as e:
            print(f"更新问卷时发生错误: {e}")
            return
        
        # 5. 验证更新结果
        print(f"\n5. 验证更新结果...")
        try:
            response = self.session.get(f"{BASE_URL}/api/questionnaires/{questionnaire_id}")
            print(f"验证响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    updated_data = result.get('data', {})
                    updated_basic_info = updated_data.get('basic_info', {})
                    
                    print(f"✅ 验证成功:")
                    print(f"  - 更新后姓名: {updated_basic_info.get('name')}")
                    print(f"  - 更新后提交日期: {updated_basic_info.get('submission_date')}")
                    print(f"  - 更新时间: {updated_data.get('updated_at')}")
                else:
                    print("❌ 获取更新后的问卷失败")
            else:
                print(f"❌ 验证失败，状态码: {response.status_code}")
                
        except Exception as e:
            print(f"验证更新结果时发生错误: {e}")
    
    def create_test_questionnaire(self):
        """创建一个简单的测试问卷"""
        print("创建测试问卷...")
        test_data = {
            "type": "parent_interview",
            "basic_info": {
                "name": "测试学生",
                "grade": "小学",
                "submission_date": "2024-01-15"
            },
            "questions": [
                {
                    "id": 1,
                    "type": "text_input",
                    "question": "孩子的主要问题是什么？",
                    "answer": "测试答案"
                }
            ]
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/api/questionnaires", json=test_data)
            print(f"创建问卷状态码: {response.status_code}")
            
            if response.status_code == 201:
                result = response.json()
                if result.get('success'):
                    questionnaire_id = result.get('id')
                    print(f"✅ 创建测试问卷成功，ID: {questionnaire_id}")
                    return questionnaire_id
            
            print(f"❌ 创建测试问卷失败: {response.text}")
            return None
            
        except Exception as e:
            print(f"创建测试问卷时发生错误: {e}")
            return None

def main():
    print("开始测试更新问卷功能（带认证）...")
    print(f"测试时间: {datetime.now()}")
    print("=" * 50)
    
    test_session = TestSession()
    
    # 登录
    if not test_session.login():
        print("登录失败，无法继续测试")
        return
    
    # 测试更新功能
    test_session.test_update_questionnaire()
    
    print("\n" + "=" * 50)
    print("测试完成")

if __name__ == "__main__":
    main()