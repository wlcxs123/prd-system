#!/usr/bin/env python3
"""
测试Frankfurt Scale问卷提交功能
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_frankfurt_submission():
    """测试Frankfurt Scale问卷数据提交"""
    print("🧪 测试Frankfurt Scale问卷提交功能")
    print("=" * 50)
    
    # 模拟Frankfurt Scale问卷提交的数据结构
    test_data = {
        "type": "frankfurt_scale_selective_mutism",
        "basic_info": {
            "name": "测试儿童",
            "grade": "小学",
            "submission_date": datetime.now().strftime("%Y-%m-%d"),
            "guardian": "测试家长"
        },
        "questions": [
            # DS部分问题示例 - 至少需要一个DS问题
            {
                "id": 1,
                "type": "multiple_choice",
                "question": "在家很能说话，但在公共/学校环境明显沉默或避免用语言。",
                "options": [
                    {"value": 1, "text": "是"},
                    {"value": 0, "text": "否"}
                ],
                "selected": [1],
                "can_speak": True,
                "section": "DS"
            },
            # SS_school部分问题示例
            {
                "id": 2,
                "type": "multiple_choice",
                "question": "在课堂与老师说话",
                "options": [
                    {"value": 0, "text": "0 无问题"},
                    {"value": 1, "text": "1 轻度限制"},
                    {"value": 2, "text": "2 偶尔"},
                    {"value": 3, "text": "3 几乎从不"},
                    {"value": 4, "text": "4 完全不说"}
                ],
                "selected": [3],
                "can_speak": True,
                "section": "SS_school"
            },
            # SS_public部分问题示例
            {
                "id": 3,
                "type": "multiple_choice",
                "question": "与公共场合的陌生儿童交谈",
                "options": [
                    {"value": 0, "text": "0 无问题"},
                    {"value": 1, "text": "1 轻度限制"},
                    {"value": 2, "text": "2 偶尔"},
                    {"value": 3, "text": "3 几乎从不"},
                    {"value": 4, "text": "4 完全不说"}
                ],
                "selected": [4],
                "can_speak": True,
                "section": "SS_public"
            },
            # SS_home部分问题示例
            {
                "id": 4,
                "type": "multiple_choice",
                "question": "与直系亲属说话",
                "options": [
                    {"value": 0, "text": "0 无问题"},
                    {"value": 1, "text": "1 轻度限制"},
                    {"value": 2, "text": "2 偶尔"},
                    {"value": 3, "text": "3 几乎从不"},
                    {"value": 4, "text": "4 完全不说"}
                ],
                "selected": [0],
                "can_speak": True,
                "section": "SS_home"
            }
        ]
    }
    
    print("📤 发送测试数据...")
    print(f"问卷类型: {test_data['type']}")
    print(f"儿童姓名: {test_data['basic_info']['name']}")
    print(f"年龄组: {test_data['basic_info']['grade']}")
    print(f"问题数量: {len(test_data['questions'])}")
    sections = [q['section'] for q in test_data['questions']]
    print(f"包含的sections: {sections}")
    print(f"测试数据准备完成")
    
    try:
        response = requests.post(f"{BASE_URL}/api/submit", 
                               json=test_data, 
                               timeout=10)
        
        print(f"\n📥 服务器响应:")
        print(f"状态码: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"响应内容: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            # 处理不同的响应格式
            if isinstance(response_data, list) and len(response_data) >= 2:
                # 如果响应是列表格式 [data, status_code]
                actual_data = response_data[0]
                actual_status = response_data[1] if len(response_data) > 1 else response.status_code
            else:
                # 标准响应格式
                actual_data = response_data
                actual_status = response.status_code
            
            if actual_status == 201 and actual_data.get('success'):
                print(f"\n✅ 提交成功!")
                print(f"问卷ID: {actual_data.get('questionnaire_id')}")
                return True
            else:
                print(f"\n❌ 提交失败:")
                error_info = actual_data.get('error', actual_data) if 'error' in actual_data else actual_data
                print(f"错误信息: {error_info.get('message', '未知错误')}")
                if 'details' in error_info:
                    print(f"详细错误: {error_info['details']}")
                elif 'errors' in error_info:
                    print(f"详细错误: {error_info['errors']}")
                return False
                
        except json.JSONDecodeError:
            print(f"响应内容 (非JSON): {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ 网络请求失败: {e}")
        print("\n💡 请确保:")
        print("1. 后端服务器正在运行 (python backend/app.py)")
        print("2. 服务器地址正确 (http://localhost:5000)")
        print("3. 网络连接正常")
        return False

def test_server_connection():
    """测试服务器连接"""
    print("🔗 测试服务器连接...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/auth/status", timeout=5)
        if response.status_code in [200, 401]:  # 200或401都表示服务器在线
            print("✅ 服务器连接正常")
            return True
        else:
            print(f"⚠️ 服务器响应异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 服务器连接失败: {e}")
        return False

def test_data_validation():
    """测试数据验证"""
    print("\n🔍 测试数据验证...")
    
    # 测试无效数据
    invalid_data = {
        "type": "frankfurt_scale_selective_mutism",
        "basic_info": {
            "name": "",  # 空姓名
            "grade": "invalid_grade",
            "submission_date": "invalid-date"
        },
        "questions": []  # 空问题列表
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/submit", 
                               json=invalid_data, 
                               timeout=10)
        
        response_data = response.json()
        
        # 处理不同的响应格式
        if isinstance(response_data, list) and len(response_data) >= 2:
            actual_data = response_data[0]
            actual_status = response_data[1]
        else:
            actual_data = response_data
            actual_status = response.status_code
        
        if actual_status == 400 or (not actual_data.get('success') and 'error' in actual_data):
            print("✅ 数据验证正常 - 正确拒绝了无效数据")
            error_info = actual_data.get('error', actual_data)
            error_msg = error_info.get('details', error_info.get('errors', error_info.get('message')))
            print(f"验证错误: {error_msg}")
            return True
        else:
            print(f"❌ 数据验证异常 - 应该返回400错误，实际返回: {actual_status}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 验证测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 Frankfurt Scale 问卷提交功能测试")
    print("=" * 60)
    
    # 测试步骤
    tests = [
        ("服务器连接", test_server_connection),
        ("数据提交", test_frankfurt_submission),
        ("数据验证", test_data_validation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}测试:")
        print("-" * 30)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ 测试执行异常: {e}")
            results.append((test_name, False))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总:")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:12}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(results)} 通过")
    
    if passed == len(results):
        print("\n🎉 所有测试通过! Frankfurt Scale问卷提交功能正常")
        print("\n📝 使用说明:")
        print("1. 打开 Frankfurt Scale of Selective Mutism.html")
        print("2. 填写儿童信息和问卷内容")
        print("3. 点击 '提交到系统' 按钮")
        print("4. 查看提交结果提示")
    else:
        print(f"\n⚠️ {len(results) - passed} 个测试失败")
        print("\n🔧 故障排查:")
        print("1. 确保后端服务器运行: cd backend && python app.py")
        print("2. 检查数据库是否初始化: python backend/init_db.py")
        print("3. 检查网络连接和端口占用")
    
    return passed == len(results)

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ 测试被用户中断")
        exit(1)
    except Exception as e:
        print(f"\n❌ 测试执行异常: {e}")
        exit(1)