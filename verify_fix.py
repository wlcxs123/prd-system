#!/usr/bin/env python3
"""
验证Frankfurt Scale提交功能修复
"""

import os
import re
import sys

def check_file_exists():
    """检查文件是否存在"""
    file_path = "Frankfurt Scale of Selective Mutism.html"
    if not os.path.exists(file_path):
        print("❌ Frankfurt Scale of Selective Mutism.html 文件不存在")
        return False
    
    print("✅ Frankfurt Scale of Selective Mutism.html 文件存在")
    return True

def check_submit_button():
    """检查是否添加了提交按钮"""
    file_path = "Frankfurt Scale of Selective Mutism.html"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查提交按钮
        if 'onclick="submitToServer()"' in content:
            print("✅ 找到提交按钮")
            
            # 计算提交按钮数量
            button_count = content.count('onclick="submitToServer()"')
            print(f"✅ 提交按钮数量: {button_count}")
            
            return True
        else:
            print("❌ 未找到提交按钮")
            return False
            
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return False

def check_submit_function():
    """检查是否添加了提交函数"""
    file_path = "Frankfurt Scale of Selective Mutism.html"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查提交函数
        if 'function submitToServer()' in content:
            print("✅ 找到submitToServer函数")
            
            # 检查关键功能
            checks = [
                ('数据验证', 'childEl.value.trim()'),
                ('数据构造', 'submitData = {'),
                ('API调用', 'fetch('),
                ('错误处理', '.catch('),
                ('成功提示', 'toast(')
            ]
            
            all_passed = True
            for check_name, pattern in checks:
                if pattern in content:
                    print(f"✅ {check_name}功能存在")
                else:
                    print(f"❌ {check_name}功能缺失")
                    all_passed = False
            
            return all_passed
        else:
            print("❌ 未找到submitToServer函数")
            return False
            
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return False

def check_server_connection_function():
    """检查服务器连接检查函数"""
    file_path = "Frankfurt Scale of Selective Mutism.html"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'function checkServerConnection()' in content:
            print("✅ 找到checkServerConnection函数")
            return True
        else:
            print("❌ 未找到checkServerConnection函数")
            return False
            
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return False

def check_test_script():
    """检查测试脚本是否存在"""
    test_file = "test_frankfurt_submit.py"
    
    if os.path.exists(test_file):
        print("✅ 测试脚本存在")
        return True
    else:
        print("❌ 测试脚本不存在")
        return False

def check_documentation():
    """检查文档是否存在"""
    doc_file = "frankfurt_submit_fix.md"
    
    if os.path.exists(doc_file):
        print("✅ 修复文档存在")
        return True
    else:
        print("❌ 修复文档不存在")
        return False

def main():
    """主验证函数"""
    print("🔍 验证Frankfurt Scale提交功能修复")
    print("=" * 50)
    
    checks = [
        ("文件存在", check_file_exists),
        ("提交按钮", check_submit_button),
        ("提交函数", check_submit_function),
        ("连接检查", check_server_connection_function),
        ("测试脚本", check_test_script),
        ("修复文档", check_documentation)
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        print(f"\n📋 检查{check_name}:")
        print("-" * 20)
        
        try:
            if check_func():
                passed += 1
        except Exception as e:
            print(f"❌ 检查异常: {e}")
    
    print("\n" + "=" * 50)
    print("📊 验证结果:")
    print("=" * 50)
    
    for i, (check_name, _) in enumerate(checks):
        status = "✅" if i < passed else "❌"
        print(f"{check_name:12}: {status}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有检查通过！修复成功")
        print("\n📝 下一步:")
        print("1. 启动后端服务: cd backend && python app.py")
        print("2. 运行测试: python test_frankfurt_submit.py")
        print("3. 打开问卷页面测试提交功能")
        return True
    else:
        print(f"\n⚠️ {total - passed} 项检查失败")
        print("\n🔧 请检查修复是否完整")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ 验证被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 验证异常: {e}")
        sys.exit(1)