#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试验证流程
"""

import sys
sys.path.append('backend')

from validation import validate_questionnaire_with_schema, normalize_questionnaire_data
from question_types import question_processor
import json

def debug_rating_scale():
    """调试rating_scale验证"""
    print("🔍 调试rating_scale验证...")
    
    # 原始数据
    raw_data = {
        'type': 'test_rating_scale',
        'basic_info': {
            'name': '测试学生',
            'grade': '小学三年级',
            'submission_date': '2025-08-29'
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
            'submission_time': '2025-08-29T15:39:33'
        }
    }
    
    print("原始数据:")
    print(json.dumps(raw_data, indent=2, ensure_ascii=False))
    
    # 数据标准化
    try:
        normalized_data = normalize_questionnaire_data(raw_data)
        print("\n标准化后的数据:")
        print(json.dumps(normalized_data, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ 数据标准化失败: {str(e)}")
        return
    
    # 问题类型处理器验证
    question = normalized_data['questions'][0]
    print(f"\n问题数据: {json.dumps(question, indent=2, ensure_ascii=False)}")
    
    try:
        type_errors = question_processor.validate_question(question)
        print(f"问题类型处理器验证结果: {type_errors}")
    except Exception as e:
        print(f"❌ 问题类型处理器验证异常: {str(e)}")
        return
    
    # 完整验证
    try:
        is_valid, validation_errors, validated_data = validate_questionnaire_with_schema(normalized_data)
        print(f"\n完整验证结果:")
        print(f"是否有效: {is_valid}")
        print(f"验证错误: {validation_errors}")
        if is_valid:
            print(f"验证后的数据: {json.dumps(validated_data, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"❌ 完整验证异常: {str(e)}")

def debug_multiple_choice():
    """调试多选题验证"""
    print("\n🔍 调试多选题验证...")
    
    # 原始数据
    raw_data = {
        'type': 'test_multiple_choice',
        'basic_info': {
            'name': '测试学生',
            'grade': '青少年访谈',
            'submission_date': '2025-08-29'
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
            'submission_time': '2025-08-29T15:39:33'
        }
    }
    
    print("原始数据:")
    print(json.dumps(raw_data, indent=2, ensure_ascii=False))
    
    # 数据标准化
    try:
        normalized_data = normalize_questionnaire_data(raw_data)
        print("\n标准化后的数据:")
        print(json.dumps(normalized_data, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ 数据标准化失败: {str(e)}")
        return
    
    # 问题类型处理器验证
    question = normalized_data['questions'][0]
    print(f"\n问题数据: {json.dumps(question, indent=2, ensure_ascii=False)}")
    
    try:
        type_errors = question_processor.validate_question(question)
        print(f"问题类型处理器验证结果: {type_errors}")
    except Exception as e:
        print(f"❌ 问题类型处理器验证异常: {str(e)}")
        return
    
    # 完整验证
    try:
        is_valid, validation_errors, validated_data = validate_questionnaire_with_schema(normalized_data)
        print(f"\n完整验证结果:")
        print(f"是否有效: {is_valid}")
        print(f"验证错误: {validation_errors}")
        if is_valid:
            print(f"验证后的数据: {json.dumps(validated_data, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"❌ 完整验证异常: {str(e)}")

if __name__ == "__main__":
    debug_rating_scale()
    debug_multiple_choice()