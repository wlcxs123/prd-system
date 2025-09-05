#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试增强的数据导出功能
"""

import requests
import json
import os
import sys
from datetime import datetime

# 测试配置
BASE_URL = 'http://localhost:5000'
TEST_USERNAME = 'admin'
TEST_PASSWORD = 'admin123'

class ExportTester:
    def __init__(self):
        self.session = requests.Session()
        self.logged_in = False
    
    def login(self):
        """登录系统"""
        try:
            response = self.session.post(f'{BASE_URL}/api/auth/login', json={
                'username': TEST_USERNAME,
                'password': TEST_PASSWORD
            })
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✓ 登录成功")
                    self.logged_in = True
                    return True
                else:
                    print(f"✗ 登录失败: {result.get('error', {}).get('message', '未知错误')}")
            else:
                print(f"✗ 登录请求失败: HTTP {response.status_code}")
            
            return False
            
        except Exception as e:
            print(f"✗ 登录异常: {e}")
            return False
    
    def get_questionnaires(self):
        """获取问卷列表"""
        try:
            response = self.session.get(f'{BASE_URL}/api/questionnaires')
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    questionnaires = result.get('data', [])
                    print(f"✓ 获取到 {len(questionnaires)} 个问卷")
                    return questionnaires
                else:
                    print(f"✗ 获取问卷失败: {result.get('error', {}).get('message', '未知错误')}")
            else:
                print(f"✗ 获取问卷请求失败: HTTP {response.status_code}")
            
            return []
            
        except Exception as e:
            print(f"✗ 获取问卷异常: {e}")
            return []
    
    def test_batch_export(self, questionnaire_ids, format_type):
        """测试批量导出功能"""
        print(f"\n--- 测试批量导出 ({format_type.upper()} 格式) ---")
        
        try:
            response = self.session.post(f'{BASE_URL}/api/questionnaires/export', json={
                'ids': questionnaire_ids,
                'format': format_type,
                'include_details': True
            })
            
            if response.status_code == 200:
                # 检查响应头
                content_type = response.headers.get('Content-Type', '')
                content_disposition = response.headers.get('Content-Disposition', '')
                
                print(f"✓ 批量导出成功 ({format_type.upper()})")
                print(f"  Content-Type: {content_type}")
                print(f"  Content-Disposition: {content_disposition}")
                print(f"  文件大小: {len(response.content)} 字节")
                
                # 保存文件用于验证
                filename = f"test_batch_export_{format_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                if format_type == 'csv':
                    filename += '.csv'
                elif format_type in ['excel', 'xlsx']:
                    filename += '.xlsx'
                elif format_type == 'pdf':
                    filename += '.pdf'
                
                with open(filename, 'wb') as f:
                    f.write(response.content)
                
                print(f"  已保存到: {filename}")
                return True
                
            else:
                print(f"✗ 批量导出失败: HTTP {response.status_code}")
                try:
                    error_info = response.json()
                    print(f"  错误信息: {error_info}")
                except:
                    print(f"  响应内容: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"✗ 批量导出异常: {e}")
            return False
    
    def test_single_export(self, questionnaire_id, format_type):
        """测试单个问卷导出功能"""
        print(f"\n--- 测试单个问卷导出 (ID: {questionnaire_id}, {format_type.upper()} 格式) ---")
        
        try:
            response = self.session.get(f'{BASE_URL}/api/export/{questionnaire_id}', params={
                'format': format_type,
                'include_details': 'true'
            })
            
            if response.status_code == 200:
                # 检查响应头
                content_type = response.headers.get('Content-Type', '')
                content_disposition = response.headers.get('Content-Disposition', '')
                
                print(f"✓ 单个问卷导出成功 ({format_type.upper()})")
                print(f"  Content-Type: {content_type}")
                print(f"  Content-Disposition: {content_disposition}")
                print(f"  文件大小: {len(response.content)} 字节")
                
                # 保存文件用于验证
                filename = f"test_single_export_{questionnaire_id}_{format_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                if format_type == 'csv':
                    filename += '.csv'
                elif format_type in ['excel', 'xlsx']:
                    filename += '.xlsx'
                elif format_type == 'pdf':
                    filename += '.pdf'
                
                with open(filename, 'wb') as f:
                    f.write(response.content)
                
                print(f"  已保存到: {filename}")
                return True
                
            else:
                print(f"✗ 单个问卷导出失败: HTTP {response.status_code}")
                try:
                    error_info = response.json()
                    print(f"  错误信息: {error_info}")
                except:
                    print(f"  响应内容: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"✗ 单个问卷导出异常: {e}")
            return False
    
    def test_advanced_export(self, format_type):
        """测试高级导出功能"""
        print(f"\n--- 测试高级导出 ({format_type.upper()} 格式) ---")
        
        try:
            # 先获取预览信息
            preview_response = self.session.post(f'{BASE_URL}/api/admin/export/preview', json={
                'filters': {
                    'date_from': '2024-01-01',
                    'date_to': '2024-12-31'
                }
            })
            
            if preview_response.status_code == 200:
                preview_result = preview_response.json()
                if preview_result.get('success'):
                    preview = preview_result.get('preview', {})
                    print(f"✓ 导出预览获取成功")
                    print(f"  总记录数: {preview.get('total_count', 0)}")
                    print(f"  类型统计: {preview.get('type_statistics', {})}")
                    print(f"  可以导出: {preview.get('can_export', False)}")
                else:
                    print(f"✗ 获取导出预览失败: {preview_result.get('error', {}).get('message', '未知错误')}")
                    return False
            else:
                print(f"✗ 获取导出预览请求失败: HTTP {preview_response.status_code}")
                return False
            
            # 执行高级导出
            response = self.session.post(f'{BASE_URL}/api/admin/export/advanced', json={
                'format': format_type,
                'include_details': True,
                'filters': {
                    'date_from': '2024-01-01',
                    'date_to': '2024-12-31'
                }
            })
            
            if response.status_code == 200:
                # 检查响应头
                content_type = response.headers.get('Content-Type', '')
                content_disposition = response.headers.get('Content-Disposition', '')
                
                print(f"✓ 高级导出成功 ({format_type.upper()})")
                print(f"  Content-Type: {content_type}")
                print(f"  Content-Disposition: {content_disposition}")
                print(f"  文件大小: {len(response.content)} 字节")
                
                # 保存文件用于验证
                filename = f"test_advanced_export_{format_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                if format_type == 'csv':
                    filename += '.csv'
                elif format_type in ['excel', 'xlsx']:
                    filename += '.xlsx'
                elif format_type == 'pdf':
                    filename += '.pdf'
                
                with open(filename, 'wb') as f:
                    f.write(response.content)
                
                print(f"  已保存到: {filename}")
                return True
                
            else:
                print(f"✗ 高级导出失败: HTTP {response.status_code}")
                try:
                    error_info = response.json()
                    print(f"  错误信息: {error_info}")
                except:
                    print(f"  响应内容: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"✗ 高级导出异常: {e}")
            return False
    
    def run_tests(self):
        """运行所有测试"""
        print("=== 增强数据导出功能测试 ===")
        
        # 登录
        if not self.login():
            print("无法登录，测试终止")
            return False
        
        # 获取问卷数据
        questionnaires = self.get_questionnaires()
        if not questionnaires:
            print("没有问卷数据，跳过导出测试")
            return True
        
        # 准备测试数据
        questionnaire_ids = [q['id'] for q in questionnaires[:5]]  # 取前5个问卷
        first_questionnaire_id = questionnaires[0]['id']
        
        # 测试格式列表
        test_formats = ['csv', 'excel', 'pdf']
        
        success_count = 0
        total_tests = 0
        
        # 测试批量导出
        for format_type in test_formats:
            total_tests += 1
            if self.test_batch_export(questionnaire_ids, format_type):
                success_count += 1
        
        # 测试单个问卷导出
        for format_type in test_formats:
            total_tests += 1
            if self.test_single_export(first_questionnaire_id, format_type):
                success_count += 1
        
        # 测试高级导出
        for format_type in test_formats:
            total_tests += 1
            if self.test_advanced_export(format_type):
                success_count += 1
        
        # 输出测试结果
        print(f"\n=== 测试结果 ===")
        print(f"总测试数: {total_tests}")
        print(f"成功: {success_count}")
        print(f"失败: {total_tests - success_count}")
        print(f"成功率: {success_count / total_tests * 100:.1f}%")
        
        return success_count == total_tests

def main():
    """主函数"""
    tester = ExportTester()
    
    try:
        success = tester.run_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"测试过程中发生异常: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()