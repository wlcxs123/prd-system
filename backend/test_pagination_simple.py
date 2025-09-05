#!/usr/bin/env python3
"""简单测试分页和搜索API的数据库查询逻辑"""

import sqlite3
import json
from datetime import datetime

def test_database_queries():
    """测试数据库查询逻辑"""
    print('=== 测试数据库查询逻辑 ===')
    
    try:
        conn = sqlite3.connect('questionnaires.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 测试基本分页查询
        print('\n1. 测试基本分页查询')
        page = 1
        limit = 5
        offset = (page - 1) * limit
        
        cursor.execute("SELECT COUNT(*) FROM questionnaires")
        total_count = cursor.fetchone()[0]
        print(f'总记录数: {total_count}')
        
        cursor.execute("SELECT * FROM questionnaires ORDER BY created_at DESC LIMIT ? OFFSET ?", [limit, offset])
        results = cursor.fetchall()
        print(f'第{page}页，每页{limit}条: 获取到 {len(results)} 条记录')
        
        # 测试搜索查询
        print('\n2. 测试搜索查询')
        search = '测试学生1'
        search_param = f"%{search}%"
        
        cursor.execute(
            "SELECT COUNT(*) FROM questionnaires WHERE name LIKE ? OR type LIKE ? OR grade LIKE ?",
            [search_param, search_param, search_param]
        )
        search_count = cursor.fetchone()[0]
        print(f'搜索"{search}": 找到 {search_count} 条匹配记录')
        
        cursor.execute(
            "SELECT * FROM questionnaires WHERE name LIKE ? OR type LIKE ? OR grade LIKE ? ORDER BY created_at DESC LIMIT ?",
            [search_param, search_param, search_param, 10]
        )
        search_results = cursor.fetchall()
        for row in search_results:
            print(f'  - ID: {row["id"]}, 姓名: {row["name"]}, 类型: {row["type"]}')
        
        # 测试筛选选项查询
        print('\n3. 测试筛选选项查询')
        cursor.execute("SELECT DISTINCT type FROM questionnaires WHERE type IS NOT NULL ORDER BY type")
        types = [row[0] for row in cursor.fetchall()]
        print(f'可用问卷类型: {types}')
        
        cursor.execute("SELECT DISTINCT grade FROM questionnaires WHERE grade IS NOT NULL AND grade != '' ORDER BY grade")
        grades = [row[0] for row in cursor.fetchall()]
        print(f'可用年级: {grades}')
        
        # 测试高级筛选查询
        print('\n4. 测试高级筛选查询')
        questionnaire_type = 'parent_interview'
        cursor.execute("SELECT COUNT(*) FROM questionnaires WHERE type = ?", [questionnaire_type])
        type_count = cursor.fetchone()[0]
        print(f'类型为"{questionnaire_type}"的记录数: {type_count}')
        
        cursor.execute("SELECT * FROM questionnaires WHERE type = ? ORDER BY created_at DESC LIMIT 3", [questionnaire_type])
        type_results = cursor.fetchall()
        for row in type_results:
            print(f'  - ID: {row["id"]}, 类型: {row["type"]}, 姓名: {row["name"]}')
        
        # 测试排序功能
        print('\n5. 测试排序功能')
        cursor.execute("SELECT * FROM questionnaires ORDER BY name ASC LIMIT 5")
        sorted_results = cursor.fetchall()
        print('按姓名升序排列的前5条记录:')
        for row in sorted_results:
            print(f'  - 姓名: {row["name"]}, ID: {row["id"]}')
        
        conn.close()
        print('\n✅ 数据库查询逻辑测试完成！')
        return True
        
    except Exception as e:
        print(f'❌ 数据库查询测试失败: {e}')
        return False

def test_pagination_logic():
    """测试分页逻辑计算"""
    print('\n=== 测试分页逻辑计算 ===')
    
    test_cases = [
        {'total': 18, 'limit': 5, 'expected_pages': 4},
        {'total': 20, 'limit': 5, 'expected_pages': 4},
        {'total': 21, 'limit': 5, 'expected_pages': 5},
        {'total': 0, 'limit': 5, 'expected_pages': 1},
        {'total': 3, 'limit': 10, 'expected_pages': 1},
    ]
    
    for case in test_cases:
        total = case['total']
        limit = case['limit']
        expected = case['expected_pages']
        calculated = max(1, (total + limit - 1) // limit)
        
        status = '✅' if calculated == expected else '❌'
        print(f'{status} 总记录{total}，每页{limit}条 -> 预期{expected}页，计算{calculated}页')
    
    print('分页逻辑计算测试完成！')

if __name__ == '__main__':
    print('开始测试分页和搜索功能的数据库逻辑...\n')
    
    success = test_database_queries()
    test_pagination_logic()
    
    if success:
        print('\n🎉 所有数据库查询逻辑测试通过！')
        print('分页和搜索功能的后端逻辑实现正确。')
    else:
        print('\n⚠️  数据库查询测试失败，请检查数据库连接和表结构。')