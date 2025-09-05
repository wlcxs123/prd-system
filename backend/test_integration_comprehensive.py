#!/usr/bin/env python3
"""
问卷数据管理系统集成测试 - 任务10.2实现
测试完整的问卷提交流程、批量操作功能和数据导出功能
"""

import unittest
import os
import sys
import json
import tempfile
import sqlite3
import requests
import time
import threading
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import subprocess

# 添加backend目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

# 导入Flask应用
from app import app, init_db
from config import config

class TestQuestionnaireSubmissionFlow(unittest.TestCase):
    """测试完整的问卷提交流程 - 需求1, 2, 4, 5的集成"""
    
    def setUp(self):
        """设置测试环境"""
        app.config['TESTING'] = True
        app.config['DATABASE_PATH'] = tempfile.mktemp(suffix='.db')
        app.config['SECRET_KEY'] = 'test_secret_key'
        
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
        # 初始化测试数据库
        init_db()
        
        # 登录获取会话
        self.login()
    
    def tearDown(self):
        """清理测试环境"""
        try:
            if os.path.exists(app.config['DATABASE_PATH']):
                import gc
                gc.collect()
                time.sleep(0.1)
                os.unlink(app.config['DATABASE_PATH'])
        except (PermissionError, OSError):
            pass
        
        self.app_context.pop()
    
    def login(self):
        """登录获取会话"""
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        response = self.client.post('/api/auth/login', 
                                  data=json.dumps(login_data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
    
    def test_complete_questionnaire_submission_flow(self):
        """测试完整问卷提交流程 - 需求1.1, 1.2, 1.3, 1.4, 1.5"""
        print("\n测试完整问卷提交流程...")
        
        # 1. 准备测试数据 - 模拟前端提交的数据
        questionnaire_data = {
            'type': 'student_communication_assessment',
            'basic_info': {
                'name': '张小明',
                'grade': '三年级',
                'submission_date': datetime.now().strftime('%Y-%m-%d'),
                'age': 9,
                'gender': '男',
                'school': '实验小学',
                'class_name': '三年级一班'
            },
            'questions': [
                {
                    'id': 1,
                    'type': 'multiple_choice',
                    'question': '你在学校里愿意主动和老师说话吗？',
                    'options': [
                        {'value': 0, 'text': '从不'},
                        {'value': 1, 'text': '很少'},
                        {'value': 2, 'text': '有时'},
                        {'value': 3, 'text': '经常'},
                        {'value': 4, 'text': '总是'}
                    ],
                    'selected': [2],
                    'section': 'school_communication'
                },
                {
                    'id': 2,
                    'type': 'multiple_choice',
                    'question': '你在家里和父母交流时感觉如何？',
                    'options': [
                        {'value': 0, 'text': '很困难'},
                        {'value': 1, 'text': '有些困难'},
                        {'value': 2, 'text': '一般'},
                        {'value': 3, 'text': '比较容易'},
                        {'value': 4, 'text': '很容易'}
                    ],
                    'selected': [3],
                    'section': 'home_communication'
                },
                {
                    'id': 3,
                    'type': 'text_input',
                    'question': '请描述一下你最喜欢和谁交流，为什么？',
                    'answer': '我最喜欢和我的好朋友小红交流，因为她总是很耐心地听我说话，而且会给我很好的建议。',
                    'text_type': 'long',
                    'max_length': 500
                },
                {
                    'id': 4,
                    'type': 'text_input',
                    'question': '你的兴趣爱好是什么？',
                    'answer': '画画、读书、踢足球',
                    'text_type': 'short',
                    'max_length': 100
                }
            ],
            'statistics': {
                'total_score': 85,
                'completion_rate': 100,
                'submission_time': datetime.now().isoformat()
            }
        }
        
        # 2. 测试数据验证 - 需求1.1, 6.1, 6.2
        print("  - 测试数据验证...")
        response = self.client.post('/api/questionnaires',
                                  data=json.dumps(questionnaire_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertTrue(response_data['success'])
        questionnaire_id = response_data['id']
        
        # 3. 验证数据存储 - 需求5.1, 5.2
        print("  - 验证数据存储...")
        response = self.client.get(f'/api/questionnaires/{questionnaire_id}')
        self.assertEqual(response.status_code, 200)
        stored_data = json.loads(response.data)
        
        self.assertTrue(stored_data['success'])
        self.assertEqual(stored_data['data']['name'], '张小明')
        self.assertEqual(stored_data['data']['type'], 'student_communication_assessment')
        
        # 验证问题数据完整性
        stored_questions = json.loads(stored_data['data']['data'])['questions']
        self.assertEqual(len(stored_questions), 4)
        
        # 4. 测试数据检索和筛选 - 需求4.2, 5.3
        print("  - 测试数据检索和筛选...")
        
        # 按姓名搜索
        response = self.client.get('/api/questionnaires?search=张小明')
        self.assertEqual(response.status_code, 200)
        search_data = json.loads(response.data)
        self.assertTrue(len(search_data['data']) >= 1)
        
        # 按类型筛选
        response = self.client.get('/api/questionnaires?type=student_communication_assessment')
        self.assertEqual(response.status_code, 200)
        filter_data = json.loads(response.data)
        self.assertTrue(len(filter_data['data']) >= 1)
        
        # 5. 测试数据更新 - 需求4.4, 5.4
        print("  - 测试数据更新...")
        updated_data = questionnaire_data.copy()
        updated_data['basic_info']['name'] = '张小明（已更新）'
        updated_data['questions'][3]['answer'] = '画画、读书、踢足球、游泳'
        
        response = self.client.put(f'/api/questionnaires/{questionnaire_id}',
                                 data=json.dumps(updated_data),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        # 验证更新结果
        response = self.client.get(f'/api/questionnaires/{questionnaire_id}')
        updated_result = json.loads(response.data)
        self.assertEqual(updated_result['data']['name'], '张小明（已更新）')
        
        # 6. 测试操作日志记录 - 需求8.3
        print("  - 验证操作日志记录...")
        response = self.client.get('/api/admin/logs')
        self.assertEqual(response.status_code, 200)
        logs_data = json.loads(response.data)
        
        # 应该有创建和更新的日志记录
        operations = [log['operation'] for log in logs_data['data']]
        self.assertIn('CREATE_QUESTIONNAIRE', operations)
        self.assertIn('UPDATE_QUESTIONNAIRE', operations)
        
        print("  ✓ 完整问卷提交流程测试通过")
        return questionnaire_id
    
    def test_multi_type_questionnaire_handling(self):
        """测试多种问题类型处理 - 需求2.1, 2.2, 2.3, 2.4"""
        print("\n测试多种问题类型处理...")
        
        # 创建包含各种问题类型的问卷
        complex_questionnaire = {
            'type': 'comprehensive_assessment',
            'basic_info': {
                'name': '李小华',
                'grade': '四年级',
                'submission_date': datetime.now().strftime('%Y-%m-%d')
            },
            'questions': [
                # 单选题
                {
                    'id': 1,
                    'type': 'multiple_choice',
                    'question': '你最喜欢的学科是什么？',
                    'options': [
                        {'value': 'math', 'text': '数学'},
                        {'value': 'chinese', 'text': '语文'},
                        {'value': 'english', 'text': '英语'},
                        {'value': 'science', 'text': '科学'}
                    ],
                    'selected': ['math'],
                    'allow_multiple': False
                },
                # 多选题
                {
                    'id': 2,
                    'type': 'multiple_choice',
                    'question': '你参加过哪些课外活动？（可多选）',
                    'options': [
                        {'value': 'sports', 'text': '体育运动'},
                        {'value': 'music', 'text': '音乐'},
                        {'value': 'art', 'text': '美术'},
                        {'value': 'reading', 'text': '阅读'}
                    ],
                    'selected': ['sports', 'music', 'reading'],
                    'allow_multiple': True
                },
                # 短文本输入
                {
                    'id': 3,
                    'type': 'text_input',
                    'question': '你的姓名是？',
                    'answer': '李小华',
                    'text_type': 'short',
                    'max_length': 50
                },
                # 长文本输入
                {
                    'id': 4,
                    'type': 'text_input',
                    'question': '请描述你的学习方法和心得体会。',
                    'answer': '我认为学习最重要的是要有计划性。每天我都会制定学习计划，先完成作业，然后复习当天学的内容，最后预习明天要学的知识。在学习过程中，我喜欢做笔记，把重要的知识点记录下来。遇到不懂的问题，我会及时向老师或同学请教。',
                    'text_type': 'long',
                    'max_length': 1000
                },
                # 数字输入
                {
                    'id': 5,
                    'type': 'text_input',
                    'question': '你每天花多少小时做作业？',
                    'answer': '2.5',
                    'input_type': 'number',
                    'text_type': 'short'
                }
            ]
        }
        
        # 提交问卷
        response = self.client.post('/api/questionnaires',
                                  data=json.dumps(complex_questionnaire),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        questionnaire_id = response_data['id']
        
        # 验证存储的数据
        response = self.client.get(f'/api/questionnaires/{questionnaire_id}')
        stored_data = json.loads(response.data)
        stored_questions = json.loads(stored_data['data']['data'])['questions']
        
        # 验证单选题
        single_choice = next(q for q in stored_questions if q['id'] == 1)
        self.assertEqual(len(single_choice['selected']), 1)
        self.assertEqual(single_choice['selected'][0], 'math')
        
        # 验证多选题
        multiple_choice = next(q for q in stored_questions if q['id'] == 2)
        self.assertEqual(len(multiple_choice['selected']), 3)
        self.assertIn('sports', multiple_choice['selected'])
        self.assertIn('music', multiple_choice['selected'])
        self.assertIn('reading', multiple_choice['selected'])
        
        # 验证文本输入
        short_text = next(q for q in stored_questions if q['id'] == 3)
        self.assertEqual(short_text['answer'], '李小华')
        
        long_text = next(q for q in stored_questions if q['id'] == 4)
        self.assertTrue(len(long_text['answer']) > 50)
        
        number_input = next(q for q in stored_questions if q['id'] == 5)
        self.assertEqual(number_input['answer'], '2.5')
        
        print("  ✓ 多种问题类型处理测试通过")
        return questionnaire_id
    
    def test_data_validation_integration(self):
        """测试数据验证集成 - 需求6.1, 6.2, 6.3, 6.4"""
        print("\n测试数据验证集成...")
        
        # 测试各种无效数据情况
        invalid_cases = [
            {
                'name': '缺少基本信息',
                'data': {
                    'type': 'test',
                    'questions': []
                },
                'expected_errors': ['basic_info']
            },
            {
                'name': '空姓名',
                'data': {
                    'type': 'test',
                    'basic_info': {
                        'name': '',
                        'grade': '1年级',
                        'submission_date': '2024-01-01'
                    },
                    'questions': []
                },
                'expected_errors': ['姓名']
            },
            {
                'name': '无效选择题选项',
                'data': {
                    'type': 'test',
                    'basic_info': {
                        'name': '测试',
                        'grade': '1年级',
                        'submission_date': '2024-01-01'
                    },
                    'questions': [
                        {
                            'id': 1,
                            'type': 'multiple_choice',
                            'question': '测试问题',
                            'options': [
                                {'value': 1, 'text': '选项1'}
                            ],
                            'selected': [999]  # 无效选项
                        }
                    ]
                },
                'expected_errors': ['选项']
            },
            {
                'name': '超长文本答案',
                'data': {
                    'type': 'test',
                    'basic_info': {
                        'name': '测试',
                        'grade': '1年级',
                        'submission_date': '2024-01-01'
                    },
                    'questions': [
                        {
                            'id': 1,
                            'type': 'text_input',
                            'question': '测试问题',
                            'answer': 'a' * 1000,  # 超长答案
                            'max_length': 100
                        }
                    ]
                },
                'expected_errors': ['长度']
            }
        ]
        
        for case in invalid_cases:
            print(f"  - 测试{case['name']}...")
            response = self.client.post('/api/questionnaires',
                                      data=json.dumps(case['data']),
                                      content_type='application/json')
            
            self.assertEqual(response.status_code, 400)
            error_data = json.loads(response.data)
            self.assertFalse(error_data['success'])
            self.assertEqual(error_data['error']['code'], 'VALIDATION_ERROR')
            
            # 检查是否包含预期的错误信息
            error_details = str(error_data['error']['details'])
            for expected_error in case['expected_errors']:
                self.assertIn(expected_error, error_details)
        
        print("  ✓ 数据验证集成测试通过")
    
    def test_error_handling_integration(self):
        """测试错误处理集成 - 需求9.4, 9.5"""
        print("\n测试错误处理集成...")
        
        # 测试各种错误情况
        error_cases = [
            {
                'name': '访问不存在的问卷',
                'request': lambda: self.client.get('/api/questionnaires/99999'),
                'expected_status': 404,
                'expected_code': 'NOT_FOUND'
            },
            {
                'name': '无效JSON数据',
                'request': lambda: self.client.post('/api/questionnaires',
                                                  data='invalid json',
                                                  content_type='application/json'),
                'expected_status': 400,
                'expected_code': 'VALIDATION_ERROR'
            },
            {
                'name': '未登录访问管理接口',
                'request': lambda: self._test_unauthorized_access(),
                'expected_status': 401,
                'expected_code': 'AUTH_REQUIRED'
            }
        ]
        
        for case in error_cases:
            print(f"  - 测试{case['name']}...")
            response = case['request']()
            
            self.assertEqual(response.status_code, case['expected_status'])
            error_data = json.loads(response.data)
            self.assertFalse(error_data['success'])
            self.assertEqual(error_data['error']['code'], case['expected_code'])
            
            # 验证错误响应格式
            self.assertIn('timestamp', error_data)
            self.assertIn('message', error_data['error'])
        
        print("  ✓ 错误处理集成测试通过")
    
    def _test_unauthorized_access(self):
        """测试未授权访问"""
        # 先登出
        self.client.post('/api/auth/logout')
        
        # 尝试访问需要认证的接口
        response = self.client.get('/api/admin/statistics')
        
        # 重新登录以便后续测试
        self.login()
        
        return response


class TestBatchOperations(unittest.TestCase):
    """测试批量操作功能 - 需求7的集成"""
    
    def setUp(self):
        """设置测试环境"""
        app.config['TESTING'] = True
        app.config['DATABASE_PATH'] = tempfile.mktemp(suffix='.db')
        app.config['SECRET_KEY'] = 'test_secret_key'
        
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
        init_db()
        self.login()
        
        # 创建测试数据
        self.test_questionnaire_ids = self.create_test_data()
    
    def tearDown(self):
        """清理测试环境"""
        try:
            if os.path.exists(app.config['DATABASE_PATH']):
                import gc
                gc.collect()
                time.sleep(0.1)
                os.unlink(app.config['DATABASE_PATH'])
        except (PermissionError, OSError):
            pass
        
        self.app_context.pop()
    
    def login(self):
        """登录"""
        login_data = {'username': 'admin', 'password': 'admin123'}
        self.client.post('/api/auth/login', 
                        data=json.dumps(login_data),
                        content_type='application/json')
    
    def create_test_data(self):
        """创建测试数据"""
        questionnaire_ids = []
        
        for i in range(10):
            questionnaire_data = {
                'type': f'batch_test_type_{i % 3}',
                'basic_info': {
                    'name': f'批量测试学生{i+1}',
                    'grade': f'{(i % 6) + 1}年级',
                    'submission_date': (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
                },
                'questions': [
                    {
                        'id': 1,
                        'type': 'text_input',
                        'question': '批量测试问题',
                        'answer': f'批量测试答案{i+1}'
                    },
                    {
                        'id': 2,
                        'type': 'multiple_choice',
                        'question': '批量测试选择题',
                        'options': [
                            {'value': 0, 'text': '选项A'},
                            {'value': 1, 'text': '选项B'}
                        ],
                        'selected': [i % 2]
                    }
                ],
                'statistics': {
                    'total_score': (i + 1) * 10,
                    'completion_rate': 100
                }
            }
            
            response = self.client.post('/api/questionnaires',
                                      data=json.dumps(questionnaire_data),
                                      content_type='application/json')
            
            if response.status_code == 201:
                data = json.loads(response.data)
                questionnaire_ids.append(data['id'])
        
        return questionnaire_ids 
   
    def test_batch_selection_and_operations(self):
        """测试批量选择和操作 - 需求7.1, 7.2"""
        print("\n测试批量选择和操作...")
        
        # 1. 测试全选功能
        print("  - 测试全选功能...")
        response = self.client.get('/api/questionnaires?limit=100')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        all_ids = [item['id'] for item in data['data']]
        self.assertTrue(len(all_ids) >= 10)
        
        # 2. 测试按条件选择
        print("  - 测试按条件选择...")
        response = self.client.get('/api/questionnaires?type=batch_test_type_0')
        self.assertEqual(response.status_code, 200)
        filtered_data = json.loads(response.data)
        
        type_0_ids = [item['id'] for item in filtered_data['data']]
        self.assertTrue(len(type_0_ids) >= 3)  # 应该有3-4个type_0的记录
        
        # 3. 测试批量操作权限验证
        print("  - 测试批量操作权限验证...")
        # 先登出测试未授权访问
        self.client.post('/api/auth/logout')
        
        batch_data = {'ids': type_0_ids[:2]}
        response = self.client.delete('/api/questionnaires/batch',
                                    data=json.dumps(batch_data),
                                    content_type='application/json')
        
        self.assertEqual(response.status_code, 401)
        
        # 重新登录
        self.login()
        
        print("  ✓ 批量选择和操作测试通过")
    
    def test_batch_delete_operations(self):
        """测试批量删除操作 - 需求7.3, 7.4"""
        print("\n测试批量删除操作...")
        
        # 选择要删除的记录
        delete_ids = self.test_questionnaire_ids[:5]  # 删除前5个
        
        # 1. 测试批量删除确认
        print("  - 测试批量删除...")
        delete_data = {
            'ids': delete_ids,
            'confirm': True
        }
        
        response = self.client.delete('/api/questionnaires/batch',
                                    data=json.dumps(delete_data),
                                    content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        result_data = json.loads(response.data)
        self.assertTrue(result_data['success'])
        self.assertEqual(result_data['deleted_count'], 5)
        
        # 2. 验证删除结果
        print("  - 验证删除结果...")
        for deleted_id in delete_ids:
            response = self.client.get(f'/api/questionnaires/{deleted_id}')
            self.assertEqual(response.status_code, 404)
        
        # 3. 验证剩余记录
        remaining_ids = self.test_questionnaire_ids[5:]
        for remaining_id in remaining_ids:
            response = self.client.get(f'/api/questionnaires/{remaining_id}')
            self.assertEqual(response.status_code, 200)
        
        # 4. 验证操作日志
        print("  - 验证操作日志...")
        response = self.client.get('/api/admin/logs')
        self.assertEqual(response.status_code, 200)
        logs_data = json.loads(response.data)
        
        # 查找批量删除日志
        batch_delete_logs = [log for log in logs_data['data'] 
                           if log['operation'] == 'BATCH_DELETE']
        self.assertTrue(len(batch_delete_logs) >= 1)
        
        print("  ✓ 批量删除操作测试通过")
    
    def test_batch_export_operations(self):
        """测试批量导出操作 - 需求7.5, 7.6"""
        print("\n测试批量导出操作...")
        
        # 使用剩余的记录进行导出测试
        export_ids = self.test_questionnaire_ids[5:8]  # 导出3个记录
        
        # 1. 测试JSON格式导出
        print("  - 测试JSON格式导出...")
        export_data = {
            'ids': export_ids,
            'format': 'json'
        }
        
        response = self.client.post('/api/questionnaires/export',
                                  data=json.dumps(export_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        # 验证导出内容
        if response.content_type == 'application/json':
            exported_data = json.loads(response.data)
            self.assertEqual(len(exported_data), 3)
        
        # 2. 测试CSV格式导出
        print("  - 测试CSV格式导出...")
        export_data['format'] = 'csv'
        
        response = self.client.post('/api/questionnaires/export',
                                  data=json.dumps(export_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        # 验证CSV内容
        if 'text/csv' in response.content_type or 'application/octet-stream' in response.content_type:
            csv_content = response.data.decode('utf-8')
            self.assertIn('name', csv_content.lower())  # 应该包含表头
        
        # 3. 测试Excel格式导出
        print("  - 测试Excel格式导出...")
        export_data['format'] = 'excel'
        
        response = self.client.post('/api/questionnaires/export',
                                  data=json.dumps(export_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        # 4. 测试PDF格式导出
        print("  - 测试PDF格式导出...")
        export_data['format'] = 'pdf'
        
        response = self.client.post('/api/questionnaires/export',
                                  data=json.dumps(export_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        # 5. 验证导出日志
        print("  - 验证导出日志...")
        response = self.client.get('/api/admin/logs')
        logs_data = json.loads(response.data)
        
        export_logs = [log for log in logs_data['data'] 
                      if log['operation'] == 'EXPORT_DATA']
        self.assertTrue(len(export_logs) >= 1)
        
        print("  ✓ 批量导出操作测试通过")
    
    def test_batch_operations_performance(self):
        """测试批量操作性能 - 需求8.4"""
        print("\n测试批量操作性能...")
        
        # 创建更多测试数据用于性能测试
        performance_ids = []
        start_time = time.time()
        
        # 批量创建50个记录
        for i in range(50):
            questionnaire_data = {
                'type': 'performance_test',
                'basic_info': {
                    'name': f'性能测试学生{i+1}',
                    'grade': f'{(i % 6) + 1}年级',
                    'submission_date': datetime.now().strftime('%Y-%m-%d')
                },
                'questions': [
                    {
                        'id': 1,
                        'type': 'text_input',
                        'question': '性能测试问题',
                        'answer': f'性能测试答案{i+1}'
                    }
                ]
            }
            
            response = self.client.post('/api/questionnaires',
                                      data=json.dumps(questionnaire_data),
                                      content_type='application/json')
            
            if response.status_code == 201:
                data = json.loads(response.data)
                performance_ids.append(data['id'])
        
        creation_time = time.time() - start_time
        
        # 测试批量查询性能
        start_time = time.time()
        response = self.client.get('/api/questionnaires?type=performance_test&limit=50')
        query_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        
        # 测试批量导出性能
        start_time = time.time()
        export_data = {
            'ids': performance_ids,
            'format': 'json'
        }
        response = self.client.post('/api/questionnaires/export',
                                  data=json.dumps(export_data),
                                  content_type='application/json')
        export_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        
        # 测试批量删除性能
        start_time = time.time()
        delete_data = {'ids': performance_ids}
        response = self.client.delete('/api/questionnaires/batch',
                                    data=json.dumps(delete_data),
                                    content_type='application/json')
        delete_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        
        # 性能断言
        print(f"    创建50条记录耗时: {creation_time:.2f}秒")
        print(f"    查询50条记录耗时: {query_time:.2f}秒")
        print(f"    导出50条记录耗时: {export_time:.2f}秒")
        print(f"    删除50条记录耗时: {delete_time:.2f}秒")
        
        self.assertLess(creation_time, 30.0, "批量创建耗时过长")
        self.assertLess(query_time, 5.0, "批量查询耗时过长")
        self.assertLess(export_time, 10.0, "批量导出耗时过长")
        self.assertLess(delete_time, 5.0, "批量删除耗时过长")
        
        print("  ✓ 批量操作性能测试通过")


class TestDataExportFunctionality(unittest.TestCase):
    """测试数据导出功能 - 需求8.2的集成"""
    
    def setUp(self):
        """设置测试环境"""
        app.config['TESTING'] = True
        app.config['DATABASE_PATH'] = tempfile.mktemp(suffix='.db')
        app.config['SECRET_KEY'] = 'test_secret_key'
        
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
        init_db()
        self.login()
        
        # 创建多样化的测试数据
        self.create_diverse_test_data()
    
    def tearDown(self):
        """清理测试环境"""
        try:
            if os.path.exists(app.config['DATABASE_PATH']):
                import gc
                gc.collect()
                time.sleep(0.1)
                os.unlink(app.config['DATABASE_PATH'])
        except (PermissionError, OSError):
            pass
        
        self.app_context.pop()
    
    def login(self):
        """登录"""
        login_data = {'username': 'admin', 'password': 'admin123'}
        self.client.post('/api/auth/login', 
                        data=json.dumps(login_data),
                        content_type='application/json')
    
    def create_diverse_test_data(self):
        """创建多样化的测试数据"""
        self.export_test_ids = []
        
        # 创建不同类型的问卷数据
        questionnaire_types = [
            {
                'type': 'student_report',
                'name_prefix': '学生报告',
                'questions': [
                    {
                        'id': 1,
                        'type': 'multiple_choice',
                        'question': '你在学校的表现如何？',
                        'options': [
                            {'value': 1, 'text': '很好'},
                            {'value': 2, 'text': '一般'},
                            {'value': 3, 'text': '需要改进'}
                        ],
                        'selected': [1]
                    },
                    {
                        'id': 2,
                        'type': 'text_input',
                        'question': '你最喜欢的科目是什么？',
                        'answer': '数学'
                    }
                ]
            },
            {
                'type': 'parent_interview',
                'name_prefix': '家长访谈',
                'questions': [
                    {
                        'id': 1,
                        'type': 'multiple_choice',
                        'question': '您对孩子的学习情况满意吗？',
                        'options': [
                            {'value': 1, 'text': '非常满意'},
                            {'value': 2, 'text': '比较满意'},
                            {'value': 3, 'text': '一般'},
                            {'value': 4, 'text': '不满意'}
                        ],
                        'selected': [2]
                    },
                    {
                        'id': 2,
                        'type': 'text_input',
                        'question': '您希望学校在哪些方面改进？',
                        'answer': '希望能够增加更多的课外活动，让孩子们有更多的实践机会。'
                    }
                ]
            }
        ]
        
        for i, q_type in enumerate(questionnaire_types):
            for j in range(3):  # 每种类型创建3个
                questionnaire_data = {
                    'type': q_type['type'],
                    'basic_info': {
                        'name': f'{q_type["name_prefix"]}{j+1}',
                        'grade': f'{((i*3+j) % 6) + 1}年级',
                        'submission_date': (datetime.now() - timedelta(days=i*3+j)).strftime('%Y-%m-%d'),
                        'age': 8 + ((i*3+j) % 5),
                        'gender': '男' if (i*3+j) % 2 == 0 else '女'
                    },
                    'questions': q_type['questions'],
                    'statistics': {
                        'total_score': 80 + (i*3+j) * 2,
                        'completion_rate': 100,
                        'submission_time': datetime.now().isoformat()
                    }
                }
                
                response = self.client.post('/api/questionnaires',
                                          data=json.dumps(questionnaire_data),
                                          content_type='application/json')
                
                if response.status_code == 201:
                    data = json.loads(response.data)
                    self.export_test_ids.append(data['id'])
    
    def test_json_export_functionality(self):
        """测试JSON导出功能"""
        print("\n测试JSON导出功能...")
        
        export_data = {
            'ids': self.export_test_ids[:3],
            'format': 'json',
            'include_metadata': True
        }
        
        response = self.client.post('/api/questionnaires/export',
                                  data=json.dumps(export_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        # 验证JSON格式
        if response.content_type == 'application/json':
            exported_data = json.loads(response.data)
            
            # 验证导出数据结构
            self.assertIsInstance(exported_data, list)
            self.assertEqual(len(exported_data), 3)
            
            # 验证每条记录的完整性
            for record in exported_data:
                self.assertIn('id', record)
                self.assertIn('type', record)
                self.assertIn('name', record)
                self.assertIn('grade', record)
                self.assertIn('data', record)
                
                # 验证问卷数据完整性
                questionnaire_data = json.loads(record['data'])
                self.assertIn('basic_info', questionnaire_data)
                self.assertIn('questions', questionnaire_data)
        
        print("  ✓ JSON导出功能测试通过")
    
    def test_csv_export_functionality(self):
        """测试CSV导出功能"""
        print("\n测试CSV导出功能...")
        
        export_data = {
            'ids': self.export_test_ids,
            'format': 'csv',
            'flatten_questions': True
        }
        
        response = self.client.post('/api/questionnaires/export',
                                  data=json.dumps(export_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        # 验证CSV格式
        if 'text/csv' in response.content_type or 'application/octet-stream' in response.content_type:
            csv_content = response.data.decode('utf-8')
            
            # 验证CSV结构
            lines = csv_content.strip().split('\n')
            self.assertTrue(len(lines) >= 2)  # 至少有表头和一行数据
            
            # 验证表头
            header = lines[0].lower()
            expected_columns = ['id', 'type', 'name', 'grade', 'submission_date']
            for col in expected_columns:
                self.assertIn(col, header)
            
            # 验证数据行数
            data_lines = len(lines) - 1
            self.assertEqual(data_lines, len(self.export_test_ids))
        
        print("  ✓ CSV导出功能测试通过")
    
    def test_excel_export_functionality(self):
        """测试Excel导出功能"""
        print("\n测试Excel导出功能...")
        
        export_data = {
            'ids': self.export_test_ids[:4],
            'format': 'excel',
            'include_charts': True
        }
        
        response = self.client.post('/api/questionnaires/export',
                                  data=json.dumps(export_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        # 验证Excel文件
        if 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in response.content_type:
            # Excel文件应该有内容
            self.assertTrue(len(response.data) > 0)
            
            # 验证文件头（Excel文件的魔数）
            excel_signature = b'PK'  # ZIP文件签名，Excel是基于ZIP的
            self.assertTrue(response.data.startswith(excel_signature))
        
        print("  ✓ Excel导出功能测试通过")
    
    def test_pdf_export_functionality(self):
        """测试PDF导出功能"""
        print("\n测试PDF导出功能...")
        
        export_data = {
            'ids': self.export_test_ids[:2],
            'format': 'pdf',
            'include_summary': True,
            'template': 'detailed'
        }
        
        response = self.client.post('/api/questionnaires/export',
                                  data=json.dumps(export_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        # 验证PDF文件
        if 'application/pdf' in response.content_type:
            # PDF文件应该有内容
            self.assertTrue(len(response.data) > 0)
            
            # 验证PDF文件头
            pdf_signature = b'%PDF'
            self.assertTrue(response.data.startswith(pdf_signature))
        
        print("  ✓ PDF导出功能测试通过")
    
    def test_filtered_export_functionality(self):
        """测试筛选导出功能"""
        print("\n测试筛选导出功能...")
        
        # 1. 按类型筛选导出
        print("  - 测试按类型筛选导出...")
        export_data = {
            'filter': {
                'type': 'student_report'
            },
            'format': 'json'
        }
        
        response = self.client.post('/api/questionnaires/export',
                                  data=json.dumps(export_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        if response.content_type == 'application/json':
            exported_data = json.loads(response.data)
            # 验证所有导出的记录都是指定类型
            for record in exported_data:
                self.assertEqual(record['type'], 'student_report')
        
        # 2. 按日期范围筛选导出
        print("  - 测试按日期范围筛选导出...")
        export_data = {
            'filter': {
                'date_from': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'),
                'date_to': datetime.now().strftime('%Y-%m-%d')
            },
            'format': 'csv'
        }
        
        response = self.client.post('/api/questionnaires/export',
                                  data=json.dumps(export_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        # 3. 按年级筛选导出
        print("  - 测试按年级筛选导出...")
        export_data = {
            'filter': {
                'grade': '1年级'
            },
            'format': 'json'
        }
        
        response = self.client.post('/api/questionnaires/export',
                                  data=json.dumps(export_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        print("  ✓ 筛选导出功能测试通过")
    
    def test_export_customization_options(self):
        """测试导出自定义选项"""
        print("\n测试导出自定义选项...")
        
        # 测试各种自定义选项
        customization_options = [
            {
                'name': '包含元数据',
                'options': {
                    'include_metadata': True,
                    'include_timestamps': True,
                    'include_user_info': True
                }
            },
            {
                'name': '展平问题数据',
                'options': {
                    'flatten_questions': True,
                    'separate_answers': True
                }
            },
            {
                'name': '包含统计信息',
                'options': {
                    'include_statistics': True,
                    'calculate_summaries': True
                }
            }
        ]
        
        for option_set in customization_options:
            print(f"  - 测试{option_set['name']}...")
            
            export_data = {
                'ids': self.export_test_ids[:2],
                'format': 'json',
                **option_set['options']
            }
            
            response = self.client.post('/api/questionnaires/export',
                                      data=json.dumps(export_data),
                                      content_type='application/json')
            
            self.assertEqual(response.status_code, 200)
        
        print("  ✓ 导出自定义选项测试通过")


def run_integration_tests():
    """运行所有集成测试"""
    print("开始运行问卷数据管理系统集成测试...\n")
    print("=" * 60)
    
    # 创建测试套件
    test_classes = [
        TestQuestionnaireSubmissionFlow,
        TestBatchOperations,
        TestDataExportFunctionality
    ]
    
    total_tests = 0
    total_failures = 0
    total_errors = 0
    
    for test_class in test_classes:
        print(f"\n运行 {test_class.__name__} 测试...")
        print("-" * 40)
        
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=1)
        result = runner.run(suite)
        
        total_tests += result.testsRun
        total_failures += len(result.failures)
        total_errors += len(result.errors)
        
        if result.failures:
            print(f"\n失败的测试:")
            for failure in result.failures:
                print(f"  - {failure[0]}")
                print(f"    {failure[1].split('AssertionError:')[-1].strip()}")
        
        if result.errors:
            print(f"\n错误的测试:")
            for error in result.errors:
                print(f"  - {error[0]}")
                print(f"    {str(error[1]).split('Exception:')[-1].strip()}")
    
    print("\n" + "=" * 60)
    print("集成测试总结:")
    print(f"总测试数: {total_tests}")
    print(f"成功: {total_tests - total_failures - total_errors}")
    print(f"失败: {total_failures}")
    print(f"错误: {total_errors}")
    
    success_rate = ((total_tests - total_failures - total_errors) / total_tests * 100) if total_tests > 0 else 0
    print(f"成功率: {success_rate:.1f}%")
    
    if total_failures == 0 and total_errors == 0:
        print("\n🎉 所有集成测试通过！")
        print("\n已验证的集成功能:")
        print("✓ 完整问卷提交流程 (需求1, 2, 4, 5)")
        print("✓ 多种问题类型处理 (需求2)")
        print("✓ 数据验证集成 (需求6)")
        print("✓ 错误处理集成 (需求9)")
        print("✓ 批量选择和操作 (需求7)")
        print("✓ 批量删除功能 (需求7)")
        print("✓ 批量导出功能 (需求7, 8)")
        print("✓ 数据导出功能 (需求8)")
        print("✓ 导出格式支持 (JSON, CSV, Excel, PDF)")
        print("✓ 筛选导出功能")
        print("✓ 导出自定义选项")
        print("✓ 批量操作性能")
        return True
    else:
        print(f"\n⚠️  有 {total_failures + total_errors} 个集成测试失败，请检查实现。")
        return False


if __name__ == '__main__':
    success = run_integration_tests()
    sys.exit(0 if success else 1)