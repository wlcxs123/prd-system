#!/usr/bin/env python3
"""
测试原始问题是否已解决
模拟小学生交流评定表.html的确切行为
"""

import requests
import json

def test_original_issue():
    """测试原始的"保存失败"问题是否已解决"""
    
    print("=== 测试原始问题修复效果 ===")
    print("模拟小学生交流评定表.html的提交行为")
    
    # 模拟前端发送的数据格式（基于代码分析）
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
    
    try:
        # 发送POST请求 - 模拟前端的确切请求
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
        
        # 模拟前端的确切处理逻辑（来自小学生交流评定表.html:1410-1420）
        if response.ok:
            result = response.json()
            print(f"响应数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # 这是前端第1419行的关键检查
            if result.get('success'):
                print("✅ result.success 为 True")
                record_id = result.get('id') or result.get('record_id')
                print(f"✅ 前端会显示: 数据保存成功！问卷ID: {record_id}")
                print("✅ 原始问题已解决 - 不会抛出'保存失败'错误")
                return True
            else:
                print("❌ result.success 不为 True")
                error_message = result.get('error', {}).get('message', '保存失败')
                print(f"❌ 前端会抛出错误: Error: {error_message}")
                print("❌ 这就是原始问题 - 会在第1419行抛出'保存失败'错误")
                return False
        else:
            print("❌ response.ok 为 False")
            print("这不是原始问题，而是HTTP错误")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_edge_cases():
    """测试边缘情况"""
    
    print("\n=== 测试边缘情况 ===")
    
    # 测试1: 空数据
    print("\n1. 测试空数据:")
    try:
        response = requests.post(
            'http://127.0.0.1:5000/api/submit',
            json={},
            headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
            timeout=10
        )
        
        print(f"状态码: {response.status_code}, response.ok: {response.ok}")
        if not response.ok:
            result = response.json()
            if isinstance(result, dict) and 'success' in result:
                print("✅ 空数据正确返回验证错误格式")
            else:
                print("❌ 空数据返回格式不正确")
        else:
            print("❌ 空数据不应该返回成功状态")
            
    except Exception as e:
        print(f"空数据测试失败: {e}")
    
    # 测试2: 无效数据
    print("\n2. 测试无效数据:")
    try:
        response = requests.post(
            'http://127.0.0.1:5000/api/submit',
            json={"type": "invalid", "basic_info": {"name": "", "grade": "", "submission_date": "invalid"}},
            headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
            timeout=10
        )
        
        print(f"状态码: {response.status_code}, response.ok: {response.ok}")
        if not response.ok:
            result = response.json()
            if isinstance(result, dict) and 'success' in result and not result['success']:
                print("✅ 无效数据正确返回验证错误格式")
            else:
                print("❌ 无效数据返回格式不正确")
        else:
            print("❌ 无效数据不应该返回成功状态")
            
    except Exception as e:
        print(f"无效数据测试失败: {e}")

if __name__ == "__main__":
    success = test_original_issue()
    test_edge_cases()
    
    if success:
        print("\n🎉 修复成功！原始的'保存失败'问题已解决")
    else:
        print("\n❌ 修复失败，问题仍然存在")