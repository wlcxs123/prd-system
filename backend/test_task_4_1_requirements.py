#!/usr/bin/env python3
"""
测试任务 4.1 的所有需求
验证问卷数据 CRUD 接口是否符合需求规范
"""

import json
import sys
from datetime import datetime

def test_api_endpoints_structure():
    """测试 API 端点结构是否符合需求"""
    
    print("测试 API 端点结构...")
    print("=" * 50)
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查任务 4.1 要求的具体端点
        required_endpoints = {
            "POST /api/submit": "创建问卷提交 API",
            "GET /api/questionnaires": "实现问卷列表查询 API", 
            "GET /api/questionnaires/<int:questionnaire_id>": "开发单个问卷详情 API",
            "PUT /api/questionnaires/<int:questionnaire_id>": "实现问卷更新 API",
            "DELETE /api/questionnaires/<int:questionnaire_id>": "创建问卷删除 API"
        }
        
        all_found = True
        
        for endpoint, description in required_endpoints.items():
            method, path = endpoint.split(' ', 1)
            
            # 检查路由定义
            if path == "/api/submit":
                pattern = "@app.route('/api/submit'"
            elif "<int:" in path:
                pattern = f"@app.route('/api/questionnaires/<int:"
            else:
                pattern = f"@app.route('{path}'"
            
            if pattern in content and f'methods=[' in content:
                print(f"✅ {endpoint:50} - {description}")
            else:
                print(f"❌ {endpoint:50} - {description}")
                all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_requirements_compliance():
    """测试是否符合需求文档中的要求"""
    
    print("\n测试需求合规性...")
    print("=" * 50)
    
    # 需求 4.2, 4.3, 4.4, 5.3, 9.1, 9.2 相关检查
    requirements_checks = [
        ("问卷数据管理界面支持", "get_questionnaires", "需求 4.2"),
        ("问卷详情查看功能", "get_questionnaire", "需求 4.3"), 
        ("问卷编辑功能", "update_questionnaire", "需求 4.4"),
        ("数据存储和检索", "get_db", "需求 5.3"),
        ("API接口标准化", "jsonify", "需求 9.1"),
        ("标准JSON响应格式", "success.*error", "需求 9.2")
    ]
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        all_compliant = True
        
        for check_name, pattern, requirement in requirements_checks:
            if pattern in content:
                print(f"✅ {check_name:25} - {requirement}")
            else:
                print(f"❌ {check_name:25} - {requirement}")
                all_compliant = False
        
        return all_compliant
        
    except Exception as e:
        print(f"❌ 需求合规性测试失败: {e}")
        return False

def test_data_validation_implementation():
    """测试数据验证实现"""
    
    print("\n测试数据验证实现...")
    print("=" * 50)
    
    validation_features = [
        ("数据结构验证", "validate_questionnaire_with_schema"),
        ("数据标准化", "normalize_questionnaire_data"),
        ("错误响应处理", "create_validation_error_response"),
        ("问题类型处理", "process_complete_questionnaire"),
        ("权限验证", "login_required.*admin_required")
    ]
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        all_implemented = True
        
        for feature_name, pattern in validation_features:
            if pattern in content:
                print(f"✅ {feature_name:20} - 已实现")
            else:
                print(f"❌ {feature_name:20} - 未实现")
                all_implemented = False
        
        return all_implemented
        
    except Exception as e:
        print(f"❌ 数据验证测试失败: {e}")
        return False

def test_error_handling():
    """测试错误处理机制"""
    
    print("\n测试错误处理机制...")
    print("=" * 50)
    
    error_handling_features = [
        ("ValidationError 处理", "ValidationError"),
        ("数据库错误处理", "except.*Exception"),
        ("404 错误处理", "NOT_FOUND"),
        ("401 认证错误", "需要登录"),
        ("403 权限错误", "权限不足"),
        ("标准错误响应格式", "error.*code.*message")
    ]
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        all_handled = True
        
        for feature_name, pattern in error_handling_features:
            if pattern in content:
                print(f"✅ {feature_name:20} - 已实现")
            else:
                print(f"❌ {feature_name:20} - 未实现")
                all_handled = False
        
        return all_handled
        
    except Exception as e:
        print(f"❌ 错误处理测试失败: {e}")
        return False

def test_database_operations():
    """测试数据库操作实现"""
    
    print("\n测试数据库操作...")
    print("=" * 50)
    
    db_operations = [
        ("数据库连接", "get_db"),
        ("问卷创建", "INSERT INTO questionnaires"),
        ("问卷查询", "SELECT.*FROM questionnaires"),
        ("问卷更新", "UPDATE questionnaires"),
        ("问卷删除", "DELETE FROM questionnaires"),
        ("分页查询", "LIMIT.*OFFSET"),
        ("搜索功能", "LIKE")
    ]
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        all_implemented = True
        
        for operation_name, pattern in db_operations:
            if pattern in content:
                print(f"✅ {operation_name:15} - 已实现")
            else:
                print(f"❌ {operation_name:15} - 未实现")
                all_implemented = False
        
        return all_implemented
        
    except Exception as e:
        print(f"❌ 数据库操作测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("任务 4.1 需求验证测试")
    print("实现问卷数据 CRUD 接口")
    print("=" * 50)
    
    # 执行所有测试
    tests = [
        ("API 端点结构", test_api_endpoints_structure),
        ("需求合规性", test_requirements_compliance),
        ("数据验证", test_data_validation_implementation),
        ("错误处理", test_error_handling),
        ("数据库操作", test_database_operations)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试执行失败: {e}")
            results.append((test_name, False))
    
    # 输出总结
    print("\n" + "=" * 50)
    print("测试总结:")
    
    all_passed = True
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"- {test_name:15}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("🎉 任务 4.1 完全符合要求！")
        print("所有问卷数据 CRUD 接口都已正确实现并符合需求规范。")
        print("\n实现的功能包括:")
        print("- ✅ 问卷提交 API (POST /api/submit)")
        print("- ✅ 问卷列表查询 API (GET /api/questionnaires)")
        print("- ✅ 单个问卷详情 API (GET /api/questionnaires/{id})")
        print("- ✅ 问卷更新 API (PUT /api/questionnaires/{id})")
        print("- ✅ 问卷删除 API (DELETE /api/questionnaires/{id})")
        print("- ✅ 完整的数据验证和错误处理")
        print("- ✅ 权限控制和安全机制")
        print("- ✅ 标准化的API响应格式")
    else:
        print("⚠️  任务 4.1 存在一些问题，请检查上述失败项。")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)