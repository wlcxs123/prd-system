#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小学生报告表提交功能测试脚本
测试完整的数据提交流程，包括基本信息验证、问题回答和数据存储
"""

import requests
import json
import sqlite3
import os
from datetime import datetime, timedelta
import time

# 配置
BASE_URL = "http://127.0.0.1:5002"
DB_PATH = "backend/questionnaires.db"

class ElementaryReportTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
    def log_result(self, test_name, success, message=""):
        """记录测试结果"""
        status = "✅ 通过" if success else "❌ 失败"
        result = f"{status} {test_name}: {message}"
        print(result)
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        
    def test_basic_info_validation(self):
        """测试基本信息验证功能"""
        print("\n=== 测试基本信息验证功能 ===")
        questionnaire_ids = []
        
        # 测试用例1: 完整有效数据（包含新字段）
        valid_data = {
            "type": "小学生报告",
            "basic_info": {
                "name": "张小明",
                "grade": "小学生报告表",
                "submission_date": datetime.now().strftime("%Y-%m-%d"),
                "gender": "男",
                "birth_date": "2015-03-15",
                "parent_phone": "13800138000",
                "parent_wechat": "zhangxiaoming_parent",
                "parent_email": "parent@example.com",
                "school_name": "阳光小学",
                "admission_date": "2021-09-01",
                "address": "北京市朝阳区阳光街123号",
                "filler_name": "张小明妈妈",
                "fill_date": datetime.now().strftime("%Y-%m-%d")
            },
            "questions": [
                {
                    "id": 1,
                    "type": "text_input",
                    "question": "孩子就读过的学校以及就读时间",
                    "answer": "阳光小学，2021年9月至今"
                },
                {
                    "id": 2,
                    "type": "text_input",
                    "question": "目前,你对[N]是否有担忧?担忧什么?",
                    "answer": "孩子在学校比较内向，不太愿意主动发言"
                },
                {
                    "id": 3,
                    "type": "multiple_choice",
                    "question": "一般能力评估",
                    "options": [
                        {"value": 1, "text": "非常低"},
                        {"value": 2, "text": "低于平均"},
                        {"value": 3, "text": "平均"},
                        {"value": 4, "text": "优于平均"},
                        {"value": 5, "text": "非常好"}
                    ],
                    "selected": [3]
                }
            ],
            "statistics": {
                "total_score": 3,
                "completion_rate": 100,
                "submission_time": datetime.now().isoformat()
            }
        }
        
        try:
            response = self.session.post(
                f"{BASE_URL}/api/submit",
                json=valid_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code in [200, 201]:  # 200 OK 或 201 Created
                result = response.json()
                if result.get('success'):
                    questionnaire_id = result.get('id')  # 后端返回的字段名是'id'
                    self.log_result("完整有效数据提交", True, f"提交成功，ID: {questionnaire_id}")
                    if questionnaire_id:
                        questionnaire_ids.append(questionnaire_id)
                else:
                    self.log_result("完整有效数据提交", False, f"提交失败: {result.get('message')}")
            else:
                self.log_result("完整有效数据提交", False, f"HTTP错误: {response.status_code}")
                
        except Exception as e:
            self.log_result("完整有效数据提交", False, f"请求异常: {str(e)}")
            
        return questionnaire_ids
        
    def test_invalid_data_validation(self):
        """测试无效数据验证"""
        print("\n=== 测试无效数据验证 ===")
        
        # 测试用例1: 缺少必填字段
        invalid_data_1 = {
            "type": "小学生报告",
            "basic_info": {
                "grade": "小学生报告表",
                "submission_date": datetime.now().strftime("%Y-%m-%d")
                # 缺少name字段
            },
            "questions": [],
            "statistics": {}
        }
        
        try:
            response = self.session.post(
                f"{BASE_URL}/api/submit",
                json=invalid_data_1,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 400:
                self.log_result("缺少必填字段验证", True, "正确拦截了缺少姓名的数据")
            else:
                self.log_result("缺少必填字段验证", False, f"未正确验证，状态码: {response.status_code}")
                
        except Exception as e:
            self.log_result("缺少必填字段验证", False, f"请求异常: {str(e)}")
            
        # 测试用例2: 无效邮箱格式
        invalid_data_2 = {
            "type": "小学生报告",
            "basic_info": {
                "name": "测试学生",
                "grade": "小学生报告表",
                "submission_date": datetime.now().strftime("%Y-%m-%d"),
                "parent_email": "invalid-email-format"  # 无效邮箱
            },
            "questions": [
                {
                    "id": 1,
                    "type": "text_input",
                    "question": "测试问题",
                    "answer": "测试回答"
                }
            ],
            "statistics": {}
        }
        
        try:
            response = self.session.post(
                f"{BASE_URL}/api/submit",
                json=invalid_data_2,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 400:
                self.log_result("无效邮箱格式验证", True, "正确拦截了无效邮箱格式")
            else:
                self.log_result("无效邮箱格式验证", False, f"未正确验证，状态码: {response.status_code}")
                
        except Exception as e:
            self.log_result("无效邮箱格式验证", False, f"请求异常: {str(e)}")
            
    def test_question_data_processing(self):
        """测试问题数据处理"""
        print("\n=== 测试问题数据处理 ===")
        
        # 测试包含多种题型的数据
        mixed_data = {
            "type": "小学生报告",
            "basic_info": {
                "name": "李小红",
                "grade": "小学生报告表",
                "submission_date": datetime.now().strftime("%Y-%m-%d"),
                "gender": "女",
                "birth_date": "2014-08-20",
                "parent_phone": "13900139000",
                "parent_wechat": "lixiaohong_parent",
                "parent_email": "lixiaohong@example.com",
                "school_name": "希望小学",
                "admission_date": "2020-09-01",
                "address": "上海市浦东新区希望路456号",
                "filler_name": "李小红爸爸",
                "fill_date": datetime.now().strftime("%Y-%m-%d")
            },
            "questions": [
                {
                    "id": 1,
                    "type": "text_input",
                    "question": "孩子就读过的学校以及就读时间",
                    "answer": "希望小学，2020年9月-2023年7月；现在的学校，2023年9月至今"
                },
                {
                    "id": 2,
                    "type": "text_input",
                    "question": "是否有任何关于[N]过去就读学校的记录或报告",
                    "answer": "有期末成绩单和老师评语，整体表现良好"
                },
                {
                    "id": 3,
                    "type": "multiple_choice",
                    "question": "一般能力评估",
                    "options": [
                        {"value": 1, "text": "非常低"},
                        {"value": 2, "text": "低于平均"},
                        {"value": 3, "text": "平均"},
                        {"value": 4, "text": "优于平均"},
                        {"value": 5, "text": "非常好"}
                    ],
                    "selected": [4]
                },
                {
                    "id": 4,
                    "type": "multiple_choice",
                    "question": "成就表现评估",
                    "options": [
                        {"value": 1, "text": "非常低"},
                        {"value": 2, "text": "低于平均"},
                        {"value": 3, "text": "平均"},
                        {"value": 4, "text": "优于平均"},
                        {"value": 5, "text": "非常好"}
                    ],
                    "selected": [3]
                }
            ],
            "statistics": {
                "total_score": 4,
                "completion_rate": 100,
                "submission_time": datetime.now().isoformat()
            }
        }
        
        try:
            response = self.session.post(
                f"{BASE_URL}/api/submit",
                json=mixed_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code in [200, 201]:  # 200 OK 或 201 Created
                result = response.json()
                if result.get('success'):
                    questionnaire_id = result.get('id')  # 后端返回的字段名是'id'
                    self.log_result("混合题型数据处理", True, f"成功处理多种题型，ID: {questionnaire_id}")
                    return questionnaire_id
                else:
                    self.log_result("混合题型数据处理", False, f"处理失败: {result.get('message')}")
            else:
                self.log_result("混合题型数据处理", False, f"HTTP错误: {response.status_code}")
                
        except Exception as e:
            self.log_result("混合题型数据处理", False, f"请求异常: {str(e)}")
            
        return None
        
    def verify_database_storage(self, questionnaire_ids):
        """验证数据库存储"""
        print("\n=== 验证数据库存储 ===")
        
        if not os.path.exists(DB_PATH):
            self.log_result("数据库文件存在性检查", False, f"数据库文件不存在: {DB_PATH}")
            return
            
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # 检查questionnaires表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='questionnaires'")
            if not cursor.fetchone():
                self.log_result("数据库表结构检查", False, "questionnaires表不存在")
                return
                
            self.log_result("数据库表结构检查", True, "questionnaires表存在")
            
            # 验证提交的数据
            for qid in questionnaire_ids:
                if qid:
                    cursor.execute(
                        "SELECT * FROM questionnaires WHERE id = ?", 
                        (qid,)
                    )
                    record = cursor.fetchone()
                    
                    if record:
                        self.log_result(
                            f"数据存储验证 (ID: {qid})", 
                            True, 
                            f"记录已正确存储，类型: {record[1] if len(record) > 1 else 'N/A'}"
                        )
                        
                        # 检查基本信息字段
                        cursor.execute(
                            "SELECT name, grade, submission_date FROM questionnaires WHERE id = ?",
                            (qid,)
                        )
                        basic_info = cursor.fetchone()
                        if basic_info and basic_info[0]:  # name不为空
                            self.log_result(
                                f"基本信息完整性 (ID: {qid})", 
                                True, 
                                f"姓名: {basic_info[0]}, 年级: {basic_info[1]}"
                            )
                        else:
                            self.log_result(
                                f"基本信息完整性 (ID: {qid})", 
                                False, 
                                "基本信息缺失或不完整"
                            )
                    else:
                        self.log_result(
                            f"数据存储验证 (ID: {qid})", 
                            False, 
                            "记录未找到"
                        )
            
            # 统计小学生报告表记录总数
            cursor.execute(
                "SELECT COUNT(*) FROM questionnaires WHERE type = '小学生报告'"
            )
            count = cursor.fetchone()[0]
            self.log_result(
                "小学生报告表记录统计", 
                True, 
                f"数据库中共有 {count} 条小学生报告表记录"
            )
            
            # 验证新字段是否正确存储
            cursor.execute(
                "SELECT school_name, admission_date, address, filler_name, fill_date FROM questionnaires WHERE type = '小学生报告' ORDER BY id DESC LIMIT 1"
            )
            new_fields = cursor.fetchone()
            if new_fields and any(new_fields):
                self.log_result(
                    "新字段存储验证", 
                    True, 
                    f"新字段已正确存储: 学校={new_fields[0]}, 入学日期={new_fields[1]}, 地址={new_fields[2][:20]}..., 填表人={new_fields[3]}, 填表日期={new_fields[4]}"
                )
            else:
                self.log_result(
                    "新字段存储验证", 
                    False, 
                    "新字段未正确存储或为空"
                )
            
            conn.close()
            
        except Exception as e:
            self.log_result("数据库验证", False, f"数据库操作异常: {str(e)}")
            
    def test_server_connectivity(self):
        """测试服务器连接"""
        print("\n=== 测试服务器连接 ===")
        
        try:
            # 尝试访问API端点来测试连接
            response = self.session.options(f"{BASE_URL}/api/submit", timeout=5)
            if response.status_code in [200, 204, 405]:  # OPTIONS请求可能返回405
                self.log_result("服务器连接测试", True, "服务器响应正常")
                return True
            else:
                self.log_result("服务器连接测试", False, f"服务器响应异常: {response.status_code}")
        except Exception as e:
            self.log_result("服务器连接测试", False, f"连接失败: {str(e)}")
            
        return False
    
    def test_admin_display_functionality(self, questionnaire_ids):
        """测试问卷管理系统显示功能"""
        print("\n=== 测试问卷管理系统显示功能 ===")
        
        if not questionnaire_ids:
            self.log_result("管理系统显示测试", False, "没有可用的问卷ID进行测试")
            return
            
        try:
            # 先登录获取管理员权限
            login_response = self.session.post(
                f"{BASE_URL}/api/auth/login",
                json={"username": "admin", "password": "admin123"},
                timeout=10
            )
            
            if login_response.status_code != 200:
                self.log_result("管理员登录", False, f"登录失败，状态码: {login_response.status_code}")
                return
                
            login_result = login_response.json()
            if not login_result.get('success'):
                self.log_result("管理员登录", False, f"登录失败: {login_result.get('message')}")
                return
                
            self.log_result("管理员登录", True, "登录成功")
            
            # 测试获取问卷列表API
            response = self.session.get(
                f"{BASE_URL}/api/questionnaires",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('data'):
                    questionnaires = data['data']
                    # 查找我们提交的问卷
                    test_questionnaire = None
                    for q in questionnaires:
                        if q.get('id') in questionnaire_ids:
                            test_questionnaire = q
                            break
                    
                    if test_questionnaire:
                        # 检查新字段是否在返回的数据中
                        has_new_fields = (
                            test_questionnaire.get('school_name') or
                            test_questionnaire.get('admission_date') or
                            test_questionnaire.get('address') or
                            test_questionnaire.get('filler_name') or
                            test_questionnaire.get('fill_date')
                        )
                        
                        if has_new_fields:
                            self.log_result(
                                "问卷列表API新字段显示", 
                                True, 
                                f"新字段正确显示在API响应中，问卷ID: {test_questionnaire.get('id')}"
                            )
                        else:
                            self.log_result(
                                "问卷列表API新字段显示", 
                                False, 
                                "新字段未在API响应中显示"
                            )
                    else:
                        self.log_result(
                            "问卷列表API测试", 
                            False, 
                            "未找到测试提交的问卷记录"
                        )
                else:
                    self.log_result(
                        "问卷列表API测试", 
                        False, 
                        "API返回数据格式异常"
                    )
            else:
                self.log_result(
                    "问卷列表API测试", 
                    False, 
                    f"API请求失败，状态码: {response.status_code}"
                )
                
        except Exception as e:
            self.log_result("管理系统显示测试", False, f"测试异常: {str(e)}")
        
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始小学生报告表提交功能测试")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"测试目标: {BASE_URL}")
        
        # 检查服务器连接
        if not self.test_server_connectivity():
            print("\n❌ 服务器连接失败，无法继续测试")
            return
            
        questionnaire_ids = []
        
        # 运行各项测试
        valid_ids = self.test_basic_info_validation()
        if valid_ids:
            questionnaire_ids.extend(valid_ids)
            
        self.test_invalid_data_validation()
        
        qid2 = self.test_question_data_processing()
        if qid2:
            questionnaire_ids.append(qid2)
            
        # 验证数据库存储
        self.verify_database_storage(questionnaire_ids)
        
        # 测试问卷管理系统显示功能
        self.test_admin_display_functionality(questionnaire_ids)
        
        # 输出测试总结
        self.print_test_summary()
        
    def print_test_summary(self):
        """打印测试总结"""
        print("\n" + "="*60)
        print("📊 测试结果总结")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests} ✅")
        print(f"失败: {failed_tests} ❌")
        print(f"成功率: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n❌ 失败的测试:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
        else:
            print("\n🎉 所有测试都通过了！")
            
        print("\n" + "="*60)

def main():
    """主函数"""
    tester = ElementaryReportTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()