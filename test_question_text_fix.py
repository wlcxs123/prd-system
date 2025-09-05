#!/usr/bin/env python3
"""
测试问题文本修复
"""

import requests
import json

def test_question_text_fix():
    """测试修复后的问题文本字段"""
    
    print("=== 测试问题文本字段修复 ===")
    
    # 模拟修复后前端发送的数据格式
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
                "question": "在家里和父母说话",  # 现在应该有正确的问题文本
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
                "selected": [1],
                "can_speak": False
            }
        ],
        "statistics": {
            "total_score": 3,
            "completion_rate": 100,
            "submission_time": "2025-08-29T15:47:41.925192"
        }
    }
    
    try:
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
        print(f"response.ok: {response.ok}")
        
        if response.ok:
            result = response.json()
            print(f"响应数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result.get('success'):
                print("✅ 提交成功！问题文本验证通过")
                print(f"问卷ID: {result.get('id')}")
                return True
            else:
                print("❌ 提交失败")
                error_message = result.get('error', {}).get('message', '未知错误')
                print(f"错误信息: {error_message}")
                if 'details' in result.get('error', {}):
                    print("详细错误:")
                    for detail in result['error']['details']:
                        print(f"  - {detail}")
                return False
        else:
            print("❌ HTTP错误")
            try:
                error_data = response.json()
                print(f"错误详情: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
                if 'error' in error_data and 'details' in error_data['error']:
                    print("验证错误详情:")
                    for detail in error_data['error']['details']:
                        print(f"  - {detail}")
            except:
                print(f"错误文本: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_empty_question_text():
    """测试空问题文本的情况"""
    
    print("\n=== 测试空问题文本验证 ===")
    
    # 发送空问题文本的数据
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
                "question": "",  # 空问题文本 - 应该触发验证错误
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
            json=test_data,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            timeout=10
        )
        
        print(f"响应状态码: {response.status_code}")
        
        if not response.ok:
            error_data = response.json()
            print("✅ 空问题文本正确触发验证错误")
            if 'error' in error_data and 'details' in error_data['error']:
                print("验证错误详情:")
                for detail in error_data['error']['details']:
                    print(f"  - {detail}")
                    if "问题文本不能为空" in detail:
                        print("✅ 找到预期的验证错误消息")
        else:
            print("❌ 空问题文本应该触发验证错误")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    success = test_question_text_fix()
    test_empty_question_text()
    
    if success:
        print("\n🎉 问题文本字段修复成功！")
    else:
        print("\n❌ 问题文本字段仍有问题")