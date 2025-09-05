"""
数据验证模块演示脚本
展示前端和后端验证功能的使用方法
"""

import json
from validation import (
    validate_questionnaire_with_schema,
    normalize_questionnaire_data,
    quick_validate,
    create_validation_error_response
)
from question_types import process_complete_questionnaire

def demo_frontend_validation():
    """演示前端验证功能"""
    print("=== 前端验证功能演示 ===")
    
    # 模拟前端数据
    frontend_data = {
        "type": "student_communication_assessment",
        "basic_info": {
            "name": "小明",
            "grade": "三年级",
            "submission_date": "2024-01-15"
        },
        "questions": [
            {
                "id": 1,
                "type": "multiple_choice",
                "question": "你在学校最喜欢和谁说话？",
                "options": [
                    {"value": 0, "text": "老师"},
                    {"value": 1, "text": "同学"},
                    {"value": 2, "text": "都喜欢"}
                ],
                "selected": [1, 2]
            },
            {
                "id": 2,
                "type": "text_input",
                "question": "请描述一下你最近和朋友的一次对话",
                "answer": "昨天我和小红聊了关于数学作业的事情，她教了我一个新的解题方法。"
            }
        ]
    }
    
    print("1. 原始前端数据:")
    print(json.dumps(frontend_data, ensure_ascii=False, indent=2))
    
    # 使用快速验证
    errors = quick_validate(frontend_data)
    if errors:
        print(f"\n❌ 验证失败: {errors}")
    else:
        print("\n✅ 前端数据验证通过")

def demo_backend_validation():
    """演示后端验证功能"""
    print("\n=== 后端验证功能演示 ===")
    
    # 模拟后端接收的数据（可能包含不规范格式）
    backend_data = {
        "type": "  PARENT_INTERVIEW  ",  # 需要标准化
        "name": "  张三  ",  # 根级别字段（向后兼容）
        "grade": "  五年级  ",
        "submission_date": "2024-01-15",
        "questions": [
            {
                "id": "1",  # 字符串ID
                "type": "multiple_choice",
                "question": "  您认为孩子的沟通能力如何？  ",
                "options": [
                    {"value": 0, "text": "  很好  "},
                    {"value": 1, "text": "  一般  "},
                    {"value": 2, "text": "  需要改进  "}
                ],
                "selected": 0  # 非数组格式
            }
        ]
    }
    
    print("1. 原始后端数据:")
    print(json.dumps(backend_data, ensure_ascii=False, indent=2))
    
    # 步骤1: 数据标准化
    print("\n2. 数据标准化...")
    normalized_data = normalize_questionnaire_data(backend_data)
    print("标准化后的数据:")
    print(json.dumps(normalized_data, ensure_ascii=False, indent=2))
    
    # 步骤2: Schema验证
    print("\n3. Schema验证...")
    is_valid, errors, validated_data = validate_questionnaire_with_schema(normalized_data)
    if is_valid:
        print("✅ Schema验证通过")
    else:
        print(f"❌ Schema验证失败: {errors}")
        return
    
    # 步骤3: 问题类型处理
    print("\n4. 问题类型处理...")
    processed_data = process_complete_questionnaire(validated_data)
    print("处理后的数据:")
    
    # 转换日期对象为字符串以便JSON序列化
    def convert_dates(obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: convert_dates(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_dates(item) for item in obj]
        return obj
    
    serializable_data = convert_dates(processed_data)
    print(json.dumps(serializable_data, ensure_ascii=False, indent=2))

def demo_error_handling():
    """演示错误处理功能"""
    print("\n=== 错误处理功能演示 ===")
    
    # 故意创建有错误的数据
    invalid_data = {
        "type": "",  # 空类型
        "basic_info": {
            "name": "",  # 空姓名
            "grade": "",  # 空年级
            "submission_date": "invalid-date"  # 无效日期
        },
        "questions": [
            {
                "id": 1,
                "type": "multiple_choice",
                "question": "",  # 空问题
                "options": [],  # 空选项
                "selected": []  # 空选择
            },
            {
                "id": 2,
                "type": "text_input",
                "question": "测试问题",
                "answer": ""  # 空答案
            }
        ]
    }
    
    print("1. 无效数据:")
    print(json.dumps(invalid_data, ensure_ascii=False, indent=2))
    
    # 使用快速验证
    errors = quick_validate(invalid_data)
    print(f"\n2. 验证错误 ({len(errors)} 个):")
    for i, error in enumerate(errors, 1):
        print(f"   {i}. {error}")
    
    # 创建标准错误响应
    error_response = create_validation_error_response(errors)
    print("\n3. 标准错误响应:")
    print(json.dumps(error_response, ensure_ascii=False, indent=2))

def demo_marshmallow_schemas():
    """演示Marshmallow Schema的使用"""
    print("\n=== Marshmallow Schema演示 ===")
    
    from validation import QuestionnaireSchema, BasicInfoSchema
    
    # 测试基本信息Schema
    print("1. 基本信息Schema验证:")
    basic_info_schema = BasicInfoSchema()
    
    valid_basic_info = {
        "name": "李四",
        "grade": "六年级",
        "submission_date": "2024-01-15",
        "age": 12
    }
    
    try:
        result = basic_info_schema.load(valid_basic_info)
        print("✅ 基本信息验证通过:")
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    except Exception as e:
        print(f"❌ 基本信息验证失败: {e}")
    
    # 测试完整问卷Schema
    print("\n2. 完整问卷Schema验证:")
    questionnaire_schema = QuestionnaireSchema()
    
    valid_questionnaire = {
        "type": "test_questionnaire",
        "basic_info": valid_basic_info,
        "questions": [
            {
                "id": 1,
                "type": "multiple_choice",
                "question": "你最喜欢的颜色？",
                "options": [
                    {"value": 0, "text": "红色"},
                    {"value": 1, "text": "蓝色"}
                ],
                "selected": [0]
            }
        ]
    }
    
    try:
        result = questionnaire_schema.load(valid_questionnaire)
        print("✅ 问卷验证通过")
        print("处理后的问题数据:")
        for question in result['questions']:
            if 'selected_texts' in question:
                print(f"   - 问题: {question['question']}")
                print(f"   - 选择: {question['selected_texts']}")
    except Exception as e:
        print(f"❌ 问卷验证失败: {e}")

if __name__ == "__main__":
    print("🔍 数据验证模块功能演示")
    print("=" * 50)
    
    # 运行所有演示
    demo_frontend_validation()
    demo_backend_validation()
    demo_error_handling()
    demo_marshmallow_schemas()
    
    print("\n" + "=" * 50)
    print("✨ 演示完成！数据验证模块功能齐全，支持:")
    print("   • 前端JavaScript验证")
    print("   • 后端Marshmallow Schema验证")
    print("   • 数据标准化和格式化")
    print("   • 多种问题类型支持")
    print("   • 完整的错误处理")
    print("   • 数据完整性检查")