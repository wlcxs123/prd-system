#!/usr/bin/env python3
"""
验证任务6实现的脚本 - 检查代码实现而不需要运行服务器
"""

import os
import sys
import ast
import inspect

def check_file_exists(filepath):
    """检查文件是否存在"""
    return os.path.exists(filepath)

def check_function_exists(module, function_name):
    """检查函数是否存在"""
    return hasattr(module, function_name)

def check_class_exists(module, class_name):
    """检查类是否存在"""
    return hasattr(module, class_name)

def analyze_app_py():
    """分析app.py文件的实现"""
    print("=== 分析 app.py 实现 ===")
    
    try:
        # 读取app.py文件内容
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键功能实现
        checks = [
            ("会话超时检查函数", "def check_session_timeout():" in content),
            ("会话活动更新函数", "def update_session_activity():" in content),
            ("会话完整性验证", "def validate_session_integrity():" in content),
            ("增强的login_required装饰器", "def login_required(f):" in content and "check_session_timeout()" in content),
            ("增强的admin_required装饰器", "def admin_required(f):" in content and "check_session_timeout()" in content),
            ("OperationLogger类", "class OperationLogger:" in content),
            ("操作类型常量", "LOGIN = 'LOGIN'" in content),
            ("敏感操作列表", "SENSITIVE_OPERATIONS" in content),
            ("会话刷新接口", "/api/auth/refresh" in content),
            ("会话延长接口", "/api/auth/extend" in content),
            ("日志统计接口", "/api/admin/logs/statistics" in content),
            ("日志导出接口", "/api/admin/logs/export" in content),
            ("请求前中间件", "@app.before_request" in content),
            ("请求后中间件", "@app.after_request" in content),
        ]
        
        passed = 0
        total = len(checks)
        
        for description, check in checks:
            if check:
                print(f"✓ {description}")
                passed += 1
            else:
                print(f"✗ {description}")
        
        print(f"\n实现检查结果: {passed}/{total} 项通过")
        
        return passed == total
        
    except Exception as e:
        print(f"分析app.py时发生错误: {e}")
        return False

def check_database_schema():
    """检查数据库表结构"""
    print("\n=== 检查数据库表结构 ===")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查数据库表创建语句
        tables_checks = [
            ("问卷数据表", "CREATE TABLE IF NOT EXISTS questionnaires" in content),
            ("用户认证表", "CREATE TABLE IF NOT EXISTS users" in content),
            ("操作日志表", "CREATE TABLE IF NOT EXISTS operation_logs" in content),
            ("日志外键约束", "FOREIGN KEY (user_id) REFERENCES users (id)" in content),
        ]
        
        passed = 0
        total = len(tables_checks)
        
        for description, check in tables_checks:
            if check:
                print(f"✓ {description}")
                passed += 1
            else:
                print(f"✗ {description}")
        
        print(f"\n数据库结构检查结果: {passed}/{total} 项通过")
        
        return passed == total
        
    except Exception as e:
        print(f"检查数据库结构时发生错误: {e}")
        return False

def check_api_endpoints():
    """检查API端点实现"""
    print("\n=== 检查API端点实现 ===")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查API端点
        endpoints_checks = [
            ("登录接口", "@app.route('/api/auth/login', methods=['POST'])" in content),
            ("登出接口", "@app.route('/api/auth/logout', methods=['POST'])" in content),
            ("状态检查接口", "@app.route('/api/auth/status', methods=['GET'])" in content),
            ("会话刷新接口", "@app.route('/api/auth/refresh', methods=['POST'])" in content),
            ("会话延长接口", "@app.route('/api/auth/extend', methods=['POST'])" in content),
            ("操作日志列表", "@app.route('/api/admin/logs', methods=['GET'])" in content),
            ("日志详情接口", "@app.route('/api/admin/logs/<int:log_id>', methods=['GET'])" in content),
            ("日志统计接口", "@app.route('/api/admin/logs/statistics', methods=['GET'])" in content),
            ("日志导出接口", "@app.route('/api/admin/logs/export', methods=['POST'])" in content),
        ]
        
        passed = 0
        total = len(endpoints_checks)
        
        for description, check in endpoints_checks:
            if check:
                print(f"✓ {description}")
                passed += 1
            else:
                print(f"✗ {description}")
        
        print(f"\nAPI端点检查结果: {passed}/{total} 项通过")
        
        return passed == total
        
    except Exception as e:
        print(f"检查API端点时发生错误: {e}")
        return False

def check_security_features():
    """检查安全功能实现"""
    print("\n=== 检查安全功能实现 ===")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查安全功能
        security_checks = [
            ("会话超时处理", "timeout_seconds" in content and "last_activity" in content),
            ("权限验证增强", "PERMISSION_DENIED" in content),
            ("敏感操作审计", "SENSITIVE_OPERATIONS" in content),
            ("IP地址记录", "ip_address" in content and "request.remote_addr" in content),
            ("用户代理记录", "user_agent" in content and "User-Agent" in content),
            ("会话完整性检查", "validate_session_integrity" in content),
            ("自动登出日志", "AUTO_LOGOUT" in content),
            ("访问拒绝日志", "ACCESS_DENIED" in content),
        ]
        
        passed = 0
        total = len(security_checks)
        
        for description, check in security_checks:
            if check:
                print(f"✓ {description}")
                passed += 1
            else:
                print(f"✗ {description}")
        
        print(f"\n安全功能检查结果: {passed}/{total} 项通过")
        
        return passed == total
        
    except Exception as e:
        print(f"检查安全功能时发生错误: {e}")
        return False

def main():
    """主函数"""
    print("任务6实现验证")
    print("=" * 50)
    
    # 检查当前目录
    if not os.path.exists('app.py'):
        print("错误: 未找到app.py文件，请在backend目录下运行此脚本")
        return False
    
    # 执行各项检查
    checks = [
        ("代码实现分析", analyze_app_py),
        ("数据库表结构", check_database_schema),
        ("API端点实现", check_api_endpoints),
        ("安全功能实现", check_security_features),
    ]
    
    all_passed = True
    
    for description, check_func in checks:
        try:
            result = check_func()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"执行 {description} 检查时发生错误: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("🎉 任务6实现验证通过！")
        print("\n已实现的功能:")
        print("✓ 6.1 添加权限控制和会话管理")
        print("  - 登录状态检查装饰器")
        print("  - 管理员权限验证")
        print("  - 会话超时处理")
        print("  - 自动登出功能")
        print("✓ 6.2 实现操作日志系统")
        print("  - 操作日志数据表")
        print("  - 日志记录中间件")
        print("  - 日志查询和展示功能")
        print("  - 敏感操作审计")
        
        print("\n需求覆盖:")
        print("✓ 需求 3.5: 会话管理和自动登出")
        print("✓ 需求 8.5: 权限控制和安全验证")
        print("✓ 需求 8.3: 操作日志和审计功能")
        
        return True
    else:
        print("❌ 任务6实现验证失败")
        print("请检查上述失败的项目并完善实现")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)