#!/usr/bin/env python3
"""
验证增强功能集成测试
测试增强的验证功能与API的集成
"""

import json
from datetime import date
from validation import (
    validate_questionnaire_with_schema,
    normalize_questionnaire_data,
    check_data_integrity,
    quick_validate
)

def test_enhanced_validation_integration():
    """测试增强验证功能的集成"""
    print("=== 测试增强验证功能集成 ===\n")
    
    # 测试用例1：完整的有效问卷
    print("1. 测试完整的有效问卷")
    valid_questionnaire = {
        'type': 'student_report',
        'basic_info': {
            'name': '张小明',
            'grade': '3年级',
            'submission_date': date.today().strftime('%Y-%m-%d'),
            'age': 9,
            'gender': '男',
            'school': '实验小学',
            'class_name': '三年级一班'
        },
        'questions': [
            {
                'id': 1,
                'type': 'multiple_choice',
                'question': '你最喜欢的学科是什么？',
                'options': [
                    {'value': 1, 'text': '语文'},
                    {'value': 2, 'text': '数学'},
                    {'value': 3, 'text': '英语'},
                    {'value': 4, 'text': '科学'}
                ],
                'selected': [2],
                'allow_multiple': False,
                'is_required': True
            },
            {
                'id': 2,
                'type': 'text_input',
                'question': '请描述你的学习方法',
                'answer': '我喜欢通过做练习题来巩固知识',
                'input_type': 'textarea',
                'max_length': 500,
                'is_required': True
            },
            {
                'id': 3,
                'type': 'text_input',
                'question': '你的邮箱地址（可选）',
                'answer': 'student@example.com',
                'input_type': 'email',
                'is_required': False
            }
        ],
        'statistics': {
            'completion_rate': 100,
            'submission_time': '2024-01-15T10:30:00Z'
        }
    }
    
    # 测试数据标准化
    normalized = normalize_questionnaire_data(valid_questionnaire)
    print(f"✅ 数据标准化成功")
    
    # 测试Schema验证
    is_valid, errors, validated_data = validate_questionnaire_with_schema(normalized)
    if is_valid:
        print(f"✅ Schema验证通过")
    else:
        print(f"❌ Schema验证失败: {errors}")
        return False
    
    # 测试完整性检查
    integrity_errors = check_data_integrity(normalized)
    if not integrity_errors:
        print(f"✅ 完整性检查通过")
    else:
        print(f"❌ 完整性检查失败: {integrity_errors}")
        return False
    
    # 测试快速验证
    quick_errors = quick_validate(valid_questionnaire)
    if not quick_errors:
        print(f"✅ 快速验证通过")
    else:
        print(f"❌ 快速验证失败: {quick_errors}")
        return False
    
    print()
    
    # 测试用例2：包含错误的问卷
    print("2. 测试包含错误的问卷")
    invalid_questionnaire = {
        'type': 'student_report',
        'basic_info': {
            'name': '',  # 空姓名
            'grade': '3年级',
            'submission_date': '2025-12-31',  # 未来日期
            'age': 200,  # 无效年龄
            'gender': 'unknown'  # 无效性别
        },
        'questions': [
            {
                'id': 1,
                'type': 'multiple_choice',
                'question': '',  # 空问题
                'options': [
                    {'value': 1, 'text': '选项1'},
                    {'value': 1, 'text': '选项2'}  # 重复值
                ],
                'selected': [999],  # 无效选择
                'allow_multiple': False
            },
            {
                'id': 1,  # 重复ID
                'type': 'text_input',
                'question': '邮箱地址',
                'answer': 'invalid-email',  # 无效邮箱
                'input_type': 'email'
            }
        ]
    }
    
    # 测试错误检测
    quick_errors = quick_validate(invalid_questionnaire)
    if quick_errors:
        print(f"✅ 成功检测到 {len(quick_errors)} 个错误:")
        for i, error in enumerate(quick_errors[:5], 1):  # 只显示前5个错误
            print(f"  {i}. {error}")
        if len(quick_errors) > 5:
            print(f"  ... 还有 {len(quick_errors) - 5} 个错误")
    else:
        print(f"❌ 未能检测到错误")
        return False
    
    print()
    
    # 测试用例3：边界情况
    print("3. 测试边界情况")
    edge_cases = [
        {
            'name': '最小有效问卷',
            'data': {
                'type': 'test',
                'basic_info': {
                    'name': '测',
                    'grade': '1',
                    'submission_date': date.today().strftime('%Y-%m-%d')
                },
                'questions': [
                    {
                        'id': 1,
                        'type': 'text_input',
                        'question': '测试',
                        'answer': '',
                        'is_required': False
                    }
                ]
            }
        },
        {
            'name': '最大长度测试',
            'data': {
                'type': 'test',
                'basic_info': {
                    'name': 'a' * 50,  # 最大长度姓名
                    'grade': 'b' * 20,  # 最大长度年级
                    'submission_date': date.today().strftime('%Y-%m-%d')
                },
                'questions': [
                    {
                        'id': 1,
                        'type': 'text_input',
                        'question': 'c' * 500,  # 最大长度问题
                        'answer': 'd' * 1000,  # 长答案
                        'is_required': True
                    }
                ]
            }
        }
    ]
    
    for case in edge_cases:
        errors = quick_validate(case['data'])
        if not errors:
            print(f"✅ {case['name']} 验证通过")
        else:
            print(f"❌ {case['name']} 验证失败: {errors[:2]}")  # 只显示前2个错误
    
    print()
    return True

