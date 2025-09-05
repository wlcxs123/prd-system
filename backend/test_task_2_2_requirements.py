"""
测试任务 2.2 的具体需求实现
验证需求 2.1-2.4 是否正确实现
"""

import unittest
from question_types import (
    MultipleChoiceHandler,
    TextInputHandler,
    QuestionTypeProcessor,
    validate_answer_format_by_type
)

class TestRequirement21(unittest.TestCase):
    """测试需求 2.1: 选择题支持单选和多选两种模式"""
    
    def setUp(self):
        self.handler = MultipleChoiceHandler()
    
    def test_single_choice_mode(self):
        """测试单选模式"""
        question = {
            'id': 1,
            'type': 'multiple_choice',
            'question': '你的性别是？',
            'options': [
                {'value': 0, 'text': '男'},
                {'value': 1, 'text': '女'}
            ],
            'selected': [0],
            'is_multiple_choice': False
        }
        
        # 验证单选模式数据
        errors = self.handler.validate_question_data(question)
        self.assertEqual(len(errors), 0, "单选模式应该验证通过")
        
        # 处理单选模式答案
        processed = self.handler.process_answer(question)
        self.assertEqual(processed['choice_mode'], 'single')
        self.assertFalse(processed['is_multiple_choice'])
        
    def test_multiple_choice_mode(self):
        """测试多选模式"""
        question = {
            'id': 1,
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
        
        # 验证多选模式数据
        errors = self.handler.validate_question_data(question)
        self.assertEqual(len(errors), 0, "多选模式应该验证通过")
        
        # 处理多选模式答案
        processed = self.handler.process_answer(question)
        self.assertEqual(processed['choice_mode'], 'multiple')
        self.assertTrue(processed['is_multiple_choice'])
        
    def test_single_choice_validation_error(self):
        """测试单选模式选择多个答案的错误"""
        question = {
            'id': 1,
            'type': 'multiple_choice',
            'question': '你的性别是？',
            'options': [
                {'value': 0, 'text': '男'},
                {'value': 1, 'text': '女'}
            ],
            'selected': [0, 1],  # 单选题选择了多个答案
            'is_multiple_choice': False
        }
        
        errors = self.handler.validate_question_data(question)
        self.assertTrue(any('单选题只能选择一个答案' in error for error in errors))

class TestRequirement22(unittest.TestCase):
    """测试需求 2.2: 填空题支持短文本和长文本输入"""
    
    def setUp(self):
        self.handler = TextInputHandler()
    
    def test_short_text_input(self):
        """测试短文本输入"""
        question = {
            'id': 1,
            'type': 'text_input',
            'question': '你的姓名是？',
            'answer': '张三',
            'text_type': 'short',
            'max_length': 50
        }
        
        # 验证短文本数据
        errors = self.handler.validate_question_data(question)
        self.assertEqual(len(errors), 0, "短文本应该验证通过")
        
        # 处理短文本答案
        processed = self.handler.process_answer(question)
        self.assertEqual(processed['text_type'], 'short')
        self.assertTrue(processed['is_short_text'])
        self.assertFalse(processed['is_long_text'])
        
    def test_long_text_input(self):
        """测试长文本输入"""
        question = {
            'id': 1,
            'type': 'text_input',
            'question': '请详细描述你的学习经历',
            'answer': '我从小学开始就对学习很感兴趣，特别是数学和科学。在初中时期，我参加了多个学科竞赛，获得了不错的成绩。高中阶段，我更加专注于理科学习，并且开始接触编程。大学期间，我选择了计算机科学专业，深入学习了算法、数据结构等核心课程。',
            'text_type': 'long',
            'max_length': 1000
        }
        
        # 验证长文本数据
        errors = self.handler.validate_question_data(question)
        self.assertEqual(len(errors), 0, "长文本应该验证通过")
        
        # 处理长文本答案
        processed = self.handler.process_answer(question)
        self.assertEqual(processed['text_type'], 'long')
        self.assertFalse(processed['is_short_text'])
        self.assertTrue(processed['is_long_text'])
        
    def test_default_text_type_limits(self):
        """测试默认文本类型限制"""
        # 短文本默认限制
        short_question = {
            'id': 1,
            'type': 'text_input',
            'question': '简短回答',
            'answer': '答案',
            'text_type': 'short'
            # 没有设置 max_length
        }
        
        processed = self.handler.process_answer(short_question)
        self.assertEqual(processed['max_length'], 200)  # 短文本默认200字符
        
        # 长文本默认限制
        long_question = {
            'id': 1,
            'type': 'text_input',
            'question': '详细回答',
            'answer': '详细答案',
            'text_type': 'long'
            # 没有设置 max_length
        }
        
        processed = self.handler.process_answer(long_question)
        self.assertEqual(processed['max_length'], 2000)  # 长文本默认2000字符
        
    def test_text_type_validation_errors(self):
        """测试文本类型验证错误"""
        # 短文本长度过长
        question = {
            'id': 1,
            'type': 'text_input',
            'question': '测试',
            'answer': 'a' * 600,  # 600字符
            'text_type': 'short',
            'max_length': 600  # 超过短文本建议的500字符限制
        }
        
        errors = self.handler.validate_question_data(question)
        self.assertTrue(any('短文本类型的最大长度不应超过500字符' in error for error in errors))
        
        # 长文本长度过短
        question = {
            'id': 1,
            'type': 'text_input',
            'question': '测试',
            'answer': 'short',
            'text_type': 'long',
            'max_length': 50  # 少于长文本建议的100字符限制
        }
        
        errors = self.handler.validate_question_data(question)
        self.assertTrue(any('长文本类型的最大长度不应少于100字符' in error for error in errors))

class TestRequirement23(unittest.TestCase):
    """测试需求 2.3: 保存问题数据时记录问题类型、题目内容和答案选项"""
    
    def setUp(self):
        self.processor = QuestionTypeProcessor()
    
    def test_multiple_choice_data_recording(self):
        """测试选择题数据记录"""
        question = {
            'id': 1,
            'type': 'multiple_choice',
            'question': '你最喜欢的科目是什么？',
            'options': [
                {'value': 0, 'text': '数学'},
                {'value': 1, 'text': '语文'},
                {'value': 2, 'text': '英语'}
            ],
            'selected': [0],
            'is_multiple_choice': False
        }
        
        processed = self.processor.process_question(question)
        
        # 验证记录了问题类型信息
        self.assertIn('question_type_info', processed)
        type_info = processed['question_type_info']
        
        self.assertEqual(type_info['type'], 'multiple_choice')
        self.assertEqual(type_info['mode'], 'single')
        self.assertEqual(type_info['question_text'], '你最喜欢的科目是什么？')
        self.assertEqual(type_info['total_options'], 3)
        self.assertEqual(type_info['selected_count'], 1)
        
    def test_text_input_data_recording(self):
        """测试填空题数据记录"""
        question = {
            'id': 1,
            'type': 'text_input',
            'question': '请描述你的兴趣爱好',
            'answer': '我喜欢阅读和运动',
            'text_type': 'short',
            'max_length': 200
        }
        
        processed = self.processor.process_question(question)
        
        # 验证记录了问题类型信息
        self.assertIn('question_type_info', processed)
        type_info = processed['question_type_info']
        
        self.assertEqual(type_info['type'], 'text_input')
        self.assertEqual(type_info['text_type'], 'short')
        self.assertEqual(type_info['question_text'], '请描述你的兴趣爱好')
        self.assertEqual(type_info['max_length'], 200)
        self.assertEqual(type_info['actual_length'], len('我喜欢阅读和运动'))

class TestRequirement24(unittest.TestCase):
    """测试需求 2.4: 根据问题类型验证答案格式"""
    
    def setUp(self):
        self.processor = QuestionTypeProcessor()
    
    def test_multiple_choice_answer_format_validation(self):
        """测试选择题答案格式验证"""
        # 正确格式
        question = {
            'type': 'multiple_choice',
            'options': [
                {'value': 0, 'text': '选项1'},
                {'value': 1, 'text': '选项2'}
            ],
            'selected': [0],
            'is_multiple_choice': False
        }
        
        errors = validate_answer_format_by_type(question)
        self.assertEqual(len(errors), 0, "正确的选择题格式应该验证通过")
        
        # 错误格式：selected不是列表
        question['selected'] = 0  # 应该是 [0]
        errors = validate_answer_format_by_type(question)
        self.assertTrue(any('选择题答案必须是列表格式' in error for error in errors))
        
        # 错误格式：选择了无效选项
        question['selected'] = [99]  # 不存在的选项
        errors = validate_answer_format_by_type(question)
        self.assertTrue(any('选择的答案值 99 不在有效选项中' in error for error in errors))
        
        # 错误格式：单选题选择多个答案
        question['selected'] = [0, 1]
        question['is_multiple_choice'] = False
        errors = validate_answer_format_by_type(question)
        self.assertTrue(any('单选题不能选择多个答案' in error for error in errors))
        
    def test_text_input_answer_format_validation(self):
        """测试填空题答案格式验证"""
        # 正确格式
        question = {
            'type': 'text_input',
            'answer': '这是一个有效的答案',
            'text_type': 'short',
            'max_length': 100
        }
        
        errors = validate_answer_format_by_type(question)
        self.assertEqual(len(errors), 0, "正确的填空题格式应该验证通过")
        
        # 错误格式：答案不是字符串
        question['answer'] = 123  # 应该是字符串
        errors = validate_answer_format_by_type(question)
        self.assertTrue(any('填空题答案必须是字符串格式' in error for error in errors))
        
        # 错误格式：答案为空
        question['answer'] = '   '  # 空白字符串
        errors = validate_answer_format_by_type(question)
        self.assertTrue(any('填空题答案不能为空' in error for error in errors))
        
        # 错误格式：答案超长
        question['answer'] = 'a' * 101  # 超过max_length
        question['max_length'] = 100
        errors = validate_answer_format_by_type(question)
        self.assertTrue(any('文本答案长度超过限制' in error for error in errors))
        
    def test_unsupported_question_type_validation(self):
        """测试不支持的问题类型验证"""
        question = {
            'type': 'unsupported_type',
            'answer': '答案'
        }
        
        errors = validate_answer_format_by_type(question)
        self.assertTrue(any('不支持的问题类型: unsupported_type' in error for error in errors))

if __name__ == '__main__':
    # 运行所有测试
    unittest.main(verbosity=2)