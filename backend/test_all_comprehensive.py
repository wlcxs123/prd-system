#!/usr/bin/env python3
"""
问卷数据管理系统完整测试套件 - 任务10实现
运行所有单元测试和集成测试，生成完整的测试报告
"""

import unittest
import os
import sys
import time
import json
from datetime import datetime
import subprocess

# 添加backend目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

# 导入所有测试模块
try:
    from test_unit_comprehensive import run_unit_tests
    from test_api_comprehensive import run_api_tests
    from test_database_comprehensive import run_database_tests
    from test_integration_comprehensive import run_integration_tests
except ImportError as e:
    print(f"导入测试模块失败: {e}")
    sys.exit(1)

class TestReportGenerator:
    """测试报告生成器"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.test_results = {}
        self.overall_success = True
    
    def start_testing(self):
        """开始测试"""
        self.start_time = datetime.now()
        print("=" * 80)
        print("问卷数据管理系统完整测试套件")
        print("=" * 80)
        print(f"测试开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
    
    def run_test_suite(self, suite_name, test_function):
        """运行测试套件"""
        print(f"\n{'='*20} {suite_name} {'='*20}")
        suite_start = time.time()
        
        try:
            success = test_function()
            suite_time = time.time() - suite_start
            
            self.test_results[suite_name] = {
                'success': success,
                'duration': suite_time,
                'error': None
            }
            
            if not success:
                self.overall_success = False
                
        except Exception as e:
            suite_time = time.time() - suite_start
            self.test_results[suite_name] = {
                'success': False,
                'duration': suite_time,
                'error': str(e)
            }
            self.overall_success = False
            print(f"测试套件 {suite_name} 执行失败: {e}")
    
    def generate_report(self):
        """生成测试报告"""
        self.end_time = datetime.now()
        total_duration = (self.end_time - self.start_time).total_seconds()
        
        print("\n" + "=" * 80)
        print("测试完成报告")
        print("=" * 80)
        
        # 基本信息
        print(f"测试开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"测试结束时间: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"总耗时: {total_duration:.2f} 秒")
        print()
        
        # 各测试套件结果
        print("测试套件结果:")
        print("-" * 60)
        
        for suite_name, result in self.test_results.items():
            status = "✓ 通过" if result['success'] else "✗ 失败"
            duration = result['duration']
            print(f"{suite_name:<30} {status:<10} {duration:>8.2f}秒")
            
            if result['error']:
                print(f"  错误: {result['error']}")
        
        print()
        
        # 总体结果
        passed_suites = sum(1 for r in self.test_results.values() if r['success'])
        total_suites = len(self.test_results)
        
        print("总体结果:")
        print("-" * 60)
        print(f"测试套件总数: {total_suites}")
        print(f"通过套件数: {passed_suites}")
        print(f"失败套件数: {total_suites - passed_suites}")
        print(f"成功率: {(passed_suites / total_suites * 100):.1f}%")
        
        if self.overall_success:
            print("\n🎉 所有测试通过！问卷数据管理系统质量验证完成。")
            self.print_verified_requirements()
        else:
            print(f"\n⚠️  有 {total_suites - passed_suites} 个测试套件失败，请检查实现。")
        
        # 生成JSON报告
        self.save_json_report(total_duration)
        
        return self.overall_success
    
    def print_verified_requirements(self):
        """打印已验证的需求"""
        print("\n已验证的系统需求:")
        print("-" * 60)
        
        requirements = [
            "✓ 需求1: 数据结构标准化和验证",
            "  - 1.1 问卷数据基本信息验证",
            "  - 1.2 选择题数据结构验证", 
            "  - 1.3 填空题数据结构验证",
            "  - 1.4 数据标准化处理",
            "  - 1.5 数据完整性检查",
            "",
            "✓ 需求2: 多种问题类型支持",
            "  - 2.1 单选和多选题支持",
            "  - 2.2 短文本和长文本输入",
            "  - 2.3 问题类型、题目内容和答案记录",
            "  - 2.4 根据问题类型验证答案格式",
            "  - 2.5 问题类型显示和处理",
            "",
            "✓ 需求3: 用户认证和登录系统",
            "  - 3.1 用户认证数据库操作",
            "  - 3.2 密码哈希和验证",
            "  - 3.3 登录页面和表单",
            "  - 3.4 会话管理机制",
            "  - 3.5 权限控制和验证",
            "",
            "✓ 需求4: 问卷数据管理界面",
            "  - 4.1 管理后台界面",
            "  - 4.2 问卷列表查看和搜索",
            "  - 4.3 问卷详情查看",
            "  - 4.4 问卷数据编辑和更新",
            "",
            "✓ 需求5: 数据存储和检索",
            "  - 5.1 数据库结构和初始化",
            "  - 5.2 问卷数据CRUD操作",
            "  - 5.3 数据检索和筛选",
            "  - 5.4 事务处理和数据完整性",
            "",
            "✓ 需求6: 数据完整性验证",
            "  - 6.1 基本信息完整性验证",
            "  - 6.2 选择题答案验证",
            "  - 6.3 填空题答案验证",
            "  - 6.4 验证错误报告生成",
            "",
            "✓ 需求7: 批量操作功能",
            "  - 7.1 批量选择界面",
            "  - 7.2 批量操作按钮",
            "  - 7.3 批量删除确认",
            "  - 7.4 批量删除执行",
            "  - 7.5 批量导出功能",
            "  - 7.6 导出格式支持",
            "",
            "✓ 需求8: 后台管理功能",
            "  - 8.1 数据统计概览",
            "  - 8.2 搜索和筛选功能",
            "  - 8.3 操作日志系统",
            "  - 8.4 系统性能监控",
            "  - 8.5 权限控制管理",
            "",
            "✓ 需求9: API接口标准化",
            "  - 9.1 标准JSON格式响应",
            "  - 9.2 统一错误代码和消息",
            "  - 9.3 API接口兼容性",
            "  - 9.4 错误处理机制",
            "  - 9.5 用户友好错误信息"
        ]
        
        for req in requirements:
            print(req)
    
    def save_json_report(self, total_duration):
        """保存JSON格式的测试报告"""
        report_data = {
            'test_run': {
                'start_time': self.start_time.isoformat(),
                'end_time': self.end_time.isoformat(),
                'total_duration': total_duration,
                'overall_success': self.overall_success
            },
            'test_suites': self.test_results,
            'summary': {
                'total_suites': len(self.test_results),
                'passed_suites': sum(1 for r in self.test_results.values() if r['success']),
                'failed_suites': sum(1 for r in self.test_results.values() if not r['success']),
                'success_rate': (sum(1 for r in self.test_results.values() if r['success']) / len(self.test_results) * 100) if self.test_results else 0
            },
            'system_info': {
                'python_version': sys.version,
                'platform': sys.platform,
                'working_directory': os.getcwd()
            }
        }
        
        report_filename = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(report_filename, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            print(f"\n测试报告已保存到: {report_filename}")
        except Exception as e:
            print(f"\n保存测试报告失败: {e}")


def check_system_requirements():
    """检查系统要求"""
    print("检查系统要求...")
    
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("❌ Python版本过低，需要Python 3.7或更高版本")
        return False
    
    print(f"✓ Python版本: {sys.version}")
    
    # 检查必需的模块
    required_modules = [
        'flask', 'sqlite3', 'bcrypt', 'marshmallow', 
        'unittest', 'json', 'datetime', 'tempfile'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ 模块 {module} 可用")
        except ImportError:
            missing_modules.append(module)
            print(f"❌ 模块 {module} 不可用")
    
    if missing_modules:
        print(f"\n缺少必需模块: {', '.join(missing_modules)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    # 检查数据库文件权限
    try:
        import tempfile
        test_db = tempfile.mktemp(suffix='.db')
        import sqlite3
        conn = sqlite3.connect(test_db)
        conn.close()
        os.unlink(test_db)
        print("✓ 数据库文件权限正常")
    except Exception as e:
        print(f"❌ 数据库文件权限检查失败: {e}")
        return False
    
    print("✓ 系统要求检查通过\n")
    return True


def main():
    """主函数"""
    print("问卷数据管理系统测试和质量保证")
    print("任务10: 测试和质量保证的完整实现")
    print()
    
    # 检查系统要求
    if not check_system_requirements():
        print("系统要求检查失败，无法继续测试")
        sys.exit(1)
    
    # 创建测试报告生成器
    reporter = TestReportGenerator()
    reporter.start_testing()
    
    # 定义测试套件
    test_suites = [
        ("单元测试", run_unit_tests),
        ("API接口测试", run_api_tests),
        ("数据库操作测试", run_database_tests),
        ("集成测试", run_integration_tests)
    ]
    
    # 运行所有测试套件
    for suite_name, test_function in test_suites:
        reporter.run_test_suite(suite_name, test_function)
    
    # 生成最终报告
    success = reporter.generate_report()
    
    # 返回适当的退出代码
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()