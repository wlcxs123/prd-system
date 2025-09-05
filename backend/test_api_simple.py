#!/usr/bin/env python3
"""
简单的API测试脚本
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_submit_endpoint():
    """测试 /api/submit 端点"""
    print("测试 /api/submit 端点...")
    
    test_data = {
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
                "selected": [1],
                "can_speak": True
            }
        ]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/submit", json=test_data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        return response.status_code == 201
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_questionnaires_endpoint():
    """测试 /api/questionnaires 端点"""
    print("\n测试 /api/questionnaires 端点...")
    
    # 先登录
    session = requests.Session()
    login_data = {"username": "admin", "password": "admin123"}
    
    try:
        login_response = session.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if login_response.status_code != 200:
            print(f"登录失败: {login_response.text}")
            return False
        
        # 测试GET
        response = session.get(f"{BASE_URL}/api/questionnaires")
        print(f"GET 状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"获取到 {len(data.get('data', []))} 条问卷记录")
            return True
        else:
            print(f"GET 失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"错误: {e}")
        return False

if __name__ == "__main__":
    print("开始API测试...")
    
    # 测试提交端点
    submit_ok = test_submit_endpoint()
    
    # 测试查询端点
    get_ok = test_questionnaires_endpoint()
    
    print(f"\n测试结果:")
    print(f"- /api/submit: {'✅' if submit_ok else '❌'}")
    print(f"- /api/questionnaires: {'✅' if get_ok else '❌'}")