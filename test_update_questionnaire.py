#!/usr/bin/env python3
"""
测试更新问卷功能
"""

import requests
import json
from datetime import datetime

# 服务器配置
BASE_URL = "http://localhost:5000"

def test_update_questionnaire():
    """测试更新问卷功能"""
    
    # 1. 首先创建一个测试问卷
    print("1. 创建测试问卷...")
    create_data = {
        "type": "frankfurt_scale_selective_mutism",
        "basic_info": {
            "name": "测试学生",
            "grade": "小学",
            "submission_date": "2024-01-15"
        },
        "questions": [
            {
                "id": 1,
                "section": "DS",
                "type": "multiple_choice",
                "question": "在家里，孩子是否愿意与家人交谈？",
                "selected": ["经常"],
                "options": [
                    {"value": "从不", "text": "从不"},
                    {"value": "偶尔", "text": "偶尔"},
                    {"value": "经常", "text": "经常"},
                    {"value": "总是", "text": "总是"}
                ],
                "can_speak": True
            },
            {
                "id": 2, 
                "section": "SS_school",
                "type": "multiple_choice",
                "question": "在学校，孩子是否愿意与老师交谈？",
                "selected": ["偶尔"],
                "options": [
                    {"value": "从不", "text": "从不"},
                    {"value": "偶尔", "text": "偶尔"},
                    {"value": "经常", "text": "经常"},
                    {"value": "总是", "text": "总是"}
                ],
                "can_speak": True
            },
            {
                "id": 3,
                "section": "SS_public", 
                "type": "multiple_choice",
                "question": "在公共场所，孩子是否愿意与陌生人交谈？",
                "selected": ["从不"],
                "options": [
                    {"value": "从不", "text": "从不"},
                    {"value": "偶尔", "text": "偶尔"},
                    {"value": "经常", "text": "经常"},
                    {"value": "总是", "text": "总是"}
                ],
                "can_speak": False
            },
            {
                "id": 4,
                "section": "SS_home",
                "type": "multiple_choice", 
                "question": "在家里，孩子是否愿意在客人面前说话？",
                "selected": ["偶尔"],
                "options": [
                    {"value": "从不", "text": "从不"},
                    {"value": "偶尔", "text": "偶尔"},
                    {"value": "经常", "text": "经常"},
                    {"value": "总是", "text": "总是"}
                ],
                "can_speak": True
            }
        ],
        "statistics": {
            "ds_total": 3,
            "ss_school_total": 2,
            "ss_public_total": 1,
            "ss_home_total": 2
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/questionnaires", json=create_data)
        print(f"创建响应状态码: {response.status_code}")
        print(f"创建响应内容: {response.text}")
        
        if response.status_code != 201:
            print("创建问卷失败，无法继续测试更新功能")
            return
            
        create_result = response.json()
        questionnaire_id = create_result.get('id')
        print(f"创建成功，问卷ID: {questionnaire_id}")
        
    except Exception as e:
        print(f"创建问卷时发生错误: {e}")
        return
    
    # 2. 测试更新问卷
    print(f"\n2. 更新问卷 ID {questionnaire_id}...")
    update_data = {
        "type": "frankfurt_scale_selective_mutism",
        "basic_info": {
            "name": "更新后的学生姓名",
            "grade": "中学",
            "submission_date": "2024-01-20"
        },
        "questions": [
            {
                "id": 1,
                "section": "DS",
                "type": "multiple_choice",
                "question": "在家里，孩子是否愿意与家人交谈？",
                "selected": ["总是"],
                "options": [
                    {"value": "从不", "text": "从不"},
                    {"value": "偶尔", "text": "偶尔"},
                    {"value": "经常", "text": "经常"},
                    {"value": "总是", "text": "总是"}
                ],
                "can_speak": True
            },
            {
                "id": 2,
                "section": "SS_school",
                "type": "multiple_choice", 
                "question": "在学校，孩子是否愿意与老师交谈？",
                "selected": ["经常"],
                "options": [
                    {"value": "从不", "text": "从不"},
                    {"value": "偶尔", "text": "偶尔"},
                    {"value": "经常", "text": "经常"},
                    {"value": "总是", "text": "总是"}
                ],
                "can_speak": True
            },
            {
                "id": 3,
                "section": "SS_public",
                "type": "multiple_choice",
                "question": "在公共场所，孩子是否愿意与陌生人交谈？",
                "selected": ["从不"],
                "options": [
                    {"value": "从不", "text": "从不"},
                    {"value": "偶尔", "text": "偶尔"},
                    {"value": "经常", "text": "经常"},
                    {"value": "总是", "text": "总是"}
                ],
                "can_speak": False
            },
            {
                "id": 4,
                "section": "SS_home",
                "type": "multiple_choice",
                "question": "在家里，孩子是否愿意在客人面前说话？",
                "selected": ["经常"],
                "options": [
                    {"value": "从不", "text": "从不"},
                    {"value": "偶尔", "text": "偶尔"},
                    {"value": "经常", "text": "经常"},
                    {"value": "总是", "text": "总是"}
                ],
                "can_speak": True
            }
        ],
        "statistics": {
            "ds_total": 4,
            "ss_school_total": 3,
            "ss_public_total": 1,
            "ss_home_total": 3
        }
    }
    
    try:
        response = requests.put(f"{BASE_URL}/api/questionnaires/{questionnaire_id}", json=update_data)
        print(f"更新响应状态码: {response.status_code}")
        print(f"更新响应内容: {response.text}")
        
        if response.status_code == 200:
            print("✅ 更新问卷成功")
        else:
            print("❌ 更新问卷失败")
            
    except Exception as e:
        print(f"更新问卷时发生错误: {e}")
    
    # 3. 验证更新结果
    print(f"\n3. 验证更新结果...")
    try:
        response = requests.get(f"{BASE_URL}/api/questionnaires/{questionnaire_id}")
        print(f"获取响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                data = result.get('data', {})
                basic_info = data.get('basic_info', {})
                questions = data.get('questions', [])
                statistics = data.get('statistics', {})
                
                print(f"✅ 验证成功:")
                print(f"  - 姓名: {basic_info.get('name')}")
                print(f"  - 年级: {basic_info.get('grade')}")
                print(f"  - 提交日期: {basic_info.get('submission_date')}")
                print(f"  - 问题数量: {len(questions)}")
                print(f"  - 总分: {statistics.get('total_score')}")
                print(f"  - 百分比: {statistics.get('percentage')}")
            else:
                print("❌ 获取更新后的问卷失败")
        else:
            print(f"❌ 获取问卷失败，状态码: {response.status_code}")
            
    except Exception as e:
        print(f"验证更新结果时发生错误: {e}")

if __name__ == "__main__":
    print("开始测试更新问卷功能...")
    print(f"测试时间: {datetime.now()}")
    print("=" * 50)
    
    test_update_questionnaire()
    
    print("\n" + "=" * 50)
    print("测试完成")