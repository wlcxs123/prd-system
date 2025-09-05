#!/usr/bin/env python3
"""
数据验证增强功能单元测试
测试Marshmallow验证Schema和数据完整性检查
"""

import unittest
from datetime import datetime, date, timedelta
import json
from marshmallow import ValidationError

# 导入验证模块
from validation import (
    BasicInfoSchema,
    MultipleChoiceQuestionSchema,
    TextInputQuestionSchema,
    QuestionnaireSchema,
    normalize_questionnaire_data,
    check_data_integrity,
    check_basic_info_integrity,
    check_questions_integrity,
    check_question_integrity,
    check_multiple_choice_integrity,
    check_text_input_integrity,
    validate_questionnaire_with_schema,
    quick_validate
)

class TestBasicInfoSchema(unittest.TestCase):
    """测试基本信息Schema验证"""
    
    def setUp(self):
        self.schema = BasicInfoSchema()
        self.valid_data = {
            'name': '张三',
            'grade': '3年级',
            'submission_date': date.today().strftime('%Y-%m-%d'),
            'age': 9,
            'gender': '男'
        }
    
    def test_valid_basic_info(self):
        """测试有效的基本信息"""
        result = self.schema.load(self.valid_data)
        self.assertEqual(result['name'], '张三')
        self.assertEqual(result['grade'], '3年级')
        self.assertEqual(result['gender'], '男')
    
    def test_required_fields(self):
        """测试必需字段验证"""
        # 测试缺少姓名
        data = self.valid_data.copy()
        del data['name']
        with self.assertRaises(ValidationError) as cm:
            self.schema.load(data)
        self.assertIn('name', cm.exception.messages)
        
        # 测试缺少年级
        data = self.valid_data.copy()
        del data['grade']
        with self.assertRaises(ValidationError) as cm:
            self.schema.load(data)
        self.assertIn('grade', cm.exception.messages)
    
    def test_name_validation(self):
        """测试姓名验证"""
        # 测试空姓名
        data = self.valid_data.copy()
        data['name'] = ''
        with self.assertRaises(ValidationError):
            self.schema.load(data)
        
        # 测试姓名长度限制
        data['name'] = 'a' * 51
        with self.assertRaises(ValidationError):
            self.schema.load(data)
        
        # 测试姓名格式（包含非法字符）
        data['name'] = '张三123'
        with self.assertRaises(ValidationError):
            self.schema.load(data)
    
    def test_grade_validation(self):
        """测试年级验证"""
        valid_grades = ['1年级', '2年级', 'Grade 3', '4', '五年级']
        for grade in valid_grades:
            data = self.valid_data.copy()
            data['grade'] = grade
            try:
                result = self.schema.load(data)
                self.assertEqual(result['grade'], grade)
            except ValidationError:
                self.fail(f"Valid grade '{grade}' should not raise ValidationError")
    
    def test_age_validation(self):
        """测试年龄验证"""
        # 测试有效年龄
        data = self.valid_data.copy()
        data['age'] = 10
        result = self.schema.load(data)
        self.assertEqual(result['age'], 10)
        
        # 测试年龄范围
        data['age'] = 0
        with self.assertRaises(ValidationError):
            self.schema.load(data)
        
        data['age'] = 151
        with self.assertRaises(ValidationError):
            self.schema.load(data)
    
    def test_gender_normalization(self):
        """测试性别标准化"""
        gender_mappings = {
            'male': '男',
            'M': '男',
            'f': '女',
            'Female': '女'
        }
        
        for input_gender, expected in gender_mappings.items():
            data = self.valid_data.copy()
            data['gender'] = input_gender
            result = self.schema.load(data)
            self.assertEqual(result['gender'], expected)
    
    def test_date_validation(self):
        """测试日期验证"""
        # 测试未来日期
        data = self.valid_data.copy()
        future_date = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        data['submission_date'] = future_date
        with self.assertRaises(ValidationError):
            self.schema.load(data)
        
        # 测试出生日期和年龄一致性
        data = self.valid_data.copy()
        data['birth_date'] = '2010-01-01'
        data['age'] = 50  # 明显不匹配的年龄
        with self.assertRaises(ValidationError):
            self.schema.load(data)

