"""
问题类型处理模块的单元测试
"""

import unittest
from question_types import (
    MultipleChoiceHandler,
    TextInputHandler,
    QuestionTypeProcessor,
    validate_question_by_type,
    process_question_by_type,
    process_complete_questionnaire
)

class TestMultipleChoiceHandler(unittest.TestCase):
    """选择题处理器测试"""
    
    def setUp(self):
        self.handler = MultipleChoiceHandler()
        self.valid_question = {
            'id': 1,
            'type': 'multiple_choice',
            'question': '你最喜欢的颜色是什么？',
            'options': [
                {'value': 0, 'text': '红色'},
                {'value': 1, 'text': '蓝色'},
                {'value': 2, 'text': '绿色'}
            ],
            'selected': [1]
        }
    
    def test_validate_valid_question(self):
        """测试验证有效的选择题"""
        errors = self.handler.validate_question_data(self.valid_question)
        self.assertEqual(len(errors), 0)
    
    def test_validate_empty_question(self):
        """测试验证空问题文本"""
        question = self.valid_question.copy()
        question['question'] = ''
        errors = self.handler.validate_question_data(question)
        self.assertIn('问题文本不能为空', errors)
    
    def test_validate_no_options(self):
        """测试验证无选项"""
        question = self.valid_question.copy()
        question['options'] = []
        errors = self.handler.validate_question_data(question)
        self.assertIn('至少需要一个选项', errors)
    
    def test_validate_no_selection(self):
        """测试验证未选择答案"""
        question = self.valid_question.copy()
        question['selected'] = []
        errors = self.handler.validate_question_data(question)
        self.assertIn('必须选择至少一个答案', errors)
    
    def test_validate_invalid_selection(self):
        """测试验证无效选择"""
        question = self.valid_question.copy()
        question['selected'] = [99]  # 不存在的选项值
        errors = self.handler.validate_question_data(question)
        self.assertTrue(any('选中的答案无效' in error for error in errors))
    
    def test_process_answer(self):
        """测试处理答案"""
        processed = self.handler.process_answer(self.valid_question)
        self.assertIn('selected_texts', processed)
        self.assertEqual(processed['selected_texts'], ['蓝色'])
        self.assertIn('is_multiple_choice', processed)
        self.assertIn('choice_mode', processed)
    
    def test_format_for_display(self):
        """测试格式化显示"""
        formatted = self.handler.format_for_display(self.valid_question)
        self.assertIn('answer_display', formatted)
        self.assertEqual(formatted['type'], 'multiple_choice')
    
    def test_calculate_score(self):
        """测试计算得分"""
        score = self.handler.calculate_score(self.valid_question)
        self.assertEqual(score, 1.0)
        
        # 测试未选择的情况
        question = self.valid_question.copy()
        question['selected'] = []
        score = self.handler.calculate_score(question)
        self.assertEqual(score, 0.0)

class TestTextInputHandler(unittest.TestCase):
    """填空题处理器测试"""
    
    def setUp(self):
        self.handler = TextInputHandler()
        self.valid_question = {
            'id': 1,
            'type': 'text_input',
            'question': '请描述你的兴趣爱好',
            'answer': '我喜欢阅读和运动',
            'max_length': 100
        }
    
    def test_validate_valid_question(self):
        """测试验证有效的填空题"""
        errors = self.handler.validate_question_data(self.valid_question)
        self.assertEqual(len(errors), 0)
    
    def test_validate_empty_question(self):
        """测试验证空问题文本"""
        question = self.valid_question.copy()
        question['question'] = ''
        errors = self.handler.validate_question_data(question)
        self.assertIn('问题文本不能为空', errors)
    
    def test_validate_empty_answer(self):
        """测试验证空答案"""
        question = self.valid_question.copy()
        question['answer'] = ''
        errors = self.handler.validate_question_data(question)
        self.assertIn('答案不能为空', errors)
    
    def test_validate_answer_too_long(self):
        """测试验证答案过长"""
        question = self.valid_question.copy()
        question['answer'] = 'a' * 101  # 超过max_length
        question['max_length'] = 100
        errors = self.handler.validate_question_data(question)
        self.assertTrue(any('答案长度超过限制' in error for error in errors))
    
    def test_process_answer(self):
        """测试处理答案"""
        processed = self.handler.process_answer(self.valid_question)
        self.assertIn('answer_length', processed)
        self.assertIn('word_count', processed)
        self.assertIn('is_empty', processed)
        self.assertEqual(processed['is_empty'], False)
    
    def test_format_for_display(self):
        """测试格式化显示"""
        formatted = self.handler.format_for_display(self.valid_question)
        self.assertIn('answer_preview', formatted)
        self.assertEqual(formatted['type'], 'text_input')
    
    def test_calculate_score(self):
        """测试计算得分"""
        score = self.handler.calculate_score(self.valid_question)
        self.assertEqual(score, 1.0)
        
        # 测试空答案的情况
        question = self.valid_question.copy()
        question['answer'] = ''
        score = self.handler.calculate_score(question)
        self.assertEqual(score, 0.0)

