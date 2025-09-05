#!/usr/bin/env python3
"""
最简单的Frankfurt Scale提交测试
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def simple_test():
    """最简单的提交测试"""
    test_data = {
        "type": "frankfurt_scale_selective_mutism",
        "basic_info": {
            "name": "测试儿童",
            "grade": "小学",
            "submission_date": "2025-08-29"
        },
        "questions": [
            {
                "id": 1,
                "type": "multiple_choice",
                "question": "测试问题DS",
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
                "question": "测试问题SS_school",
                "options": [
                    {"value": 0, "text": "0 无问题"},
                    {"value": 1, "text": "1 轻度限制"}
                ],
                "selected": [1],
                "can_speak": True,
                "section": "SS_school"
            },
            {
                "id": 3,
                "type": "multiple_choice",
                "question": "测试问题SS_public",
                "options": [
                    {"value": 0, "text": "0 无问题"},
                    {"value": 1, "text": "1 轻度限制"}
                ],
                "selected": [1],
                "can_speak": True,
                "section": "SS_public"
            },
            {
                "id": 4,
                "type": "multiple_choice",
                "question": "测试问题SS_home",
                "options": [
                    {"value": 0, "text": "0 无问题"},
                    {"value": 1, "text": "1 轻度限制"}
                ],
                "selected": [0],
                "can_speak": True,
                "section": "SS_home"
            }
        ]
    }
    
    print("🧪 最简单的Frankfurt Scale提交测试")
    print("=" * 50)
    
    try:
        response = requests.post(f"{BASE_URL}/api/submit", 
                               json=test_data, 
                               timeout=10)
        
        print(f"状态码: {response.status_code}")
        
        response_data = response.json()
        print(f"响应内容:")
        print(json.dumps(response_data, indent=2, ensure_ascii=False))
        
        # 处理不同的响应格式
        if isinstance(response_data, list) and len(response_data) >= 2:
            actual_data = response_data[0]
            actual_status = response_data[1]
        else:
            actual_data = response_data
            actual_status = response.status_code
        
        if actual_status == 201 and actual_data.get('success'):
            print(f"\n✅ 提交成功!")
            print(f"问卷ID: {actual_data.get('questionnaire_id')}")
            return True
        else:
            print(f"\n❌ 提交失败:")
            error_info = actual_data.get('error', actual_data) if 'error' in actual_data else actual_data
            print(f"错误信息: {error_info.get('message', '未知错误')}")
            if 'details' in error_info:
                print(f"详细错误: {error_info['details']}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

if __name__ == "__main__":
    simple_test()