class TestMultipleChoiceQuestionSchema(unittest.TestCase):
    """测试选择题Schema验证"""
    
    def setUp(self):
        self.schema = MultipleChoiceQuestionSchema()
        self.valid_data = {
            'id': 1,
            'type': 'multiple_choice',
            'question': '你喜欢什么颜色？',
            'options': [
                {'value': 1, 'text': '红色'},
                {'value': 2, 'text': '蓝色'},
                {'value': 3, 'text': '绿色'}
            ],
            'selected': [1],
            'allow_multiple': False
        }
    
    def test_valid_multiple_choice(self):
        """测试有效的选择题"""
        result = self.schema.load(self.valid_data)
        self.assertEqual(result['question'], '你喜欢什么颜色？')
        self.assertEqual(len(result['options']), 3)
        self.assertEqual(result['selected'], [1])
    
    def test_option_uniqueness(self):
        """测试选项唯一性"""
        # 测试选项值重复
        data = self.valid_data.copy()
        data['options'] = [
            {'value': 1, 'text': '红色'},
            {'value': 1, 'text': '蓝色'}  # 重复的value
        ]
        with self.assertRaises(ValidationError):
            self.schema.load(data)
        
        # 测试选项文本重复
        data['options'] = [
            {'value': 1, 'text': '红色'},
            {'value': 2, 'text': '红色'}  # 重复的text
        ]
        with self.assertRaises(ValidationError):
            self.schema.load(data)
    
    def test_selected_validation(self):
        """测试选中答案验证"""
        # 测试无效的选中值
        data = self.valid_data.copy()
        data['selected'] = [999]  # 不存在的选项值
        with self.assertRaises(ValidationError):
            self.schema.load(data)
        
        # 测试单选题多选
        data = self.valid_data.copy()
        data['allow_multiple'] = False
        data['selected'] = [1, 2]  # 单选题选择多个
        with self.assertRaises(ValidationError):
            self.schema.load(data)
    
    def test_question_limits(self):
        """测试问题限制"""
        # 测试选项数量限制
        data = self.valid_data.copy()
        data['options'] = [{'value': i, 'text': f'选项{i}'} for i in range(25)]  # 超过20个选项
        with self.assertRaises(ValidationError):
            self.schema.load(data)
        
        # 测试问题文本长度
        data = self.valid_data.copy()
        data['question'] = 'a' * 501  # 超过500字符
        with self.assertRaises(ValidationError):
            self.schema.load(data)

class TestTextInputQuestionSchema(unittest.TestCase):
    """测试填空题Schema验证"""
    
    def setUp(self):
        self.schema = TextInputQuestionSchema()
        self.valid_data = {
            'id': 1,
            'type': 'text_input',
            'question': '请输入你的姓名',
            'answer': '张三',
            'input_type': 'text',
            'is_required': True
        }
    
    def test_valid_text_input(self):
        """测试有效的填空题"""
        result = self.schema.load(self.valid_data)
        self.assertEqual(result['answer'], '张三')
        self.assertEqual(result['input_type'], 'text')
    
    def test_input_type_validation(self):
        """测试输入类型验证"""
        # 测试数字类型
        data = self.valid_data.copy()
        data['input_type'] = 'number'
        data['answer'] = '123.45'
        result = self.schema.load(data)
        self.assertEqual(result['answer'], '123.45')
        
        # 测试无效数字
        data['answer'] = 'abc'
        with self.assertRaises(ValidationError):
            self.schema.load(data)
        
        # 测试邮箱类型
        data = self.valid_data.copy()
        data['input_type'] = 'email'
        data['answer'] = 'test@example.com'
        result = self.schema.load(data)
        self.assertEqual(result['answer'], 'test@example.com')
        
        # 测试无效邮箱
        data['answer'] = 'invalid-email'
        with self.assertRaises(ValidationError):
            self.schema.load(data)
    
    def test_length_validation(self):
        """测试长度验证"""
        data = self.valid_data.copy()
        data['min_length'] = 5
        data['max_length'] = 10
        
        # 测试长度在范围内
        data['answer'] = '12345'
        result = self.schema.load(data)
        self.assertEqual(result['answer'], '12345')
        
        # 测试长度过短
        data['answer'] = '123'
        with self.assertRaises(ValidationError):
            self.schema.load(data)
        
        # 测试长度过长
        data['answer'] = '12345678901'
        with self.assertRaises(ValidationError):
            self.schema.load(data)
    
    def test_required_validation(self):
        """测试必答题验证"""
        data = self.valid_data.copy()
        data['is_required'] = True
        data['answer'] = ''
        with self.assertRaises(ValidationError):
            self.schema.load(data)
        
        # 非必答题可以为空
        data['is_required'] = False
        result = self.schema.load(data)
        self.assertEqual(result['answer'], '')

