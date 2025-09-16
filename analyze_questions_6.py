#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析questions.6字段问题的脚本
"""

import sqlite3
import json
from datetime import datetime

def analyze_questions_6_issue():
    """分析questions.6字段的问题"""
    print("=== 分析questions.6字段问题 ===")
    
    # 1. 查看小学生报告表HTML中的问题配置
    print("\n1. 小学生报告表HTML中的rating-scale问题配置:")
    print("   - ID: 501 (第6个问题，索引为5，所以是questions.5，但可能被误认为questions.6)")
    print("   - 类型: rating-scale")
    print("   - 选项: value 1-5 (非常低, 低于平均, 平均, 优于平均, 非常好)")
    print("   - 但前端代码将其转换为multiple_choice类型，选项值0-4")
    
    # 2. 分析前端转换逻辑
    print("\n2. 前端转换逻辑问题:")
    print("   - rating-scale问题被转换为multiple_choice")
    print("   - 选项值从1-5变成了0-4 (从不, 很少, 有时, 经常, 总是)")
    print("   - 这与原始问题的含义不符")
    
    # 3. 后端验证逻辑
    print("\n3. 后端验证逻辑:")
    print("   - MultipleChoiceQuestionSchema验证选中值必须在options的value范围内")
    print("   - 如果前端发送的selected值不在options中，就会验证失败")
    
    # 4. 查看数据库中的实际数据
    try:
        conn = sqlite3.connect('questionnaires.db')
        cursor = conn.cursor()
        
        print("\n4. 数据库中的实际数据:")
        cursor.execute("""
            SELECT id, type, data 
            FROM questionnaires 
            WHERE type = '小学生报告' 
            ORDER BY id DESC 
            LIMIT 3
        """)
        
        records = cursor.fetchall()
        for record in records:
            record_id, record_type, data_json = record
            print(f"\n   记录ID: {record_id}")
            print(f"   类型: {record_type}")
            
            try:
                data = json.loads(data_json)
                questions = data.get('questions', [])
                print(f"   问题总数: {len(questions)}")
                
                # 查找第6个问题（索引5）
                if len(questions) > 5:
                    q6 = questions[5]
                    print(f"   questions[5] (第6个问题):")
                    print(f"     - ID: {q6.get('id', 'N/A')}")
                    print(f"     - 类型: {q6.get('type', 'N/A')}")
                    print(f"     - 问题: {q6.get('question', 'N/A')[:50]}...")
                    print(f"     - 选项数: {len(q6.get('options', []))}")
                    if q6.get('options'):
                        print(f"     - 选项值范围: {[opt.get('value') for opt in q6.get('options', [])]}")
                    print(f"     - 选中值: {q6.get('selected', [])}")
                else:
                    print(f"   没有第6个问题（questions[5]）")
                    
            except json.JSONDecodeError as e:
                print(f"   JSON解析错误: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"   数据库查询错误: {e}")
    
    # 5. 问题总结和解决方案
    print("\n5. 问题总结:")
    print("   - 前端将rating-scale问题错误转换为multiple_choice")
    print("   - 选项值映射不正确（1-5 -> 0-4）")
    print("   - 问题文本也被改变了")
    print("   - 后端验证时发现选中值不在有效选项范围内")
    
    print("\n6. 解决方案:")
    print("   A. 修复前端转换逻辑，保持rating-scale类型")
    print("   B. 或者调整后端验证逻辑以兼容当前前端")
    print("   C. 统一前后端的问题类型和选项配置")

if __name__ == '__main__':
    analyze_questions_6_issue()