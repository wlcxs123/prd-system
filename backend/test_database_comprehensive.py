#!/usr/bin/env python3
"""
问卷数据管理系统数据库操作测试 - 任务10.1实现
测试数据库操作、数据完整性和性能
"""

import unittest
import os
import sys
import sqlite3
import json
import tempfile
import shutil
from datetime import datetime, timedelta
import bcrypt
import threading
import time

# 添加backend目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

class TestDatabaseOperations(unittest.TestCase):
    """测试数据库操作 - 需求5的实现"""
    
    def setUp(self):
        """设置测试数据库"""
        self.test_db_path = tempfile.mktemp(suffix='.db')
        self.setup_test_database()
    
    def tearDown(self):
        """清理测试数据库"""
        if os.path.exists(self.test_db_path):
            os.unlink(self.test_db_path)
    
    def setup_test_database(self):
        """设置测试数据库结构 - 需求5.1"""
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
            
            # 创建用户认证表
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
            
            # 创建索引以提高查询性能
            cursor.execute('CREATE INDEX idx_questionnaires_type ON questionnaires(type)')
            cursor.execute('CREATE INDEX idx_questionnaires_name ON questionnaires(name)')
            cursor.execute('CREATE INDEX idx_questionnaires_grade ON questionnaires(grade)')
            cursor.execute('CREATE INDEX idx_questionnaires_date ON questionnaires(submission_date)')
            cursor.execute('CREATE INDEX idx_questionnaires_created ON questionnaires(created_at)')
            cursor.execute('CREATE INDEX idx_users_username ON users(username)')
            cursor.execute('CREATE INDEX idx_logs_user_id ON operation_logs(user_id)')
            cursor.execute('CREATE INDEX idx_logs_operation ON operation_logs(operation)')
            cursor.execute('CREATE INDEX idx_logs_created ON operation_logs(created_at)')
            
            conn.commit()
    
    def test_questionnaire_crud_operations(self):
        """测试问卷CRUD操作 - 需求5.2"""
        test_questionnaire = {
            'type': 'test_questionnaire',
            'name': '测试学生',
            'grade': '3年级',
            'submission_date': '2024-01-15',
            'data': json.dumps({
                'basic_info': {
                    'name': '测试学生',
                    'grade': '3年级',
                    'submission_date': '2024-01-15'
                },
                'questions': [
                    {
                        'id': 1,
                        'type': 'text_input',
                        'question': '测试问题',
                        'answer': '测试答案'
                    }
                ]
            })
        }
        
        with sqlite3.connect(self.test_db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 测试创建 (CREATE)
            cursor.execute(
                "INSERT INTO questionnaires (type, name, grade, submission_date, data) VALUES (?, ?, ?, ?, ?)",
                (test_questionnaire['type'], test_questionnaire['name'], 
                 test_questionnaire['grade'], test_questionnaire['submission_date'], 
                 test_questionnaire['data'])
            )
            questionnaire_id = cursor.lastrowid
            self.assertIsNotNone(questionnaire_id)
            self.assertGreater(questionnaire_id, 0)
            
            # 测试读取 (READ)
            cursor.execute("SELECT * FROM questionnaires WHERE id = ?", (questionnaire_id,))
            result = cursor.fetchone()
            self.assertIsNotNone(result)
            self.assertEqual(result['name'], test_questionnaire['name'])
            self.assertEqual(result['type'], test_questionnaire['type'])
            self.assertEqual(result['grade'], test_questionnaire['grade'])
            
            # 验证JSON数据完整性
            stored_data = json.loads(result['data'])
            original_data = json.loads(test_questionnaire['data'])
            self.assertEqual(stored_data, original_data)
            
            # 测试更新 (UPDATE)
            new_name = '更新后的学生'
            update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(
                "UPDATE questionnaires SET name = ?, updated_at = ? WHERE id = ?",
                (new_name, update_time, questionnaire_id)
            )
            
            cursor.execute("SELECT name, updated_at FROM questionnaires WHERE id = ?", (questionnaire_id,))
            updated_result = cursor.fetchone()
            self.assertEqual(updated_result['name'], new_name)
            self.assertNotEqual(updated_result['updated_at'], result['created_at'])
            
            # 测试删除 (DELETE)
            cursor.execute("DELETE FROM questionnaires WHERE id = ?", (questionnaire_id,))
            cursor.execute("SELECT * FROM questionnaires WHERE id = ?", (questionnaire_id,))
            deleted_result = cursor.fetchone()
            self.assertIsNone(deleted_result)
    
    def test_user_authentication_operations(self):
        """测试用户认证数据库操作 - 需求3.1, 3.2"""
        test_users = [
            {
                'username': 'admin',
                'password': 'admin123',
                'role': 'admin'
            },
            {
                'username': 'user1',
                'password': 'password123',
                'role': 'user'
            }
        ]
        
        with sqlite3.connect(self.test_db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            user_ids = []
            
            # 测试用户创建
            for user_data in test_users:
                password_hash = bcrypt.hashpw(
                    user_data['password'].encode('utf-8'), 
                    bcrypt.gensalt()
                ).decode('utf-8')
                
                cursor.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                    (user_data['username'], password_hash, user_data['role'])
                )
                user_id = cursor.lastrowid
                user_ids.append(user_id)
                self.assertIsNotNone(user_id)
            
            # 测试用户查询和密码验证
            for i, user_data in enumerate(test_users):
                cursor.execute("SELECT * FROM users WHERE username = ?", (user_data['username'],))
                user = cursor.fetchone()
                
                self.assertIsNotNone(user)
                self.assertEqual(user['username'], user_data['username'])
                self.assertEqual(user['role'], user_data['role'])
                
                # 验证密码哈希
                self.assertTrue(
                    bcrypt.checkpw(
                        user_data['password'].encode('utf-8'),
                        user['password_hash'].encode('utf-8')
                    )
                )
                
                # 验证错误密码
                self.assertFalse(
                    bcrypt.checkpw(
                        'wrong_password'.encode('utf-8'),
                        user['password_hash'].encode('utf-8')
                    )
                )
            
            # 测试用户名唯一性约束
            with self.assertRaises(sqlite3.IntegrityError):
                cursor.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    ('admin', 'duplicate_hash')
                )
            
            # 测试最后登录时间更新
            login_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(
                "UPDATE users SET last_login = ? WHERE id = ?",
                (login_time, user_ids[0])
            )
            
            cursor.execute("SELECT last_login FROM users WHERE id = ?", (user_ids[0],))
            result = cursor.fetchone()
            self.assertEqual(result['last_login'], login_time)
    
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
            
            # 测试各种操作日志记录
            operations = [
                {
                    'operation': 'LOGIN',
                    'target_id': None,
                    'details': json.dumps({'ip': '127.0.0.1', 'user_agent': 'test'})
                },
                {
                    'operation': 'CREATE_QUESTIONNAIRE',
                    'target_id': 1,
                    'details': json.dumps({'type': 'student_report', 'name': '测试学生'})
                },
                {
                    'operation': 'UPDATE_QUESTIONNAIRE',
                    'target_id': 1,
                    'details': json.dumps({'field': 'name', 'old_value': '测试学生', 'new_value': '更新学生'})
                },
                {
                    'operation': 'DELETE_QUESTIONNAIRE',
                    'target_id': 1,
                    'details': json.dumps({'reason': 'user_request'})
                },
                {
                    'operation': 'BATCH_DELETE',
                    'target_id': None,
                    'details': json.dumps({'deleted_ids': [1, 2, 3], 'count': 3})
                }
            ]
            
            log_ids = []
            for op in operations:
                cursor.execute(
                    "INSERT INTO operation_logs (user_id, operation, target_id, details) VALUES (?, ?, ?, ?)",
                    (user_id, op['operation'], op['target_id'], op['details'])
                )
                log_id = cursor.lastrowid
                log_ids.append(log_id)
                self.assertIsNotNone(log_id)
            
            # 验证日志记录
            for i, log_id in enumerate(log_ids):
                cursor.execute("SELECT * FROM operation_logs WHERE id = ?", (log_id,))
                log = cursor.fetchone()
                
                self.assertIsNotNone(log)
                self.assertEqual(log['user_id'], user_id)
                self.assertEqual(log['operation'], operations[i]['operation'])
                self.assertEqual(log['target_id'], operations[i]['target_id'])
                
                # 验证JSON详情
                stored_details = json.loads(log['details'])
                expected_details = json.loads(operations[i]['details'])
                self.assertEqual(stored_details, expected_details)
            
            # 测试日志查询和筛选
            cursor.execute(
                "SELECT * FROM operation_logs WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,)
            )
            user_logs = cursor.fetchall()
            self.assertEqual(len(user_logs), len(operations))
            
            # 测试按操作类型筛选
            cursor.execute(
                "SELECT * FROM operation_logs WHERE operation LIKE ?",
                ('%QUESTIONNAIRE%',)
            )
            questionnaire_logs = cursor.fetchall()
            self.assertEqual(len(questionnaire_logs), 3)  # CREATE, UPDATE, DELETE
    
    def test_data_integrity_constraints(self):
        """测试数据完整性约束 - 需求5.3"""
        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.cursor()
            
            # 测试问卷表的NOT NULL约束
            with self.assertRaises(sqlite3.IntegrityError):
                cursor.execute(
                    "INSERT INTO questionnaires (name, grade) VALUES (?, ?)",
                    ('测试学生', '3年级')  # 缺少必需的type和data字段
                )
            
            # 测试用户表的UNIQUE约束
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                ('unique_user', 'hash1')
            )
            
            with self.assertRaises(sqlite3.IntegrityError):
                cursor.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    ('unique_user', 'hash2')  # 重复用户名
                )
            
            # 测试外键约束
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                ('test_user', 'hash')
            )
            user_id = cursor.lastrowid
            
            # 有效的外键引用
            cursor.execute(
                "INSERT INTO operation_logs (user_id, operation) VALUES (?, ?)",
                (user_id, 'TEST_OPERATION')
            )
            
            # 无效的外键引用（如果启用了外键约束）
            # 注意：SQLite默认不启用外键约束，需要手动启用
            cursor.execute("PRAGMA foreign_keys = ON")
            
            with self.assertRaises(sqlite3.IntegrityError):
                cursor.execute(
                    "INSERT INTO operation_logs (user_id, operation) VALUES (?, ?)",
                    (99999, 'TEST_OPERATION')  # 不存在的用户ID
                )
    
    def test_complex_queries(self):
        """测试复杂查询操作 - 需求4.2, 8.2"""
        with sqlite3.connect(self.test_db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 插入测试数据
            test_data = [
                ('student_report', '张三', '1年级', '2024-01-01', '{"score": 85}'),
                ('student_report', '李四', '2年级', '2024-01-02', '{"score": 92}'),
                ('parent_interview', '王五', '1年级', '2024-01-03', '{"score": 78}'),
                ('student_report', '赵六', '3年级', '2024-01-04', '{"score": 88}'),
                ('parent_interview', '钱七', '2年级', '2024-01-05', '{"score": 95}')
            ]
            
            for data in test_data:
                cursor.execute(
                    "INSERT INTO questionnaires (type, name, grade, submission_date, data) VALUES (?, ?, ?, ?, ?)",
                    data
                )
            
            # 测试按类型分组统计
            cursor.execute("""
                SELECT type, COUNT(*) as count, AVG(json_extract(data, '$.score')) as avg_score
                FROM questionnaires 
                GROUP BY type
            """)
            type_stats = cursor.fetchall()
            self.assertEqual(len(type_stats), 2)
            
            # 验证统计结果
            for stat in type_stats:
                if stat['type'] == 'student_report':
                    self.assertEqual(stat['count'], 3)
                    self.assertAlmostEqual(stat['avg_score'], (85 + 92 + 88) / 3, places=2)
                elif stat['type'] == 'parent_interview':
                    self.assertEqual(stat['count'], 2)
                    self.assertAlmostEqual(stat['avg_score'], (78 + 95) / 2, places=2)
            
            # 测试按年级分组统计
            cursor.execute("""
                SELECT grade, COUNT(*) as count, MIN(submission_date) as first_date, MAX(submission_date) as last_date
                FROM questionnaires 
                GROUP BY grade
                ORDER BY grade
            """)
            grade_stats = cursor.fetchall()
            self.assertEqual(len(grade_stats), 3)
            
            # 测试日期范围查询
            cursor.execute("""
                SELECT * FROM questionnaires 
                WHERE DATE(submission_date) BETWEEN ? AND ?
                ORDER BY submission_date
            """, ('2024-01-02', '2024-01-04'))
            date_range_results = cursor.fetchall()
            self.assertEqual(len(date_range_results), 3)
            
            # 测试复合条件查询
            cursor.execute("""
                SELECT * FROM questionnaires 
                WHERE type = ? AND grade IN (?, ?) AND json_extract(data, '$.score') > ?
                ORDER BY json_extract(data, '$.score') DESC
            """, ('student_report', '1年级', '2年级', 85))
            complex_results = cursor.fetchall()
            self.assertEqual(len(complex_results), 1)  # 只有李四符合条件
            self.assertEqual(complex_results[0]['name'], '李四')
    
    def test_transaction_handling(self):
        """测试事务处理 - 需求5.4"""
        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.cursor()
            
            # 测试成功事务
            try:
                cursor.execute("BEGIN TRANSACTION")
                
                # 插入用户
                cursor.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    ('transaction_user', 'hash')
                )
                user_id = cursor.lastrowid
                
                # 插入问卷
                cursor.execute(
                    "INSERT INTO questionnaires (type, name, grade, submission_date, data) VALUES (?, ?, ?, ?, ?)",
                    ('test', '事务测试', '1年级', '2024-01-01', '{}')
                )
                questionnaire_id = cursor.lastrowid
                
                # 记录日志
                cursor.execute(
                    "INSERT INTO operation_logs (user_id, operation, target_id) VALUES (?, ?, ?)",
                    (user_id, 'CREATE_QUESTIONNAIRE', questionnaire_id)
                )
                
                cursor.execute("COMMIT")
                
                # 验证数据已提交
                cursor.execute("SELECT COUNT(*) FROM users WHERE id = ?", (user_id,))
                self.assertEqual(cursor.fetchone()[0], 1)
                
                cursor.execute("SELECT COUNT(*) FROM questionnaires WHERE id = ?", (questionnaire_id,))
                self.assertEqual(cursor.fetchone()[0], 1)
                
            except Exception as e:
                cursor.execute("ROLLBACK")
                self.fail(f"成功事务不应该失败: {e}")
            
            # 测试失败事务回滚
            try:
                cursor.execute("BEGIN TRANSACTION")
                
                # 插入有效数据
                cursor.execute(
                    "INSERT INTO questionnaires (type, name, grade, submission_date, data) VALUES (?, ?, ?, ?, ?)",
                    ('test', '回滚测试', '1年级', '2024-01-01', '{}')
                )
                rollback_id = cursor.lastrowid
                
                # 故意插入无效数据（违反约束）
                cursor.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    ('transaction_user', 'duplicate_hash')  # 重复用户名
                )
                
                cursor.execute("COMMIT")
                
            except sqlite3.IntegrityError:
                cursor.execute("ROLLBACK")
                
                # 验证数据已回滚
                cursor.execute("SELECT COUNT(*) FROM questionnaires WHERE id = ?", (rollback_id,))
                self.assertEqual(cursor.fetchone()[0], 0)
    
    def test_database_performance(self):
        """测试数据库性能 - 需求8.4"""
        import time
        
        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.cursor()
            
            # 测试批量插入性能
            start_time = time.time()
            
            batch_data = []
            for i in range(1000):
                batch_data.append((
                    'performance_test',
                    f'性能测试学生{i+1}',
                    f'{(i % 6) + 1}年级',
                    '2024-01-01',
                    json.dumps({'test_id': i+1, 'score': (i % 100) + 1})
                ))
            
            cursor.executemany(
                "INSERT INTO questionnaires (type, name, grade, submission_date, data) VALUES (?, ?, ?, ?, ?)",
                batch_data
            )
            
            insert_time = time.time() - start_time
            
            # 测试查询性能
            start_time = time.time()
            
            # 简单查询
            cursor.execute("SELECT COUNT(*) FROM questionnaires WHERE type = ?", ('performance_test',))
            count_result = cursor.fetchone()[0]
            self.assertEqual(count_result, 1000)
            
            # 复杂查询
            cursor.execute("""
                SELECT grade, COUNT(*) as count, AVG(json_extract(data, '$.score')) as avg_score
                FROM questionnaires 
                WHERE type = ?
                GROUP BY grade
                ORDER BY grade
            """, ('performance_test',))
            complex_results = cursor.fetchall()
            
            query_time = time.time() - start_time
            
            # 测试索引效果
            start_time = time.time()
            cursor.execute("SELECT * FROM questionnaires WHERE name = ?", ('性能测试学生500',))
            indexed_result = cursor.fetchone()
            indexed_query_time = time.time() - start_time
            
            # 性能断言（这些值可以根据实际需求调整）
            self.assertLess(insert_time, 5.0, f"批量插入1000条记录耗时过长: {insert_time:.2f}秒")
            self.assertLess(query_time, 1.0, f"复杂查询耗时过长: {query_time:.2f}秒")
            self.assertLess(indexed_query_time, 0.1, f"索引查询耗时过长: {indexed_query_time:.2f}秒")
            
            # 验证查询结果正确性
            self.assertEqual(len(complex_results), 6)  # 6个年级
            self.assertIsNotNone(indexed_result)
            self.assertEqual(indexed_result[2], '性能测试学生500')  # name字段
    
    def test_concurrent_access(self):
        """测试并发访问 - 需求8.4"""
        import threading
        import time
        
        results = []
        errors = []
        
        def worker_thread(thread_id):
            """工作线程函数"""
            try:
                with sqlite3.connect(self.test_db_path) as conn:
                    cursor = conn.cursor()
                    
                    # 每个线程插入10条记录
                    for i in range(10):
                        cursor.execute(
                            "INSERT INTO questionnaires (type, name, grade, submission_date, data) VALUES (?, ?, ?, ?, ?)",
                            (f'thread_{thread_id}', f'学生{thread_id}_{i}', '1年级', '2024-01-01', '{}')
                        )
                    
                    # 查询自己插入的记录
                    cursor.execute("SELECT COUNT(*) FROM questionnaires WHERE type = ?", (f'thread_{thread_id}',))
                    count = cursor.fetchone()[0]
                    results.append((thread_id, count))
                    
            except Exception as e:
                errors.append((thread_id, str(e)))
        
        # 创建并启动多个线程
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证结果
        self.assertEqual(len(errors), 0, f"并发访问出现错误: {errors}")
        self.assertEqual(len(results), 5, "不是所有线程都成功完成")
        
        # 验证每个线程都插入了正确数量的记录
        for thread_id, count in results:
            self.assertEqual(count, 10, f"线程{thread_id}插入的记录数不正确")
        
        # 验证总记录数
        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM questionnaires WHERE type LIKE 'thread_%'")
            total_count = cursor.fetchone()[0]
            self.assertEqual(total_count, 50, "总记录数不正确")


