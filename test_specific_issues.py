#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试特定问题的脚本
专门测试rating_scale和多选题问题
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"
API_ENDPOINT = f"{BASE_URL}/api/submit"

def test_rating_scale():
    """测试rating_scale问题类型"""
    print("🔍 测试rating_scale问题类型...")
    
    data = {
        'type': 'test_rating_scale',
        'basic_info': {
            'name': '测试学生',
            'grade': '小学三年级',
            'submission_date': datetime.now().strftime('%Y-%m-%d')
        },
        'questions': [
            {
                'id': 1,
                'type': 'rating_scale',
                'question': '测试评分问题',
                'rating': 3,
                'can_speak': True
            }
        ],
        'statistics': {
            'total_score': 3,
            'completion_rate': 100,
            'submission_time': datetime.now().isoformat()
        }
    }
    
    try:
        response = requests.post(API_ENDPOINT, json=data, timeout=10)
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 201:
            result = response.json()
            if result.get('success'):
                print("✅ rating_scale测试成功")
                return True
            else:
                print("❌ rating_scale测试失败")
                return False
        else:
            print("❌ rating_scale测试失败")
            return False
            
    except Exception as e:
        print(f"❌ rating_scale测试异常: {str(e)}")
        return False

def test_multiple_choice():
    """测试多选题"""
    print("\n🔍 测试多选题...")
    
    data = {
        'type': 'test_multiple_choice',
        'basic_info': {
            'name': '测试学生',
            'grade': '青少年访谈',
            'submission_date': datetime.now().strftime('%Y-%m-%d')
        },
        'questions': [
            {
                'id': 1,
                'type': 'multiple_choice',
                'question': '测试多选题',
                'options': [
                    {'value': '1', 'text': '选项1'},
                    {'value': '2', 'text': '选项2'},
                    {'value': '3', 'text': '选项3'},
                    {'value': '4', 'text': '选项4'}
                ],
                'selected': ['2', '3'],
                'allow_multiple': True
            }
        ],
        'statistics': {
            'total_score': 1,
            'completion_rate': 100,
            'submission_time': datetime.now().isoformat()
        }
    }
    
    try:
        response = requests.post(API_ENDPOINT, json=data, timeout=10)
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 201:
            result = response.json()
            if result.get('success'):
                print("✅ 多选题测试成功")
                return True
            else:
                print("❌ 多选题测试失败")
                return False
        else:
            print("❌ 多选题测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 多选题测试异常: {str(e)}")
        return False

def main():
    print("🎯 特定问题测试工具")
    print("=" * 40)
    
    # 测试rating_scale
    rating_success = test_rating_scale()
    
    # 测试多选题
    multiple_success = test_multiple_choice()
    
    print("\n" + "=" * 40)
    print("📊 测试结果总结")
    print(f"rating_scale: {'✅ 成功' if rating_success else '❌ 失败'}")
    print(f"多选题: {'✅ 成功' if multiple_success else '❌ 失败'}")

if __name__ == "__main__":
    main()