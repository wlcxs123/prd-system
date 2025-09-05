#!/usr/bin/env python3
"""
模拟前端的确切行为来测试修复效果
"""

import requests
import json

def simulate_frontend_behavior():
    """模拟前端的确切行为"""
    
    # 模拟前端发送的数据
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
    
    print("=== 模拟前端提交行为 ===")
    
    try:
        # 发送请求
        response = requests.post(
            'http://127.0.0.1:5000/api/submit',
            json=test_data,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            timeout=10
        )
        
        print(f"响应状态: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        # 模拟前端的处理逻辑
        if response.ok:  # response.ok 检查
            print("✅ response.ok 为 True")
            
            result = response.json()
            print(f"响应数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # 模拟前端的success检查
            if result.get('success'):
                print("✅ result.success 为 True - 前端会显示成功消息")
                record_id = result.get('id') or result.get('record_id')
                print(f"✅ 数据保存成功！问卷ID: {record_id}")
                # 这里前端会调用 showCompletion(record_id)
                print("前端会显示: ✅ 数据保存成功！")
            else:
                print("❌ result.success 不为 True - 前端会抛出错误")
                error_message = result.get('error', {}).get('message', '保存失败')
                print(f"前端会抛出错误: Error: {error_message}")
                
        else:
            print("❌ response.ok 为 False - 前端会处理HTTP错误")
            try:
                error_data = response.json()
                if error_data.get('error'):
                    if error_data['error'].get('details') and isinstance(error_data['error']['details'], list):
                        error_message = '数据验证失败：\n' + '\n'.join(error_data['error']['details'])
                    else:
                        error_message = error_data['error'].get('message') or error_data.get('message') or f"服务器错误 ({response.status_code})"
                else:
                    error_message = f"服务器错误 ({response.status_code})"
            except:
                error_message = f"HTTP {response.status_code}: {response.reason}"
            
            print(f"前端会显示错误: ❌ 数据保存失败:\n{error_message}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络错误: {e}")
        print("前端会显示网络错误诊断信息")

def test_validation_error_frontend():
    """测试验证错误时前端的行为"""
    
    print("\n=== 测试验证错误时前端行为 ===")
    
    # 发送无效数据
    invalid_data = {
        "type": "elementary_school_communication_assessment",
        "basic_info": {
            "name": "",  # 空姓名
            "grade": "三年级",
            "submission_date": "2025-08-29"
        },
        "questions": []  # 空问题
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
        
        print(f"响应状态: {response.status_code}")
        
        if response.ok:
            print("✅ response.ok 为 True (这不应该发生在验证错误时)")
            result = response.json()
            if result.get('success'):
                print("✅ result.success 为 True - 意外成功")
            else:
                print("❌ result.success 为 False - 前端会抛出错误")
                error_message = result.get('error', {}).get('message', '保存失败')
                print(f"前端会抛出错误: Error: {error_message}")
        else:
            print("❌ response.ok 为 False - 前端会处理验证错误")
            try:
                error_data = response.json()
                if error_data.get('error') and error_data['error'].get('details'):
                    error_message = '数据验证失败：\n' + '\n'.join(error_data['error']['details'])
                    print(f"前端会显示: ❌ 数据保存失败:\n{error_message}")
                else:
                    print("前端会显示通用错误消息")
            except:
                print("前端会显示HTTP错误消息")
                
    except Exception as e:
        print(f"❌ 请求失败: {e}")

if __name__ == "__main__":
    simulate_frontend_behavior()
    test_validation_error_frontend()