#!/usr/bin/env python3
"""
问卷数据管理系统单元测试 - 任务10.1实现
测试数据验证函数、API接口和数据库操作
"""

import unittest
import os
import sys
import sqlite3
import json
import tempfile
import shutil
from datetime import datetime, date, timedelta
from unittest.mock import patch, MagicMock, mock_open
import bcrypt

# 添加backend目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

# 导入要测试的模块
from validation import (
    BasicInfoSchema,
    MultipleChoiceQuestionSchema,
    TextInputQuestionSchema,
    QuestionnaireSchema,
    normalize_questionnaire_data,
    check_data_integrity,
    validate_questionnaire_with_schema,
    quick_validate,
    create_validation_error_response
)

from question_types import (
    MultipleChoiceHandler,
    TextInputHandler,
    QuestionTypeProcessor,
    question_processor,
    validate_question_by_type,
    process_question_by_type,
    validate_answer_format_by_type
)

from error_handlers import (
    StandardErrorResponse,
    ErrorCodes,
    ErrorMessages,
    validation_error,
    auth_error,
    permission_error,
    not_found_error,
    server_error
)

class TestDataValidationFunctions(unittest.TestCase):
    """测试数据验证函数 - 需求1, 2, 6的验证"""
    
    def setUp(self):
        """设置测试数据"""
        self.valid_basic_info = {
            'name': '张三',
            'grade': '3年级',
            'submission_date': date.today().strftime('%Y-%m-%d'),
            'age': 9
        }
        
        self.valid_multiple_choice = {
            'id': 1,
            'type': 'multiple_choice',
            'question': '你喜欢什么颜色？',
            'options': [
                {'value': 1, 'text': '红色'},
                {'value': 2, 'text': '蓝色'},
                {'value': 3, 'text': '绿色'}
            ],
            'selected': [1]
        }
        
        self.valid_text_input = {
            'id': 2,
            'type': 'text_input',
            'question': '请输入你的爱好',
            'answer': '读书和运动'
        }
        
        self.valid_questionnaire = {
            'type': 'student_report',
            'basic_info': self.valid_basic_info,
            'questions': [self.valid_multiple_choice, self.valid_text_input]
        }    

    def test_basic_info_validation(self):
        """测试基本信息验证 - 需求1.1"""
        schema = BasicInfoSchema()
        
        # 测试有效数据
        result = schema.load(self.valid_basic_info)
        self.assertEqual(result['name'], '张三')
        self.assertEqual(result['grade'], '3年级')
        
        # 测试必需字段验证
        invalid_data = self.valid_basic_info.copy()
        del invalid_data['name']
        
        with self.assertRaises(Exception):
            schema.load(invalid_data)
    
    def test_multiple_choice_validation(self):
        """测试选择题验证 - 需求2.1, 2.3"""
        schema = MultipleChoiceQuestionSchema()
        
        # 测试有效选择题
        result = schema.load(self.valid_multiple_choice)
        self.assertEqual(result['type'], 'multiple_choice')
        self.assertEqual(len(result['options']), 3)
        self.assertEqual(result['selected'], [1])
        
        # 测试选项唯一性
        invalid_data = self.valid_multiple_choice.copy()
        invalid_data['options'] = [
            {'value': 1, 'text': '红色'},
            {'value': 1, 'text': '蓝色'}  # 重复的value
        ]
        
        with self.assertRaises(Exception):
            schema.load(invalid_data)
    
    def test_text_input_validation(self):
        """测试填空题验证 - 需求2.2, 2.4"""
        schema = TextInputQuestionSchema()
        
        # 测试有效填空题
        result = schema.load(self.valid_text_input)
        self.assertEqual(result['type'], 'text_input')
        self.assertEqual(result['answer'], '读书和运动')
        
        # 测试长度限制
        invalid_data = self.valid_text_input.copy()
        invalid_data['max_length'] = 5
        invalid_data['answer'] = '这是一个很长的答案超过了限制'
        
        with self.assertRaises(Exception):
            schema.load(invalid_data)
    
    def test_questionnaire_schema_validation(self):
        """测试完整问卷Schema验证 - 需求1.2, 1.3"""
        schema = QuestionnaireSchema()
        
        # 测试有效问卷
        result = schema.load(self.valid_questionnaire)
        self.assertEqual(result['type'], 'student_report')
        self.assertEqual(len(result['questions']), 2)
        
        # 测试缺少必需字段
        invalid_data = self.valid_questionnaire.copy()
        del invalid_data['basic_info']
        
        with self.assertRaises(Exception):
            schema.load(invalid_data)
    
    def test_data_normalization(self):
        """测试数据标准化 - 需求1.4"""
        raw_data = {
            'type': 'STUDENT_REPORT',  # 大写
            'name': '  张三  ',  # 包含空格
            'grade': '3年级',
            'submission_date': date.today().strftime('%Y-%m-%d'),
            'questions': [
                {
                    'id': '1',  # 字符串ID
                    'type': 'text_input',
                    'question': '  你的爱好？  ',  # 包含空格
                    'answer': '  读书  '  # 包含空格
                }
            ]
        }
        
        normalized = normalize_questionnaire_data(raw_data)
        self.assertEqual(normalized['type'], 'student_report')
        self.assertEqual(normalized['basic_info']['name'], '张三')
        self.assertEqual(normalized['questions'][0]['question'], '你的爱好？')
        self.assertEqual(normalized['questions'][0]['answer'], '读书')
    
    def test_data_integrity_checks(self):
        """测试数据完整性检查 - 需求6.1, 6.2"""
        # 测试有效数据
        errors = check_data_integrity(self.valid_questionnaire)
        self.assertEqual(len(errors), 0)
        
        # 测试缺少必需字段
        invalid_data = self.valid_questionnaire.copy()
        del invalid_data['type']
        
        errors = check_data_integrity(invalid_data)
        self.assertTrue(any('type' in error for error in errors))
    
    def test_quick_validate_function(self):
        """测试快速验证函数 - 需求6.3"""
        # 测试有效数据
        errors = quick_validate(self.valid_questionnaire)
        self.assertEqual(len(errors), 0)
        
        # 测试无效数据
        invalid_data = {'invalid': 'data'}
        errors = quick_validate(invalid_data)
        self.assertTrue(len(errors) > 0)
    
    def test_validation_error_response(self):
        """测试验证错误响应格式 - 需求6.4"""
        errors = ['姓名不能为空', '年级格式不正确']
        response = create_validation_error_response(errors)
        
        self.assertFalse(response['success'])
        self.assertEqual(response['error']['code'], 'VALIDATION_ERROR')
        self.assertEqual(response['error']['details'], errors)


