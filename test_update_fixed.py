#!/usr/bin/env python3
"""
修复后的更新问卷功能测试
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
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✅ 登录成功")
                    return True
            
            print(f"❌ 登录失败")
            return False
                
        except Exception as e:
            print(f"登录时发生错误: {e}")
            return False
    
    def test_update_questionnaire(self):
        """测试更新问卷功能"""
        
        # 1. 获取问卷列表
        print("1. 获取问卷列表...")
        try:
            response = self.session.get(f"{BASE_URL}/api/questionnaires")
            
            if response.status_code != 200:
                print("无法获取问卷列表")
                return
                
            result = response.json()
            questionnaires = result.get('data', [])
            
            if not questionnaires:
                print("没有找到问卷")
                return
            
            questionnaire = questionnaires[0]
            questionnaire_id = questionnaire['id']
            print(f"选择问卷ID {questionnaire_id}")
            
        except Exception as e:
            print(f"获取问卷列表时发生错误: {e}")
            return
        
        # 2. 获取详细数据
        print(f"\n2. 获取问卷 {questionnaire_id} 的详细数据...")
        try:
            response = self.session.get(f"{BASE_URL}/api/questionnaires/{questionnaire_id}")
            
            if response.status_code != 200:
                print("无法获取问卷详情")
                return
                
            detail_result = response.json()
            if not detail_result.get('success'):
                print("获取问卷详情失败")
                return
                
            original_data = detail_result.get('data', {})
            
            # 从返回的数据中提取正确的结构
            inner_data = original_data.get('data', {})
            
            print(f"原始问卷类型: {inner_data.get('type')}")
            print(f"原始问题数量: {len(inner_data.get('questions', []))}")
            
        except Exception as e:
            print(f"获取问卷详情时发生错误: {e}")
            return
        
        # 3. 构建正确的更新数据结构
        print(f"\n3. 构建更新数据...")
        
        # 使用内部数据结构，这是验证器期望的格式
        update_data = {
            "type": inner_data.get('type'),
            "basic_info": inner_data.get('basic_info', {}),
            "questions": inner_data.get('questions', [])
        }
        
        # 暂时不包含统计信息，让问题处理器重新生成
        # update_data['statistics'] = {}
        
        # 修改基本信息（使用符合验证规则的姓名格式）
        update_data['basic_info']['name'] = "更新后的测试学生"
        update_data['basic_info']['submission_date'] = datetime.now().strftime('%Y-%m-%d')
        
        print(f"更新数据结构:")
        print(f"  - 类型: {update_data['type']}")
        print(f"  - 基本信息: {update_data['basic_info']}")
        print(f"  - 问题数量: {len(update_data['questions'])}")
        print(f"  - 统计信息: 让系统重新生成")
        
        # 4. 执行更新
        print(f"\n4. 执行更新问卷 {questionnaire_id}...")
        try:
            response = self.session.put(f"{BASE_URL}/api/questionnaires/{questionnaire_id}", json=update_data)
            print(f"更新响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 更新问卷成功")
                print(f"响应: {result}")
            else:
                print("❌ 更新问卷失败")
                print(f"错误响应: {response.text}")
                return
                
        except Exception as e:
            print(f"更新问卷时发生错误: {e}")
            return
        
        # 5. 验证更新结果
        print(f"\n5. 验证更新结果...")
        try:
            response = self.session.get(f"{BASE_URL}/api/questionnaires/{questionnaire_id}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    updated_data = result.get('data', {})
                    inner_updated_data = updated_data.get('data', {})
                    updated_basic_info = inner_updated_data.get('basic_info', {})
                    
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

def main():
    print("开始测试更新问卷功能（修复版）...")
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