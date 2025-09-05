#!/usr/bin/env python3
"""测试分页和搜索API功能"""

import requests
import json

def test_pagination():
    """测试基本分页功能"""
    print('=== 测试基本分页功能 ===')
    try:
        response = requests.get('http://localhost:5000/api/questionnaires?page=1&limit=5')
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f'第1页，每页5条: 获取到 {len(data["data"])} 条记录')
                print(f'分页信息: 第{data["pagination"]["page"]}页，共{data["pagination"]["pages"]}页，总计{data["pagination"]["total"]}条')
                return True
            else:
                print(f'API返回错误: {data.get("error", "未知错误")}')
        else:
            print(f'HTTP错误: {response.status_code}')
    except Exception as e:
        print(f'请求失败: {e}')
    return False

def test_search():
    """测试搜索功能"""
    print('\n=== 测试搜索功能 ===')
    try:
        response = requests.get('http://localhost:5000/api/questionnaires?search=测试学生1')
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f'搜索"测试学生1": 找到 {len(data["data"])} 条记录')
                for item in data['data']:
                    print(f'  - ID: {item["id"]}, 姓名: {item["name"]}, 类型: {item["type"]}')
                return True
            else:
                print(f'搜索失败: {data.get("error", "未知错误")}')
        else:
            print(f'HTTP错误: {response.status_code}')
    except Exception as e:
        print(f'搜索请求失败: {e}')
    return False

def test_filters():
    """测试筛选选项API"""
    print('\n=== 测试筛选选项API ===')
    try:
        response = requests.get('http://localhost:5000/api/questionnaires/filters')
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f'可用问卷类型: {data["data"]["types"]}')
                print(f'可用年级: {data["data"]["grades"]}')
                print(f'日期范围: {data["data"]["date_range"]}')
                return True
            else:
                print(f'获取筛选选项失败: {data.get("error", "未知错误")}')
        else:
            print(f'HTTP错误: {response.status_code}')
    except Exception as e:
        print(f'筛选选项请求失败: {e}')
    return False

def test_advanced_filters():
    """测试高级筛选功能"""
    print('\n=== 测试高级筛选功能 ===')
    try:
        # 测试按类型筛选
        response = requests.get('http://localhost:5000/api/questionnaires?type=parent_interview&limit=3')
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f'筛选parent_interview类型: 找到 {len(data["data"])} 条记录')
                for item in data['data']:
                    print(f'  - ID: {item["id"]}, 类型: {item["type"]}, 姓名: {item["name"]}')
                return True
            else:
                print(f'类型筛选失败: {data.get("error", "未知错误")}')
        else:
            print(f'HTTP错误: {response.status_code}')
    except Exception as e:
        print(f'高级筛选请求失败: {e}')
    return False

if __name__ == '__main__':
    print('开始测试分页和搜索API...\n')
    
    # 注意：这些测试需要服务器运行且用户已登录
    print('注意：这些测试需要服务器运行且用户已登录')
    print('如果测试失败，请先启动服务器并登录管理后台\n')
    
    results = []
    results.append(test_pagination())
    results.append(test_search())
    results.append(test_filters())
    results.append(test_advanced_filters())
    
    print(f'\n=== 测试结果 ===')
    print(f'成功: {sum(results)}/{len(results)} 项测试')
    
    if all(results):
        print('✅ 所有测试通过！分页和搜索功能实现成功。')
    else:
        print('❌ 部分测试失败，请检查服务器状态和登录状态。')