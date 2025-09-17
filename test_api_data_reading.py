#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试后端API数据读取功能
验证API能否正确返回包含家长联系方式的问卷数据
"""

import requests
import json
from datetime import datetime

def login_to_api():
    """登录到API获取会话"""
    print("正在登录到API...")
    login_url = "http://localhost:5002/api/auth/login"
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    session = requests.Session()
    try:
        response = session.post(login_url, json=login_data, timeout=10)
        if response.status_code == 200:
            print("✅ 登录成功")
            return session
        else:
            print(f"❌ 登录失败: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 登录错误: {e}")
        return None

def test_api_data_reading():
    """测试API数据读取功能"""
    print("=== 后端API数据读取测试 ===")
    
    # 先登录获取会话
    session = login_to_api()
    if not session:
        print("❌ 无法登录，跳过数据读取测试")
        return False
    
    try:
        # 1. 测试获取问卷列表
        print("\n1. 测试获取问卷列表...")
        list_url = "http://localhost:5002/api/questionnaires"
        
        response = session.get(list_url, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取问卷列表成功")
            
            if 'questionnaires' in data:
                questionnaires = data['questionnaires']
                print(f"问卷总数: {len(questionnaires)}")
                
                # 查找最新的家长访谈表记录
                parent_interviews = [q for q in questionnaires if q.get('type') == 'parent_interview']
                
                if parent_interviews:
                    latest_record = max(parent_interviews, key=lambda x: x.get('id', 0))
                    record_id = latest_record.get('id')
                    print(f"找到最新的家长访谈表记录，ID: {record_id}")
                    
                    # 检查列表中是否包含家长联系方式信息
                    print("\n检查列表数据中的家长联系方式字段:")
                    print(f"  姓名: {latest_record.get('name', 'N/A')}")
                    print(f"  家长手机: {latest_record.get('parent_phone', 'N/A')}")
                    print(f"  家长微信: {latest_record.get('parent_wechat', 'N/A')}")
                    print(f"  家长邮箱: {latest_record.get('parent_email', 'N/A')}")
                    
                    # 2. 测试获取单个问卷详情
                    print(f"\n2. 测试获取问卷详情 (ID: {record_id})...")
                    detail_url = f"http://localhost:5002/api/questionnaires/{record_id}"
                    
                    detail_response = session.get(detail_url, timeout=10)
                    print(f"状态码: {detail_response.status_code}")
                    
                    if detail_response.status_code == 200:
                        detail_data = detail_response.json()
                        print(f"✅ 获取问卷详情成功")
                        
                        # 检查详情数据中的家长联系方式
                        print("\n检查详情数据中的家长联系方式字段:")
                        basic_info = detail_data.get('basic_info', {})
                        print(f"  姓名: {basic_info.get('name', 'N/A')}")
                        print(f"  性别: {basic_info.get('gender', 'N/A')}")
                        print(f"  出生日期: {basic_info.get('birth_date', 'N/A')}")
                        print(f"  家长手机: {basic_info.get('parent_phone', 'N/A')}")
                        print(f"  家长微信: {basic_info.get('parent_wechat', 'N/A')}")
                        print(f"  家长邮箱: {basic_info.get('parent_email', 'N/A')}")
                        
                        # 验证数据完整性
                        required_fields = ['parent_phone', 'parent_wechat', 'parent_email']
                        missing_fields = []
                        
                        for field in required_fields:
                            if not basic_info.get(field):
                                missing_fields.append(field)
                        
                        if missing_fields:
                            print(f"\n⚠️  缺少字段: {', '.join(missing_fields)}")
                        else:
                            print(f"\n✅ 所有家长联系方式字段都存在且有值")
                            
                        return True
                    else:
                        print(f"❌ 获取问卷详情失败")
                        print(f"错误信息: {detail_response.text}")
                else:
                    print("❌ 未找到家长访谈表记录")
            else:
                print("❌ 响应数据格式异常，缺少questionnaires字段")
        else:
            print(f"❌ 获取问卷列表失败")
            print(f"错误信息: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误: 无法连接到服务器，请确保Flask服务器正在运行")
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        
    return False

def test_search_and_filter():
    """测试搜索和筛选功能"""
    print("\n=== 搜索和筛选功能测试 ===")
    
    # 先登录获取会话
    session = login_to_api()
    if not session:
        print("❌ 无法登录，跳过搜索测试")
        return False
    
    try:
        # 测试按类型筛选
        print("\n测试按类型筛选家长访谈表...")
        filter_url = "http://localhost:5002/api/questionnaires?type=parent_interview"
        
        response = session.get(filter_url, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            questionnaires = data.get('questionnaires', [])
            print(f"✅ 筛选成功，找到 {len(questionnaires)} 条家长访谈表记录")
            
            # 检查筛选结果中的家长联系方式字段
            if questionnaires:
                sample_record = questionnaires[0]
                print("\n样本记录的家长联系方式:")
                print(f"  家长手机: {sample_record.get('parent_phone', 'N/A')}")
                print(f"  家长微信: {sample_record.get('parent_wechat', 'N/A')}")
                print(f"  家长邮箱: {sample_record.get('parent_email', 'N/A')}")
                
            return True
        else:
            print(f"❌ 筛选失败")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 搜索测试发生错误: {e}")
        
    return False

if __name__ == "__main__":
    # 运行测试
    success1 = test_api_data_reading()
    success2 = test_search_and_filter()
    
    print("\n=== 测试总结 ===")
    if success1 and success2:
        print("✅ 所有API数据读取测试通过")
        print("✅ 后端API能正确读取和返回家长联系方式数据")
    else:
        print("❌ 部分测试失败，请检查API实现")