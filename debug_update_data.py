#!/usr/bin/env python3
"""
调试更新问卷数据结构
"""

import requests
import json
from datetime import datetime

# 服务器配置
BASE_URL = "http://localhost:5000"

class DebugSession:
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
    
    def debug_questionnaire_data(self):
        """调试问卷数据结构"""
        
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
        
        # 2. 获取详细数据并打印结构
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
            
            print("原始数据结构:")
            print(json.dumps(original_data, indent=2, ensure_ascii=False))
            
            # 3. 分析数据结构
            print(f"\n3. 数据结构分析:")
            print(f"  - 问卷类型: {original_data.get('type')}")
            print(f"  - 基本信息: {original_data.get('basic_info', {}).keys()}")
            print(f"  - 问题数量: {len(original_data.get('questions', []))}")
            
            questions = original_data.get('questions', [])
            if questions:
                print(f"  - 第一个问题结构: {questions[0].keys()}")
                print(f"  - 第一个问题内容: {json.dumps(questions[0], indent=2, ensure_ascii=False)}")
            
            statistics = original_data.get('statistics', {})
            if statistics:
                print(f"  - 统计信息: {statistics.keys()}")
                print(f"  - 统计内容: {json.dumps(statistics, indent=2, ensure_ascii=False)}")
            
        except Exception as e:
            print(f"获取问卷详情时发生错误: {e}")
            return
        
        # 4. 尝试最小修改更新
        print(f"\n4. 尝试最小修改更新...")
        try:
            # 只修改姓名，其他保持不变
            update_data = original_data.copy()
            if 'basic_info' in update_data:
                update_data['basic_info']['name'] = f"调试更新-{datetime.now().strftime('%H%M%S')}"
            
            print("准备发送的更新数据:")
            print(json.dumps(update_data, indent=2, ensure_ascii=False))
            
            response = self.session.put(f"{BASE_URL}/api/questionnaires/{questionnaire_id}", json=update_data)
            print(f"\n更新响应状态码: {response.status_code}")
            print(f"更新响应内容: {response.text}")
            
        except Exception as e:
            print(f"更新时发生错误: {e}")

def main():
    print("开始调试更新问卷数据结构...")
    print(f"调试时间: {datetime.now()}")
    print("=" * 50)
    
    debug_session = DebugSession()
    
    # 登录
    if not debug_session.login():
        print("登录失败，无法继续调试")
        return
    
    # 调试数据结构
    debug_session.debug_questionnaire_data()
    
    print("\n" + "=" * 50)
    print("调试完成")

if __name__ == "__main__":
    main()