#!/usr/bin/env python3
"""
测试小学生交流评定表提交问题
"""

import requests
import json

def test_submit_elementary_communication():
    """测试小学生交流评定表提交"""
    
    # 构建测试数据 - 模拟前端发送的数据格式
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
            },
            {
                "id": 2,
                "type": "multiple_choice", 
                "question": "在学校和老师说话",
                "options": [
                    {"value": 0, "text": "非常容易(没有焦虑)"},
                    {"value": 1, "text": "相当容易(有点焦虑)"},
                    {"value": 2, "text": "有点困难(有不少焦虑)"},
                    {"value": 3, "text": "困难(更加焦虑)"},
                    {"value": 4, "text": "非常困难(高度焦虑)"}
                ],
                "selected": [3],
                "can_speak": False
            }
        ],
        "statistics": {
            "total_score": 5,
            "completion_rate": 100,
            "submission_time": "2025-08-29T10:30:00.000Z"
        }
    }
    
    print("=== 测试小学生交流评定表提交 ===")
    print(f"测试数据: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
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
        
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            print(f"响应数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # 检查响应格式
            if 'success' in result:
                print(f"✅ success字段存在: {result['success']} (类型: {type(result['success'])})")
                if result['success']:
                    print("✅ 提交成功!")
                    if 'id' in result:
                        print(f"✅ 问卷ID: {result['id']}")
                else:
                    print("❌ success为False")
                    if 'error' in result:
                        print(f"错误信息: {result['error']}")
            else:
                print("❌ 响应中缺少success字段")
                
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            try:
                error_data = response.json()
                print(f"错误详情: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"错误文本: {response.text}")
                
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求失败: {e}")
    except Exception as e:
        print(f"❌ 其他错误: {e}")

if __name__ == "__main__":
    test_submit_elementary_communication()