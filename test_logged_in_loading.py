#!/usr/bin/env python3
"""
测试已登录状态下的数据加载问题
"""

import requests
import json

def login_and_get_session():
    """登录并获取session"""
    
    print("=== 登录获取session ===")
    
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    session = requests.Session()
    
    try:
        response = session.post(
            'http://127.0.0.1:5000/api/auth/login',
            json=login_data,
            headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
            timeout=10
        )
        
        print(f"登录响应状态码: {response.status_code}")
        
        if response.ok:
            result = response.json()
            if result.get('success'):
                print("✅ 登录成功")
                print(f"用户信息: {result.get('user', {})}")
                return session
            else:
                print(f"❌ 登录失败: {result.get('message', '未知错误')}")
                return None
        else:
            print(f"❌ 登录HTTP错误: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 登录请求失败: {e}")
        return None

def test_questionnaires_api_with_session(session):
    """使用session测试问卷API"""
    
    print("\n=== 测试问卷API (已登录) ===")
    
    try:
        # 测试基本的问卷列表API
        response = session.get(
            'http://127.0.0.1:5000/api/questionnaires',
            headers={'Accept': 'application/json'},
            timeout=10
        )
        
        print(f"问卷API响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.ok:
            result = response.json()
            print("✅ 问卷API调用成功")
            print(f"响应数据结构: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # 分析响应数据结构
            if 'data' in result:
                questionnaires = result['data']
                print(f"问卷数量: {len(questionnaires)}")
                print(f"总记录数: {result.get('total', 'N/A')}")
                print(f"当前页: {result.get('page', 'N/A')}")
                print(f"每页数量: {result.get('limit', 'N/A')}")
                
                if len(questionnaires) > 0:
                    print("\n前3个问卷详情:")
                    for i, q in enumerate(questionnaires[:3]):
                        print(f"  {i+1}. ID: {q.get('id')}, 姓名: {q.get('name')}, 类型: {q.get('type')}, 创建时间: {q.get('created_at')}")
                else:
                    print("❌ 问卷列表为空")
                    
                return True, result
            else:
                print("❌ 响应数据格式不正确，缺少'data'字段")
                return False, result
        else:
            print(f"❌ 问卷API调用失败: {response.status_code}")
            try:
                error_data = response.json()
                print(f"错误详情: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"错误文本: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ 问卷API请求失败: {e}")
        return False, None

def test_different_api_parameters(session):
    """测试不同的API参数"""
    
    print("\n=== 测试不同API参数 ===")
    
    test_cases = [
        {"name": "默认参数", "params": {}},
        {"name": "指定页码", "params": {"page": 1, "limit": 10}},
        {"name": "搜索参数", "params": {"search": ""}},
        {"name": "类型筛选", "params": {"type": "elementary_school_communication_assessment"}},
        {"name": "排序参数", "params": {"sort_by": "created_at", "sort_order": "desc"}},
    ]
    
    for test_case in test_cases:
        print(f"\n测试: {test_case['name']}")
        try:
            response = session.get(
                'http://127.0.0.1:5000/api/questionnaires',
                params=test_case['params'],
                headers={'Accept': 'application/json'},
                timeout=10
            )
            
            print(f"  状态码: {response.status_code}")
            
            if response.ok:
                result = response.json()
                if 'data' in result:
                    print(f"  ✅ 成功，返回 {len(result['data'])} 条记录")
                else:
                    print(f"  ❌ 响应格式错误")
            else:
                print(f"  ❌ 失败: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ 请求失败: {e}")

def test_auth_status_with_session(session):
    """测试认证状态"""
    
    print("\n=== 测试认证状态 (已登录) ===")
    
    try:
        response = session.get(
            'http://127.0.0.1:5000/api/auth/status',
            headers={'Accept': 'application/json'},
            timeout=10
        )
        
        print(f"认证状态响应码: {response.status_code}")
        
        if response.ok:
            result = response.json()
            print(f"认证状态: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result.get('authenticated'):
                print("✅ 用户已认证")
                return True
            else:
                print("❌ 用户未认证 - 这可能是问题所在")
                return False
        else:
            print(f"❌ 认证状态检查失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 认证状态检查失败: {e}")
        return False

def check_database_directly():
    """直接检查数据库"""
    
    print("\n=== 直接检查数据库 ===")
    
    try:
        import sqlite3
        import os
        
        db_path = 'backend/questionnaires.db'
        if not os.path.exists(db_path):
            print(f"❌ 数据库文件不存在: {db_path}")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查questionnaires表的结构
        cursor.execute("PRAGMA table_info(questionnaires)")
        columns = cursor.fetchall()
        print("数据库表结构:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # 检查数据
        cursor.execute("SELECT COUNT(*) FROM questionnaires")
        total_count = cursor.fetchone()[0]
        print(f"\n总记录数: {total_count}")
        
        if total_count > 0:
            cursor.execute("SELECT id, name, type, created_at FROM questionnaires ORDER BY created_at DESC LIMIT 5")
            rows = cursor.fetchall()
            print("\n最新5条记录:")
            for row in rows:
                print(f"  ID: {row[0]}, 姓名: {row[1]}, 类型: {row[2]}, 创建时间: {row[3]}")
        
        conn.close()
        return total_count > 0
        
    except Exception as e:
        print(f"❌ 数据库检查失败: {e}")
        return False

def test_raw_api_call():
    """测试原始API调用（模拟浏览器）"""
    
    print("\n=== 模拟浏览器API调用 ===")
    
    # 首先登录获取cookies
    session = requests.Session()
    
    # 登录
    login_response = session.post(
        'http://127.0.0.1:5000/api/auth/login',
        json={"username": "admin", "password": "admin123"},
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    )
    
    if not login_response.ok:
        print("❌ 登录失败")
        return False
    
    print("✅ 登录成功，模拟浏览器请求...")
    
    # 模拟浏览器的API调用
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Referer': 'http://127.0.0.1:5000/admin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    try:
        response = session.get(
            'http://127.0.0.1:5000/api/questionnaires',
            headers=headers,
            timeout=10
        )
        
        print(f"浏览器模拟请求状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应大小: {len(response.content)} 字节")
        
        if response.ok:
            try:
                result = response.json()
                print("✅ JSON解析成功")
                print(f"数据结构: {list(result.keys()) if isinstance(result, dict) else type(result)}")
                
                if isinstance(result, dict) and 'data' in result:
                    print(f"问卷数量: {len(result['data'])}")
                    return True
                else:
                    print("❌ 数据结构不正确")
                    print(f"完整响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
                    return False
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析失败: {e}")
                print(f"响应内容: {response.text[:500]}...")
                return False
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

if __name__ == "__main__":
    print("诊断已登录状态下的数据加载问题...")
    
    # 1. 检查数据库
    db_ok = check_database_directly()
    
    # 2. 登录并获取session
    session = login_and_get_session()
    
    if session:
        # 3. 测试认证状态
        auth_ok = test_auth_status_with_session(session)
        
        # 4. 测试问卷API
        api_ok, api_result = test_questionnaires_api_with_session(session)
        
        # 5. 测试不同参数
        test_different_api_parameters(session)
        
        # 6. 模拟浏览器请求
        browser_ok = test_raw_api_call()
        
        print("\n=== 诊断结果 ===")
        print(f"数据库有数据: {'✅' if db_ok else '❌'}")
        print(f"登录成功: {'✅' if session else '❌'}")
        print(f"认证状态正常: {'✅' if auth_ok else '❌'}")
        print(f"API调用成功: {'✅' if api_ok else '❌'}")
        print(f"浏览器模拟成功: {'✅' if browser_ok else '❌'}")
        
        if not api_ok:
            print("\n💡 可能的问题:")
            print("1. API响应格式与前端期望不匹配")
            print("2. 前端JavaScript处理逻辑有问题")
            print("3. 浏览器缓存或Cookie问题")
            print("4. CORS或其他网络问题")
            
        if api_result:
            print(f"\n📊 API响应数据样本:")
            print(json.dumps(api_result, indent=2, ensure_ascii=False))
    else:
        print("\n❌ 无法获取有效session，请检查登录功能")