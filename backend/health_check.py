#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
健康检查模块
提供系统健康状态检查功能
"""

import os
import sqlite3
import psutil
import time
from datetime import datetime
from flask import jsonify

def check_database_health():
    """检查数据库连接健康状态"""
    try:
        db_path = os.environ.get('DATABASE_PATH', 'data/questionnaires.db')
        
        # 检查数据库文件是否存在
        if not os.path.exists(db_path):
            return {
                'status': 'unhealthy',
                'message': '数据库文件不存在',
                'details': {'path': db_path}
            }
        
        # 尝试连接数据库
        start_time = time.time()
        conn = sqlite3.connect(db_path, timeout=5)
        
        # 执行简单查询
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        result = cursor.fetchone()
        
        conn.close()
        
        response_time = (time.time() - start_time) * 1000  # 转换为毫秒
        
        if result and result[0] == 1:
            return {
                'status': 'healthy',
                'response_time_ms': round(response_time, 2),
                'details': {'path': db_path}
            }
        else:
            return {
                'status': 'unhealthy',
                'message': '数据库查询失败',
                'details': {'path': db_path}
            }
            
    except Exception as e:
        return {
            'status': 'unhealthy',
            'message': f'数据库连接错误: {str(e)}',
            'details': {'error_type': type(e).__name__}
        }

def check_disk_space():
    """检查磁盘空间"""
    try:
        # 获取当前目录的磁盘使用情况
        disk_usage = psutil.disk_usage('.')
        
        total_gb = disk_usage.total / (1024**3)
        used_gb = disk_usage.used / (1024**3)
        free_gb = disk_usage.free / (1024**3)
        usage_percent = (disk_usage.used / disk_usage.total) * 100
        
        # 磁盘空间警告阈值
        warning_threshold = 80  # 80%
        critical_threshold = 90  # 90%
        
        if usage_percent >= critical_threshold:
            status = 'critical'
            message = f'磁盘空间严重不足: {usage_percent:.1f}%'
        elif usage_percent >= warning_threshold:
            status = 'warning'
            message = f'磁盘空间不足: {usage_percent:.1f}%'
        else:
            status = 'healthy'
            message = f'磁盘空间充足: {usage_percent:.1f}%'
        
        return {
            'status': status,
            'message': message,
            'details': {
                'total_gb': round(total_gb, 2),
                'used_gb': round(used_gb, 2),
                'free_gb': round(free_gb, 2),
                'usage_percent': round(usage_percent, 1)
            }
        }
        
    except Exception as e:
        return {
            'status': 'unhealthy',
            'message': f'磁盘检查错误: {str(e)}',
            'details': {'error_type': type(e).__name__}
        }

def check_memory_usage():
    """检查内存使用情况"""
    try:
        memory = psutil.virtual_memory()
        
        total_mb = memory.total / (1024**2)
        used_mb = memory.used / (1024**2)
        available_mb = memory.available / (1024**2)
        usage_percent = memory.percent
        
        # 内存使用警告阈值
        warning_threshold = 80  # 80%
        critical_threshold = 90  # 90%
        
        if usage_percent >= critical_threshold:
            status = 'critical'
            message = f'内存使用率过高: {usage_percent:.1f}%'
        elif usage_percent >= warning_threshold:
            status = 'warning'
            message = f'内存使用率较高: {usage_percent:.1f}%'
        else:
            status = 'healthy'
            message = f'内存使用正常: {usage_percent:.1f}%'
        
        return {
            'status': status,
            'message': message,
            'details': {
                'total_mb': round(total_mb, 2),
                'used_mb': round(used_mb, 2),
                'available_mb': round(available_mb, 2),
                'usage_percent': round(usage_percent, 1)
            }
        }
        
    except Exception as e:
        return {
            'status': 'unhealthy',
            'message': f'内存检查错误: {str(e)}',
            'details': {'error_type': type(e).__name__}
        }

def check_application_health():
    """检查应用程序健康状态"""
    try:
        # 检查关键目录是否存在
        required_dirs = ['data', 'logs', 'sessions']
        missing_dirs = []
        
        for dir_name in required_dirs:
            if not os.path.exists(dir_name):
                missing_dirs.append(dir_name)
        
        if missing_dirs:
            return {
                'status': 'unhealthy',
                'message': f'缺少必要目录: {", ".join(missing_dirs)}',
                'details': {'missing_directories': missing_dirs}
            }
        
        # 检查配置文件
        config_status = 'healthy'
        config_details = {}
        
        # 检查环境变量
        required_env_vars = ['SECRET_KEY', 'FLASK_ENV']
        missing_env_vars = []
        
        for var in required_env_vars:
            if not os.environ.get(var):
                missing_env_vars.append(var)
        
        if missing_env_vars:
            config_status = 'warning'
            config_details['missing_env_vars'] = missing_env_vars
        
        return {
            'status': config_status,
            'message': '应用程序配置正常' if config_status == 'healthy' else f'缺少环境变量: {", ".join(missing_env_vars)}',
            'details': config_details
        }
        
    except Exception as e:
        return {
            'status': 'unhealthy',
            'message': f'应用程序检查错误: {str(e)}',
            'details': {'error_type': type(e).__name__}
        }

def get_system_info():
    """获取系统信息"""
    try:
        return {
            'hostname': os.uname().nodename if hasattr(os, 'uname') else 'unknown',
            'platform': os.name,
            'python_version': os.sys.version.split()[0],
            'cpu_count': psutil.cpu_count(),
            'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat(),
            'current_time': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'error': f'获取系统信息失败: {str(e)}'
        }

def perform_health_check(detailed=False):
    """执行完整的健康检查"""
    start_time = time.time()
    
    # 基本健康检查
    checks = {
        'database': check_database_health(),
        'application': check_application_health()
    }
    
    # 详细检查（可选）
    if detailed:
        checks.update({
            'disk_space': check_disk_space(),
            'memory': check_memory_usage()
        })
    
    # 确定整体状态
    overall_status = 'healthy'
    critical_issues = []
    warnings = []
    
    for check_name, check_result in checks.items():
        if check_result['status'] == 'unhealthy' or check_result['status'] == 'critical':
            overall_status = 'unhealthy'
            critical_issues.append(f"{check_name}: {check_result['message']}")
        elif check_result['status'] == 'warning':
            if overall_status == 'healthy':
                overall_status = 'warning'
            warnings.append(f"{check_name}: {check_result['message']}")
    
    response_time = (time.time() - start_time) * 1000  # 转换为毫秒
    
    result = {
        'status': overall_status,
        'timestamp': datetime.now().isoformat(),
        'response_time_ms': round(response_time, 2),
        'checks': checks
    }
    
    if critical_issues:
        result['critical_issues'] = critical_issues
    
    if warnings:
        result['warnings'] = warnings
    
    if detailed:
        result['system_info'] = get_system_info()
    
    return result

def create_health_check_response(detailed=False):
    """创建健康检查的 Flask 响应"""
    try:
        health_data = perform_health_check(detailed)
        
        # 根据状态设置 HTTP 状态码
        if health_data['status'] == 'healthy':
            status_code = 200
        elif health_data['status'] == 'warning':
            status_code = 200  # 警告仍然返回 200
        else:
            status_code = 503  # Service Unavailable
        
        return jsonify(health_data), status_code
        
    except Exception as e:
        error_response = {
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': f'健康检查失败: {str(e)}',
            'error_type': type(e).__name__
        }
        return jsonify(error_response), 503