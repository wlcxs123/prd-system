#!/usr/bin/env python3
"""
测试统一错误处理系统
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from error_handlers import (
    StandardErrorResponse, 
    ErrorCodes, 
    ErrorMessages,
    validation_error,
    auth_error,
    server_error,
    not_found_error
)

def test_error_response_creation():
    """测试错误响应创建"""
    print("测试错误响应创建...")
    
    # 测试验证错误
    response, status_code = validation_error(['姓名不能为空', '年级必须选择'])
    print(f"验证错误响应: {response}")
    print(f"状态码: {status_code}")
    assert response['success'] == False
    assert response['error']['code'] == ErrorCodes.VALIDATION_ERROR
    assert len(response['error']['details']) == 2
    print("✅ 验证错误测试通过\n")
    
    # 测试认证错误
    response, status_code = auth_error('用户名或密码错误')
    print(f"认证错误响应: {response}")
    print(f"状态码: {status_code}")
    assert response['success'] == False
    assert response['error']['code'] == ErrorCodes.AUTH_ERROR
    assert status_code == 401
    print("✅ 认证错误测试通过\n")
    
    # 测试服务器错误
    response, status_code = server_error('数据库连接失败', '详细错误信息')
    print(f"服务器错误响应: {response}")
    print(f"状态码: {status_code}")
    assert response['success'] == False
    assert response['error']['code'] == ErrorCodes.SERVER_ERROR
    assert status_code == 500
    assert 'retry_after' in response
    print("✅ 服务器错误测试通过\n")
    
    # 测试资源不存在错误
    response, status_code = not_found_error('问卷')
    print(f"资源不存在错误响应: {response}")
    print(f"状态码: {status_code}")
    assert response['success'] == False
    assert response['error']['code'] == ErrorCodes.NOT_FOUND
    assert status_code == 404
    print("✅ 资源不存在错误测试通过\n")

def test_error_messages():
    """测试错误消息映射"""
    print("测试错误消息映射...")
    
    # 测试已定义的错误代码
    message = ErrorMessages.get_message(ErrorCodes.VALIDATION_ERROR)
    print(f"验证错误消息: {message}")
    assert message == '输入的数据格式不正确，请检查后重试'
    
    # 测试未定义的错误代码
    message = ErrorMessages.get_message('UNKNOWN_ERROR', '默认消息')
    print(f"未知错误消息: {message}")
    assert message == '默认消息'
    
    print("✅ 错误消息映射测试通过\n")

def test_standard_error_response():
    """测试标准错误响应类"""
    print("测试标准错误响应类...")
    
    # 测试创建标准错误响应
    response, status_code = StandardErrorResponse.create_error_response(
        ErrorCodes.BUSINESS_ERROR,
        '业务逻辑错误',
        ['详细错误1', '详细错误2'],
        400,
        '操作失败，请重试'
    )
    
    print(f"标准错误响应: {response}")
    assert response['success'] == False
    assert response['error']['code'] == ErrorCodes.BUSINESS_ERROR
    assert response['error']['message'] == '操作失败，请重试'
    assert response['error']['technical_message'] == '业务逻辑错误'
    assert len(response['error']['details']) == 2
    assert 'request_id' in response['error']
    assert 'timestamp' in response
    
    print("✅ 标准错误响应测试通过\n")

def main():
    """运行所有测试"""
    print("开始测试统一错误处理系统...\n")
    
    try:
        test_error_response_creation()
        test_error_messages()
        test_standard_error_response()
        
        print("🎉 所有测试通过！")
        print("\n错误处理系统功能验证：")
        print("✅ 标准化错误响应格式")
        print("✅ 错误代码和消息映射")
        print("✅ 用户友好的错误消息")
        print("✅ 请求ID生成和追踪")
        print("✅ 重试机制支持")
        print("✅ 多种错误类型支持")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())