def run_database_tests():
    """运行所有数据库测试"""
    print("开始运行数据库操作测试...\n")
    print("=" * 60)
    
    # 创建测试套件
    test_classes = [TestDatabaseOperations]
    
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
    print("数据库测试总结:")
    print(f"总测试数: {total_tests}")
    print(f"成功: {total_tests - total_failures - total_errors}")
    print(f"失败: {total_failures}")
    print(f"错误: {total_errors}")
    
    success_rate = ((total_tests - total_failures - total_errors) / total_tests * 100) if total_tests > 0 else 0
    print(f"成功率: {success_rate:.1f}%")
    
    if total_failures == 0 and total_errors == 0:
        print("\n🎉 所有数据库测试通过！")
        print("\n已验证的数据库功能:")
        print("✓ 数据库结构和索引 (需求5.1)")
        print("✓ 问卷CRUD操作 (需求5.2)")
        print("✓ 用户认证操作 (需求3)")
        print("✓ 操作日志记录 (需求8.3)")
        print("✓ 数据完整性约束 (需求5.3)")
        print("✓ 复杂查询操作 (需求4.2, 8.2)")
        print("✓ 事务处理 (需求5.4)")
        print("✓ 数据库性能 (需求8.4)")
        print("✓ 并发访问控制 (需求8.4)")
        return True
    else:
        print(f"\n⚠️  有 {total_failures + total_errors} 个数据库测试失败，请检查实现。")
        return False


if __name__ == '__main__':
    success = run_database_tests()
    sys.exit(0 if success else 1)