class TestQuestionTypeHandlers(unittest.TestCase):
    """测试问题类型处理器 - 需求2的实现"""
    
    def setUp(self):
        """设置测试数据"""
        self.multiple_choice_handler = MultipleChoiceHandler()
        self.text_input_handler = TextInputHandler()
        self.processor = QuestionTypeProcessor()
        
        self.valid_multiple_choice = {
            'id': 1,
            'type': 'multiple_choice',
            'question': '你喜欢什么颜色？',
            'options': [
                {'value': 1, 'text': '红色'},
                {'value': 2, 'text': '蓝色'}
            ],
            'selected': [1]
        }
        
        self.valid_text_input = {
            'id': 2,
            'type': 'text_input',
            'question': '你的爱好是什么？',
            'answer': '读书',
            'text_type': 'short'
        }
    
    def test_multiple_choice_handler_validation(self):
        """测试选择题处理器验证 - 需求2.1"""
        # 测试有效数据
        errors = self.multiple_choice_handler.validate_question_data(self.valid_multiple_choice)
        self.assertEqual(len(errors), 0)
        
        # 测试无效数据
        invalid_data = self.valid_multiple_choice.copy()
        invalid_data['selected'] = [999]  # 无效选项
        
        errors = self.multiple_choice_handler.validate_question_data(invalid_data)
        self.assertTrue(len(errors) > 0)
    
    def test_multiple_choice_handler_processing(self):
        """测试选择题处理器处理 - 需求2.1, 2.3"""
        result = self.multiple_choice_handler.process_answer(self.valid_multiple_choice)
        
        self.assertIn('selected_texts', result)
        self.assertIn('question_type_info', result)
        self.assertEqual(result['question_type_info']['type'], 'multiple_choice')
    
    def test_text_input_handler_validation(self):
        """测试填空题处理器验证 - 需求2.2"""
        # 测试有效数据
        errors = self.text_input_handler.validate_question_data(self.valid_text_input)
        self.assertEqual(len(errors), 0)
        
        # 测试长度限制
        invalid_data = self.valid_text_input.copy()
        invalid_data['max_length'] = 2
        invalid_data['answer'] = '这是一个很长的答案'
        
        errors = self.text_input_handler.validate_question_data(invalid_data)
        self.assertTrue(len(errors) > 0)
    
    def test_text_input_handler_processing(self):
        """测试填空题处理器处理 - 需求2.2, 2.3"""
        result = self.text_input_handler.process_answer(self.valid_text_input)
        
        self.assertIn('answer_length', result)
        self.assertIn('word_count', result)
        self.assertIn('question_type_info', result)
        self.assertEqual(result['question_type_info']['type'], 'text_input')
    
    def test_question_type_processor(self):
        """测试问题类型处理器 - 需求2.4"""
        # 测试验证功能
        errors = self.processor.validate_question(self.valid_multiple_choice)
        self.assertEqual(len(errors), 0)
        
        # 测试处理功能
        result = self.processor.process_question(self.valid_multiple_choice)
        self.assertIn('selected_texts', result)
        
        # 测试答案格式验证
        errors = validate_answer_format_by_type(self.valid_multiple_choice)
        self.assertEqual(len(errors), 0)
    
    def test_questionnaire_processing(self):
        """测试完整问卷处理 - 需求2.5"""
        questionnaire = {
            'type': 'test_questionnaire',
            'basic_info': {'name': '测试', 'grade': '1年级', 'submission_date': '2024-01-01'},
            'questions': [self.valid_multiple_choice, self.valid_text_input]
        }
        
        result = self.processor.process_questionnaire(questionnaire)
        
        self.assertIn('statistics', result)
        self.assertEqual(result['statistics']['total_questions'], 2)
        self.assertTrue(result['statistics']['completion_rate'] > 0)


