#!/usr/bin/env python3
"""
问卷数据管理系统API接口测试 - 任务10.1实现
测试所有API接口的功能和错误处理
"""

import unittest
import os
import sys
import json
import tempfile
import sqlite3
from unittest.mock import patch, MagicMock
from datetime import datetime

# 添加backend目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

# 导入Flask应用
from app import app, init_db, get_db
from config import config

class TestAPIInterfaces(unittest.TestCase):
    """测试API接口 - 需求4, 9的实现"""
    
    def setUp(self):
        """设置测试环境"""
        # 配置测试环境
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
        # 删除测试数据库
        if os.path.exists(app.config['DATABASE_PATH']):
            os.unlink(app.config['DATABASE_PATH'])
        
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
    
    def test_authentication_apis(self):
        """测试认证API - 需求3.1, 3.2"""
        # 测试登录API
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        response = self.client.post('/api/auth/login',
                                  data=json.dumps(login_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('user', data)
        
        # 测试错误登录
        wrong_login = {
            'username': 'admin',
            'password': 'wrong_password'
        }
        response = self.client.post('/api/auth/login',
                                  data=json.dumps(wrong_login),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        
        # 测试登录状态检查
        response = self.client.get('/api/auth/status')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['authenticated'])
        
        # 测试登出
        response = self.client.post('/api/auth/logout')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
    
    def test_questionnaire_crud_apis(self):
        """测试问卷CRUD API - 需求4.2, 4.3, 4.4"""
        # 测试数据
        questionnaire_data = {
            'type': 'test_questionnaire',
            'basic_info': {
                'name': '测试学生',
                'grade': '3年级',
                'submission_date': '2024-01-15'
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
                    'question': '你的爱好是什么？',
                    'answer': '读书'
                }
            ]
        }
        
        # 测试创建问卷 (POST /api/questionnaires)
        response = self.client.post('/api/questionnaires',
                                  data=json.dumps(questionnaire_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        questionnaire_id = data['id']
        
        # 测试获取问卷列表 (GET /api/questionnaires)
        response = self.client.get('/api/questionnaires')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertIn('pagination', data)
        
        # 测试获取单个问卷 (GET /api/questionnaires/{id})
        response = self.client.get(f'/api/questionnaires/{questionnaire_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['name'], '测试学生')
        
        # 测试更新问卷 (PUT /api/questionnaires/{id})
        updated_data = questionnaire_data.copy()
        updated_data['basic_info']['name'] = '更新后的学生'
        
        response = self.client.put(f'/api/questionnaires/{questionnaire_id}',
                                 data=json.dumps(updated_data),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        
        # 验证更新
        response = self.client.get(f'/api/questionnaires/{questionnaire_id}')
        data = json.loads(response.data)
        self.assertEqual(data['data']['name'], '更新后的学生')
        
        # 测试删除问卷 (DELETE /api/questionnaires/{id})
        response = self.client.delete(f'/api/questionnaires/{questionnaire_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        
        # 验证删除
        response = self.client.get(f'/api/questionnaires/{questionnaire_id}')
        self.assertEqual(response.status_code, 404)
    
    def test_batch_operations_apis(self):
        """测试批量操作API - 需求7.3, 7.4"""
        # 创建测试数据
        questionnaire_ids = []
        for i in range(3):
            questionnaire_data = {
                'type': 'test_questionnaire',
                'basic_info': {
                    'name': f'测试学生{i+1}',
                    'grade': '3年级',
                    'submission_date': '2024-01-15'
                },
                'questions': [
                    {
                        'id': 1,
                        'type': 'text_input',
                        'question': '测试问题',
                        'answer': f'测试答案{i+1}'
                    }
                ]
            }
            
            response = self.client.post('/api/questionnaires',
                                      data=json.dumps(questionnaire_data),
                                      content_type='application/json')
            
            self.assertEqual(response.status_code, 201)
            data = json.loads(response.data)
            questionnaire_ids.append(data['id'])
        
        # 测试批量导出
        export_data = {
            'ids': questionnaire_ids,
            'format': 'json'
        }
        response = self.client.post('/api/questionnaires/export',
                                  data=json.dumps(export_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        # 测试批量删除
        delete_data = {
            'ids': questionnaire_ids[1:]  # 删除后两个
        }
        response = self.client.delete('/api/questionnaires/batch',
                                    data=json.dumps(delete_data),
                                    content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted_count'], 2)
    
    def test_admin_apis(self):
        """测试管理API - 需求8.1, 8.3"""
        # 测试统计数据API
        response = self.client.get('/api/admin/statistics')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        
        # 测试操作日志API
        response = self.client.get('/api/admin/logs')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
    
    def test_search_and_pagination_apis(self):
        """测试搜索和分页API - 需求4.2"""
        # 创建测试数据
        for i in range(5):
            questionnaire_data = {
                'type': 'test_questionnaire',
                'basic_info': {
                    'name': f'学生{i+1}',
                    'grade': f'{(i % 3) + 1}年级',
                    'submission_date': '2024-01-15'
                },
                'questions': [
                    {
                        'id': 1,
                        'type': 'text_input',
                        'question': '测试问题',
                        'answer': f'答案{i+1}'
                    }
                ]
            }
            
            response = self.client.post('/api/questionnaires',
                                      data=json.dumps(questionnaire_data),
                                      content_type='application/json')
            self.assertEqual(response.status_code, 201)
        
        # 测试分页
        response = self.client.get('/api/questionnaires?page=1&limit=3')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['data']), 3)
        self.assertIn('pagination', data)
        
        # 测试搜索
        response = self.client.get('/api/questionnaires?search=学生1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        # 应该找到包含"学生1"的记录
        
        # 测试筛选
        response = self.client.get('/api/questionnaires?grade=1年级')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
    
    def test_data_validation_in_apis(self):
        """测试API中的数据验证 - 需求1.1, 1.2, 6.1"""
        # 测试无效数据提交
        invalid_data = {
            'type': '',  # 空类型
            'basic_info': {
                'name': '',  # 空姓名
                'grade': '',  # 空年级
                'submission_date': 'invalid-date'  # 无效日期
            },
            'questions': []  # 空问题列表
        }
        
        response = self.client.post('/api/questionnaires',
                                  data=json.dumps(invalid_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error']['code'], 'VALIDATION_ERROR')
        self.assertIn('details', data['error'])
    
    def test_error_handling_in_apis(self):
        """测试API错误处理 - 需求9.4, 9.5"""
        # 测试404错误
        response = self.client.get('/api/questionnaires/99999')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error']['code'], 'NOT_FOUND')
        
        # 测试无效JSON
        response = self.client.post('/api/questionnaires',
                                  data='invalid json',
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    def test_authentication_required_apis(self):
        """测试需要认证的API - 需求3.4, 3.5"""
        # 先登出
        self.client.post('/api/auth/logout')
        
        # 测试未登录访问需要认证的API
        response = self.client.get('/api/questionnaires')
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error']['code'], 'AUTH_REQUIRED')
        
        # 测试未登录访问管理API
        response = self.client.get('/api/admin/statistics')
        self.assertEqual(response.status_code, 401)
    
    def test_api_response_format(self):
        """测试API响应格式标准化 - 需求9.1, 9.2"""
        # 测试成功响应格式
        response = self.client.get('/api/auth/status')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # 检查标准字段
        self.assertIn('success', data)
        self.assertIn('timestamp', data)
        
        # 测试错误响应格式
        response = self.client.get('/api/questionnaires/99999')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        
        # 检查错误响应标准字段
        self.assertIn('success', data)
        self.assertIn('error', data)
        self.assertIn('timestamp', data)
        self.assertIn('code', data['error'])
        self.assertIn('message', data['error'])


class TestAPIPerformance(unittest.TestCase):
    """测试API性能 - 需求8.4"""
    
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
    
    def tearDown(self):
        """清理测试环境"""
        if os.path.exists(app.config['DATABASE_PATH']):
            os.unlink(app.config['DATABASE_PATH'])
        self.app_context.pop()
    
    def login(self):
        """登录"""
        login_data = {'username': 'admin', 'password': 'admin123'}
        self.client.post('/api/auth/login', 
                        data=json.dumps(login_data),
                        content_type='application/json')
    
    def test_bulk_data_handling(self):
        """测试批量数据处理性能"""
        import time
        
        # 创建大量测试数据
        start_time = time.time()
        
        questionnaire_ids = []
        for i in range(50):  # 创建50条记录
            questionnaire_data = {
                'type': 'performance_test',
                'basic_info': {
                    'name': f'性能测试学生{i+1}',
                    'grade': f'{(i % 6) + 1}年级',
                    'submission_date': '2024-01-15'
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
                questionnaire_ids.append(data['id'])
        
        creation_time = time.time() - start_time
        
        # 测试批量查询性能
        start_time = time.time()
        response = self.client.get('/api/questionnaires?limit=50')
        query_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        
        # 测试批量删除性能
        start_time = time.time()
        delete_data = {'ids': questionnaire_ids}
        response = self.client.delete('/api/questionnaires/batch',
                                    data=json.dumps(delete_data),
                                    content_type='application/json')
        delete_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        
        # 性能断言（这些值可以根据实际需求调整）
        self.assertLess(creation_time, 30.0, "批量创建耗时过长")
        self.assertLess(query_time, 5.0, "批量查询耗时过长")
        self.assertLess(delete_time, 10.0, "批量删除耗时过长")


def run_api_tests():
    """运行所有API测试"""
    print("开始运行API接口测试...\n")
    print("=" * 60)
    
    # 创建测试套件
    test_classes = [
        TestAPIInterfaces,
        TestAPIPerformance
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
                print(f"  - {failure[0]}")
        
        if result.errors:
            print(f"\n错误的测试:")
            for error in result.errors:
                print(f"  - {error[0]}")
    
    print("\n" + "=" * 60)
    print("API测试总结:")
    print(f"总测试数: {total_tests}")
    print(f"成功: {total_tests - total_failures - total_errors}")
    print(f"失败: {total_failures}")
    print(f"错误: {total_errors}")
    
    success_rate = ((total_tests - total_failures - total_errors) / total_tests * 100) if total_tests > 0 else 0
    print(f"成功率: {success_rate:.1f}%")
    
    if total_failures == 0 and total_errors == 0:
        print("\n🎉 所有API测试通过！")
        print("\n已验证的API功能:")
        print("✓ 用户认证API (需求3)")
        print("✓ 问卷CRUD API (需求4)")
        print("✓ 批量操作API (需求7)")
        print("✓ 管理功能API (需求8)")
        print("✓ 搜索分页API (需求4)")
        print("✓ 数据验证API (需求1, 6)")
        print("✓ 错误处理API (需求9)")
        print("✓ API性能测试 (需求8)")
        return True
    else:
        print(f"\n⚠️  有 {total_failures + total_errors} 个API测试失败，请检查实现。")
        return False


if __name__ == '__main__':
    success = run_api_tests()
    sys.exit(0 if success else 1)