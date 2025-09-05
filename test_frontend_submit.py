#!/usr/bin/env python3
"""
测试前端提交数据的格式和后端处理
"""

import requests
import json
from datetime import datetime

# 服务器配置
BASE_URL = "http://localhost:5000"

def test_frontend_submit():
    """测试前端提交的数据格式"""
    
    # 模拟前端提交的数据结构
    submit_data = {
        "type": "frankfurt_scale_selective_mutism",
        "basic_info": {
            "name": "测试儿童",
            "grade": "小学",
            "submission_date": "2025-08-29",
            "guardian": "测试家长"
        },
        "questions": [
            {
                "id": 1,
                "type": "multiple_choice",
                "question": "在家很能说话，但在公共/学校环境明显沉默或避免用语言。",
                "options": [
                    {"value": 1, "text": "是"},
                    {"value": 0, "text": "否"}
                ],
                "selected": [1],
                "can_speak": True,
                "section": "DS"
            },
            {
                "id": 2,
                "type": "multiple_choice",
                "question": "在课堂与老师说话",
                "options": [
                    {"value": 0, "text": "0 无问题"},
                    {"value": 1, "text": "1 轻度限制"},
                    {"value": 2, "text": "2 偶尔"},
                    {"value": 3, "text": "3 几乎从不"},
                    {"value": 4, "text": "4 完全不说"}
                ],
                "selected": [3],
                "can_speak": True,
                "section": "SS_school"
            },
            {
                "id": 3,
                "type": "multiple_choice",
                "question": "与公共场合的陌生儿童交谈",
                "options": [
                    {"value": 0, "text": "0 无问题"},
                    {"value": 1, "text": "1 轻度限制"},
                    {"value": 2, "text": "2 偶尔"},
                    {"value": 3, "text": "3 几乎从不"},
                    {"value": 4, "text": "4 完全不说"}
                ],
                "selected": [4],
                "can_speak": True,
                "section": "SS_public"
            },
            {
                "id": 4,
                "type": "multiple_choice",
                "question": "与直系亲属说话",
                "options": [
                    {"value": 0, "text": "0 无问题"},
                    {"value": 1, "text": "1 轻度限制"},
                    {"value": 2, "text": "2 偶尔"},
                    {"value": 3, "text": "3 几乎从不"},
                    {"value": 4, "text": "4 完全不说"}
                ],
                "selected": [0],
                "can_speak": True,
                "section": "SS_home"
            }
        ],
        "statistics": {
            "age_group": "6_11",
            "ds_total": 1,
            "ss_school_total": 3,
            "ss_public_total": 4,
            "ss_home_total": 0,
            "ss_total": 7,
            "risk_level": "low",
            "completion_rate": 100
        }
    }
    
    print("测试前端提交数据...")
    print(f"提交数据结构:")
    print(json.dumps(submit_data, indent=2, ensure_ascii=False))
    
    # 1. 测试 /api/submit 端点
    print(f"\n1. 测试 /api/submit 端点...")
    try:
        response = requests.post(f"{BASE_URL}/api/submit", json=submit_data)
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 201:
            result = response.json()
            if result.get('success'):
                print("✅ /api/submit 提交成功")
                return result.get('id')
            else:
                print("❌ /api/submit 提交失败")
        else:
            print("❌ /api/submit 提交失败")
            
    except Exception as e:
        print(f"❌ /api/submit 请求异常: {e}")
    
    # 2. 测试 /api/questionnaires 端点
    print(f"\n2. 测试 /api/questionnaires 端点...")
    try:
        response = requests.post(f"{BASE_URL}/api/questionnaires", json=submit_data)
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 201:
            result = response.json()
            if result.get('success'):
                print("✅ /api/questionnaires 提交成功")
                return result.get('id')
            else:
                print("❌ /api/questionnaires 提交失败")
        else:
            print("❌ /api/questionnaires 提交失败")
            
    except Exception as e:
        print(f"❌ /api/questionnaires 请求异常: {e}")
    
    return None

def test_server_status():
    """测试服务器状态"""
    print("测试服务器状态...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/auth/status", timeout=5)
        print(f"服务器状态响应: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"服务器在线: {result}")
            return True
        else:
            print("服务器响应异常")
            return False
            
    except Exception as e:
        print(f"服务器连接失败: {e}")
        return False

def main():
    print("开始测试前端提交功能...")
    print(f"测试时间: {datetime.now()}")
    print("=" * 50)
    
    # 检查服务器状态
    if not test_server_status():
        print("服务器不可用，无法继续测试")
        return
    
    print("\n" + "=" * 50)
    
    # 测试提交功能
    questionnaire_id = test_frontend_submit()
    
    if questionnaire_id:
        print(f"\n✅ 测试成功，问卷ID: {questionnaire_id}")
    else:
        print(f"\n❌ 测试失败")
    
    print("\n" + "=" * 50)
    print("测试完成")

if __name__ == "__main__":
    main()