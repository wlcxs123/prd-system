#!/usr/bin/env python3
"""
系统监控功能测试脚本
测试任务 8.2 的实现：添加系统监控和统计
"""

import requests
import json
import time
from datetime import datetime

# 测试配置
BASE_URL = 'http://localhost:5000'
TEST_USERNAME = 'admin'
TEST_PASSWORD = 'admin123'

class MonitoringSystemTester:
    def __init__(self):
        self.session = requests.Session()
        self.logged_in = False
    
    def login(self):
        """登录系统"""
        print("🔐 测试用户登录...")
        
        login_data = {
            'username': TEST_USERNAME,
            'password': TEST_PASSWORD
        }
        
        response = self.session.post(f'{BASE_URL}/api/auth/login', json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ 登录成功: {data.get('message')}")
                self.logged_in = True
                return True
            else:
                print(f"❌ 登录失败: {data.get('error', {}).get('message', '未知错误')}")
        else:
            print(f"❌ 登录请求失败: HTTP {response.status_code}")
        
        return False
    
    def test_statistics_endpoint(self):
        """测试统计数据接口"""
        print("\n📊 测试统计数据接口...")
        
        response = self.session.get(f'{BASE_URL}/api/admin/statistics')
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                stats = data.get('data', {})
                overview = stats.get('overview', {})
                
                print("✅ 统计数据获取成功:")
                print(f"   - 总问卷数: {overview.get('total_questionnaires', 0)}")
                print(f"   - 今日新增: {overview.get('today_submissions', 0)}")
                print(f"   - 本周新增: {overview.get('week_submissions', 0)}")
                print(f"   - 本月新增: {overview.get('month_submissions', 0)}")
                print(f"   - 总用户数: {overview.get('total_users', 0)}")
                print(f"   - 今日活跃用户: {overview.get('active_users_today', 0)}")
                print(f"   - 总操作数: {overview.get('total_operations', 0)}")
                print(f"   - 今日操作数: {overview.get('operations_today', 0)}")
                
                # 检查分布数据
                distributions = stats.get('distributions', {})
                if distributions.get('type_distribution'):
                    print(f"   - 问卷类型分布: {distributions['type_distribution']}")
                if distributions.get('grade_distribution'):
                    print(f"   - 年级分布: {distributions['grade_distribution']}")
                
                return True
            else:
                print(f"❌ 统计数据获取失败: {data.get('error', {}).get('message', '未知错误')}")
        else:
            print(f"❌ 统计数据请求失败: HTTP {response.status_code}")
        
        return False
    
    def test_health_check_endpoint(self):
        """测试系统健康检查接口"""
        print("\n🏥 测试系统健康检查接口...")
        
        response = self.session.get(f'{BASE_URL}/api/admin/system/health')
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                health = data.get('data', {})
                
                print(f"✅ 系统健康检查成功:")
                print(f"   - 整体状态: {health.get('status', 'unknown')}")
                
                checks = health.get('checks', {})
                for check_name, check_result in checks.items():
                    status = check_result.get('status', 'unknown')
                    message = check_result.get('message', '无消息')
                    status_icon = {
                        'healthy': '✅',
                        'warning': '⚠️',
                        'critical': '❌',
                        'unhealthy': '❌',
                        'unknown': '❓'
                    }.get(status, '❓')
                    
                    print(f"   - {check_name}: {status_icon} {message}")
                
                return True
            else:
                print(f"❌ 健康检查失败: {data.get('error', {}).get('message', '未知错误')}")
        else:
            print(f"❌ 健康检查请求失败: HTTP {response.status_code}")
        
        return False
    
    def test_performance_metrics_endpoint(self):
        """测试性能指标接口"""
        print("\n⚡ 测试性能指标接口...")
        
        response = self.session.get(f'{BASE_URL}/api/admin/system/performance')
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                metrics = data.get('data', {})
                
                print(f"✅ 性能指标获取成功:")
                print(f"   - 运行时间: {metrics.get('uptime', 0):.2f} 秒")
                
                # 数据库指标
                db_metrics = metrics.get('metrics', {}).get('database', {})
                if not db_metrics.get('error'):
                    print(f"   - 数据库大小: {db_metrics.get('size_mb', 0)} MB")
                    print(f"   - 问卷数量: {db_metrics.get('questionnaire_count', 0)}")
                    print(f"   - 日志数量: {db_metrics.get('log_count', 0)}")
                    print(f"   - 用户数量: {db_metrics.get('user_count', 0)}")
                    print(f"   - 最近1小时操作: {db_metrics.get('operations_last_hour', 0)}")
                else:
                    print(f"   - 数据库指标: ❌ {db_metrics.get('error')}")
                
                # 系统指标
                sys_metrics = metrics.get('metrics', {}).get('system', {})
                if not sys_metrics.get('error'):
                    print(f"   - CPU使用率: {sys_metrics.get('cpu_percent', 0)}%")
                    memory = sys_metrics.get('memory', {})
                    print(f"   - 内存使用: {memory.get('percent', 0)}% ({memory.get('available_gb', 0)} GB 可用)")
                    disk = sys_metrics.get('disk', {})
                    print(f"   - 磁盘使用: {disk.get('percent', 0)}% ({disk.get('free_gb', 0)} GB 可用)")
                else:
                    print(f"   - 系统指标: ⚠️ {sys_metrics.get('error')}")
                
                # 应用指标
                app_metrics = metrics.get('metrics', {}).get('application', {})
                if not app_metrics.get('error'):
                    print(f"   - 活跃会话: {app_metrics.get('active_sessions', 0)}")
                    print(f"   - 24小时错误: {app_metrics.get('errors_24h', 0)}")
                    print(f"   - Flask环境: {app_metrics.get('flask_env', 'unknown')}")
                    print(f"   - 调试模式: {app_metrics.get('debug_mode', False)}")
                else:
                    print(f"   - 应用指标: ❌ {app_metrics.get('error')}")
                
                return True
            else:
                print(f"❌ 性能指标获取失败: {data.get('error', {}).get('message', '未知错误')}")
        else:
            print(f"❌ 性能指标请求失败: HTTP {response.status_code}")
        
        return False
    
    def test_realtime_statistics_endpoint(self):
        """测试实时统计接口"""
        print("\n🔄 测试实时统计接口...")
        
        response = self.session.get(f'{BASE_URL}/api/admin/system/realtime')
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                realtime_data = data.get('data', {})
                
                print(f"✅ 实时统计获取成功:")
                
                # 活动统计
                activity = realtime_data.get('activity', {})
                print(f"   - 最近1小时提交: {activity.get('submissions_last_hour', 0)}")
                print(f"   - 最近1小时操作: {activity.get('operations_last_hour', 0)}")
                print(f"   - 最近5分钟提交: {activity.get('submissions_last_5min', 0)}")
                
                # 最近记录
                recent = realtime_data.get('recent', {})
                submissions = recent.get('submissions', [])
                operations = recent.get('operations', [])
                
                print(f"   - 最近提交数量: {len(submissions)}")
                print(f"   - 最近操作数量: {len(operations)}")
                
                if submissions:
                    print("   - 最新提交:")
                    for sub in submissions[:3]:  # 只显示前3个
                        print(f"     * {sub.get('name', '未知')} - {sub.get('type', '未知')} ({sub.get('created_at', '未知时间')})")
                
                if operations:
                    print("   - 最新操作:")
                    for op in operations[:3]:  # 只显示前3个
                        print(f"     * {op.get('operation', '未知')} ({op.get('created_at', '未知时间')})")
                
                return True
            else:
                print(f"❌ 实时统计获取失败: {data.get('error', {}).get('message', '未知错误')}")
        else:
            print(f"❌ 实时统计请求失败: HTTP {response.status_code}")
        
        return False
    
    def test_dashboard_access(self):
        """测试管理后台访问"""
        print("\n🖥️ 测试管理后台访问...")
        
        response = self.session.get(f'{BASE_URL}/admin')
        
        if response.status_code == 200:
            content = response.text
            # 检查是否包含监控相关的HTML元素
            monitoring_elements = [
                'monitoringDashboard',
                'toggleMonitoring',
                'systemStatus',
                'totalQuestionnaires',
                'todaySubmissions',
                'realtimeStats',
                'performanceStats'
            ]
            
            missing_elements = []
            for element in monitoring_elements:
                if element not in content:
                    missing_elements.append(element)
            
            if not missing_elements:
                print("✅ 管理后台包含所有监控元素")
                return True
            else:
                print(f"⚠️ 管理后台缺少监控元素: {missing_elements}")
                return False
        else:
            print(f"❌ 管理后台访问失败: HTTP {response.status_code}")
        
        return False
    
    def create_test_data(self):
        """创建测试数据以便测试监控功能"""
        print("\n📝 创建测试数据...")
        
        test_questionnaire = {
            "type": "test_monitoring",
            "basic_info": {
                "name": "监控测试用户",
                "grade": "测试年级",
                "submission_date": datetime.now().strftime('%Y-%m-%d')
            },
            "questions": [
                {
                    "id": 1,
                    "type": "multiple_choice",
                    "question": "这是一个测试问题",
                    "options": [
                        {"value": 0, "text": "选项A"},
                        {"value": 1, "text": "选项B"}
                    ],
                    "selected": [0]
                }
            ],
            "statistics": {
                "total_score": 100,
                "completion_rate": 100,
                "submission_time": datetime.now().isoformat()
            }
        }
        
        response = self.session.post(f'{BASE_URL}/api/questionnaires', json=test_questionnaire)
        
        if response.status_code == 201:
            data = response.json()
            if data.get('success'):
                print(f"✅ 测试问卷创建成功: ID {data.get('id')}")
                return data.get('id')
            else:
                print(f"❌ 测试问卷创建失败: {data.get('error', {}).get('message', '未知错误')}")
        else:
            print(f"❌ 测试问卷创建请求失败: HTTP {response.status_code}")
        
        return None
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始系统监控功能测试")
        print("=" * 50)
        
        # 登录
        if not self.login():
            print("❌ 登录失败，无法继续测试")
            return False
        
        # 创建测试数据
        test_id = self.create_test_data()
        
        # 等待一下让数据生效
        time.sleep(1)
        
        # 运行各项测试
        tests = [
            ("统计数据接口", self.test_statistics_endpoint),
            ("系统健康检查", self.test_health_check_endpoint),
            ("性能指标接口", self.test_performance_metrics_endpoint),
            ("实时统计接口", self.test_realtime_statistics_endpoint),
            ("管理后台访问", self.test_dashboard_access)
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} 测试异常: {e}")
                results.append((test_name, False))
        
        # 清理测试数据
        if test_id:
            print(f"\n🧹 清理测试数据 (ID: {test_id})...")
            delete_response = self.session.delete(f'{BASE_URL}/api/questionnaires/{test_id}')
            if delete_response.status_code == 200:
                print("✅ 测试数据清理成功")
            else:
                print("⚠️ 测试数据清理失败，请手动删除")
        
        # 输出测试结果
        print("\n" + "=" * 50)
        print("📋 测试结果汇总:")
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"   {test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\n总计: {passed}/{total} 项测试通过")
        
        if passed == total:
            print("🎉 所有监控功能测试通过！")
            return True
        else:
            print("⚠️ 部分测试失败，请检查实现")
            return False

def main():
    """主函数"""
    tester = MonitoringSystemTester()
    
    try:
        success = tester.run_all_tests()
        exit_code = 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n⏹️ 测试被用户中断")
        exit_code = 1
    except Exception as e:
        print(f"\n\n💥 测试过程中发生异常: {e}")
        exit_code = 1
    
    return exit_code

if __name__ == '__main__':
    exit(main())