#!/usr/bin/env python3
"""
测试问卷提交集成
验证修复后的问卷页面能够成功提交到后端API
"""

import sys
import os
sys.path.append('backend')

import requests
import json
from datetime import datetime

def test_api_submission():
    """测试API提交功能"""
    print("=== 测试API提交功能 ===")
    
    # 测试数据 - 小学生交流评定表格式
    test_data = {
        "type": "elementary_school_communication_assessment",
        "basic_info": {
            "name": "测试学生",
            "grade": "三年级",
            "submission_date": "2024-01-15"
        },
        "questions": [
            {
                "id": 1,
                "type": "multiple_choice",
                "question": "在家里和亲密的家人交谈",
                "options": [
                    {"value": 0, "text": "非常容易(没有焦虑)"},
                    {"value": 1, "text": "相当容易(有点焦虑)"},
                    {"value": 2, "text": "有点困难(有不少焦虑)"},
                    {"value": 3, "text": "困难(更加焦虑)"},
                    {"value": 4, "text": "非常困难(高度焦虑)"}
                ],
                "selected": [1],
                "can_speak": True
            }
        ],
        "statistics": {
            "total_score": 1,
            "completion_rate": 100,
            "submission_time": datetime.now().isoformat()
        }
    }
    
    try:
        # 尝试连接到后端API
        response = requests.post(
            'http://127.0.0.1:5000/api/submit',
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            if result.get('success'):
                print("✅ API提交测试成功")
                print(f"   - 问卷ID: {result.get('id')}")
                print(f"   - 消息: {result.get('message')}")
                return True
            else:
                print("❌ API返回失败状态")
                print(f"   - 错误: {result.get('error')}")
                return False
        else:
            print(f"❌ API请求失败: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   - 错误详情: {error_data}")
            except:
                print(f"   - 响应内容: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务器")
        print("   请确保后端服务正在运行 (python backend/app.py)")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_validation_errors():
    """测试数据验证错误处理"""
    print("\n=== 测试数据验证错误处理 ===")
    
    # 故意提交无效数据
    invalid_data = {
        "type": "test_questionnaire",
        "basic_info": {
            "name": "",  # 空姓名应该失败
            "grade": "三年级",
            "submission_date": "2024-01-15"
        },
        "questions": []  # 空问题列表应该失败
    }
    
    try:
        response = requests.post(
            'http://127.0.0.1:5000/api/submit',
            json=invalid_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 400:
            result = response.json()
            if not result.get('success') and result.get('error'):
                print("✅ 数据验证错误处理正常")
                print(f"   - 错误类型: {result['error'].get('code')}")
                print(f"   - 错误消息: {result['error'].get('message')}")
                if result['error'].get('details'):
                    print(f"   - 详细信息: {result['error']['details']}")
                return True
            else:
                print("❌ 错误响应格式不正确")
                return False
        else:
            print(f"❌ 期望400错误，但得到: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务器")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    """运行所有集成测试"""
    print("问卷提交集成测试")
    print("=" * 50)
    
    test1_result = test_api_submission()
    test2_result = test_validation_errors()
    
    print("\n" + "=" * 50)
    print("集成测试结果总结:")
    print(f"API提交测试: {'✅ 通过' if test1_result else '❌ 失败'}")
    print(f"验证错误处理: {'✅ 通过' if test2_result else '❌ 失败'}")
    
    if test1_result and test2_result:
        print("\n🎉 所有集成测试通过！问卷提交功能修复成功。")
        return 0
    else:
        print("\n⚠️  部分测试失败。")
        if not test1_result:
            print("   - 请确保后端服务正在运行")
            print("   - 运行命令: python backend/app.py")
        return 1

if __name__ == "__main__":
    exit(main())