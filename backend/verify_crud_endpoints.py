#!/usr/bin/env python3
"""
验证问卷数据 CRUD API 接口的完整性
检查任务 4.1 要求的所有端点是否正确实现
"""

import re
import sys

def check_endpoints_in_code():
    """检查代码中是否包含所有必需的端点"""
    
    required_endpoints = [
        ("POST", "/api/submit", "创建问卷提交 API"),
        ("GET", "/api/questionnaires", "实现问卷列表查询 API"),
        ("GET", "/api/questionnaires/<int:questionnaire_id>", "开发单个问卷详情 API"),
        ("PUT", "/api/questionnaires/<int:questionnaire_id>", "实现问卷更新 API"),
        ("DELETE", "/api/questionnaires/<int:questionnaire_id>", "创建问卷删除 API")
    ]
    
    print("检查 app.py 中的端点实现...")
    print("=" * 60)
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        found_endpoints = []
        missing_endpoints = []
        
        for method, path, description in required_endpoints:
            # 构建正则表达式来匹配路由定义
            if "<int:" in path:
                # 处理带参数的路径
                pattern_path = path.replace("<int:questionnaire_id>", r"<int:\w+>")
            else:
                pattern_path = re.escape(path)
            
            pattern = rf"@app\.route\(['\"]({pattern_path})['\"].*methods=\[.*['\"]({method})['\"].*\]"
            
            if re.search(pattern, content, re.MULTILINE | re.DOTALL):
                found_endpoints.append((method, path, description))
                print(f"✅ {method:6} {path:45} - {description}")
            else:
                missing_endpoints.append((method, path, description))
                print(f"❌ {method:6} {path:45} - {description}")
        
        print("\n" + "=" * 60)
        print(f"检查结果: {len(found_endpoints)}/{len(required_endpoints)} 个端点已实现")
        
        if missing_endpoints:
            print("\n缺失的端点:")
            for method, path, description in missing_endpoints:
                print(f"  - {method} {path}: {description}")
            return False
        else:
            print("\n✅ 所有必需的端点都已实现!")
            return True
            
    except FileNotFoundError:
        print("❌ 找不到 app.py 文件")
        return False
    except Exception as e:
        print(f"❌ 检查过程中出错: {e}")
        return False

def check_function_implementations():
    """检查端点对应的函数是否正确实现"""
    
    print("\n检查端点函数实现...")
    print("=" * 60)
    
    required_functions = [
        ("submit_questionnaire_legacy", "/api/submit"),
        ("submit_questionnaire", "/api/questionnaires POST"),
        ("get_questionnaires", "/api/questionnaires GET"),
        ("get_questionnaire", "/api/questionnaires/<id> GET"),
        ("update_questionnaire", "/api/questionnaires/<id> PUT"),
        ("delete_questionnaire", "/api/questionnaires/<id> DELETE")
    ]
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        found_functions = []
        missing_functions = []
        
        for func_name, endpoint in required_functions:
            if f"def {func_name}(" in content:
                found_functions.append((func_name, endpoint))
                print(f"✅ {func_name:30} - {endpoint}")
            else:
                missing_functions.append((func_name, endpoint))
                print(f"❌ {func_name:30} - {endpoint}")
        
        print(f"\n函数实现结果: {len(found_functions)}/{len(required_functions)} 个函数已实现")
        
        return len(missing_functions) == 0
        
    except Exception as e:
        print(f"❌ 检查函数实现时出错: {e}")
        return False

def check_data_validation():
    """检查数据验证逻辑"""
    
    print("\n检查数据验证实现...")
    print("=" * 60)
    
    validation_checks = [
        ("validate_questionnaire_with_schema", "问卷数据验证"),
        ("normalize_questionnaire_data", "数据标准化"),
        ("create_validation_error_response", "错误响应创建"),
        ("login_required", "登录验证装饰器"),
        ("admin_required", "管理员权限装饰器")
    ]
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        all_found = True
        
        for item, description in validation_checks:
            if item in content:
                print(f"✅ {item:35} - {description}")
            else:
                print(f"❌ {item:35} - {description}")
                all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"❌ 检查验证逻辑时出错: {e}")
        return False

def main():
    """主检查函数"""
    print("验证问卷数据 CRUD API 接口实现")
    print("任务 4.1: 实现问卷数据 CRUD 接口")
    print("=" * 60)
    
    # 检查端点
    endpoints_ok = check_endpoints_in_code()
    
    # 检查函数实现
    functions_ok = check_function_implementations()
    
    # 检查数据验证
    validation_ok = check_data_validation()
    
    print("\n" + "=" * 60)
    print("总体检查结果:")
    print(f"- API 端点: {'✅ 通过' if endpoints_ok else '❌ 失败'}")
    print(f"- 函数实现: {'✅ 通过' if functions_ok else '❌ 失败'}")
    print(f"- 数据验证: {'✅ 通过' if validation_ok else '❌ 失败'}")
    
    overall_success = endpoints_ok and functions_ok and validation_ok
    
    if overall_success:
        print("\n🎉 任务 4.1 已完成！所有 CRUD API 接口都已正确实现。")
    else:
        print("\n⚠️  任务 4.1 尚未完全完成，请检查上述缺失项。")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)