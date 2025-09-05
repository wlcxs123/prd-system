#!/usr/bin/env python3
"""
测试问卷数据格式兼容性
验证修复后的问卷页面数据格式是否与后端API兼容
"""

import sys
import os
sys.path.append('backend')

from validation import validate_questionnaire_with_schema, normalize_questionnaire_data
import json

def test_elementary_school_format():
    """测试小学生交流评定表数据格式"""
    print("=== 测试小学生交流评定表数据格式 ===")
    
    # 模拟修复后的数据格式
    test_data = {
        "type": "elementary_school_communication_assessment",
        "basic_info": {
            "name": "张三",
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
            },
            {
                "id": 2,
                "type": "multiple_choice",
                "question": "在商店或餐厅与你的亲密家人交谈,其他人可能会听到",
                "options": [
                    {"value": 0, "text": "非常容易(没有焦虑)"},
                    {"value": 1, "text": "相当容易(有点焦虑)"},
                    {"value": 2, "text": "有点困难(有不少焦虑)"},
                    {"value": 3, "text": "困难(更加焦虑)"},
                    {"value": 4, "text": "非常困难(高度焦虑)"}
                ],
                "selected": [2],
                "can_speak": False
            }
        ],
        "statistics": {
            "total_score": 3,
            "completion_rate": 100,
            "submission_time": "2024-01-15T10:30:00Z"
        }
    }
    
    try:
        # 数据标准化
        normalized_data = normalize_questionnaire_data(test_data)
        print("✅ 数据标准化成功")
        
        # 数据验证
        is_valid, errors, validated_data = validate_questionnaire_with_schema(normalized_data)
        
        if is_valid:
            print("✅ 数据验证成功")
            print(f"   - 问卷类型: {validated_data['type']}")
            print(f"   - 姓名: {validated_data['basic_info']['name']}")
            print(f"   - 年级: {validated_data['basic_info']['grade']}")
            print(f"   - 问题数量: {len(validated_data['questions'])}")
            return True
        else:
            print("❌ 数据验证失败:")
            for error in errors:
                print(f"   - {error}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_parent_interview_format():
    """测试家长访谈表数据格式"""
    print("\n=== 测试家长访谈表数据格式 ===")
    
    # 模拟修复后的数据格式
    test_data = {
        "type": "parent_interview",
        "basic_info": {
            "name": "李四",
            "grade": "男 - 阳光幼儿园",
            "submission_date": "2010-05-15"
        },
        "questions": [
            {
                "id": 1,
                "type": "text_input",
                "question": "请列出您所有担忧的事。",
                "answer": "孩子在学校不愿意说话，与同学交流困难。"
            },
            {
                "id": 2,
                "type": "text_input",
                "question": "您认为孩子在其他方面的情况和其他同龄孩子一样好吗？",
                "answer": "在家里表现正常，但在外面比较内向。"
            },
            {
                "id": 3,
                "type": "text_input",
                "question": "这些问题出现多久了？",
                "answer": "大约从上幼儿园开始，已经有一年多了。"
            }
        ],
        "statistics": {
            "total_score": 3,
            "completion_rate": 75,
            "submission_time": "2024-01-15T10:30:00Z"
        }
    }
    
    try:
        # 数据标准化
        normalized_data = normalize_questionnaire_data(test_data)
        print("✅ 数据标准化成功")
        
        # 数据验证
        is_valid, errors, validated_data = validate_questionnaire_with_schema(normalized_data)
        
        if is_valid:
            print("✅ 数据验证成功")
            print(f"   - 问卷类型: {validated_data['type']}")
            print(f"   - 姓名: {validated_data['basic_info']['name']}")
            print(f"   - 年级: {validated_data['basic_info']['grade']}")
            print(f"   - 问题数量: {len(validated_data['questions'])}")
            return True
        else:
            print("❌ 数据验证失败:")
            for error in errors:
                print(f"   - {error}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_additional_questionnaires():
    """测试其他问卷数据格式"""
    print("\n=== 测试其他问卷数据格式 ===")
    
    # 测试数据集
    test_cases = [
        {
            "name": "SM维持因素清单",
            "data": {
                "type": "sm_maintenance_factors",
                "basic_info": {
                    "name": "王五",
                    "grade": "8岁 - 家长填写",
                    "submission_date": "2024-01-15"
                },
                "questions": [
                    {
                        "id": 1,
                        "type": "text_input",
                        "question": "家庭环境因素",
                        "answer": "家庭氛围较为安静，父母工作忙碌。"
                    }
                ],
                "statistics": {
                    "total_score": 1,
                    "completion_rate": 100,
                    "submission_time": "2024-01-15T10:30:00Z"
                }
            }
        },
        {
            "name": "青少年访谈表",
            "data": {
                "type": "adolescent_interview",
                "basic_info": {
                    "name": "赵六",
                    "grade": "青少年访谈",
                    "submission_date": "2024-01-15"
                },
                "questions": [
                    {
                        "id": 1,
                        "type": "text_input",
                        "question": "你觉得在什么情况下说话最困难？",
                        "answer": "在陌生人面前或者人多的时候。"
                    }
                ],
                "statistics": {
                    "total_score": 1,
                    "completion_rate": 100,
                    "submission_time": "2024-01-15T10:30:00Z"
                }
            }
        },
        {
            "name": "说话习惯记录",
            "data": {
                "type": "speech_habit",
                "basic_info": {
                    "name": "孙七",
                    "grade": "10岁 - 男",
                    "submission_date": "2024-01-15"
                },
                "questions": [
                    {
                        "id": 1,
                        "type": "multiple_choice",
                        "question": "family_familiar_passive",
                        "options": [
                            { "value": "0", "text": "从不" },
                            { "value": "1", "text": "很少" },
                            { "value": "2", "text": "有时" },
                            { "value": "3", "text": "经常" },
                            { "value": "4", "text": "总是" }
                        ],
                        "selected": ["2"]
                    }
                ],
                "statistics": {
                    "total_score": 1,
                    "completion_rate": 100,
                    "submission_time": "2024-01-15T10:30:00Z"
                }
            }
        },
        {
            "name": "小学生报告表",
            "data": {
                "type": "elementary_school_report",
                "basic_info": {
                    "name": "周八",
                    "grade": "小学生报告表",
                    "submission_date": "2024-01-15"
                },
                "questions": [
                    {
                        "id": 1,
                        "type": "text_input",
                        "question": "学习情况描述",
                        "answer": "学习成绩良好，但课堂参与度较低。"
                    }
                ],
                "statistics": {
                    "total_score": 1,
                    "completion_rate": 100,
                    "submission_time": "2024-01-15T10:30:00Z"
                }
            }
        }
    ]
    
    success_count = 0
    total_count = len(test_cases)
    
    for test_case in test_cases:
        try:
            print(f"\n  测试 {test_case['name']}:")
            
            # 数据标准化
            normalized_data = normalize_questionnaire_data(test_case['data'])
            print(f"    ✅ 数据标准化成功")
            
            # 数据验证
            is_valid, errors, validated_data = validate_questionnaire_with_schema(normalized_data)
            
            if is_valid:
                print(f"    ✅ 数据验证成功")
                print(f"       - 问卷类型: {validated_data['type']}")
                print(f"       - 姓名: {validated_data['basic_info']['name']}")
                success_count += 1
            else:
                print(f"    ❌ 数据验证失败:")
                for error in errors:
                    print(f"       - {error}")
                    
        except Exception as e:
            print(f"    ❌ 测试失败: {e}")
    
    print(f"\n  测试结果: {success_count}/{total_count} 通过")
    return success_count == total_count

def main():
    """运行所有测试"""
    print("问卷数据格式兼容性测试")
    print("=" * 50)
    
    test1_result = test_elementary_school_format()
    test2_result = test_parent_interview_format()
    test3_result = test_additional_questionnaires()
    
    print("\n" + "=" * 50)
    print("测试结果总结:")
    print(f"小学生交流评定表: {'✅ 通过' if test1_result else '❌ 失败'}")
    print(f"家长访谈表: {'✅ 通过' if test2_result else '❌ 失败'}")
    print(f"其他问卷表格: {'✅ 通过' if test3_result else '❌ 失败'}")
    
    if test1_result and test2_result and test3_result:
        print("\n🎉 所有测试通过！问卷数据格式修复成功。")
        return 0
    else:
        print("\n⚠️  部分测试失败，需要进一步修复。")
        return 1

if __name__ == "__main__":
    exit(main())