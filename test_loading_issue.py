#!/usr/bin/env python3
"""
测试加载问题
"""

import requests
import json

def test_questionnaires_api():
    """测试问卷列表API"""
    
    print("=== 测试问卷列表API ===")
    
    try:
        # 测试不带认证的请求
        response = requests.get(
            'http://127.0.0.1:5000/api/questionnaires',
            headers={'Accept': 'application/json'},
            timeout=10
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 401:
            print("❌ 需要认证 - 这可能是加载问题的原因")
            result = response.json()
            print(f"错误详情: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return False
        elif response.ok:
            result = response.json()
            print(f"✅ 成功获取数据")
            print(f"响应数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            try:
                result = response.json()
                print(f"错误详情: {json.dumps(result, indent=2, ensure_ascii=False)}")
            except:
                print(f"错误文本: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_auth_status():
    """测试认证状态API"""
    
    print("\n=== 测试认证状态API ===")
    
    try:
        response = requests.get(
            'http://127.0.0.1:5000/api/auth/status',
            headers={'Accept': 'application/json'},
            timeout=10
        )
        
        print(f"响应状态码: {response.status_code}")
        
        if response.ok:
            result = response.json()
            print(f"认证状态: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return result.get('authenticated', False)
        else:
            print(f"❌ 认证状态检查失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 认证状态检查失败: {e}")
        return False

def test_login():
    """测试登录"""
    
    print("\n=== 测试登录 ===")
    
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            'http://127.0.0.1:5000/api/auth/login',
            json=login_data,
            headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
            timeout=10
        )
        
        print(f"登录响应状态码: {response.status_code}")
        
        if response.ok:
            result = response.json()
            print(f"✅ 登录成功")
            print(f"登录结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # 获取session cookie
            session_cookie = response.cookies.get('session')
            if session_cookie:
                print(f"✅ 获得session cookie: {session_cookie[:20]}...")
                return session_cookie
            else:
                print("❌ 未获得session cookie")
                return None
        else:
            print(f"❌ 登录失败: {response.status_code}")
            try:
                result = response.json()
                print(f"错误详情: {json.dumps(result, indent=2, ensure_ascii=False)}")
            except:
                print(f"错误文本: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 登录请求失败: {e}")
        return None

def test_questionnaires_with_auth(session_cookie):
    """使用认证测试问卷列表API"""
    
    print("\n=== 使用认证测试问卷列表API ===")
    
    try:
        cookies = {'session': session_cookie} if session_cookie else {}
        
        response = requests.get(
            'http://127.0.0.1:5000/api/questionnaires',
            headers={'Accept': 'application/json'},
            cookies=cookies,
            timeout=10
        )
        
        print(f"响应状态码: {response.status_code}")
        
        if response.ok:
            result = response.json()
            print(f"✅ 成功获取问卷列表")
            
            if 'data' in result:
                questionnaires = result['data']
                print(f"问卷数量: {len(questionnaires)}")
                print(f"总记录数: {result.get('total', 'N/A')}")
                
                if len(questionnaires) > 0:
                    print("前3个问卷:")
                    for i, q in enumerate(questionnaires[:3]):
                        print(f"  {i+1}. ID: {q.get('id')}, 姓名: {q.get('name')}, 类型: {q.get('type')}")
                else:
                    print("❌ 没有问卷数据 - 这可能是'加载中'问题的原因")
            else:
                print(f"响应格式: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            return True
        else:
            print(f"❌ 获取问卷列表失败: {response.status_code}")
            try:
                result = response.json()
                print(f"错误详情: {json.dumps(result, indent=2, ensure_ascii=False)}")
            except:
                print(f"错误文本: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def check_database():
    """检查数据库中是否有数据"""
    
    print("\n=== 检查数据库 ===")
    
    try:
        import sqlite3
        import os
        
        db_path = 'backend/questionnaires.db'
        if not os.path.exists(db_path):
            print(f"❌ 数据库文件不存在: {db_path}")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查questionnaires表
        cursor.execute("SELECT COUNT(*) FROM questionnaires")
        count = cursor.fetchone()[0]
        print(f"数据库中的问卷数量: {count}")
        
        if count > 0:
            cursor.execute("SELECT id, name, type, created_at FROM questionnaires LIMIT 5")
            rows = cursor.fetchall()
            print("前5个问卷:")
            for row in rows:
                print(f"  ID: {row[0]}, 姓名: {row[1]}, 类型: {row[2]}, 创建时间: {row[3]}")
        else:
            print("❌ 数据库中没有问卷数据")
        
        conn.close()
        return count > 0
        
    except Exception as e:
        print(f"❌ 数据库检查失败: {e}")
        return False

if __name__ == "__main__":
    print("诊断'加载中'问题...")
    
    # 1. 检查数据库
    has_data = check_database()
    
    # 2. 检查认证状态
    is_authenticated = test_auth_status()
    
    # 3. 测试问卷API（无认证）
    api_works = test_questionnaires_api()
    
    # 4. 如果需要认证，尝试登录
    session_cookie = None
    if not api_works:
        session_cookie = test_login()
        if session_cookie:
            api_works = test_questionnaires_with_auth(session_cookie)
    
    print("\n=== 诊断结果 ===")
    print(f"数据库有数据: {'✅' if has_data else '❌'}")
    print(f"用户已认证: {'✅' if is_authenticated else '❌'}")
    print(f"API正常工作: {'✅' if api_works else '❌'}")
    
    if not has_data:
        print("\n💡 建议: 数据库中没有数据，这可能是'加载中'问题的原因")
    elif not api_works:
        print("\n💡 建议: API调用失败，可能需要登录或检查权限")
    else:
        print("\n💡 建议: 后端工作正常，问题可能在前端JavaScript或网络连接")