class TestDataIntegrityChecks(unittest.TestCase):
    """测试数据完整性检查"""
    
    def setUp(self):
        self.valid_questionnaire = {
            'type': 'student_report',
            'basic_info': {
                'name': '张三',
                'grade': '3年级',
                'submission_date': date.today().strftime('%Y-%m-%d')
            },
            'questions': [
                {
                    'id': 1,
                    'type': 'multiple_choice',
                    'question': '你喜欢什么颜色？',
                    'options': [
                        {'value': 1, 'text': '红色'},
                        {'value': 2, 'text': '蓝色'}
                    ],
                    'selected': [1]
                },
                {
                    'id': 2,
                    'type': 'text_input',
                    'question': '请输入你的爱好',
                    'answer': '读书'
                }
            ]
        }
    
    def test_valid_questionnaire_integrity(self):
        """测试有效问卷的完整性检查"""
        errors = check_data_integrity(self.valid_questionnaire)
        self.assertEqual(len(errors), 0, f"Valid questionnaire should have no errors, but got: {errors}")
    
    def test_missing_required_fields(self):
        """测试缺少必需字段"""
        # 测试缺少type
        data = self.valid_questionnaire.copy()
        del data['type']
        errors = check_data_integrity(data)
        self.assertTrue(any('type' in error for error in errors))
        
        # 测试缺少basic_info
        data = self.valid_questionnaire.copy()
        del data['basic_info']
        errors = check_data_integrity(data)
        self.assertTrue(any('basic_info' in error for error in errors))
    
    def test_question_id_uniqueness(self):
        """测试问题ID唯一性"""
        data = self.valid_questionnaire.copy()
        data['questions'].append({
            'id': 1,  # 重复的ID
            'type': 'text_input',
            'question': '另一个问题',
            'answer': '答案'
        })
        errors = check_data_integrity(data)
        self.assertTrue(any('ID重复' in error for error in errors))
    
    def test_business_logic_validation(self):
        """测试业务逻辑验证"""
        # 测试Frankfurt Scale特定验证
        frankfurt_data = {
            'type': 'frankfurt_scale_selective_mutism',
            'basic_info': self.valid_questionnaire['basic_info'],
            'questions': [
                {
                    'id': 1,
                    'type': 'multiple_choice',
                    'question': 'DS问题',
                    'section': 'DS',
                    'options': [{'value': 0, 'text': '从不'}],
                    'selected': [0]
                }
            ]
        }
        errors = check_data_integrity(frankfurt_data)
        # 应该报告缺少其他必需章节
        self.assertTrue(any('缺少必需的章节' in error for error in errors))

class TestQuestionnaireSchema(unittest.TestCase):
    """测试完整问卷Schema验证"""
    
    def setUp(self):
        self.schema = QuestionnaireSchema()
        self.valid_data = {
            'type': 'student_report',
            'basic_info': {
                'name': '张三',
                'grade': '3年级',
                'submission_date': date.today().strftime('%Y-%m-%d')
            },
            'questions': [
                {
                    'id': 1,
                    'type': 'multiple_choice',
                    'question': '你喜欢什么颜色？',
                    'options': [
                        {'value': 1, 'text': '红色'},
                        {'value': 2, 'text': '蓝色'}
                    ],
                    'selected': [1]
                }
            ]
        }
    
    def test_valid_questionnaire_schema(self):
        """测试有效问卷Schema验证"""
        result = self.schema.load(self.valid_data)
        self.assertEqual(result['type'], 'student_report')
        self.assertEqual(len(result['questions']), 1)
    
    def test_question_validation_in_schema(self):
        """测试Schema中的问题验证"""
        data = self.valid_data.copy()
        data['questions'][0]['selected'] = [999]  # 无效选项
        with self.assertRaises(ValidationError):
            self.schema.load(data)

