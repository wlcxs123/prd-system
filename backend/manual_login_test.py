#!/usr/bin/env python3
"""
手动登录功能测试
启动服务器并提供测试说明
"""

import os
import sys
import subprocess
import time
import webbrowser

def main():
    print("=" * 60)
    print("用户认证系统手动测试")
    print("=" * 60)
    
    print("\n1. 启动Flask服务器...")
    print("   访问地址: http://localhost:5000")
    print("   登录页面: http://localhost:5000/login")
    print("   管理页面: http://localhost:5000/admin")
    
    print("\n2. 测试账号:")
    print("   用户名: admin")
    print("   密码: admin123")
    
    print("\n3. 测试步骤:")
    print("   a) 访问 http://localhost:5000 (应该重定向到登录页面)")
    print("   b) 输入用户名和密码")
    print("   c) 点击登录按钮")
    print("   d) 验证是否成功跳转到管理页面")
    print("   e) 测试登出功能")
    
    print("\n4. 预期行为:")
    print("   - 未登录时访问 /admin 应重定向到 /login")
    print("   - 登录成功后应跳转到 /admin")
    print("   - 已登录时访问 /login 应重定向到 /admin")
    print("   - 登出后应清除会话")
    
    print("\n按 Ctrl+C 停止服务器")
    print("=" * 60)
    
    try:
        # 启动Flask应用
        os.chdir(os.path.dirname(__file__))
        subprocess.run([sys.executable, 'app.py'], check=True)
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"启动服务器失败: {e}")

if __name__ == '__main__':
    main()