#!/usr/bin/env python3
"""
简单的更新问卷功能测试
"""

import requests
import json
from datetime import datetime

# 服务器配置
BASE_URL = "http://localhost:5000"

def test_update_existing_questionnaire():
    """测试更新现有问卷功能"""
    
    # 1. 先获取现有问卷列表
    print("1. 获取现有问卷列表...")
    try:
        response = requests.get(f"{BASE_URL}/api/questionnaires")
        print(f"获取问卷列表状态码: {response.status_code}")
        
        if response.status_code != 200:
            print("无法获取问卷列表，可能需要登录")
            return
            
        result = response.json()
        questionnaires = result.get('data', [])
        
        if not questionnaires:
            print("没有找到现有问卷，无法测试更新功能")
            return
            
        # 选择第一个问卷进行更新测试
        questionnaire = questionnaires[0]
        questionnaire_id = questionnaire['id']
        print(f"选择问卷ID {questionnaire_id} 进行更新测试")
        print(f"原始问卷信息: {questionnaire['name']} - {questionnaire['type']}")
        
    except Exception as e:
        print(f"获取问卷列表时发生错误: {e}")
        return
    
    # 2. 获取问卷详细信息
    print(f"\n2. 获取问卷 {questionnaire_id} 的详细信息...")
    try:
        response = requests.get(f"{BASE_URL}/api/questionnaires/{questionnaire_id}")
        print(f"获取详情状态码: {response.status_code}")
        
        if response.status_code != 200:
            print("无法获取问卷详情")
            return
            
        detail_result = response.json()
        if not detail_result.get('success'):
            print("获取问卷详情失败")
            return
            
        original_data = detail_result.get('data', {})
        print(f"原始数据获取成功")
        
    except Exception as e:
        print(f"获取问卷详情时发生错误: {e}")
        return
    
    # 3. 构建更新数据（基于原始数据进行小幅修改）
    print(f"\n3. 构建更新数据...")
    update_data = original_data.copy()
    
    # 修改基本信息
    if 'basic_info' in update_data:
        update_data['basic_info']['name'] = f"更新测试-{datetime.now().strftime('%H%M%S')}"
        update_data['basic_info']['submission_date'] = datetime.now().strftime('%Y-%m-%d')
    
    # 如果有问题数据，稍作修改
    if 'questions' in update_data and update_data['questions']:
        # 只修改第一个问题的某些字段（如果存在）
        first_question = update_data['questions'][0]
        if 'selected' in first_question and first_question['selected']:
            # 保持原有选择，只是确保数据结构正确
            pass
    
    print(f"更新数据构建完成")
    
    # 4. 执行更新
    print(f"\n4. 执行更新问卷 {questionnaire_id}...")
    try:
        response = requests.put(f"{BASE_URL}/api/questionnaires/{questionnaire_id}", json=update_data)
        print(f"更新响应状态码: {response.status_code}")
        print(f"更新响应内容: {response.text}")
        
        if response.status_code == 200:
            print("✅ 更新问卷成功")
        else:
            print("❌ 更新问卷失败")
            return
            
    except Exception as e:
        print(f"更新问卷时发生错误: {e}")
        return
    
    # 5. 验证更新结果
    print(f"\n5. 验证更新结果...")
    try:
        response = requests.get(f"{BASE_URL}/api/questionnaires/{questionnaire_id}")
        print(f"验证响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                updated_data = result.get('data', {})
                updated_basic_info = updated_data.get('basic_info', {})
                
                print(f"✅ 验证成功:")
                print(f"  - 更新后姓名: {updated_basic_info.get('name')}")
                print(f"  - 更新后提交日期: {updated_basic_info.get('submission_date')}")
                print(f"  - 更新时间: {updated_data.get('updated_at')}")
            else:
                print("❌ 获取更新后的问卷失败")
        else:
            print(f"❌ 验证失败，状态码: {response.status_code}")
            
    except Exception as e:
        print(f"验证更新结果时发生错误: {e}")

if __name__ == "__main__":
    print("开始测试更新现有问卷功能...")
    print(f"测试时间: {datetime.now()}")
    print("=" * 50)
    
    test_update_existing_questionnaire()
    
    print("\n" + "=" * 50)
    print("测试完成")