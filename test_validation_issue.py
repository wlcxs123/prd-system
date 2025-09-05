#!/usr/bin/env python3
"""
测试验证错误的具体情况
"""

import requests
import json

def test_validation_error_response():
    """测试验证错误时的响应格式"""
    
    # 发送无效数据触发验证错误
    invalid_data = {
        "type": "elementary_school_communication_assessment",
        "basic_info": {
            "name": "",  # 空姓名 - 应该触发验证错误
            "grade": "三年级",
            "submission_date": "2025-08-29"
        },
        "questions": []  # 空问题列表 - 应该触发验证错误
    }
    
    print("=== 测试验证错误响应格式 ===")
    
    try:
        response = requests.post(
            'http://127.0.0.1:5000/api/submit',
            json=invalid_data,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            timeout=10
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应原始内容: {response.text}")
        
        # 尝试解析JSON
        try:
            result = response.json()
            print(f"解析后的JSON: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # 检查响应格式
            if isinstance(result, list) and len(result) == 2:
                print("❌ 响应是一个包含两个元素的列表 - 这是问题所在!")
                print(f"第一个元素 (应该是响应数据): {result[0]}")
                print(f"第二个元素 (应该是状态码): {result[1]}")
                
                # 检查第一个元素是否有success字段
                if isinstance(result[0], dict) and 'success' in result[0]:
                    print(f"success字段值: {result[0]['success']}")
                
            elif isinstance(result, dict):
                print("✅ 响应是一个字典 - 格式正确")
                if 'success' in result:
                    print(f"success字段值: {result['success']}")
                    
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")

def test_successful_submission():
    """测试成功提交时的响应格式"""
    
    print("\n=== 测试成功提交响应格式 ===")
    
    valid_data = {
        "type": "elementary_school_communication_assessment",
        "basic_info": {
            "name": "测试学生",
            "grade": "三年级",
            "submission_date": "2025-08-29"
        },
        "questions": [
            {
                "id": 1,
                "type": "multiple_choice",
                "question": "在家里和父母说话",
                "options": [
                    {"value": 0, "text": "非常容易(没有焦虑)"},
                    {"value": 1, "text": "相当容易(有点焦虑)"},
                    {"value": 2, "text": "有点困难(有不少焦虑)"},
                    {"value": 3, "text": "困难(更加焦虑)"},
                    {"value": 4, "text": "非常困难(高度焦虑)"}
                ],
                "selected": [2],
                "can_speak": True
            }
        ],
        "statistics": {
            "total_score": 2,
            "completion_rate": 100,
            "submission_time": "2025-08-29T15:47:41.925192"
        }
    }
    
    try:
        response = requests.post(
            'http://127.0.0.1:5000/api/submit',
            json=valid_data,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            timeout=10
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应原始内容: {response.text}")
        
        try:
            result = response.json()
            print(f"解析后的JSON: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if isinstance(result, dict):
                print("✅ 响应是一个字典 - 格式正确")
                if 'success' in result:
                    print(f"success字段值: {result['success']} (类型: {type(result['success'])})")
                    
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")

if __name__ == "__main__":
    test_validation_error_response()
    test_successful_submission()