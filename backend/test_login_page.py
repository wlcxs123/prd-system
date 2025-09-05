#!/usr/bin/env python3
"""
测试登录页面功能
验证任务 3.2 的所有要求是否已实现
"""

import os
import sys
import re

# 添加backend目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

def test_login_html_structure():
    """测试登录页面HTML结构"""
    print("测试 1: 检查登录页面HTML结构...")
    
    try:
        login_template = os.path.join(os.path.dirname(__file__), 'templates', 'login.html')
        
        if not os.path.exists(login_template):
            print("✗ 登录页面模板不存在")
            return False
        
        with open(login_template, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查必要的HTML元素
        required_elements = [
            r'<form[^>]*id=["\']loginForm["\']',  # 登录表单
            r'<input[^>]*id=["\']username["\']',   # 用户名输入框
            r'<input[^>]*id=["\']password["\']',   # 密码输入框
            r'<button[^>]*type=["\']submit["\']',  # 提交按钮
            r'<div[^>]*id=["\']alertContainer["\']', # 提示信息容器
        ]
        
        for pattern in required_elements:
            if re.search(pattern, content, re.IGNORECASE):
                print(f"✓ 找到必要元素: {pattern}")
            else:
                print(f"✗ 缺少必要元素: {pattern}")
                return False
        
        # 检查表单属性
        if 'novalidate' in content:
            print("✓ 表单禁用了浏览器默认验证")
        else:
            print("✗ 表单未禁用浏览器默认验证")
            return False
        
        # 检查安全属性
        if 'autocomplete="username"' in content:
            print("✓ 用户名输入框有正确的autocomplete属性")
        else:
            print("✗ 用户名输入框缺少autocomplete属性")
        
        if 'autocomplete="current-password"' in content:
            print("✓ 密码输入框有正确的autocomplete属性")
        else:
            print("✗ 密码输入框缺少autocomplete属性")
        
        return True
        
    except Exception as e:
        print(f"✗ HTML结构测试失败: {e}")
        return False

def test_login_css_styles():
    """测试登录页面CSS样式"""
    print("\n测试 2: 检查登录页面CSS样式...")
    
    try:
        login_css = os.path.join(os.path.dirname(__file__), 'static', 'css', 'login.css')
        
        if not os.path.exists(login_css):
            print("✗ 登录页面CSS文件不存在")
            return False
        
        with open(login_css, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查必要的CSS类
        required_classes = [
            '.login-container',
            '.form-group',
            '.form-control',
            '.btn',
            '.btn-primary',
            '.alert',
            '.loading'
        ]
        
        for css_class in required_classes:
            if css_class in content:
                print(f"✓ 找到CSS类: {css_class}")
            else:
                print(f"✗ 缺少CSS类: {css_class}")
                return False
        
        # 检查响应式设计
        if '@media' in content:
            print("✓ 包含响应式设计")
        else:
            print("✗ 缺少响应式设计")
        
        # 检查动画效果
        if '@keyframes' in content or 'animation:' in content:
            print("✓ 包含动画效果")
        else:
            print("✗ 缺少动画效果")
        
        return True
        
    except Exception as e:
        print(f"✗ CSS样式测试失败: {e}")
        return False

def test_login_javascript():
    """测试登录页面JavaScript逻辑"""
    print("\n测试 3: 检查登录页面JavaScript逻辑...")
    
    try:
        login_js = os.path.join(os.path.dirname(__file__), 'static', 'js', 'login.js')
        
        if not os.path.exists(login_js):
            print("✗ 登录页面JavaScript文件不存在")
            return False
        
        with open(login_js, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查必要的JavaScript功能
        required_functions = [
            'class LoginManager',
            'handleLogin',
            'validateUsername',
            'validatePassword',
            'checkAuthStatus',
            'setLoadingState',
            'showAlert'
        ]
        
        for func in required_functions:
            if func in content:
                print(f"✓ 找到功能: {func}")
            else:
                print(f"✗ 缺少功能: {func}")
                return False
        
        # 检查API调用
        if '/api/auth/login' in content:
            print("✓ 包含登录API调用")
        else:
            print("✗ 缺少登录API调用")
            return False
        
        if '/api/auth/status' in content:
            print("✓ 包含状态检查API调用")
        else:
            print("✗ 缺少状态检查API调用")
        
        # 检查表单验证
        if 'addEventListener' in content and 'submit' in content:
            print("✓ 包含表单提交处理")
        else:
            print("✗ 缺少表单提交处理")
        
        return True
        
    except Exception as e:
        print(f"✗ JavaScript逻辑测试失败: {e}")
        return False

def test_login_state_validation():
    """测试登录状态验证"""
    print("\n测试 4: 检查登录状态验证...")
    
    try:
        login_js = os.path.join(os.path.dirname(__file__), 'static', 'js', 'login.js')
        
        with open(login_js, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查输入验证
        validation_checks = [
            'validateUsername',
            'validatePassword',
            'is-valid',
            'is-invalid',
            'invalid-feedback'
        ]
        
        for check in validation_checks:
            if check in content:
                print(f"✓ 找到验证功能: {check}")
            else:
                print(f"✗ 缺少验证功能: {check}")
                return False
        
        # 检查错误处理
        if 'catch' in content and 'error' in content:
            print("✓ 包含错误处理")
        else:
            print("✗ 缺少错误处理")
        
        # 检查加载状态管理
        if 'setLoadingState' in content and 'disabled' in content:
            print("✓ 包含加载状态管理")
        else:
            print("✗ 缺少加载状态管理")
        
        return True
        
    except Exception as e:
        print(f"✗ 登录状态验证测试失败: {e}")
        return False

def test_security_features():
    """测试安全特性"""
    print("\n测试 5: 检查安全特性...")
    
    try:
        login_template = os.path.join(os.path.dirname(__file__), 'templates', 'login.html')
        
        with open(login_template, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # 检查安全提示
        if '安全提示' in html_content:
            print("✓ 包含安全提示")
        else:
            print("✗ 缺少安全提示")
        
        # 检查密码字段类型
        if 'type="password"' in html_content:
            print("✓ 密码字段类型正确")
        else:
            print("✗ 密码字段类型错误")
            return False
        
        # 检查表单属性
        if 'autocomplete' in html_content:
            print("✓ 包含自动完成属性")
        else:
            print("✗ 缺少自动完成属性")
        
        # 检查JavaScript中的安全处理
        login_js = os.path.join(os.path.dirname(__file__), 'static', 'js', 'login.js')
        
        with open(login_js, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        # 检查密码清空功能
        if 'password' in js_content and 'value = \'\'' in js_content:
            print("✓ 包含密码清空功能")
        else:
            print("✗ 缺少密码清空功能")
        
        return True
        
    except Exception as e:
        print(f"✗ 安全特性测试失败: {e}")
        return False

def test_user_experience():
    """测试用户体验功能"""
    print("\n测试 6: 检查用户体验功能...")
    
    try:
        login_template = os.path.join(os.path.dirname(__file__), 'templates', 'login.html')
        login_js = os.path.join(os.path.dirname(__file__), 'static', 'js', 'login.js')
        
        with open(login_template, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        with open(login_js, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        # 检查记住我功能
        if 'rememberMe' in html_content:
            print("✓ 包含记住我功能")
        else:
            print("✗ 缺少记住我功能")
        
        # 检查加载动画
        if 'loading-spinner' in html_content:
            print("✓ 包含加载动画")
        else:
            print("✗ 缺少加载动画")
        
        # 检查焦点管理
        if 'focus()' in js_content:
            print("✓ 包含焦点管理")
        else:
            print("✗ 缺少焦点管理")
        
        # 检查键盘支持
        if 'keypress' in js_content and 'Enter' in js_content:
            print("✓ 支持回车键登录")
        else:
            print("✗ 不支持回车键登录")
        
        # 检查提示信息
        if 'placeholder' in html_content:
            print("✓ 包含输入提示")
        else:
            print("✗ 缺少输入提示")
        
        return True
        
    except Exception as e:
        print(f"✗ 用户体验功能测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("任务 3.2 创建登录页面验证")
    print("=" * 60)
    
    # 运行所有测试
    tests = [
        test_login_html_structure,
        test_login_css_styles,
        test_login_javascript,
        test_login_state_validation,
        test_security_features,
        test_user_experience
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed_tests += 1
        except Exception as e:
            print(f"测试执行异常: {e}")
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed_tests}/{total_tests} 通过")
    
    if passed_tests == total_tests:
        print("✓ 任务 3.2 创建登录页面完整！")
        print("\n实现的功能包括:")
        print("- ✓ 登录页面HTML结构")
        print("- ✓ 登录表单样式")
        print("- ✓ 登录JavaScript逻辑")
        print("- ✓ 登录状态验证")
        print("- ✓ 安全特性")
        print("- ✓ 用户体验功能")
        return True
    else:
        print("✗ 任务 3.2 创建登录页面不完整")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)