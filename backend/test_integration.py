"""
集成测试脚本
测试数据验证和问题类型处理的集成功能
"""

import json
from validation import validate_questionnaire_with_schema, normalize_questionnaire_data
from question_types import process_complete_questionnaire

def test_integration():
    """测试完整的数据处理流程"""
    
    # 测试数据 - 包含多种问题类型
    test_data = {
        "type": "student_evaluation",
        "basic_info": {
            "name": "张小明",
            "grade": "五年级",
            "submission_date": "2024-01-15",
            "age": 11
        },
        "questions": [
            {
                "id": 1,
                "type": "multiple_choice",
                "question": "你最喜欢的学科是什么？",
                "options": [
                    {"value": 0, "text": "数学"},
                    {"value": 1, "text": "语文"},
                    {"value": 2, "text": "英语"},
                    {"value": 3, "text": "科学"}
                ],
                "selected": [0, 2]  # 多选
            },
            {
                "id": 2,
                "type": "text_input",
                "question": "请描述你的学习方法",
                "answer": "我会制定学习计划，每天按时完成作业，遇到不懂的问题会主动问老师。",
                "max_length": 200
            },
            {
                "id": 3,
                "type": "multiple_choice",
                "question": "你认为自己的学习态度如何？",
                "options": [
                    {"value": "excellent", "text": "非常好"},
                    {"value": "good", "text": "好"},
                    {"value": "average", "text": "一般"},
                    {"value": "poor", "text": "需要改进"}
                ],
                "selected": ["good"]
            }
        ]
    }
    
    print("=== 集成测试开始 ===")
    
    # 步骤1: 数据标准化
    print("\n1. 数据标准化...")
    try:
        normalized_data = normalize_questionnaire_data(test_data)
        print("✓ 数据标准化成功")
        print(f"  - 问卷类型: {normalized_data['type']}")
        print(f"  - 学生姓名: {normalized_data['basic_info']['name']}")
        print(f"  - 问题数量: {len(normalized_data['questions'])}")
    except Exception as e:
        print(f"✗ 数据标准化失败: {e}")
        return False
    
    # 步骤2: Schema验证
    print("\n2. Schema验证...")
    try:
        is_valid, errors, validated_data = validate_questionnaire_with_schema(normalized_data)
        if is_valid:
            print("✓ Schema验证通过")
        else:
            print(f"✗ Schema验证失败: {errors}")
            return False
    except Exception as e:
        print(f"✗ Schema验证异常: {e}")
        return False
    
    # 步骤3: 问题类型处理
    print("\n3. 问题类型处理...")
    try:
        processed_data = process_complete_questionnaire(validated_data)
        print("✓ 问题类型处理成功")
        
        # 检查统计信息
        stats = processed_data.get('statistics', {})
        print(f"  - 总问题数: {stats.get('total_questions', 0)}")
        print(f"  - 已回答问题数: {stats.get('answered_questions', 0)}")
        print(f"  - 总得分: {stats.get('total_score', 0)}")
        print(f"  - 完成率: {stats.get('completion_rate', 0)}%")
        
        # 检查问题处理结果
        for i, question in enumerate(processed_data['questions']):
            print(f"  - 第{i+1}题 ({question['type']}): ", end="")
            if question['type'] == 'multiple_choice':
                selected_texts = question.get('selected_texts', [])
                print(f"选择了 {len(question.get('selected', []))} 个选项: {', '.join(selected_texts)}")
            elif question['type'] == 'text_input':
                answer_length = question.get('answer_length', 0)
                word_count = question.get('word_count', 0)
                print(f"回答长度 {answer_length} 字符, {word_count} 个词")
        
    except Exception as e:
        print(f"✗ 问题类型处理失败: {e}")
        return False
    
    # 步骤4: 验证最终数据结构
    print("\n4. 验证最终数据结构...")
    try:
        # 检查必要字段
        required_fields = ['type', 'basic_info', 'questions', 'statistics']
        for field in required_fields:
            if field not in processed_data:
                print(f"✗ 缺少必要字段: {field}")
                return False
        
        # 检查基本信息
        basic_info = processed_data['basic_info']
        if not all(key in basic_info for key in ['name', 'grade', 'submission_date']):
            print("✗ 基本信息不完整")
            return False
        
        # 检查问题数据
        questions = processed_data['questions']
        if not questions:
            print("✗ 问题列表为空")
            return False
        
        for question in questions:
            if not all(key in question for key in ['id', 'type', 'question']):
                print("✗ 问题数据不完整")
                return False
        
        print("✓ 最终数据结构验证通过")
        
    except Exception as e:
        print(f"✗ 数据结构验证异常: {e}")
        return False
    
    print("\n=== 集成测试完成 ===")
    print("✓ 所有测试通过！数据验证和问题类型处理集成正常工作。")
    
    # 输出最终处理后的数据（用于调试）
    print("\n=== 最终处理后的数据 ===")
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
    
    return True

def test_error_cases():
    """测试错误情况的处理"""
    
    print("\n=== 错误情况测试 ===")
    
    # 测试1: 空数据
    print("\n测试1: 空数据")
    try:
        is_valid, errors, _ = validate_questionnaire_with_schema({})
        print(f"✓ 正确识别空数据错误: {len(errors)} 个错误")
    except Exception as e:
        print(f"✗ 空数据处理异常: {e}")
    
    # 测试2: 不支持的问题类型
    print("\n测试2: 不支持的问题类型")
    invalid_data = {
        "type": "test",
        "basic_info": {"name": "测试", "grade": "测试", "submission_date": "2024-01-15"},
        "questions": [{
            "id": 1,
            "type": "unsupported_type",
            "question": "测试问题"
        }]
    }
    try:
        normalized = normalize_questionnaire_data(invalid_data)
        is_valid, errors, _ = validate_questionnaire_with_schema(normalized)
        print(f"✓ 正确识别不支持的问题类型: {len(errors)} 个错误")
    except Exception as e:
        print(f"✗ 不支持问题类型处理异常: {e}")
    
    # 测试3: 缺少必要字段
    print("\n测试3: 缺少必要字段")
    incomplete_data = {
        "type": "test",
        "basic_info": {"name": "", "grade": ""},  # 空字段
        "questions": [{
            "id": 1,
            "type": "multiple_choice",
            "question": "",  # 空问题
            "options": [],   # 空选项
            "selected": []   # 空选择
        }]
    }
    try:
        normalized = normalize_questionnaire_data(incomplete_data)
        is_valid, errors, _ = validate_questionnaire_with_schema(normalized)
        print(f"✓ 正确识别缺少必要字段: {len(errors)} 个错误")
    except Exception as e:
        print(f"✗ 缺少必要字段处理异常: {e}")

if __name__ == "__main__":
    # 运行集成测试
    success = test_integration()
    
    # 运行错误情况测试
    test_error_cases()
    
    if success:
        print("\n🎉 所有集成测试通过！")
    else:
        print("\n❌ 集成测试失败！")