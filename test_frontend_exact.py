#!/usr/bin/env python3
"""
测试前端发送的确切数据格式
"""

import requests
import json

def test_exact_frontend_data():
    """测试前端发送的确切数据格式"""
    
    # 这是前端实际发送的数据格式（基于代码分析）
    test_data = {
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
    
    print("=== 测试前端确切数据格式 ===")
    
    try:
        # 发送POST请求
        response = requests.post(
            'http://127.0.0.1:5000/api/submit',
            json=test_data,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            timeout=10
        )
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"响应数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # 模拟前端的检查逻辑
            if response.ok:
                print("✅ response.ok 为 True")
                if result.get('success'):
                    print("✅ result.success 为 True - 前端应该成功")
                    print(f"问卷ID: {result.get('id', result.get('record_id'))}")
                else:
                    print("❌ result.success 不为 True - 这会导致前端报错")
                    print(f"错误信息: {result.get('error', {}).get('message', '保存失败')}")
            else:
                print("❌ response.ok 为 False")
                
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            try:
                error_data = response.json()
                print(f"错误详情: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"错误文本: {response.text}")
                
    except Exception as e:
        print(f"❌ 请求失败: {e}")

def test_empty_data():
    """测试空数据的情况"""
    print("\n=== 测试空数据 ===")
    
    try:
        response = requests.post(
            'http://127.0.0.1:5000/api/submit',
            json={},
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            timeout=10
        )
        
        print(f"响应状态码: {response.status_code}")
        result = response.json()
        print(f"响应数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
    except Exception as e:
        print(f"❌ 请求失败: {e}")

def test_invalid_data():
    """测试无效数据的情况"""
    print("\n=== 测试无效数据 ===")
    
    invalid_data = {
        "type": "elementary_school_communication_assessment",
        "basic_info": {
            "name": "",  # 空姓名
            "grade": "",  # 空年级
            "submission_date": "invalid-date"  # 无效日期
        },
        "questions": []  # 空问题列表
    }
    
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
        result = response.json()
        print(f"响应数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
    except Exception as e:
        print(f"❌ 请求失败: {e}")

if __name__ == "__main__":
    test_exact_frontend_data()
    test_empty_data()
    test_invalid_data()