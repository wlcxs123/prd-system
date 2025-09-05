#!/usr/bin/env python3
"""
完整测试前端修复效果
模拟真实的前端数据收集和提交流程
"""

import requests
import json

def simulate_frontend_data_collection():
    """模拟前端数据收集过程"""
    
    # 模拟 collectDetailedData() 函数的返回结果
    detailed_data = [
        {
            "questionNumber": 1,
            "questionText": "在家里和父母说话",
            "options": [
                {"value": 0, "text": "0=非常容易", "selected": False},
                {"value": 1, "text": "1=相当容易", "selected": False},
                {"value": 2, "text": "2=有点困难", "selected": True},
                {"value": 3, "text": "3=困难", "selected": False},
                {"value": 4, "text": "4=非常困难", "selected": False}
            ],
            "selectedOption": 2,
            "selectedText": "2=有点困难",
            "canSpeak": True,
            "canSpeakText": "可以说话"
        },
        {
            "questionNumber": 2,
            "questionText": "在学校和老师说话",
            "options": [
                {"value": 0, "text": "0=非常容易", "selected": False},
                {"value": 1, "text": "1=相当容易", "selected": True},
                {"value": 2, "text": "2=有点困难", "selected": False},
                {"value": 3, "text": "3=困难", "selected": False},
                {"value": 4, "text": "4=非常困难", "selected": False}
            ],
            "selectedOption": 1,
            "selectedText": "1=相当容易",
            "canSpeak": False,
            "canSpeakText": "不可以说话"
        },
        {
            "questionNumber": 3,
            "questionText": "和同学一起玩耍时说话",
            "options": [
                {"value": 0, "text": "0=非常容易", "selected": False},
                {"value": 1, "text": "1=相当容易", "selected": False},
                {"value": 2, "text": "2=有点困难", "selected": False},
                {"value": 3, "text": "3=困难", "selected": True},
                {"value": 4, "text": "4=非常困难", "selected": False}
            ],
            "selectedOption": 3,
            "selectedText": "3=困难",
            "canSpeak": True,
            "canSpeakText": "可以说话"
        }
    ]
    
    return detailed_data

