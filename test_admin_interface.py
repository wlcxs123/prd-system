#!/usr/bin/env python3
"""
测试管理员界面的问卷显示功能
"""

import requests
import json
import sys
import os

# 添加backend目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_admin_interface():
    """测试管理员界面功能"""
    base_url = "http://localhost:5000"
    
    print("=== 测试管理员界面问卷显示功能 ===\n")
    
    # 1. 测试获取问卷列表
    print("1. 测试获取问卷列表...")
    try:
        response = requests.get(f"{base_url}/api/questionnaires")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                questionnaires = data.get('data', [])
                print(f"   ✓ 成功获取 {len(questionnaires)} 个问卷")
                
                if questionnaires:
                    # 测试获取第一个问卷的详情
                    first_q = questionnaires[0]
                    print(f"   - 第一个问卷: ID={first_q['id']}, 类型={first_q['type']}")
                    
                    # 2. 测试获取问卷详情
                    print(f"\n2. 测试获取问卷详情 (ID: {first_q['id']})...")
                    detail_response = requests.get(f"{base_url}/api/questionnaires/{first_q['id']}")
                    
                    if detail_response.status_code == 200:
                        detail_data = detail_response.json()
                        if detail_data.get('success'):
                            questionnaire = detail_data['data']
                            print("   ✓ 成功获取问卷详情")
                            
                            # 分析问卷数据结构
                            print("   - 问卷数据结构分析:")
                            print(f"     * ID: {questionnaire.get('id')}")
                            print(f"     * 类型: {questionnaire.get('type')}")
                            print(f"     * 创建时间: {questionnaire.get('created_at')}")
                            
                            data_content = questionnaire.get('data', {})
                            print(f"     * 数据字段: {list(data_content.keys())}")
                            
                            # 检查基本信息
                            if 'basic_info' in data_content:
                                basic_info = data_content['basic_info']
                                print(f"     * 基本信息字段: {list(basic_info.keys())}")
                                print(f"       - 姓名: {basic_info.get('name', '未知')}")
                                print(f"       - 性别: {basic_info.get('gender', '未知')}")
                            
                            # 检查详细数据
                            if 'detailedData' in data_content:
                                detailed_data = data_content['detailedData']
                                if isinstance(detailed_data, list):
                                    print(f"     * 详细问题数量: {len(detailed_data)}")
                                    if detailed_data:
                                        first_question = detailed_data[0]
                                        print(f"       - 第一个问题: {first_question.get('questionText', '未知')}")
                                        print(f"       - 答案: {first_question.get('selectedText', '未选择')}")
                                        if 'score' in first_question:
                                            print(f"       - 评分: {first_question['score']}")
                            
                            # 检查其他问题
                            if 'questions' in data_content:
                                questions = data_content['questions']
                                print(f"     * 其他问题部分: {list(questions.keys())}")
                            
                            # 检查评分信息
                            if 'totalScore' in data_content:
                                print(f"     * 总分: {data_content['totalScore']}")
                            if 'averageScore' in data_content:
                                print(f"     * 平均分: {data_content['averageScore']:.2f}")
                            
                            print("\n   ✓ 问卷数据结构分析完成")
                            
                        else:
                            print(f"   ✗ 获取问卷详情失败: {detail_data.get('error', {}).get('message', '未知错误')}")
                    else:
                        print(f"   ✗ 获取问卷详情失败: HTTP {detail_response.status_code}")
                        
                else:
                    print("   - 没有找到问卷数据")
                    
            else:
                print(f"   ✗ 获取问卷列表失败: {data.get('error', {}).get('message', '未知错误')}")
        else:
            print(f"   ✗ 获取问卷列表失败: HTTP {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("   ✗ 无法连接到服务器，请确保后端服务正在运行")
        return False
    except Exception as e:
        print(f"   ✗ 测试过程中出现错误: {e}")
        return False
    
    print("\n=== 测试完成 ===")
    return True

def print_questionnaire_structure_guide():
    """打印问卷数据结构指南"""
    print("\n=== 问卷数据结构指南 ===")
    print("""
管理员界面现在支持以下问卷数据结构：

1. 基本信息 (basic_info):
   - name: 姓名
   - gender: 性别
   - age: 年龄
   - grade: 年级
   - birthdate/birth_date: 出生日期
   - evaluator: 评估者
   - relationship: 与孩子关系

2. 详细问题数据 (detailedData) - 数组格式:
   - questionNumber: 问题编号
   - questionText: 问题文本
   - selectedText: 选择的答案文本
   - score: 评分 (0-4)
   - speechIssue: 是否有言语问题 (boolean)

3. 评分总结:
   - totalScore: 总分
   - averageScore: 平均分
   - speechIssueCount: 言语问题数量

4. 其他问题 (questions):
   - 按部分组织的问题和答案

管理员界面功能：
- 查看: 显示完整的问卷内容，包括所有问题和答案
- 编辑: 可以修改基本信息、问题答案和评分
- 导出: 导出问卷数据
- 删除: 删除问卷记录

特别支持小学生交流评定表的24个标准问题显示。
""")

if __name__ == "__main__":
    success = test_admin_interface()
    print_questionnaire_structure_guide()
    
    if success:
        print("\n建议：")
        print("1. 在浏览器中打开 http://localhost:5000/admin 测试管理员界面")
        print("2. 点击'查看'按钮查看问卷详情")
        print("3. 点击'编辑'按钮修改问卷数据")
        print("4. 验证所有问题和答案都能正确显示")