class TestQuestionTypeProcessor(unittest.TestCase):
    """问题类型处理器管理类测试"""
    
    def setUp(self):
        self.processor = QuestionTypeProcessor()
        self.sample_questionnaire = {
            'type': 'test_questionnaire',
            'basic_info': {
                'name': '张三',
                'grade': '五年级',
                'submission_date': '2024-01-15'
            },
            'questions': [
                {
                    'id': 1,
                    'type': 'multiple_choice',
                    'question': '你最喜欢的科目是什么？',
                    'options': [
                        {'value': 0, 'text': '数学'},
                        {'value': 1, 'text': '语文'},
                        {'value': 2, 'text': '英语'}
                    ],
                    'selected': [0]
                },
                {
                    'id': 2,
                    'type': 'text_input',
                    'question': '请描述你的学习方法',
                    'answer': '我会制定学习计划，按时完成作业'
                }
            ]
        }
    
    def test_get_supported_types(self):
        """测试获取支持的问题类型"""
        types = self.processor.get_supported_types()
        self.assertIn('multiple_choice', types)
        self.assertIn('text_input', types)
    
    def test_validate_questionnaire(self):
        """测试验证完整问卷"""
        errors = self.processor.validate_questionnaire(self.sample_questionnaire)
        self.assertEqual(len(errors), 0)
    
    def test_validate_empty_questionnaire(self):
        """测试验证空问卷"""
        empty_questionnaire = {'questions': []}
        errors = self.processor.validate_questionnaire(empty_questionnaire)
        self.assertIn('问卷至少需要一个问题', errors)
    
    def test_process_questionnaire(self):
        """测试处理完整问卷"""
        processed = self.processor.process_questionnaire(self.sample_questionnaire)
        
        # 检查统计信息是否正确计算
        self.assertIn('statistics', processed)
        stats = processed['statistics']
        self.assertEqual(stats['total_questions'], 2)
        self.assertEqual(stats['answered_questions'], 2)
        self.assertEqual(stats['total_score'], 2.0)
        self.assertEqual(stats['completion_rate'], 100.0)
    
    def test_validate_unsupported_question_type(self):
        """测试验证不支持的问题类型"""
        question = {
            'id': 1,
            'type': 'unsupported_type',
            'question': '测试问题'
        }
        errors = self.processor.validate_question(question)
        self.assertTrue(any('不支持的问题类型' in error for error in errors))

class TestConvenienceFunctions(unittest.TestCase):
    """便捷函数测试"""
    
    def test_validate_question_by_type(self):
        """测试按类型验证问题的便捷函数"""
        question = {
            'id': 1,
            'type': 'multiple_choice',
            'question': '测试问题',
            'options': [{'value': 0, 'text': '选项1'}],
            'selected': [0]
        }
        errors = validate_question_by_type(question)
        self.assertEqual(len(errors), 0)
    
    def test_process_question_by_type(self):
        """测试按类型处理问题的便捷函数"""
        question = {
            'id': 1,
            'type': 'text_input',
            'question': '测试问题',
            'answer': '测试答案'
        }
        processed = process_question_by_type(question)
        self.assertIn('answer_length', processed)
    
    def test_process_complete_questionnaire(self):
        """测试处理完整问卷的便捷函数"""
        questionnaire = {
            'questions': [
                {
                    'id': 1,
                    'type': 'multiple_choice',
                    'question': '测试问题',
                    'options': [{'value': 0, 'text': '选项1'}],
                    'selected': [0]
                }
            ]
        }
        processed = process_complete_questionnaire(questionnaire)
        self.assertIn('statistics', processed)

if __name__ == '__main__':
    # 运行所有测试
    unittest.main(verbosity=2)