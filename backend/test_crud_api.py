#!/usr/bin/env python3
"""
测试问卷数据 CRUD API 接口
验证任务 4.1 的实现
"""

import requests
import json
import sys
from datetime import datetime

# API 基础URL
BASE_URL = "http://localhost:5000"

def test_submit_questionnaire():
    """测试问卷提交 API (POST /api/submit)"""
    print("测试问卷提交 API...")
    
    # 测试数据
    test_data = {
        "type": "test_questionnaire",
        "basic_info": {
            "name": "测试学生",
            "grade": "三年级",
            "submission_date": "2024-01-15"
        },
        "questions": [
            {
                "id": 1,
                "type": "multiple_choice",
                "question": "你喜欢什么颜色？",
                "options": [
                    {"value": 0, "text": "红色"},
                    {"value": 1, "text": "蓝色"},
                    {"value": 2, "text": "绿色"}
                ],
                "selected": [1],
                "can_speak": True
            },
            {
                "id": 2,
                "type": "text_input",
                "question": "请描述你的爱好",
                "answer": "我喜欢阅读和画画"
            }
        ],
        "statistics": {
            "total_score": 85,
            "completion_rate": 100,
            "submission_time": datetime.now().isoformat()
        }
    }
    
    try:
        # 测试 POST /api/submit
        response = requests.post(f"{BASE_URL}/api/submit", json=test_data)
        print(f"POST /api/submit - 状态码: {response.status_code}")
        
        if response.status_code == 404:
            print("❌ /api/submit 端点不存在，需要创建")
            return False
        elif response.status_code == 201:
            result = response.json()
            print(f"✅ 问卷提交成功，ID: {result.get('id')}")
            return result.get('id')
        else:
            print(f"❌ 提交失败: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保 Flask 应用正在运行")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_questionnaires_crud():
    """测试问卷 CRUD API"""
    print("\n测试问卷 CRUD API...")
    
    # 首先需要登录获取会话
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    session = requests.Session()
    
    try:
        # 登录
        login_response = session.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if login_response.status_code != 200:
            print(f"❌ 登录失败: {login_response.text}")
            return False
        
        print("✅ 登录成功")
        
        # 测试获取问卷列表 (GET /api/questionnaires)
        response = session.get(f"{BASE_URL}/api/questionnaires")
        print(f"GET /api/questionnaires - 状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 获取问卷列表成功，共 {len(result.get('data', []))} 条记录")
            questionnaires = result.get('data', [])
            
            if questionnaires:
                # 测试获取单个问卷详情 (GET /api/questionnaires/{id})
                first_id = questionnaires[0]['id']
                detail_response = session.get(f"{BASE_URL}/api/questionnaires/{first_id}")
                print(f"GET /api/questionnaires/{first_id} - 状态码: {detail_response.status_code}")
                
                if detail_response.status_code == 200:
                    print("✅ 获取问卷详情成功")
                else:
                    print(f"❌ 获取问卷详情失败: {detail_response.text}")
                
                # 测试更新问卷 (PUT /api/questionnaires/{id})
                update_data = questionnaires[0]['data']
                update_data['basic_info']['name'] = "更新后的姓名"
                
                update_response = session.put(f"{BASE_URL}/api/questionnaires/{first_id}", json=update_data)
                print(f"PUT /api/questionnaires/{first_id} - 状态码: {update_response.status_code}")
                
                if update_response.status_code == 200:
                    print("✅ 更新问卷成功")
                else:
                    print(f"❌ 更新问卷失败: {update_response.text}")
                
                # 测试删除问卷 (DELETE /api/questionnaires/{id})
                # 注意：这会实际删除数据，在生产环境中要小心
                # delete_response = session.delete(f"{BASE_URL}/api/questionnaires/{first_id}")
                # print(f"DELETE /api/questionnaires/{first_id} - 状态码: {delete_response.status_code}")
                print("⚠️  跳过删除测试以保护数据")
            
        else:
            print(f"❌ 获取问卷列表失败: {response.text}")
            return False
            
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保 Flask 应用正在运行")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试问卷数据 CRUD API 接口...")
    print("=" * 50)
    
    # 测试 /api/submit 端点
    submit_result = test_submit_questionnaire()
    
    # 测试其他 CRUD 端点
    crud_result = test_questionnaires_crud()
    
    print("\n" + "=" * 50)
    print("测试总结:")
    print(f"- /api/submit 端点: {'✅ 通过' if submit_result else '❌ 失败'}")
    print(f"- CRUD API 端点: {'✅ 通过' if crud_result else '❌ 失败'}")
    
    if not submit_result:
        print("\n需要创建 /api/submit 端点")
    
    return submit_result and crud_result

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)