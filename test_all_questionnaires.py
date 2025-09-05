#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合问卷测试脚本
模拟正常用户填写所有问卷表单，检查服务器是否能收到结果
"""

import requests
import json
import time
import random
from datetime import datetime, date
from typing import Dict, List, Any

# 服务器配置
BASE_URL = "http://127.0.0.1:5000"
API_ENDPOINT = f"{BASE_URL}/api/submit"

class QuestionnaireTestSuite:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # 基础信息模板
        self.basic_info_template = {
            'name': '测试学生',
            'birthdate': '2015-03-15',
            'gender': '男',
            'grade': '小学三年级',
            'submission_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        self.test_results = []
    
    def log_result(self, questionnaire_type: str, success: bool, message: str, record_id: str = None):
        """记录测试结果"""
        result = {
            'questionnaire_type': questionnaire_type,
            'success': success,
            'message': message,
            'record_id': record_id,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ 成功" if success else "❌ 失败"
        print(f"{status} - {questionnaire_type}: {message}")
        if record_id:
            print(f"   记录ID: {record_id}")
    
    def test_server_connection(self) -> bool:
        """测试服务器连接"""
        try:
            response = self.session.get(f"{BASE_URL}/")
            if response.status_code == 200:
                self.log_result("服务器连接", True, "服务器正常运行")
                return True
            else:
                self.log_result("服务器连接", False, f"服务器响应异常: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("服务器连接", False, f"无法连接到服务器: {str(e)}")
            return False
    
    def submit_questionnaire(self, data: Dict[str, Any]) -> tuple:
        """提交问卷数据"""
        try:
            print(f"   提交数据: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
            response = self.session.post(API_ENDPOINT, json=data, timeout=30)
            
            print(f"   响应状态码: {response.status_code}")
            print(f"   响应内容: {response.text[:500]}...")
            
            if response.status_code == 201:  # 创建成功应该是201
                result = response.json()
                if result.get('success'):
                    return True, result.get('id') or result.get('record_id'), "提交成功"
                else:
                    error_msg = result.get('error', {}).get('message', '未知错误')
                    return False, None, f"服务器返回错误: {error_msg}"
            elif response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return True, result.get('id') or result.get('record_id'), "提交成功"
                else:
                    error_msg = result.get('error', {}).get('message', '未知错误')
                    return False, None, f"服务器返回错误: {error_msg}"
            else:
                try:
                    error_data = response.json()
                    if isinstance(error_data, list) and len(error_data) >= 2:
                        # 处理Flask返回的错误格式 (error_dict, status_code)
                        error_dict = error_data[0]
                        if 'error' in error_dict:
                            error_details = error_dict['error'].get('details', [])
                            error_msg = f"验证失败: {'; '.join(error_details)}"
                        else:
                            error_msg = error_dict.get('message', f"HTTP {response.status_code}")
                    elif isinstance(error_data, dict):
                        if 'error' in error_data:
                            error_details = error_data['error'].get('details', [])
                            error_msg = f"验证失败: {'; '.join(error_details)}"
                        else:
                            error_msg = error_data.get('message', f"HTTP {response.status_code}")
                    else:
                        error_msg = f"HTTP {response.status_code}: 未知错误格式"
                except:
                    error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                return False, None, error_msg
                
        except requests.exceptions.Timeout:
            return False, None, "请求超时"
        except requests.exceptions.ConnectionError:
            return False, None, "连接错误"
        except Exception as e:
            return False, None, f"提交异常: {str(e)}"
    
    def test_primary_communication_scale(self):
        """测试小学生交流评定表"""
        print("\n🔍 测试小学生交流评定表...")
        
        # 构建测试数据
        questions = []
        for i in range(1, 21):  # 20个问题
            questions.append({
                'id': i,
                'type': 'rating_scale',
                'question': f'问题{i}',
                'rating': random.randint(0, 4),
                'can_speak': random.choice([True, False])
            })
        
        data = {
            'type': 'primary_communication_scale',
            'basic_info': {
                'name': '张小明',
                'grade': '小学三年级',
                'submission_date': self.basic_info_template['submission_date']
            },
            'questions': questions,
            'statistics': {
                'total_score': sum(q['rating'] for q in questions),
                'completion_rate': 100,
                'submission_time': datetime.now().isoformat()
            }
        }
        
        success, record_id, message = self.submit_questionnaire(data)
        self.log_result("小学生交流评定表", success, message, record_id)
        
        # 等待一秒避免请求过快
        time.sleep(1)
    
    def test_primary_report_form(self):
        """测试小学生报告表"""
        print("\n🔍 测试小学生报告表...")
        
        questions = [
            {
                'id': 1,
                'type': 'text_input',
                'question': '孩子就读过的学校以及就读时间',
                'answer': '测试小学，2020年9月至今'
            },
            {
                'id': 2,
                'type': 'text_input',
                'question': '目前对孩子是否有担忧',
                'answer': '在学校不太愿意主动发言，比较内向'
            },
            {
                'id': 3,
                'type': 'rating_scale',
                'question': '一般能力评估',
                'rating': 3
            },
            {
                'id': 4,
                'type': 'rating_scale',
                'question': '成就表现评估',
                'rating': 3
            }
        ]
        
        data = {
            'type': 'primary_report_form',
            'basic_info': {
                'name': '李小红',
                'grade': '小学二年级',
                'submission_date': self.basic_info_template['submission_date']
            },
            'questions': questions,
            'statistics': {
                'total_score': 6,
                'completion_rate': 100,
                'submission_time': datetime.now().isoformat()
            }
        }
        
        success, record_id, message = self.submit_questionnaire(data)
        self.log_result("小学生报告表", success, message, record_id)
        time.sleep(1)
    
    def test_speech_habit_record(self):
        """测试说话习惯记录"""
        print("\n🔍 测试说话习惯记录...")
        
        questions = []
        categories = ['family', 'frequent_contacts', 'strangers']
        situations = ['alone_passive', 'alone_active', 'with_others_passive', 'with_others_active', 'group_passive', 'group_active']
        
        question_id = 1
        for category in categories:
            for situation in situations:
                questions.append({
                    'id': question_id,
                    'type': 'multiple_choice',
                    'question': f'{category}_{situation}',
                    'options': [
                        {'value': 'normal', 'text': '正常音量'},
                        {'value': 'quiet', 'text': '小声说话'},
                        {'value': 'whisper', 'text': '悄声/耳语'}
                    ],
                    'selected': [random.choice(['normal', 'quiet', 'whisper'])]
                })
                question_id += 1
        
        data = {
            'type': 'speech_habit',
            'basic_info': {
                'name': '王小刚',
                'grade': '8岁 - 男',
                'submission_date': self.basic_info_template['submission_date']
            },
            'questions': questions,
            'statistics': {
                'total_score': len(questions),
                'completion_rate': 100,
                'submission_time': datetime.now().isoformat()
            }
        }
        
        success, record_id, message = self.submit_questionnaire(data)
        self.log_result("说话习惯记录", success, message, record_id)
        time.sleep(1)
    
    def test_adolescent_interview(self):
        """测试青少年访谈表格"""
        print("\n🔍 测试青少年访谈表格...")
        
        questions = [
            {
                'id': 1,
                'type': 'text_input',
                'question': '告诉我一些你喜欢或进展顺利的事情',
                'answer': '我喜欢画画和看书，在这些方面做得还不错'
            },
            {
                'id': 2,
                'type': 'text_input',
                'question': '什么事情进展得不是那么顺利',
                'answer': '在学校发言时会感到紧张，不太敢主动和陌生人说话'
            },
            {
                'id': 3,
                'type': 'text_input',
                'question': '现在有谁住在家里',
                'answer': '爸爸、妈妈、我和弟弟'
            },
            {
                'id': 4,
                'type': 'text_input',
                'question': '在某些场合中,你是否非常担心与某些人交谈',
                'answer': '是的，特别是在课堂上回答问题时，或者和不熟悉的大人说话时'
            },
            {
                'id': 5,
                'type': 'multiple_choice',
                'question': '当你担心说话时,你经常会有以下哪种想法',
                'options': [
                    {'value': '1', 'text': '我想不出要说什么话'},
                    {'value': '2', 'text': '人们会对我有不好的看法'},
                    {'value': '3', 'text': '我说不出话来'},
                    {'value': '4', 'text': '如果我说话,人们会认为这很奇怪'}
                ],
                'selected': ['2', '3'],
                'allow_multiple': True
            }
        ]
        
        data = {
            'type': 'adolescent_interview',
            'basic_info': {
                'name': '陈小华',
                'grade': '青少年访谈',
                'submission_date': self.basic_info_template['submission_date']
            },
            'questions': questions,
            'statistics': {
                'total_score': len(questions),
                'completion_rate': 100,
                'submission_time': datetime.now().isoformat()
            }
        }
        
        success, record_id, message = self.submit_questionnaire(data)
        self.log_result("青少年访谈表格", success, message, record_id)
        time.sleep(1)
    
    def test_sm_maintenance_factors(self):
        """测试可能的SM维持因素清单"""
        print("\n🔍 测试可能的SM维持因素清单...")
        
        questions = []
        for i in range(1, 11):  # 10个测试项目
            questions.append({
                'id': i,
                'type': 'text_input',
                'question': f'维持因素项目{i}',
                'answer': f'这是第{i}个维持因素的测试回答，描述了相关的情境和案例。'
            })
        
        data = {
            'type': 'sm_maintenance_factors',
            'basic_info': {
                'name': '刘小丽',
                'grade': '9岁 - 家长填写',
                'submission_date': self.basic_info_template['submission_date']
            },
            'questions': questions,
            'statistics': {
                'total_score': len(questions),
                'completion_rate': 100,
                'submission_time': datetime.now().isoformat()
            }
        }
        
        success, record_id, message = self.submit_questionnaire(data)
        self.log_result("可能的SM维持因素清单", success, message, record_id)
        time.sleep(1)
    
    def test_parent_interview(self):
        """测试家长访谈表"""
        print("\n🔍 测试家长访谈表...")
        
        questions = [
            {
                'id': 1,
                'type': 'text_input',
                'question': '请列出您所有担忧的事',
                'answer': '孩子在学校不愿意主动发言，和陌生人交流时显得很紧张'
            },
            {
                'id': 2,
                'type': 'text_input',
                'question': '您认为孩子在其他方面的情况和其他同龄孩子一样好吗',
                'answer': '在家里和熟悉的人交流时很正常，学习能力也没有问题'
            },
            {
                'id': 3,
                'type': 'text_input',
                'question': '目前家里住着哪些人',
                'answer': '爸爸、妈妈、孩子和奶奶，一共四口人'
            },
            {
                'id': 4,
                'type': 'text_input',
                'question': '孩子跟谁、在什么场景下能够尽情、自在地说话',
                'answer': '在家里和爸爸妈妈说话很自然，和要好的同学玩耍时也很活泼'
            },
            {
                'id': 5,
                'type': 'text_input',
                'question': '您是否担心孩子的一般智力或学习',
                'answer': '不担心，孩子的学习成绩中等偏上，理解能力很好'
            }
        ]
        
        data = {
            'type': 'parent_interview',
            'basic_info': {
                'name': '赵小强',
                'grade': '男 - 实验小学',
                'submission_date': self.basic_info_template['submission_date']
            },
            'questions': questions,
            'statistics': {
                'total_score': len(questions),
                'completion_rate': 100,
                'submission_time': datetime.now().isoformat()
            }
        }
        
        success, record_id, message = self.submit_questionnaire(data)
        self.log_result("家长访谈表", success, message, record_id)
        time.sleep(1)
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始综合问卷测试...")
        print("=" * 60)
        
        # 首先测试服务器连接
        if not self.test_server_connection():
            print("\n❌ 服务器连接失败，无法继续测试")
            return
        
        # 运行所有问卷测试
        test_methods = [
            self.test_primary_communication_scale,
            self.test_primary_report_form,
            self.test_speech_habit_record,
            self.test_adolescent_interview,
            self.test_sm_maintenance_factors,
            self.test_parent_interview
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                questionnaire_name = test_method.__name__.replace('test_', '').replace('_', ' ')
                self.log_result(questionnaire_name, False, f"测试异常: {str(e)}")
        
        # 输出测试总结
        self.print_summary()
    
    def print_summary(self):
        """打印测试总结"""
        print("\n" + "=" * 60)
        print("📊 测试总结")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - successful_tests
        
        print(f"总测试数: {total_tests}")
        print(f"成功: {successful_tests} ✅")
        print(f"失败: {failed_tests} ❌")
        print(f"成功率: {(successful_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n❌ 失败的测试:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['questionnaire_type']}: {result['message']}")
        
        print("\n✅ 成功提交的记录:")
        for result in self.test_results:
            if result['success'] and result['record_id']:
                print(f"  - {result['questionnaire_type']}: ID {result['record_id']}")
        
        # 保存详细结果到文件
        with open('test_results.json', 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 详细测试结果已保存到: test_results.json")
    
    def test_data_retrieval(self):
        """测试数据检索功能"""
        print("\n🔍 测试数据检索功能...")
        
        try:
            # 测试获取所有记录
            response = self.session.get(f"{BASE_URL}/api/questionnaires")
            if response.status_code == 200:
                data = response.json()
                record_count = len(data.get('questionnaires', []))
                self.log_result("数据检索", True, f"成功获取 {record_count} 条记录")
                
                # 显示最近的几条记录
                if record_count > 0:
                    print("   最近的记录:")
                    for record in data['questionnaires'][:3]:  # 显示前3条
                        print(f"     - ID: {record.get('id')}, 类型: {record.get('type')}, 姓名: {record.get('basic_info', {}).get('name')}")
            else:
                self.log_result("数据检索", False, f"获取记录失败: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("数据检索", False, f"检索异常: {str(e)}")

def main():
    """主函数"""
    print("🎯 问卷系统综合测试工具")
    print("模拟正常用户填写所有问卷表单，检查服务器接收情况")
    print()
    
    # 创建测试套件并运行
    test_suite = QuestionnaireTestSuite()
    test_suite.run_all_tests()
    
    # 测试数据检索
    test_suite.test_data_retrieval()
    
    print("\n🎉 测试完成！")

if __name__ == "__main__":
    main()