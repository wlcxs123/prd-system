#!/usr/bin/env python3
"""
调试数据处理的每个步骤
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from validation import normalize_questionnaire_data, validate_questionnaire_with_schema
from question_types import process_complete_questionnaire
import json

def debug_processing():
    """调试数据处理的每个步骤"""
    
    # 模拟前端提交的数据
    original_data = {
        "type": "frankfurt_scale_selective_mutism",
        "basic_info": {
            "name": "测试儿童",
            "grade": "小学",
            "submission_date": "2025-08-29",
            "guardian": "测试家长"
        },
        "questions": [
            {
                "id": 1,
                "type": "multiple_choice",
                "question": "在家很能说话，但在公共/学校环境明显沉默或避免用语言。",
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
                "question": "在课堂与老师说话",
                "options": [
                    {"value": 0, "text": "0 无问题"},
                    {"value": 1, "text": "1 轻度限制"},
                    {"value": 2, "text": "2 偶尔"},
                    {"value": 3, "text": "3 几乎从不"},
                    {"value": 4, "text": "4 完全不说"}
                ],
                "selected": [3],
                "can_speak": True,
                "section": "SS_school"
            }
        ],
        "statistics": {
            "age_group": "6_11",
            "ds_total": 1,
            "ss_school_total": 3,
            "completion_rate": 100
        }
    }
    
    print("=== 调试数据处理步骤 ===")
    print(f"原始数据:")
    print(json.dumps(original_data, indent=2, ensure_ascii=False))
    
    # 步骤1: 数据标准化
    print(f"\n=== 步骤1: 数据标准化 ===")
    try:
        normalized_data = normalize_questionnaire_data(original_data)
        print("标准化成功")
        print("标准化后的统计信息:")
        stats = normalized_data.get('statistics', {})
        for key, value in stats.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"标准化失败: {e}")
        return
    
    # 步骤2: 数据验证
    print(f"\n=== 步骤2: 数据验证 ===")
    try:
        is_valid, validation_errors, validated_data = validate_questionnaire_with_schema(normalized_data)
        if is_valid:
            print("验证成功")
            print("验证后的统计信息:")
            stats = validated_data.get('statistics', {})
            for key, value in stats.items():
                print(f"  {key}: {value}")
        else:
            print(f"验证失败: {validation_errors}")
            return
    except Exception as e:
        print(f"验证异常: {e}")
        return
    
    # 步骤3: 问题类型处理
    print(f"\n=== 步骤3: 问题类型处理 ===")
    try:
        final_data = process_complete_questionnaire(validated_data)
        print("问题类型处理成功")
        print("最终的统计信息:")
        stats = final_data.get('statistics', {})
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # 检查是否有total_score字段
        if 'total_score' in final_data.get('statistics', {}):
            print("❌ 发现了total_score字段！")
        else:
            print("✅ 没有total_score字段")
            
    except Exception as e:
        print(f"问题类型处理异常: {e}")
        return
    
    print(f"\n=== 处理完成 ===")

if __name__ == "__main__":
    debug_processing()