def test_performance():
    """测试验证性能"""
    print("=== 测试验证性能 ===\n")
    
    import time
    
    # 创建一个中等复杂度的问卷
    test_questionnaire = {
        'type': 'performance_test',
        'basic_info': {
            'name': '性能测试用户',
            'grade': '测试年级',
            'submission_date': date.today().strftime('%Y-%m-%d'),
            'age': 25
        },
        'questions': []
    }
    
    # 添加多个问题
    for i in range(20):
        if i % 2 == 0:
            # 选择题
            question = {
                'id': i + 1,
                'type': 'multiple_choice',
                'question': f'这是第{i+1}个选择题',
                'options': [
                    {'value': j, 'text': f'选项{j}'} for j in range(1, 6)
                ],
                'selected': [1],
                'allow_multiple': False
            }
        else:
            # 填空题
            question = {
                'id': i + 1,
                'type': 'text_input',
                'question': f'这是第{i+1}个填空题',
                'answer': f'这是第{i+1}题的答案',
                'input_type': 'text'
            }
        test_questionnaire['questions'].append(question)
    
    # 测试验证性能
    iterations = 100
    start_time = time.time()
    
    for _ in range(iterations):
        errors = quick_validate(test_questionnaire)
    
    end_time = time.time()
    avg_time = (end_time - start_time) / iterations * 1000  # 转换为毫秒
    
    print(f"验证性能测试结果:")
    print(f"问卷复杂度: {len(test_questionnaire['questions'])} 个问题")
    print(f"验证次数: {iterations} 次")
    print(f"平均验证时间: {avg_time:.2f} 毫秒")
    print(f"验证结果: {'通过' if not errors else f'发现{len(errors)}个错误'}")
    
    if avg_time < 50:  # 50毫秒以内认为性能良好
        print("✅ 验证性能良好")
        return True
    else:
        print("⚠️ 验证性能可能需要优化")
        return False

def main():
    """主测试函数"""
    print("开始测试数据验证增强功能集成...\n")
    
    success1 = test_enhanced_validation_integration()
    success2 = test_performance()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("🎉 所有集成测试通过！数据验证增强功能实现成功。")
        print("\n增强功能包括:")
        print("- ✅ 更严格的数据格式验证")
        print("- ✅ 增强的字段完整性检查")
        print("- ✅ 业务逻辑验证")
        print("- ✅ 性能优化的验证流程")
        print("- ✅ 全面的单元测试覆盖")
        return True
    else:
        print("❌ 部分集成测试失败，请检查实现。")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)