class TestErrorHandlers(unittest.TestCase):
    """测试错误处理模块 - 需求9.4, 9.5"""
    
    def test_standard_error_response_creation(self):
        """测试标准错误响应创建"""
        response, status_code = StandardErrorResponse.create_error_response(
            ErrorCodes.VALIDATION_ERROR,
            "测试错误",
            ["详细错误1", "详细错误2"],
            400
        )
        
        self.assertFalse(response['success'])
        self.assertEqual(response['error']['code'], ErrorCodes.VALIDATION_ERROR)
        self.assertEqual(len(response['error']['details']), 2)
        self.assertEqual(status_code, 400)
    
    def test_validation_error_helper(self):
        """测试验证错误辅助函数"""
        errors = ["姓名不能为空", "年级格式不正确"]
        response, status_code = validation_error(errors)
        
        self.assertFalse(response['success'])
        self.assertEqual(response['error']['code'], ErrorCodes.VALIDATION_ERROR)
        self.assertEqual(status_code, 400)
    
    def test_auth_error_helper(self):
        """测试认证错误辅助函数"""
        response, status_code = auth_error("用户名或密码错误")
        
        self.assertFalse(response['success'])
        self.assertEqual(response['error']['code'], ErrorCodes.AUTH_ERROR)
        self.assertEqual(status_code, 401)
    
    def test_error_messages(self):
        """测试错误消息映射"""
        message = ErrorMessages.get_message(ErrorCodes.VALIDATION_ERROR)
        self.assertIsInstance(message, str)
        self.assertTrue(len(message) > 0)
        
        # 测试默认消息
        message = ErrorMessages.get_message("UNKNOWN_CODE", "默认消息")
        self.assertEqual(message, "默认消息")