def test_complete_submission():
    """测试完整的提交流程"""
    
    print("=== 测试完整的前端提交流程 ===")
    
    # 模拟前端数据收集
    detailed_data = simulate_frontend_data_collection()
    
    # 模拟基本信息
    basic_info = {
        "name": "张小明",
        "grade": "三年级",
        "date": "2025-08-29"
    }
    
    # 计算统计数据（模拟前端逻辑）
    total_score = sum(q["selectedOption"] for q in detailed_data)
    speech_count = sum(1 for q in detailed_data if q["canSpeak"])
    
    # 构建符合API标准的问题数据（使用修复后的逻辑）
    questions = []
    for q in detailed_data:
        question = {
            "id": q["questionNumber"],
            "type": "multiple_choice",
            "question": q["questionText"],  # 使用正确的属性名
            "options": [
                {"value": 0, "text": "非常容易(没有焦虑)"},
                {"value": 1, "text": "相当容易(有点焦虑)"},
                {"value": 2, "text": "有点困难(有不少焦虑)"},
                {"value": 3, "text": "困难(更加焦虑)"},
                {"value": 4, "text": "非常困难(高度焦虑)"}
            ],
            "selected": [q["selectedOption"]],
            "can_speak": q["canSpeak"]
        }
        questions.append(question)
    
    # 构建完整提交数据
    data_to_submit = {
        "type": "elementary_school_communication_assessment",
        "basic_info": {
            "name": basic_info["name"].strip(),
            "grade": basic_info["grade"].strip(),
            "submission_date": basic_info["date"]
        },
        "questions": questions,
        "statistics": {
            "total_score": total_score,
            "completion_rate": 100,
            "submission_time": "2025-08-29T16:00:00.000Z"
        }
    }
    
    print(f"提交数据预览:")
    print(f"- 学生姓名: {basic_info['name']}")
    print(f"- 年级: {basic_info['grade']}")
    print(f"- 问题数量: {len(questions)}")
    print(f"- 总分: {total_score}")
    print(f"- 可以说话的情况数: {speech_count}")
    
    try:
        # 发送请求
        response = requests.post(
            'http://127.0.0.1:5000/api/submit',
            json=data_to_submit,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            timeout=10
        )
        
        print(f"\n响应状态码: {response.status_code}")
        print(f"response.ok: {response.ok}")
        
        # 模拟前端的处理逻辑
        if response.ok:
            result = response.json()
            print(f"响应数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # 模拟前端第1419行的关键检查
            if result.get('success'):
                print("✅ result.success 为 True")
                record_id = result.get('id') or result.get('record_id')
                print(f"✅ 数据保存成功！问卷ID: {record_id}")
                print("✅ 前端会调用 showCompletion() 显示成功页面")
                return True
            else:
                print("❌ result.success 不为 True")
                error_message = result.get('error', {}).get('message', '保存失败')
                print(f"❌ 前端会抛出错误: Error: {error_message}")
                return False
        else:
            print("❌ response.ok 为 False")
            try:
                error_data = response.json()
                if error_data.get('error'):
                    if error_data['error'].get('details') and isinstance(error_data['error']['details'], list):
                        error_message = '数据验证失败：\n' + '\n'.join(error_data['error']['details'])
                    else:
                        error_message = error_data['error'].get('message') or error_data.get('message') or f"服务器错误 ({response.status_code})"
                else:
                    error_message = f"服务器错误 ({response.status_code})"
                print(f"前端会显示错误: ❌ 数据保存失败:\n{error_message}")
            except:
                error_message = f"HTTP {response.status_code}: {response.reason}"
                print(f"前端会显示错误: ❌ 数据保存失败:\n{error_message}")
            return False
            
    except Exception as e:
        print(f"❌ 网络错误: {e}")
        print("前端会显示网络错误诊断信息")
        return False

def test_validation_scenarios():
    """测试各种验证场景"""
    
    print("\n=== 测试验证场景 ===")
    
    scenarios = [
        {
            "name": "空姓名",
            "data": {
                "type": "elementary_school_communication_assessment",
                "basic_info": {"name": "", "grade": "三年级", "submission_date": "2025-08-29"},
                "questions": [{"id": 1, "type": "multiple_choice", "question": "测试问题", "options": [], "selected": [1], "can_speak": True}],
                "statistics": {"total_score": 1, "completion_rate": 100, "submission_time": "2025-08-29T16:00:00.000Z"}
            },
            "expected_error": "姓名"
        },
        {
            "name": "空问题文本",
            "data": {
                "type": "elementary_school_communication_assessment",
                "basic_info": {"name": "测试", "grade": "三年级", "submission_date": "2025-08-29"},
                "questions": [{"id": 1, "type": "multiple_choice", "question": "", "options": [], "selected": [1], "can_speak": True}],
                "statistics": {"total_score": 1, "completion_rate": 100, "submission_time": "2025-08-29T16:00:00.000Z"}
            },
            "expected_error": "问题文本不能为空"
        },
        {
            "name": "空问题列表",
            "data": {
                "type": "elementary_school_communication_assessment",
                "basic_info": {"name": "测试", "grade": "三年级", "submission_date": "2025-08-29"},
                "questions": [],
                "statistics": {"total_score": 0, "completion_rate": 100, "submission_time": "2025-08-29T16:00:00.000Z"}
            },
            "expected_error": "至少需要一个问题"
        }
    ]
    
    for scenario in scenarios:
        print(f"\n测试场景: {scenario['name']}")
        try:
            response = requests.post(
                'http://127.0.0.1:5000/api/submit',
                json=scenario['data'],
                headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
                timeout=10
            )
            
            if not response.ok:
                error_data = response.json()
                if 'error' in error_data and 'details' in error_data['error']:
                    details = error_data['error']['details']
                    found_expected = any(scenario['expected_error'] in detail for detail in details)
                    if found_expected:
                        print(f"✅ 正确检测到预期错误: {scenario['expected_error']}")
                    else:
                        print(f"❌ 未找到预期错误: {scenario['expected_error']}")
                        print(f"实际错误: {details}")
                else:
                    print(f"❌ 错误格式不正确")
            else:
                print(f"❌ 应该返回验证错误，但返回了成功")
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    success = test_complete_submission()
    test_validation_scenarios()
    
    if success:
        print("\n🎉 完整修复成功！")
        print("✅ 原始的'保存失败'错误已解决")
        print("✅ 问题文本字段错误已解决")
        print("✅ 前端现在可以正常提交数据")
    else:
        print("\n❌ 仍有问题需要解决")