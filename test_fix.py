#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from datetime import datetime

# 测试修复后的问卷提交功能
BASE_URL = 'http://127.0.0.1:5002'

def test_questionnaire_submission():
    """测试问卷提交功能"""
    
    # 准备测试数据
    test_data = {
        "type": "sm_maintenance_factors",
        "basic_info": {
            "name": "修复测试儿童",
            "grade": "小学二年级", 
            "gender": "男",
            "birthdate": "2018-05-20",
            "age": "6",
            "parent_phone": "13900139000",
            "parent_wechat": "fix_test_wechat",
            "parent_email": "fixtest@example.com",
            "filler_name": "修复测试家长",
            "fill_date": "2025-01-27",
            "relationship": "父亲",
            "submission_date": "2025-01-27"
        },
        "questions": {
            "q1": {
                "type": "single_choice",
                "question": "测试问题1",
                "answer": "选项A"
            }
        }
    }
    
    print("🚀 开始测试修复后的问卷提交功能")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试目标: {BASE_URL}")
    print()
    
    try:
        # 提交问卷
        response = requests.post(
            f'{BASE_URL}/api/questionnaires',
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                questionnaire_id = result.get('questionnaire_id')
                print(f"✅ 问卷提交成功，ID: {questionnaire_id}")
                return questionnaire_id
            else:
                print(f"❌ 问卷提交失败: {result.get('error', '未知错误')}")
                return None
        else:
            print(f"❌ HTTP请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return None

def check_questionnaire_data(questionnaire_id):
    """检查问卷数据是否正确存储"""
    
    import sqlite3
    
    try:
        with sqlite3.connect('backend/questionnaire.db') as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM questionnaires WHERE id = ?", (questionnaire_id,))
            record = cursor.fetchone()
            
            if record:
                print(f"\n=== 检查问卷记录 (ID: {questionnaire_id}) ===")
                print(f"类型: {record['type']}")
                print(f"姓名: {record['name']}")
                print(f"年级: {record['grade']}")
                print(f"性别: {record['gender']}")
                print(f"出生日期: {record['birthdate']}")
                print(f"填写人: {record['filler_name']}")
                
                # 解析data字段
                try:
                    data = json.loads(record['data'])
                    basic_info = data.get('basic_info', {})
                    print(f"\n=== basic_info数据 ===")
                    print(f"姓名: {basic_info.get('name')}")
                    print(f"年级: {basic_info.get('grade')}")
                    print(f"性别: {basic_info.get('gender')}")
                    print(f"出生日期: {basic_info.get('birthdate')}")
                    print(f"填写人: {basic_info.get('filler_name')}")
                    
                    # 验证数据一致性
                    print(f"\n=== 数据一致性检查 ===")
                    checks = [
                        ('姓名', record['name'], basic_info.get('name')),
                        ('年级', record['grade'], basic_info.get('grade')),
                        ('性别', record['gender'], basic_info.get('gender')),
                        ('出生日期', record['birthdate'], basic_info.get('birthdate')),
                        ('填写人', record['filler_name'], basic_info.get('filler_name'))
                    ]
                    
                    all_correct = True
                    for field_name, main_value, basic_value in checks:
                        if main_value == basic_value:
                            print(f"✅ {field_name}: 主表='{main_value}' == basic_info='{basic_value}'")
                        else:
                            print(f"❌ {field_name}: 主表='{main_value}' != basic_info='{basic_value}'")
                            all_correct = False
                    
                    if all_correct:
                        print(f"\n🎉 所有字段数据一致性检查通过！")
                    else:
                        print(f"\n⚠️  存在数据不一致问题")
                        
                except Exception as e:
                    print(f"❌ 解析data字段失败: {str(e)}")
            else:
                print(f"❌ 未找到ID为{questionnaire_id}的记录")
                
    except Exception as e:
        print(f"❌ 数据库查询失败: {str(e)}")

if __name__ == '__main__':
    questionnaire_id = test_questionnaire_submission()
    if questionnaire_id:
        check_questionnaire_data(questionnaire_id)