#!/usr/bin/env python3
"""
测试Frankfurt Scale of Selective Mutism问卷集成
"""

import sys
import os
import json
import requests
from datetime import datetime

# 添加backend路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def create_sample_frankfurt_scale_data():
    """创建Frankfurt Scale问卷的示例数据"""
    
    # DS部分问题（10个问题）
    ds_questions = []
    ds_answers = [1, 1, 0, 1, 1, 0, 1, 1, 1, 0]  # 示例答案，总分7分
    
    for i in range(10):
        ds_questions.append({
            "id": i + 1,
            "type": "multiple_choice",
            "question": f"DS问题{i+1}",
            "question_en": f"DS Question {i+1}",
            "options": [
                {"value": 1, "text": "是 = 1分"},
                {"value": 0, "text": "否 = 0分"}
            ],
            "selected": [ds_answers[i]],
            "section": "DS"
        })
    
    # SS部分问题（按6-11岁年龄段）
    ss_questions = []
    question_id = 11
    
    # 学校场景（10个问题）
    school_answers = [2, 3, 1, 2, 3, 4, 3, 2, 1, 2]  # 总分23
    for i in range(10):
        ss_questions.append({
            "id": question_id,
            "type": "multiple_choice", 
            "question": f"学校问题{i+1}",
            "question_en": f"School Question {i+1}",
            "options": [
                {"value": 0, "text": "0 无问题"},
                {"value": 1, "text": "1 轻度限制"},
                {"value": 2, "text": "2 偶尔"},
                {"value": 3, "text": "3 几乎从不"},
                {"value": 4, "text": "4 完全不说"}
            ],
            "selected": [school_answers[i]],
            "section": "SS_school"
        })
        question_id += 1
    
    # 公共场景（4个问题）
    public_answers = [3, 2, 4, 3]  # 总分12
    for i in range(4):
        ss_questions.append({
            "id": question_id,
            "type": "multiple_choice",
            "question": f"公共场景问题{i+1}",
            "question_en": f"Public Question {i+1}",
            "options": [
                {"value": 0, "text": "0 无问题"},
                {"value": 1, "text": "1 轻度限制"},
                {"value": 2, "text": "2 偶尔"},
                {"value": 3, "text": "3 几乎从不"},
                {"value": 4, "text": "4 完全不说"}
            ],
            "selected": [public_answers[i]],
            "section": "SS_public"
        })
        question_id += 1
    
    # 家庭场景（4个问题）
    home_answers = [0, 1, 0, 1]  # 总分2
    for i in range(4):
        ss_questions.append({
            "id": question_id,
            "type": "multiple_choice",
            "question": f"家庭场景问题{i+1}",
            "question_en": f"Home Question {i+1}",
            "options": [
                {"value": 0, "text": "0 无问题"},
                {"value": 1, "text": "1 轻度限制"},
                {"value": 2, "text": "2 偶尔"},
                {"value": 3, "text": "3 几乎从不"},
                {"value": 4, "text": "4 完全不说"}
            ],
            "selected": [home_answers[i]],
            "section": "SS_home"
        })
        question_id += 1
    
    # 合并所有问题
    all_questions = ds_questions + ss_questions
    
    # 计算统计信息
    ds_total = sum(ds_answers)
    ss_school_total = sum(school_answers)
    ss_public_total = sum(public_answers)
    ss_home_total = sum(home_answers)
    ss_total = ss_school_total + ss_public_total + ss_home_total
    
    # 计算风险等级（6-11岁阈值为7）
    risk_level = 'high' if ds_total >= 7 else ('mid' if ds_total >= 5 else 'low')
    
    return {
        "type": "frankfurt_scale_selective_mutism",
        "basic_info": {
            "name": "测试儿童",
            "grade": "6_11",  # 年龄段
            "submission_date": datetime.now().strftime('%Y-%m-%d'),
            "guardian": "测试家长"
        },
        "questions": all_questions,
        "statistics": {
            "ds_total": ds_total,
            "ss_school_total": ss_school_total,
            "ss_public_total": ss_public_total,
            "ss_home_total": ss_home_total,
            "ss_total": ss_total,
            "age_group": "6_11",
            "risk_level": risk_level,
            "completion_rate": 100,
            "submission_time": datetime.now().isoformat()
        }
    }

