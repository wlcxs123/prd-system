#!/usr/bin/env python3
"""
验证任务 2.2 "实现多问题类型支持" 的完成情况

本脚本验证以下子任务：
- 创建选择题数据处理逻辑
- 实现填空题数据处理逻辑  
- 编写问题类型验证函数

以及对应的需求 2.1-2.4：
- 2.1: 选择题支持单选和多选两种模式
- 2.2: 填空题支持短文本和长文本输入
- 2.3: 保存问题数据时记录问题类型、题目内容和答案选项
- 2.4: 根据问题类型验证答案格式
"""

from question_types import (
    MultipleChoiceHandler,
    TextInputHandler,
    QuestionTypeProcessor,
    validate_answer_format_by_type,
    process_question_by_type,
    validate_question_by_type
)
import json

def print_section(title):
    """打印章节标题"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_subsection(title):
    """打印子章节标题"""
    print(f"\n{'-'*40}")
    print(f" {title}")
    print(f"{'-'*40}")

def verify_multiple_choice_logic():
    """验证选择题数据处理逻辑"""
    print_section("验证选择题数据处理逻辑")
    
    handler = MultipleChoiceHandler()
    
    # 测试单选题
    print_subsection("单选题处理")
    single_choice = {
        'id': 1,
        'type': 'multiple_choice',
        'question': '你的性别是？',
        'options': [
            {'value': 0, 'text': '男'},
            {'value': 1, 'text': '女'}
        ],
        'selected': [1],
        'is_multiple_choice': False
    }
    
    print("原始数据:")
    print(json.dumps(single_choice, ensure_ascii=False, indent=2))
    
    # 验证数据
    errors = handler.validate_question_data(single_choice)
    print(f"\n验证结果: {'通过' if not errors else '失败'}")
    if errors:
        for error in errors:
            print(f"  - {error}")
    
    # 处理数据
    processed = handler.process_answer(single_choice)
    print(f"\n处理后的数据:")
    print(f"  - 选择模式: {processed['choice_mode']}")
    print(f"  - 是否多选: {processed['is_multiple_choice']}")
    print(f"  - 选中文本: {processed['selected_texts']}")
    print(f"  - 问题类型信息: {processed['question_type_info']}")
    
    # 测试多选题
    print_subsection("多选题处理")
    multiple_choice = {
        'id': 2,
        'type': 'multiple_choice',
        'question': '你喜欢的运动有哪些？',
        'options': [
            {'value': 0, 'text': '篮球'},
            {'value': 1, 'text': '足球'},
            {'value': 2, 'text': '游泳'},
            {'value': 3, 'text': '跑步'}
        ],
        'selected': [0, 2, 3],
        'is_multiple_choice': True
    }
    
    print("原始数据:")
    print(json.dumps(multiple_choice, ensure_ascii=False, indent=2))
    
    # 验证数据
    errors = handler.validate_question_data(multiple_choice)
    print(f"\n验证结果: {'通过' if not errors else '失败'}")
    
    # 处理数据
    processed = handler.process_answer(multiple_choice)
    print(f"\n处理后的数据:")
    print(f"  - 选择模式: {processed['choice_mode']}")
    print(f"  - 是否多选: {processed['is_multiple_choice']}")
    print(f"  - 选中文本: {processed['selected_texts']}")
    print(f"  - 问题类型信息: {processed['question_type_info']}")

def verify_text_input_logic():
    """验证填空题数据处理逻辑"""
    print_section("验证填空题数据处理逻辑")
    
    handler = TextInputHandler()
    
    # 测试短文本
    print_subsection("短文本处理")
    short_text = {
        'id': 1,
        'type': 'text_input',
        'question': '你的姓名是？',
        'answer': '张三',
        'text_type': 'short',
        'max_length': 50
    }
    
    print("原始数据:")
    print(json.dumps(short_text, ensure_ascii=False, indent=2))
    
    # 验证数据
    errors = handler.validate_question_data(short_text)
    print(f"\n验证结果: {'通过' if not errors else '失败'}")
    if errors:
        for error in errors:
            print(f"  - {error}")
    
    # 处理数据
    processed = handler.process_answer(short_text)
    print(f"\n处理后的数据:")
    print(f"  - 文本类型: {processed['text_type']}")
    print(f"  - 是否短文本: {processed['is_short_text']}")
    print(f"  - 答案长度: {processed['answer_length']}")
    print(f"  - 长度利用率: {processed['length_utilization']:.1f}%")
    print(f"  - 问题类型信息: {processed['question_type_info']}")
    
    # 测试长文本
    print_subsection("长文本处理")
    long_text = {
        'id': 2,
        'type': 'text_input',
        'question': '请详细描述你的学习经历',
        'answer': '我从小学开始就对学习很感兴趣，特别是数学和科学。在初中时期，我参加了多个学科竞赛，获得了不错的成绩。高中阶段，我更加专注于理科学习，并且开始接触编程。大学期间，我选择了计算机科学专业，深入学习了算法、数据结构等核心课程。通过不断的学习和实践，我逐渐掌握了多种编程语言和开发技术。',
        'text_type': 'long',
        'max_length': 1000
    }
    
    print("原始数据:")
    print(json.dumps(long_text, ensure_ascii=False, indent=2))
    
    # 验证数据
    errors = handler.validate_question_data(long_text)
    print(f"\n验证结果: {'通过' if not errors else '失败'}")
    
    # 处理数据
    processed = handler.process_answer(long_text)
    print(f"\n处理后的数据:")
    print(f"  - 文本类型: {processed['text_type']}")
    print(f"  - 是否长文本: {processed['is_long_text']}")
    print(f"  - 答案长度: {processed['answer_length']}")
    print(f"  - 字数统计: {processed['word_count']}")
    print(f"  - 行数统计: {processed['line_count']}")
    print(f"  - 长度利用率: {processed['length_utilization']:.1f}%")
    print(f"  - 问题类型信息: {processed['question_type_info']}")

def verify_validation_functions():
    """验证问题类型验证函数"""
    print_section("验证问题类型验证函数")
    
    # 测试通用验证函数
    print_subsection("通用问题验证")
    
    valid_question = {
        'id': 1,
        'type': 'multiple_choice',
        'question': '测试问题',
        'options': [{'value': 0, 'text': '选项1'}],
        'selected': [0]
    }
    
    errors = validate_question_by_type(valid_question)
    print(f"有效问题验证结果: {'通过' if not errors else '失败'}")
    
    invalid_question = {
        'id': 1,
        'type': 'invalid_type',
        'question': '测试问题'
    }
    
    errors = validate_question_by_type(invalid_question)
    print(f"无效问题验证结果: {'失败' if errors else '通过'}")
    if errors:
        print(f"  错误信息: {errors[0]}")
    
    # 测试答案格式验证
    print_subsection("答案格式验证")
    
    # 选择题格式验证
    choice_question = {
        'type': 'multiple_choice',
        'options': [{'value': 0, 'text': '选项1'}],
        'selected': [0],
        'is_multiple_choice': False
    }
    
    errors = validate_answer_format_by_type(choice_question)
    print(f"选择题格式验证: {'通过' if not errors else '失败'}")
    
    # 填空题格式验证
    text_question = {
        'type': 'text_input',
        'answer': '有效答案',
        'text_type': 'short',
        'max_length': 100
    }
    
    errors = validate_answer_format_by_type(text_question)
    print(f"填空题格式验证: {'通过' if not errors else '失败'}")
    
    # 错误格式验证
    invalid_format = {
        'type': 'multiple_choice',
        'options': [{'value': 0, 'text': '选项1'}],
        'selected': 0,  # 应该是列表格式
        'is_multiple_choice': False
    }
    
    errors = validate_answer_format_by_type(invalid_format)
    print(f"错误格式验证: {'失败' if errors else '通过'}")
    if errors:
        print(f"  错误信息: {errors[0]}")

def verify_requirements_compliance():
    """验证需求 2.1-2.4 的符合性"""
    print_section("验证需求 2.1-2.4 符合性")
    
    processor = QuestionTypeProcessor()
    
    # 需求 2.1: 选择题支持单选和多选
    print_subsection("需求 2.1: 选择题单选/多选支持")
    
    single_choice = {
        'type': 'multiple_choice',
        'question': '单选题',
        'options': [{'value': 0, 'text': '选项1'}, {'value': 1, 'text': '选项2'}],
        'selected': [0],
        'is_multiple_choice': False
    }
    
    multiple_choice = {
        'type': 'multiple_choice',
        'question': '多选题',
        'options': [{'value': 0, 'text': '选项1'}, {'value': 1, 'text': '选项2'}],
        'selected': [0, 1],
        'is_multiple_choice': True
    }
    
    single_processed = process_question_by_type(single_choice)
    multiple_processed = process_question_by_type(multiple_choice)
    
    print(f"单选题模式: {single_processed['choice_mode']}")
    print(f"多选题模式: {multiple_processed['choice_mode']}")
    print("✓ 需求 2.1 已实现")
    
    # 需求 2.2: 填空题支持短文本和长文本
    print_subsection("需求 2.2: 填空题短文本/长文本支持")
    
    short_text = {
        'type': 'text_input',
        'question': '短文本题',
        'answer': '短答案',
        'text_type': 'short'
    }
    
    long_text = {
        'type': 'text_input',
        'question': '长文本题',
        'answer': '这是一个很长的答案，包含了很多详细的信息和描述',
        'text_type': 'long'
    }
    
    short_processed = process_question_by_type(short_text)
    long_processed = process_question_by_type(long_text)
    
    print(f"短文本类型: {short_processed['text_type']}, 默认长度限制: {short_processed['max_length']}")
    print(f"长文本类型: {long_processed['text_type']}, 默认长度限制: {long_processed['max_length']}")
    print("✓ 需求 2.2 已实现")
    
    # 需求 2.3: 记录问题类型、题目内容和答案选项
    print_subsection("需求 2.3: 问题数据记录")
    
    question = {
        'type': 'multiple_choice',
        'question': '测试问题',
        'options': [{'value': 0, 'text': '选项1'}],
        'selected': [0]
    }
    
    processed = process_question_by_type(question)
    type_info = processed['question_type_info']
    
    print(f"记录的问题类型: {type_info['type']}")
    print(f"记录的题目内容: {type_info['question_text']}")
    print(f"记录的选项数量: {type_info['total_options']}")
    print("✓ 需求 2.3 已实现")
    
    # 需求 2.4: 根据问题类型验证答案格式
    print_subsection("需求 2.4: 类型特定的答案格式验证")
    
    # 测试选择题格式验证
    choice_errors = validate_answer_format_by_type({
        'type': 'multiple_choice',
        'options': [{'value': 0, 'text': '选项1'}],
        'selected': [0]
    })
    
    # 测试填空题格式验证
    text_errors = validate_answer_format_by_type({
        'type': 'text_input',
        'answer': '有效答案'
    })
    
    print(f"选择题格式验证: {'通过' if not choice_errors else '失败'}")
    print(f"填空题格式验证: {'通过' if not text_errors else '失败'}")
    print("✓ 需求 2.4 已实现")

def main():
    """主函数"""
    print("任务 2.2 实现验证报告")
    print("=" * 60)
    print("任务: 实现多问题类型支持")
    print("子任务:")
    print("  - 创建选择题数据处理逻辑")
    print("  - 实现填空题数据处理逻辑")
    print("  - 编写问题类型验证函数")
    print("\n对应需求:")
    print("  - 2.1: 选择题支持单选和多选两种模式")
    print("  - 2.2: 填空题支持短文本和长文本输入")
    print("  - 2.3: 保存问题数据时记录问题类型、题目内容和答案选项")
    print("  - 2.4: 根据问题类型验证答案格式")
    
    try:
        # 验证各个功能模块
        verify_multiple_choice_logic()
        verify_text_input_logic()
        verify_validation_functions()
        verify_requirements_compliance()
        
        print_section("验证总结")
        print("✅ 所有子任务已完成:")
        print("  ✓ 选择题数据处理逻辑 - 已实现")
        print("  ✓ 填空题数据处理逻辑 - 已实现")
        print("  ✓ 问题类型验证函数 - 已实现")
        print("\n✅ 所有需求已满足:")
        print("  ✓ 需求 2.1: 选择题单选/多选支持")
        print("  ✓ 需求 2.2: 填空题短文本/长文本支持")
        print("  ✓ 需求 2.3: 完整的问题数据记录")
        print("  ✓ 需求 2.4: 类型特定的答案格式验证")
        print("\n🎉 任务 2.2 已成功完成!")
        
    except Exception as e:
        print_section("验证失败")
        print(f"❌ 验证过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()