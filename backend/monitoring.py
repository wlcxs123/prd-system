#!/usr/bin/env python3
"""
系统监控模块
用于监控应用性能、健康状态和资源使用情况
"""

import os
import sys
import time
import psutil
import sqlite3
import json
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
import threading
import logging

class SystemMonitor:
    """系统监控类"""
    
    def __init__(self, app=None, config=None):
        self.app = app
        self.config = config or {}
        self.metrics = {}
        self.alerts = []
        self.start_time = time.time()
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """初始化 Flask 应用"""
        self.app = app
        
        # 注册监控路由
        app.add_url_rule('/health', 'health_check', self.health_check, methods=['GET'])
        app.add_url_rule('/metrics', 'metrics', self.get_metrics, methods=['GET'])
        app.add_url_rule('/api/admin/system/status', 'system_status', self.get_system_status, methods=['GET'])
        
        # 启动监控线程
        if self.config.get('enable_monitoring', True):
            self.start_monitoring()
    
    def health_check(self):
        """健康检查端点"""
        try:
            # 检查数据库连接
            db_status = self.check_database_health()
            
            # 检查磁盘空间
            disk_status = self.check_disk_space()
            
            # 检查内存使用
            memory_status = self.check_memory_usage()
            
            # 整体健康状态
            overall_status = all([db_status['healthy'], disk_status['healthy'], memory_status['healthy']])
            
            response = {
                'status': 'healthy' if overall_status else 'unhealthy',
                'timestamp': datetime.now().isoformat(),
                'uptime': time.time() - self.start_time,
                'checks': {
                    'database': db_status,
                    'disk': disk_status,
                    'memory': memory_status
                }
            }
            
            status_code = 200 if overall_status else 503
            return jsonify(response), status_code
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500
    
    def check_database_health(self):
        """检查数据库健康状态"""
        try:
            db_path = self.app.config.get('DATABASE_PATH', 'questionnaires.db')
            
            with sqlite3.connect(db_path, timeout=5) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM questionnaires")
                count = cursor.fetchone()[0]
                
                # 检查数据库文件大小
                db_size = os.path.getsize(db_path) if os.path.exists(db_path) else 0
                
                return {
                    'healthy': True,
                    'records_count': count,
                    'database_size': db_size,
                    'response_time': time.time()
                }
                
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }
    
    def check_disk_space(self):
        """检查磁盘空间"""
        try:
            disk_usage = psutil.disk_usage('/')
            free_percent = (disk_usage.free / disk_usage.total) * 100
            
            # 磁盘空间不足警告阈值
            warning_threshold = self.config.get('disk_warning_threshold', 20)  # 20%
            critical_threshold = self.config.get('disk_critical_threshold', 10)  # 10%
            
            if free_percent < critical_threshold:
                status = 'critical'
                healthy = False
            elif free_percent < warning_threshold:
                status = 'warning'
                healthy = True
            else:
                status = 'ok'
                healthy = True
            
            return {
                'healthy': healthy,
                'status': status,
                'free_space': disk_usage.free,
                'total_space': disk_usage.total,
                'free_percent': round(free_percent, 2)
            }
            
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }
    
    def check_memory_usage(self):
        """检查内存使用情况"""
        try:
            memory = psutil.virtual_memory()
            used_percent = memory.percent
            
            # 内存使用警告阈值
            warning_threshold = self.config.get('memory_warning_threshold', 80)  # 80%
            critical_threshold = self.config.get('memory_critical_threshold', 90)  # 90%
            
            if used_percent > critical_threshold:
                status = 'critical'
                healthy = False
            elif used_percent > warning_threshold:
                status = 'warning'
                healthy = True
            else:
                status = 'ok'
                healthy = True
            
            return {
                'healthy': healthy,
                'status': status,
                'used_percent': used_percent,
                'available': memory.available,
                'total': memory.total
            }
            
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }
    
    def get_metrics(self):
        """获取系统指标"""
        try:
            # CPU 使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 内存使用情况
            memory = psutil.virtual_memory()
            
            # 磁盘使用情况
            disk = psutil.disk_usage('/')
            
            # 网络统计
            network = psutil.net_io_counters()
            
            # 进程信息
            process = psutil.Process()
            process_info = {
                'pid': process.pid,
                'cpu_percent': process.cpu_percent(),
                'memory_percent': process.memory_percent(),
                'memory_info': process.memory_info()._asdict(),
                'num_threads': process.num_threads(),
                'create_time': process.create_time()
            }
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'uptime': time.time() - self.start_time,
                'cpu': {
                    'percent': cpu_percent,
                    'count': psutil.cpu_count()
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                'process': process_info
            }
            
            return jsonify(metrics)
            
        except Exception as e:
            return jsonify({
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500
    
    def get_system_status(self):
        """获取系统状态（管理员接口）"""
        try:
            # 获取基本系统信息
            system_info = {
                'platform': sys.platform,
                'python_version': sys.version,
                'pid': os.getpid(),
                'working_directory': os.getcwd(),
                'start_time': datetime.fromtimestamp(self.start_time).isoformat(),
                'uptime_seconds': time.time() - self.start_time
            }
            
            # 获取应用配置信息（敏感信息已过滤）
            app_config = {
                'debug': self.app.config.get('DEBUG', False),
                'testing': self.app.config.get('TESTING', False),
                'database_path': self.app.config.get('DATABASE_PATH', ''),
                'session_timeout': str(self.app.config.get('PERMANENT_SESSION_LIFETIME', '')),
            }
            
            # 获取数据库统计信息
            db_stats = self.get_database_stats()
            
            # 获取最近的错误日志
            recent_errors = self.get_recent_errors()
            
            return jsonify({
                'success': True,
                'data': {
                    'system_info': system_info,
                    'app_config': app_config,
                    'database_stats': db_stats,
                    'recent_errors': recent_errors,
                    'alerts': self.alerts[-10:]  # 最近10个警告
                }
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    def get_database_stats(self):
        """获取数据库统计信息"""
        try:
            db_path = self.app.config.get('DATABASE_PATH', 'questionnaires.db')
            
            if not os.path.exists(db_path):
                return {'error': '数据库文件不存在'}
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                stats = {
                    'file_size': os.path.getsize(db_path),
                    'tables': {}
                }
                
                # 获取表统计信息
                tables = ['questionnaires', 'users', 'operation_logs']
                
                for table in tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        stats['tables'][table] = {'count': count}
                        
                        # 获取最近记录的时间
                        if table in ['questionnaires', 'operation_logs']:
                            cursor.execute(f"SELECT MAX(created_at) FROM {table}")
                            latest = cursor.fetchone()[0]
                            stats['tables'][table]['latest_record'] = latest
                            
                    except sqlite3.OperationalError:
                        stats['tables'][table] = {'error': '表不存在'}
                
                return stats
                
        except Exception as e:
            return {'error': str(e)}
    
    def get_recent_errors(self):
        """获取最近的错误日志"""
        try:
            log_file = self.app.config.get('LOG_FILE', 'app.log')
            
            if not os.path.exists(log_file):
                return []
            
            errors = []
            
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
                # 查找最近的错误日志（最多10条）
                for line in reversed(lines[-1000:]):  # 只检查最后1000行
                    if 'ERROR' in line or 'CRITICAL' in line:
                        errors.append(line.strip())
                        if len(errors) >= 10:
                            break
            
            return errors
            
        except Exception as e:
            return [f'读取日志文件失败: {str(e)}']
    
    def start_monitoring(self):
        """启动监控线程"""
        def monitor_loop():
            while True:
                try:
                    self.collect_metrics()
                    self.check_alerts()
                    time.sleep(60)  # 每分钟收集一次指标
                except Exception as e:
                    print(f"监控线程错误: {e}")
                    time.sleep(60)
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
    
    def collect_metrics(self):
        """收集系统指标"""
        try:
            timestamp = datetime.now()
            
            # 收集系统指标
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # 存储指标（简单的内存存储，生产环境可以考虑使用时序数据库）
            metric_key = timestamp.strftime('%Y-%m-%d %H:%M')
            
            self.metrics[metric_key] = {
                'timestamp': timestamp.isoformat(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': (disk.used / disk.total) * 100
            }
            
            # 只保留最近24小时的指标
            cutoff_time = timestamp - timedelta(hours=24)
            self.metrics = {
                k: v for k, v in self.metrics.items() 
                if datetime.fromisoformat(v['timestamp']) > cutoff_time
            }
            
        except Exception as e:
            print(f"收集指标失败: {e}")
    
    def check_alerts(self):
        """检查警告条件"""
        try:
            current_time = datetime.now()
            
            # 检查 CPU 使用率
            cpu_percent = psutil.cpu_percent()
            if cpu_percent > 90:
                self.add_alert('high_cpu', f'CPU 使用率过高: {cpu_percent}%', 'critical')
            elif cpu_percent > 80:
                self.add_alert('high_cpu', f'CPU 使用率较高: {cpu_percent}%', 'warning')
            
            # 检查内存使用率
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                self.add_alert('high_memory', f'内存使用率过高: {memory.percent}%', 'critical')
            elif memory.percent > 80:
                self.add_alert('high_memory', f'内存使用率较高: {memory.percent}%', 'warning')
            
            # 检查磁盘空间
            disk = psutil.disk_usage('/')
            free_percent = (disk.free / disk.total) * 100
            if free_percent < 10:
                self.add_alert('low_disk', f'磁盘空间不足: {free_percent:.1f}%', 'critical')
            elif free_percent < 20:
                self.add_alert('low_disk', f'磁盘空间较少: {free_percent:.1f}%', 'warning')
            
            # 检查数据库连接
            db_health = self.check_database_health()
            if not db_health['healthy']:
                self.add_alert('database_error', f'数据库连接失败: {db_health.get("error", "未知错误")}', 'critical')
            
        except Exception as e:
            self.add_alert('monitoring_error', f'监控检查失败: {str(e)}', 'warning')
    
    def add_alert(self, alert_type, message, severity='info'):
        """添加警告"""
        alert = {
            'type': alert_type,
            'message': message,
            'severity': severity,
            'timestamp': datetime.now().isoformat()
        }
        
        # 避免重复警告（相同类型的警告在5分钟内只记录一次）
        recent_alerts = [
            a for a in self.alerts 
            if a['type'] == alert_type and 
            datetime.fromisoformat(a['timestamp']) > datetime.now() - timedelta(minutes=5)
        ]
        
        if not recent_alerts:
            self.alerts.append(alert)
            
            # 只保留最近100个警告
            if len(self.alerts) > 100:
                self.alerts = self.alerts[-100:]
            
            # 记录到日志
            if hasattr(self.app, 'logger'):
                log_level = {
                    'info': self.app.logger.info,
                    'warning': self.app.logger.warning,
                    'critical': self.app.logger.critical
                }.get(severity, self.app.logger.info)
                
                log_level(f"系统警告 [{alert_type}]: {message}")

def create_monitoring_app():
    """创建独立的监控应用"""
    app = Flask(__name__)
    monitor = SystemMonitor(app)
    return app

if __name__ == '__main__':
    # 独立运行监控服务
    app = create_monitoring_app()
    app.run(host='0.0.0.0', port=5001, debug=False)