class TestValidationIntegration(unittest.TestCase):
    """测试验证功能集成"""
    
    def test_quick_validate_function(self):
        """测试快速验证函数"""
        valid_data = {
            'type': 'student_report',
            'basic_info': {
                'name': '张三',
                'grade': '3年级',
                'submission_date': date.today().strftime('%Y-%m-%d')
            },
            'questions': [
                {
                    'id': 1,
                    'type': 'text_input',
                    'question': '你的爱好是什么？',
                    'answer': '读书'
                }
            ]
        }
        
        errors = quick_validate(valid_data)
        self.assertEqual(len(errors), 0, f"Valid data should have no errors, but got: {errors}")
    
    def test_validate_questionnaire_with_schema_function(self):
        """测试Schema验证函数"""
        valid_data = {
            'type': 'student_report',
            'basic_info': {
                'name': '张三',
                'grade': '3年级',
                'submission_date': date.today().strftime('%Y-%m-%d')
            },
            'questions': [
                {
                    'id': 1,
                    'type': 'text_input',
                    'question': '你的爱好是什么？',
                    'answer': '读书'
                }
            ]
        }
        
        is_valid, errors, validated_data = validate_questionnaire_with_schema(valid_data)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
        self.assertIsNotNone(validated_data)
    
    def test_normalization_integration(self):
        """测试数据标准化集成"""
        raw_data = {
            'type': 'STUDENT_REPORT',  # 大写
            'name': '  张三  ',  # 包含空格
            'grade': '3年级',
            'submission_date': date.today().strftime('%Y-%m-%d'),
            'questions': [
                {
                    'id': '1',  # 字符串ID
                    'type': 'text_input',
                    'question': '  你的爱好是什么？  ',  # 包含空格
                    'answer': '  读书  '  # 包含空格
                }
            ]
        }
        
        normalized = normalize_questionnaire_data(raw_data)
        self.assertEqual(normalized['type'], 'student_report')
        self.assertEqual(normalized['basic_info']['name'], '张三')
        self.assertEqual(normalized['questions'][0]['question'], '你的爱好是什么？')
        self.assertEqual(normalized['questions'][0]['answer'], '读书')

def run_validation_tests():
    """运行所有验证测试"""
    print("开始运行数据验证增强功能测试...\n")
    
    # 创建测试套件
    test_classes = [
        TestBasicInfoSchema,
        TestMultipleChoiceQuestionSchema,
        TestTextInputQuestionSchema,
        TestDataIntegrityChecks,
        TestQuestionnaireSchema,
        TestValidationIntegration
    ]
    
    total_tests = 0
    total_failures = 0
    total_errors = 0
    
    for test_class in test_classes:
        print(f"运行 {test_class.__name__} 测试...")
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        import os
        null_stream = open(os.devnull, 'w') if os.name != 'nt' else open('nul', 'w')
        runner = unittest.TextTestRunner(verbosity=1, stream=null_stream)
        result = runner.run(suite)
        
        total_tests += result.testsRun
        total_failures += len(result.failures)
        total_errors += len(result.errors)
        
        if result.failures or result.errors:
            print(f"  ❌ {len(result.failures)} 失败, {len(result.errors)} 错误")
            for failure in result.failures:
                print(f"    失败: {failure[0]}")
            for error in result.errors:
                print(f"    错误: {error[0]}")
        else:
            print(f"  ✅ 所有测试通过 ({result.testsRun} 个测试)")
        print()
    
    print("=" * 50)
    print(f"测试总结:")
    print(f"总测试数: {total_tests}")
    print(f"失败: {total_failures}")
    print(f"错误: {total_errors}")
    print(f"成功率: {((total_tests - total_failures - total_errors) / total_tests * 100):.1f}%")
    
    if total_failures == 0 and total_errors == 0:
        print("\n🎉 所有验证测试通过！数据验证增强功能实现成功。")
        return True
    else:
        print(f"\n⚠️  有 {total_failures + total_errors} 个测试失败，请检查实现。")
        return False

if __name__ == '__main__':
    success = run_validation_tests()
    exit(0 if success else 1)