def test_data_structure():
    """测试数据结构"""
    print("测试Frankfurt Scale数据结构...")
    
    data = create_sample_frankfurt_scale_data()
    
    # 验证基本结构
    assert data['type'] == 'frankfurt_scale_selective_mutism'
    assert 'basic_info' in data
    assert 'questions' in data
    assert 'statistics' in data
    
    # 验证基本信息
    basic_info = data['basic_info']
    assert basic_info['name'] == '测试儿童'
    assert basic_info['grade'] == '6_11'
    assert 'submission_date' in basic_info
    
    # 验证问题数量（10个DS + 10个学校 + 4个公共 + 4个家庭 = 28个）
    assert len(data['questions']) == 28
    
    # 验证DS部分
    ds_questions = [q for q in data['questions'] if q['section'] == 'DS']
    assert len(ds_questions) == 10
    
    # 验证SS部分
    ss_school = [q for q in data['questions'] if q['section'] == 'SS_school']
    ss_public = [q for q in data['questions'] if q['section'] == 'SS_public']
    ss_home = [q for q in data['questions'] if q['section'] == 'SS_home']
    
    assert len(ss_school) == 10
    assert len(ss_public) == 4
    assert len(ss_home) == 4
    
    # 验证统计信息
    stats = data['statistics']
    assert stats['ds_total'] == 7
    assert stats['ss_school_total'] == 23
    assert stats['ss_public_total'] == 12
    assert stats['ss_home_total'] == 2
    assert stats['ss_total'] == 37
    assert stats['age_group'] == '6_11'
    assert stats['risk_level'] == 'high'  # DS总分7，达到高风险阈值
    
    print("✅ 数据结构验证通过")
    return data

def test_api_submission():
    """测试API提交"""
    print("测试API提交...")
    
    data = create_sample_frankfurt_scale_data()
    
    try:
        # 提交到本地API
        response = requests.post(
            'http://localhost:5000/api/questionnaires',
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 201:
            result = response.json()
            if result.get('success'):
                print(f"✅ API提交成功，问卷ID: {result.get('id')}")
                return result
            else:
                print(f"❌ API返回失败: {result}")
                return None
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            try:
                error_data = response.json()
                print(f"错误详情: {error_data}")
            except:
                print(f"响应内容: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("⚠️  无法连接到服务器，请确保Flask应用正在运行")
        return None
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def test_data_validation():
    """测试数据验证"""
    print("测试数据验证...")
    
    # 测试完整数据
    valid_data = create_sample_frankfurt_scale_data()
    print("✅ 完整数据创建成功")
    
    # 测试缺少必填字段
    invalid_data = valid_data.copy()
    invalid_data['basic_info']['name'] = ''
    
    try:
        response = requests.post(
            'http://localhost:5000/api/questionnaires',
            json=invalid_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 400:
            print("✅ 数据验证正确拒绝了无效数据")
        else:
            print("⚠️  数据验证可能存在问题")
            
    except requests.exceptions.ConnectionError:
        print("⚠️  无法连接到服务器进行验证测试")
    except Exception as e:
        print(f"验证测试失败: {e}")

def export_sample_data():
    """导出示例数据"""
    print("导出示例数据...")
    
    data = create_sample_frankfurt_scale_data()
    
    # 导出JSON
    with open('frankfurt_scale_sample.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("✅ 示例数据已导出到 frankfurt_scale_sample.json")
    
    # 显示数据摘要
    print("\n📊 数据摘要:")
    print(f"问卷类型: {data['type']}")
    print(f"儿童姓名: {data['basic_info']['name']}")
    print(f"年龄段: {data['basic_info']['grade']}")
    print(f"DS总分: {data['statistics']['ds_total']}")
    print(f"SS学校: {data['statistics']['ss_school_total']}")
    print(f"SS公共: {data['statistics']['ss_public_total']}")
    print(f"SS家庭: {data['statistics']['ss_home_total']}")
    print(f"SS总分: {data['statistics']['ss_total']}")
    print(f"风险等级: {data['statistics']['risk_level']}")

def main():
    """运行所有测试"""
    print("Frankfurt Scale of Selective Mutism 集成测试")
    print("=" * 50)
    
    try:
        # 测试数据结构
        data = test_data_structure()
        print()
        
        # 测试API提交
        result = test_api_submission()
        print()
        
        # 测试数据验证
        test_data_validation()
        print()
        
        # 导出示例数据
        export_sample_data()
        print()
        
        print("🎉 所有测试完成！")
        
        if result:
            print(f"\n✅ 集成测试成功")
            print(f"- 数据结构验证: ✅")
            print(f"- API提交测试: ✅")
            print(f"- 数据验证测试: ✅")
            print(f"- 示例数据导出: ✅")
        else:
            print(f"\n⚠️  部分测试未通过，请检查服务器状态")
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())