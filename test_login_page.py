#!/usr/bin/env python3
"""
测试登录页面访问
"""

import requests

def test_login_page_access():
    """测试登录页面访问"""
    
    print("=== 测试登录页面访问 ===")
    
    try:
        # 测试访问登录页面
        response = requests.get(
            'http://127.0.0.1:5000/login',
            timeout=10
        )
        
        print(f"登录页面响应状态码: {response.status_code}")
        
        if response.ok:
            print("✅ 登录页面可以正常访问")
            print(f"页面内容长度: {len(response.text)} 字符")
            
            # 检查页面内容
            if "问卷管理系统" in response.text:
                print("✅ 登录页面内容正确")
            else:
                print("❌ 登录页面内容可能有问题")
                
            return True
        else:
            print(f"❌ 登录页面访问失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 登录页面访问失败: {e}")
        return False

def test_root_redirect():
    """测试根路径重定向"""
    
    print("\n=== 测试根路径重定向 ===")
    
    try:
        # 测试访问根路径
        response = requests.get(
            'http://127.0.0.1:5000/',
            allow_redirects=False,  # 不自动跟随重定向
            timeout=10
        )
        
        print(f"根路径响应状态码: {response.status_code}")
        
        if response.status_code in [301, 302, 303, 307, 308]:
            location = response.headers.get('Location', '')
            print(f"✅ 根路径正确重定向到: {location}")
            
            if '/login' in location:
                print("✅ 重定向到登录页面")
                return True
            else:
                print("❌ 重定向目标不是登录页面")
                return False
        else:
            print(f"❌ 根路径没有重定向: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 根路径测试失败: {e}")
        return False

def test_admin_page_redirect():
    """测试管理页面重定向"""
    
    print("\n=== 测试管理页面访问（未登录） ===")
    
    try:
        # 测试访问管理页面
        response = requests.get(
            'http://127.0.0.1:5000/admin',
            allow_redirects=False,
            timeout=10
        )
        
        print(f"管理页面响应状态码: {response.status_code}")
        
        if response.status_code in [301, 302, 303, 307, 308]:
            location = response.headers.get('Location', '')
            print(f"✅ 管理页面正确重定向到: {location}")
            
            if '/login' in location:
                print("✅ 未登录用户被重定向到登录页面")
                return True
            else:
                print("❌ 重定向目标不是登录页面")
                return False
        else:
            print(f"❌ 管理页面没有重定向: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 管理页面测试失败: {e}")
        return False

if __name__ == "__main__":
    print("测试登录相关页面...")
    
    login_page_ok = test_login_page_access()
    root_redirect_ok = test_root_redirect()
    admin_redirect_ok = test_admin_page_redirect()
    
    print("\n=== 测试结果 ===")
    print(f"登录页面正常: {'✅' if login_page_ok else '❌'}")
    print(f"根路径重定向正常: {'✅' if root_redirect_ok else '❌'}")
    print(f"管理页面重定向正常: {'✅' if admin_redirect_ok else '❌'}")
    
    if all([login_page_ok, root_redirect_ok, admin_redirect_ok]):
        print("\n🎉 登录系统工作正常！")
        print("\n💡 解决'加载中'问题的步骤:")
        print("1. 在浏览器中访问: http://127.0.0.1:5000/login")
        print("2. 使用以下凭据登录:")
        print("   用户名: admin")
        print("   密码: admin123")
        print("3. 登录成功后即可正常查看问卷数据")
    else:
        print("\n❌ 登录系统有问题，需要进一步检查")