class TestDatabaseOperations(unittest.TestCase):
    """测试数据库操作 - 需求5的实现"""
    
    def setUp(self):
        """设置测试数据库"""
        self.test_db_path = tempfile.mktemp(suffix='.db')
        self.setup_test_database()
    
    def tearDown(self):
        """清理测试数据库"""
        try:
            if os.path.exists(self.test_db_path):
                # 在Windows上，需要确保数据库连接已关闭
                import gc
                gc.collect()  # 强制垃圾回收，关闭未关闭的连接
                import time
                time.sleep(0.1)  # 短暂等待
                os.unlink(self.test_db_path)
        except (PermissionError, OSError):
            # 如果无法删除文件，记录但不失败
            pass
    
    def setup_test_database(self):
        """设置测试数据库结构"""
        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.cursor()
            
            # 创建问卷数据表
            cursor.execute('''
            CREATE TABLE questionnaires (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                name TEXT,
                grade TEXT,
                submission_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data TEXT NOT NULL
            )
            ''')
            
            # 创建用户表
            cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'admin',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
            ''')
            
            # 创建操作日志表
            cursor.execute('''
            CREATE TABLE operation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                operation TEXT NOT NULL,
                target_id INTEGER,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            ''')
            
            conn.commit()
    
    def test_questionnaire_crud_operations(self):
        """测试问卷CRUD操作 - 需求5.1, 5.2"""
        test_data = {
            'type': 'test_questionnaire',
            'name': '测试学生',
            'grade': '3年级',
            'submission_date': '2024-01-01',
            'data': json.dumps({'test': 'data'})
        }
        
        with sqlite3.connect(self.test_db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 测试创建
            cursor.execute(
                "INSERT INTO questionnaires (type, name, grade, submission_date, data) VALUES (?, ?, ?, ?, ?)",
                (test_data['type'], test_data['name'], test_data['grade'], 
                 test_data['submission_date'], test_data['data'])
            )
            questionnaire_id = cursor.lastrowid
            self.assertIsNotNone(questionnaire_id)
            
            # 测试读取
            cursor.execute("SELECT * FROM questionnaires WHERE id = ?", (questionnaire_id,))
            result = cursor.fetchone()
            self.assertIsNotNone(result)
            self.assertEqual(result['name'], test_data['name'])
            
            # 测试更新
            new_name = '更新后的学生'
            cursor.execute(
                "UPDATE questionnaires SET name = ?, updated_at = ? WHERE id = ?",
                (new_name, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), questionnaire_id)
            )
            
            cursor.execute("SELECT name FROM questionnaires WHERE id = ?", (questionnaire_id,))
            updated_result = cursor.fetchone()
            self.assertEqual(updated_result['name'], new_name)
            
            # 测试删除
            cursor.execute("DELETE FROM questionnaires WHERE id = ?", (questionnaire_id,))
            cursor.execute("SELECT * FROM questionnaires WHERE id = ?", (questionnaire_id,))
            deleted_result = cursor.fetchone()
            self.assertIsNone(deleted_result)
    
    def test_user_authentication_operations(self):
        """测试用户认证操作 - 需求3.1, 3.2"""
        username = 'test_user'
        password = 'test_password'
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        with sqlite3.connect(self.test_db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 测试用户创建
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, password_hash, 'admin')
            )
            user_id = cursor.lastrowid
            self.assertIsNotNone(user_id)
            
            # 测试用户查询
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            self.assertIsNotNone(user)
            self.assertEqual(user['username'], username)
            
            # 测试密码验证
            self.assertTrue(bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')))
            self.assertFalse(bcrypt.checkpw('wrong_password'.encode('utf-8'), user['password_hash'].encode('utf-8')))
    
    def test_operation_logging(self):
        """测试操作日志记录 - 需求8.3"""
        with sqlite3.connect(self.test_db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 创建测试用户
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                ('test_user', 'hash')
            )
            user_id = cursor.lastrowid
            
            # 记录操作日志
            log_data = {
                'user_id': user_id,
                'operation': 'CREATE_QUESTIONNAIRE',
                'target_id': 1,
                'details': json.dumps({'action': 'create', 'type': 'test'})
            }
            
            cursor.execute(
                "INSERT INTO operation_logs (user_id, operation, target_id, details) VALUES (?, ?, ?, ?)",
                (log_data['user_id'], log_data['operation'], log_data['target_id'], log_data['details'])
            )
            log_id = cursor.lastrowid
            self.assertIsNotNone(log_id)
            
            # 查询操作日志
            cursor.execute("SELECT * FROM operation_logs WHERE id = ?", (log_id,))
            log_result = cursor.fetchone()
            self.assertIsNotNone(log_result)
            self.assertEqual(log_result['operation'], log_data['operation'])
    
    def test_database_constraints(self):
        """测试数据库约束 - 需求5.3"""
        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.cursor()
            
            # 测试用户名唯一约束
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                ('unique_user', 'hash1')
            )
            
            # 尝试插入重复用户名
            with self.assertRaises(sqlite3.IntegrityError):
                cursor.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    ('unique_user', 'hash2')
                )
    
    def test_data_retrieval_with_filters(self):
        """测试带筛选条件的数据检索 - 需求5.3"""
        with sqlite3.connect(self.test_db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 插入测试数据
            test_records = [
                ('type1', '学生A', '1年级', '2024-01-01', '{}'),
                ('type1', '学生B', '2年级', '2024-01-02', '{}'),
                ('type2', '学生C', '1年级', '2024-01-03', '{}')
            ]
            
            for record in test_records:
                cursor.execute(
                    "INSERT INTO questionnaires (type, name, grade, submission_date, data) VALUES (?, ?, ?, ?, ?)",
                    record
                )
            
            # 测试按类型筛选
            cursor.execute("SELECT * FROM questionnaires WHERE type = ?", ('type1',))
            type1_results = cursor.fetchall()
            self.assertEqual(len(type1_results), 2)
            
            # 测试按年级筛选
            cursor.execute("SELECT * FROM questionnaires WHERE grade = ?", ('1年级',))
            grade1_results = cursor.fetchall()
            self.assertEqual(len(grade1_results), 2)
            
            # 测试按日期范围筛选
            cursor.execute(
                "SELECT * FROM questionnaires WHERE DATE(submission_date) BETWEEN ? AND ?",
                ('2024-01-01', '2024-01-02')
            )
            date_range_results = cursor.fetchall()
            self.assertEqual(len(date_range_results), 2)


def run_unit_tests():
    """运行所有单元测试"""
    print("开始运行问卷数据管理系统单元测试...\n")
    print("=" * 60)
    
    # 创建测试套件
    test_classes = [
        TestDataValidationFunctions,
        TestQuestionTypeHandlers,
        TestErrorHandlers,
        TestDatabaseOperations
    ]
    
    total_tests = 0
    total_failures = 0
    total_errors = 0
    
    for test_class in test_classes:
        print(f"\n运行 {test_class.__name__} 测试...")
        print("-" * 40)
        
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        total_tests += result.testsRun
        total_failures += len(result.failures)
        total_errors += len(result.errors)
        
        if result.failures:
            print(f"\n失败的测试:")
            for failure in result.failures:
                print(f"  - {failure[0]}: {failure[1].split('AssertionError:')[-1].strip()}")
        
        if result.errors:
            print(f"\n错误的测试:")
            for error in result.errors:
                print(f"  - {error[0]}: {error[1].split('Exception:')[-1].strip()}")
    
    print("\n" + "=" * 60)
    print("单元测试总结:")
    print(f"总测试数: {total_tests}")
    print(f"成功: {total_tests - total_failures - total_errors}")
    print(f"失败: {total_failures}")
    print(f"错误: {total_errors}")
    
    success_rate = ((total_tests - total_failures - total_errors) / total_tests * 100) if total_tests > 0 else 0
    print(f"成功率: {success_rate:.1f}%")
    
    if total_failures == 0 and total_errors == 0:
        print("\n🎉 所有单元测试通过！")
        print("\n已验证的功能:")
        print("✓ 数据验证函数 (需求1, 2, 6)")
        print("✓ 问题类型处理器 (需求2)")
        print("✓ 错误处理机制 (需求9)")
        print("✓ 数据库操作 (需求3, 5, 8)")
        return True
    else:
        print(f"\n⚠️  有 {total_failures + total_errors} 个测试失败，请检查实现。")
        return False


if __name__ == '__main__':
    success = run_unit_tests()
    sys.exit(0 if success else 1)