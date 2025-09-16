from flask import Flask, request, jsonify, render_template, redirect, url_for, send_file, make_response, session, g
import sqlite3
import json
import os
from datetime import datetime, timedelta
import csv
from io import StringIO
import bcrypt
from functools import wraps
from flask_cors import CORS
from marshmallow import ValidationError
import time

from config import config
from validation import (
    validate_questionnaire_with_schema, 
    normalize_questionnaire_data, 
    quick_validate,
    create_validation_error_response
)
from question_types import (
    question_processor,
    process_complete_questionnaire,
    format_question_for_display
)
from error_handlers import (
    register_error_handlers,
    StandardErrorResponse,
    validation_error,
    auth_error,
    permission_error,
    not_found_error,
    server_error,
    business_error
)

def merge_questionnaire_data(original_data, update_data):
    """智能合并问卷数据，只更新改动的部分"""
    import copy
    
    # 深拷贝原始数据作为基础
    merged = copy.deepcopy(original_data)
    
    # 合并基本信息
    if 'basic_info' in update_data:
        if 'basic_info' not in merged:
            merged['basic_info'] = {}
        merged['basic_info'].update(update_data['basic_info'])
    
    # 合并问题数据
    if 'questions' in update_data:
        if 'questions' not in merged:
            merged['questions'] = []
        
        # 确保merged['questions']有足够的元素
        while len(merged['questions']) < len(update_data['questions']):
            merged['questions'].append({})
        
        # 逐个更新问题
        for i, update_question in enumerate(update_data['questions']):
            if i < len(merged['questions']):
                # 只更新有值的字段
                for key, value in update_question.items():
                    if value is not None and value != '':
                        merged['questions'][i][key] = value
            else:
                # 新增问题
                merged['questions'].append(update_question)
    
    # 处理其他可能的数据结构（data, detailedData等）
    for key in ['data', 'detailedData']:
        if key in update_data:
            if key not in merged:
                merged[key] = []
            
            if isinstance(update_data[key], list):
                # 确保merged[key]有足够的元素
                while len(merged[key]) < len(update_data[key]):
                    merged[key].append({})
                
                # 逐个更新元素
                for i, update_item in enumerate(update_data[key]):
                    if i < len(merged[key]):
                        if isinstance(update_item, dict):
                            for field_key, field_value in update_item.items():
                                if field_value is not None and field_value != '':
                                    merged[key][i][field_key] = field_value
                        else:
                            merged[key][i] = update_item
                    else:
                        merged[key].append(update_item)
            else:
                merged[key] = update_data[key]
    
    # 更新其他顶级字段
    for key, value in update_data.items():
        if key not in ['basic_info', 'questions', 'data', 'detailedData'] and value is not None:
            merged[key] = value
    
    return merged

app = Flask(__name__, template_folder='templates', static_folder='static')

# 加载配置
config_name = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[config_name])

# 记录应用启动时间用于性能监控
app.config['START_TIME'] = time.time()

# 动态baseUrl配置
def get_base_url():
    """根据环境动态获取baseUrl"""
    # 获取主机名
    hostname = os.environ.get('SERVER_NAME', '')
    
    # 判断是否为本地环境：如果没有设置SERVER_NAME或者是本地地址
    is_local = (not hostname or 
                hostname in ['localhost', '127.0.0.1', '0.0.0.0'] or
                hostname.startswith('192.168.') or
                hostname.startswith('10.') or
                hostname.startswith('172.'))
    
    if is_local:
        # 本地环境使用完整URL，确保前端可以正确跳转
        port = os.environ.get('PORT', '5002')
        return f'http://127.0.0.1:{port}'
    else:
        # 服务器环境使用完整URL
        port = os.environ.get('PORT', '5002')
        return f'http://{hostname}:{port}'

# 将baseUrl添加到应用配置中
app.config['BASE_URL'] = get_base_url()

# 启用CORS支持 - 增强配置
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:*", "http://127.0.0.1:*", "*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept"],
        "supports_credentials": True,
        "max_age": 3600
    }
})

# ==================== 中间件 ====================

@app.before_request
def before_request():
    """请求前处理 - 会话管理中间件"""
    # 跳过静态文件和登录相关的请求
    if (request.endpoint and 
        (request.endpoint.startswith('static') or 
         request.path in ['/api/auth/login', '/api/auth/status', '/login'] or
         request.path.startswith('/static/'))):
        return
    
    # 对于需要认证的API请求，检查会话状态
    if request.path.startswith('/api/') and 'user_id' in session:
        # 检查会话超时（但不自动清除，让装饰器处理）
        timeout_seconds = app.config.get('PERMANENT_SESSION_LIFETIME', timedelta(hours=1)).total_seconds()
        current_time = time.time()
        last_activity = session.get('last_activity', current_time)
        
        # 如果会话即将过期（剩余时间少于5分钟），在响应头中添加警告
        if current_time - last_activity > timeout_seconds - 300:  # 5分钟警告
            g.session_warning = True

@app.after_request
def after_request(response):
    """请求后处理 - 添加会话警告头"""
    if hasattr(g, 'session_warning') and g.session_warning:
        response.headers['X-Session-Warning'] = 'Session will expire soon'
        
        # 如果是JSON响应，添加警告信息
        if response.content_type and 'application/json' in response.content_type:
            try:
                data = response.get_json()
                if isinstance(data, dict) and data.get('success'):
                    data['session_warning'] = '会话即将过期，请及时刷新'
                    response.data = json.dumps(data, default=str, ensure_ascii=False)
            except:
                pass  # 如果无法解析JSON，忽略警告
    
    return response

# 数据库配置
DATABASE = app.config['DATABASE_PATH']

# 初始化数据库
def init_db():
    """初始化数据库，创建所有必要的表"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        
        # 创建问卷数据表 - 根据设计文档更新
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS questionnaires (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            name TEXT,
            grade TEXT,
            submission_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data TEXT NOT NULL,
            report_data TEXT,
            report_generated_at TIMESTAMP,
            parent_phone TEXT,
            parent_wechat TEXT,
            parent_email TEXT,
            gender TEXT,
            birthdate TEXT,
            school TEXT,
            teacher TEXT
        )
        ''')
        
        # 检查并添加新字段（用于数据库升级）
        try:
            cursor.execute("ALTER TABLE questionnaires ADD COLUMN report_data TEXT")
        except sqlite3.OperationalError:
            pass  # 字段已存在
        
        try:
            cursor.execute("ALTER TABLE questionnaires ADD COLUMN report_generated_at TIMESTAMP")
        except sqlite3.OperationalError:
            pass  # 字段已存在
        
        # 添加家长联系方式字段
        try:
            cursor.execute("ALTER TABLE questionnaires ADD COLUMN parent_phone TEXT")
        except sqlite3.OperationalError:
            pass  # 字段已存在
        
        try:
            cursor.execute("ALTER TABLE questionnaires ADD COLUMN parent_wechat TEXT")
        except sqlite3.OperationalError:
            pass  # 字段已存在
        
        try:
            cursor.execute("ALTER TABLE questionnaires ADD COLUMN parent_email TEXT")
        except sqlite3.OperationalError:
            pass  # 字段已存在
        
        # 添加性别和出生日期字段
        try:
            cursor.execute("ALTER TABLE questionnaires ADD COLUMN gender TEXT")
        except sqlite3.OperationalError:
            pass  # 字段已存在
        
        try:
            cursor.execute("ALTER TABLE questionnaires ADD COLUMN birthdate TEXT")
        except sqlite3.OperationalError:
            pass  # 字段已存在
        
        # 添加学校和老师字段
        try:
            cursor.execute("ALTER TABLE questionnaires ADD COLUMN school TEXT")
        except sqlite3.OperationalError:
            pass  # 字段已存在
        
        try:
            cursor.execute("ALTER TABLE questionnaires ADD COLUMN teacher TEXT")
        except sqlite3.OperationalError:
            pass  # 字段已存在
        
        # 创建用户认证表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'admin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
        ''')
        
        # 创建操作日志表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS operation_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            operation TEXT NOT NULL,
            target_id INTEGER,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # 创建默认管理员用户（如果不存在）
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            # 默认密码: admin123
            password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                ('admin', password_hash.decode('utf-8'), 'admin')
            )
        
        conn.commit()
        print("数据库初始化完成")

# 获取数据库连接
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ==================== 会话管理和权限控制 ====================

def check_session_timeout():
    """检查会话是否超时"""
    if 'user_id' in session:
        # 检查会话是否设置了最后活动时间
        if 'last_activity' not in session:
            session['last_activity'] = time.time()
            return True
        
        # 计算会话超时时间（从配置中获取，默认1小时）
        timeout_seconds = app.config.get('PERMANENT_SESSION_LIFETIME', timedelta(hours=1)).total_seconds()
        current_time = time.time()
        last_activity = session.get('last_activity', current_time)
        
        # 如果超时，清除会话
        if current_time - last_activity > timeout_seconds:
            user_id = session.get('user_id')
            username = session.get('username')
            
            # 记录自动登出日志
            if user_id:
                OperationLogger.log(OperationLogger.AUTO_LOGOUT, user_id, f'用户 {username} 会话超时自动登出')
            
            session.clear()
            return False
        
        # 更新最后活动时间
        session['last_activity'] = current_time
        return True
    
    return False

def update_session_activity():
    """更新会话活动时间"""
    if 'user_id' in session:
        session['last_activity'] = time.time()

# 认证装饰器
def login_required(f):
    """要求用户登录的装饰器 - 增强版本，包含会话超时检查"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查会话超时
        if not check_session_timeout():
            # 如果是API请求，返回JSON错误
            if request.path.startswith('/api/'):
                return jsonify({
                    'success': False, 
                    'error': {
                        'code': 'SESSION_EXPIRED',
                        'message': '会话已过期，请重新登录'
                    }
                }), 401
            # 如果是页面请求，重定向到登录页面
            else:
                return redirect(url_for('login_page'))
        
        # 检查用户是否登录
        if 'user_id' not in session:
            # 如果是API请求，返回JSON错误
            if request.path.startswith('/api/'):
                return jsonify({
                    'success': False, 
                    'error': {
                        'code': 'AUTH_REQUIRED',
                        'message': '需要登录'
                    }
                }), 401
            # 如果是页面请求，重定向到登录页面
            else:
                return redirect(url_for('login_page'))
        
        # 更新会话活动时间
        update_session_activity()
        
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """要求管理员权限的装饰器 - 增强版本，包含会话超时和权限检查"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查会话超时
        if not check_session_timeout():
            return jsonify({
                'success': False, 
                'error': {
                    'code': 'SESSION_EXPIRED',
                    'message': '会话已过期，请重新登录'
                }
            }), 401
        
        # 检查用户是否登录
        if 'user_id' not in session:
            return jsonify({
                'success': False, 
                'error': {
                    'code': 'AUTH_REQUIRED',
                    'message': '需要登录'
                }
            }), 401
        
        # 检查管理员权限
        user_role = session.get('user_role')
        if user_role != 'admin':
            # 记录权限不足的尝试
            OperationLogger.log(OperationLogger.ACCESS_DENIED, session.get('user_id'), 
                         f'用户尝试访问需要管理员权限的资源: {request.path}')
            
            return jsonify({
                'success': False, 
                'error': {
                    'code': 'PERMISSION_DENIED',
                    'message': '权限不足，需要管理员权限'
                }
            }), 403
        
        # 更新会话活动时间
        update_session_activity()
        
        return f(*args, **kwargs)
    return decorated_function

def validate_session_integrity():
    """验证会话完整性"""
    if 'user_id' in session:
        user_id = session.get('user_id')
        
        # 验证用户是否仍然存在且有效
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, username, role FROM users WHERE id = ?", (user_id,))
                user = cursor.fetchone()
                
                if not user:
                    # 用户不存在，清除会话
                    session.clear()
                    return False
                
                # 更新会话中的用户信息（防止权限变更后仍使用旧权限）
                session['username'] = user['username']
                session['user_role'] = user['role']
                
                return True
        except Exception as e:
            print(f"验证会话完整性失败: {e}")
            session.clear()
            return False
    
    return False

# ==================== 操作日志系统 ====================

class OperationLogger:
    """操作日志记录器"""
    
    # 操作类型常量
    LOGIN = 'LOGIN'
    LOGOUT = 'LOGOUT'
    AUTO_LOGOUT = 'AUTO_LOGOUT'
    CREATE_QUESTIONNAIRE = 'CREATE_QUESTIONNAIRE'
    UPDATE_QUESTIONNAIRE = 'UPDATE_QUESTIONNAIRE'
    DELETE_QUESTIONNAIRE = 'DELETE_QUESTIONNAIRE'
    BATCH_DELETE = 'BATCH_DELETE'
    VIEW_QUESTIONNAIRE = 'VIEW_QUESTIONNAIRE'
    EXPORT_DATA = 'EXPORT_DATA'
    ACCESS_DENIED = 'ACCESS_DENIED'
    EXTEND_SESSION = 'EXTEND_SESSION'
    SYSTEM_ERROR = 'SYSTEM_ERROR'
    
    # 敏感操作列表
    SENSITIVE_OPERATIONS = {
        DELETE_QUESTIONNAIRE, BATCH_DELETE, EXPORT_DATA, 
        EXTEND_SESSION, ACCESS_DENIED
    }
    
    @staticmethod
    def log(operation, target_id=None, details=None, ip_address=None, user_agent=None):
        """记录操作日志"""
        try:
            user_id = session.get('user_id')
            username = session.get('username', 'anonymous')
            
            # 获取请求信息
            if not ip_address:
                ip_address = request.remote_addr or 'unknown'
            if not user_agent:
                user_agent = request.headers.get('User-Agent', 'unknown')[:500]  # 限制长度
            
            # 构建详细信息
            log_details = {
                'operation': operation,
                'user_details': details or '',
                'ip_address': ip_address,
                'user_agent': user_agent,
                'timestamp': datetime.now().isoformat(),
                'request_path': request.path if request else 'unknown',
                'request_method': request.method if request else 'unknown'
            }
            
            # 对于敏感操作，记录更多信息
            if operation in OperationLogger.SENSITIVE_OPERATIONS:
                log_details['sensitive'] = True
                log_details['session_id'] = session.get('_id', 'unknown')
            
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO operation_logs (user_id, operation, target_id, details) VALUES (?, ?, ?, ?)",
                    (user_id, operation, target_id, json.dumps(log_details, default=str, ensure_ascii=False))
                )
                conn.commit()
                
        except Exception as e:
            # 记录日志失败不应该影响主要功能
            print(f"记录操作日志失败: {e}")
            
            # 尝试记录到文件作为备份
            try:
                log_file = os.path.join(os.path.dirname(__file__), 'logs', 'operation_errors.log')
                os.makedirs(os.path.dirname(log_file), exist_ok=True)
                
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(f"{datetime.now().isoformat()} - 日志记录失败: {e}\n")
                    f.write(f"操作: {operation}, 用户: {username}, 详情: {details}\n\n")
            except:
                pass  # 如果文件记录也失败，则忽略
    
    @staticmethod
    def log_system_event(event_type, details=None):
        """记录系统事件（无用户上下文）"""
        try:
            log_details = {
                'event_type': event_type,
                'details': details or '',
                'timestamp': datetime.now().isoformat(),
                'system_event': True
            }
            
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO operation_logs (user_id, operation, target_id, details) VALUES (?, ?, ?, ?)",
                    (None, f'SYSTEM_{event_type}', None, json.dumps(log_details, default=str, ensure_ascii=False))
                )
                conn.commit()
                
        except Exception as e:
            print(f"记录系统事件失败: {e}")

# 兼容性函数
def log_operation(operation, target_id=None, details=None):
    """记录用户操作日志 - 兼容性函数"""
    OperationLogger.log(operation, target_id, details)

# ==================== 认证相关API ====================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """用户登录接口"""
    try:
        data = request.json
        
        if not data:
            response_data, status_code = validation_error(['请求数据不能为空'])
            return jsonify(response_data), status_code
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            response_data, status_code = validation_error(['用户名和密码不能为空'])
            return jsonify(response_data), status_code
        
        # 查询用户
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
        
        if not user:
            response_data, status_code = auth_error('用户名或密码错误')
            return jsonify(response_data), status_code
        
        # 验证密码
        if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            response_data, status_code = auth_error('用户名或密码错误')
            return jsonify(response_data), status_code
        
        # 创建会话
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['user_role'] = user['role']
        session['last_activity'] = time.time()
        session['login_time'] = time.time()
        session.permanent = True
        
        # 更新最后登录时间
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET last_login = ? WHERE id = ?",
                (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), user['id'])
            )
            conn.commit()
        
        # 记录登录日志
        OperationLogger.log(OperationLogger.LOGIN, user['id'], f'用户 {username} 登录系统')
        
        return jsonify({
            'success': True,
            'message': '登录成功',
            'user': {
                'id': user['id'],
                'username': user['username'],
                'role': user['role']
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        response_data, status_code = server_error('登录失败', str(e))
        return jsonify(response_data), status_code

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """用户登出接口"""
    try:
        user_id = session.get('user_id')
        username = session.get('username')
        
        # 记录登出日志
        if user_id:
            OperationLogger.log(OperationLogger.LOGOUT, user_id, f'用户 {username} 登出系统')
        
        # 清除会话
        session.clear()
        
        return jsonify({
            'success': True,
            'message': '登出成功',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': '登出失败',
                'details': str(e)
            }
        }), 500

@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    """检查登录状态接口 - 增强版本，包含会话超时检查"""
    try:
        # 检查会话超时
        if not check_session_timeout():
            return jsonify({
                'success': True,
                'authenticated': False,
                'user': None,
                'session_expired': True
            })
        
        # 验证会话完整性
        if not validate_session_integrity():
            return jsonify({
                'success': True,
                'authenticated': False,
                'user': None,
                'session_invalid': True
            })
        
        if 'user_id' in session:
            # 计算会话剩余时间
            timeout_seconds = app.config.get('PERMANENT_SESSION_LIFETIME', timedelta(hours=1)).total_seconds()
            last_activity = session.get('last_activity', time.time())
            remaining_time = timeout_seconds - (time.time() - last_activity)
            
            return jsonify({
                'success': True,
                'authenticated': True,
                'user': {
                    'id': session['user_id'],
                    'username': session['username'],
                    'role': session['user_role']
                },
                'session_info': {
                    'remaining_time': max(0, int(remaining_time)),
                    'last_activity': datetime.fromtimestamp(last_activity).isoformat(),
                    'expires_at': datetime.fromtimestamp(last_activity + timeout_seconds).isoformat()
                }
            })
        else:
            return jsonify({
                'success': True,
                'authenticated': False,
                'user': None
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': '检查登录状态失败',
                'details': str(e)
            }
        }), 500

@app.route('/api/auth/refresh', methods=['POST'])
@login_required
def refresh_session():
    """刷新会话接口"""
    try:
        # 更新会话活动时间
        update_session_activity()
        
        # 验证会话完整性
        if not validate_session_integrity():
            return jsonify({
                'success': False,
                'error': {
                    'code': 'SESSION_INVALID',
                    'message': '会话无效，请重新登录'
                }
            }), 401
        
        # 计算会话剩余时间
        timeout_seconds = app.config.get('PERMANENT_SESSION_LIFETIME', timedelta(hours=1)).total_seconds()
        last_activity = session.get('last_activity', time.time())
        remaining_time = timeout_seconds - (time.time() - last_activity)
        
        return jsonify({
            'success': True,
            'message': '会话已刷新',
            'session_info': {
                'remaining_time': max(0, int(remaining_time)),
                'last_activity': datetime.fromtimestamp(last_activity).isoformat(),
                'expires_at': datetime.fromtimestamp(last_activity + timeout_seconds).isoformat()
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': '刷新会话失败',
                'details': str(e)
            }
        }), 500

@app.route('/api/auth/extend', methods=['POST'])
@admin_required
def extend_session():
    """延长会话接口（仅管理员）"""
    try:
        data = request.json or {}
        extend_minutes = data.get('minutes', 60)  # 默认延长60分钟
        
        # 限制延长时间（最多4小时）
        if extend_minutes > 240:
            extend_minutes = 240
        
        # 更新会话活动时间，相当于延长会话
        session['last_activity'] = time.time() + (extend_minutes * 60)
        
        # 记录会话延长操作
        OperationLogger.log(OperationLogger.EXTEND_SESSION, session.get('user_id'), 
                     f'管理员延长会话 {extend_minutes} 分钟')
        
        return jsonify({
            'success': True,
            'message': f'会话已延长 {extend_minutes} 分钟',
            'extended_minutes': extend_minutes,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': '延长会话失败',
                'details': str(e)
            }
        }), 500

# 使用新的验证模块替换原有的验证函数
def validate_questionnaire_data(data):
    """验证问卷数据格式 - 使用新的验证模块"""
    return quick_validate(data)

# 问卷提交API - 任务4.1要求的端点
@app.route('/api/submit', methods=['POST'])
def submit_questionnaire_legacy():
    """问卷提交接口 - 兼容旧版本API路径"""
    return submit_questionnaire()

# 保存问卷数据 - 标准化API路径
@app.route('/api/questionnaires', methods=['POST'])
def submit_questionnaire():
    try:
        data = request.json
        
        if not data:
            response_data, status_code = validation_error(['请求数据不能为空'])
            return jsonify(response_data), status_code
        
        # 数据标准化
        try:
            normalized_data = normalize_questionnaire_data(data)
        except Exception as e:
            response_data, status_code = validation_error([f'数据标准化失败: {str(e)}'])
            return jsonify(response_data), status_code
        
        # 使用新的验证模块进行验证
        is_valid, validation_errors, validated_data = validate_questionnaire_with_schema(normalized_data)
        
        if not is_valid:
            response_data, status_code = validation_error(validation_errors)
            return jsonify(response_data), status_code
        
        # 从验证后的数据中提取基本信息
        questionnaire_type = validated_data.get('type', 'unknown')
        basic_info = validated_data.get('basic_info', {})
        
        # 调试输出
        print("\n" + "=" * 80)
        print("🔍 DEBUG: 问卷提交调试信息")
        print("=" * 80)
        print(f"DEBUG: Complete basic_info content: {basic_info}")
        print(f"DEBUG: basic_info keys: {list(basic_info.keys())}")
        print(f"📋 validated_data keys: {list(validated_data.keys())}")
        print(f"📋 basic_info keys: {list(basic_info.keys()) if basic_info else 'None'}")
        print(f"👤 validated_data gender: '{validated_data.get('gender')}'")
        print(f"🎂 validated_data birthdate: '{validated_data.get('birthdate')}'")
        if basic_info:
            print(f"👤 basic_info gender: '{basic_info.get('gender')}'")
            print(f"🎂 basic_info birthdate: '{basic_info.get('birthdate')}'")
            print(f"🎂 basic_info birth_date: '{basic_info.get('birth_date')}'")
        print("=" * 80 + "\n")
        
        name = basic_info.get('name', '') or validated_data.get('name', '')
        grade = basic_info.get('grade', '') or validated_data.get('grade', '')
        submission_date = basic_info.get('submission_date', datetime.now().strftime('%Y-%m-%d'))
        
        # 提取家长联系方式
        parent_phone = basic_info.get('parent_phone', '') or validated_data.get('parent_phone', '')
        parent_wechat = basic_info.get('parent_wechat', '') or validated_data.get('parent_wechat', '')
        parent_email = basic_info.get('parent_email', '') or validated_data.get('parent_email', '')
        
        # 提取性别和出生日期，优先从basic_info获取，如果没有则从顶级字段获取
        gender = basic_info.get('gender', '') or validated_data.get('gender', '')
        birthdate = basic_info.get('birthdate', '') or basic_info.get('birth_date', '') or validated_data.get('birthdate', '') or validated_data.get('birth_date', '')
        
        # 提取学校和老师信息
        school = basic_info.get('school', '') or validated_data.get('school', '')
        teacher = basic_info.get('teacher', '') or validated_data.get('teacher', '')
        
        # 提取新增字段
        school_name = basic_info.get('school_name', '')
        admission_date = basic_info.get('admission_date', '')
        address = basic_info.get('address', '')
        filler_name = basic_info.get('filler_name', '')
        fill_date = basic_info.get('fill_date', '')
        
        print(f"DEBUG: Final extracted values - gender: '{gender}', birthdate: '{birthdate}', school: '{school}', teacher: '{teacher}'")
        print(f"DEBUG: New fields - school_name: '{school_name}', admission_date: '{admission_date}', address: '{address}', filler_name: '{filler_name}', fill_date: '{fill_date}'")
        
        # 始终使用服务器当前时间作为创建时间
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 使用问题类型处理器进行最终处理
        final_data = process_complete_questionnaire(validated_data)
        
        # 将处理后的数据保存到数据库
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO questionnaires (type, name, grade, submission_date, created_at, updated_at, data, parent_phone, parent_wechat, parent_email, gender, birthdate, school, teacher, school_name, admission_date, address, filler_name) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (questionnaire_type, name, grade, submission_date, created_at, created_at, json.dumps(final_data, default=str, ensure_ascii=False), parent_phone, parent_wechat, parent_email, gender, birthdate, school, teacher, school_name, admission_date, address, filler_name)
            )
            conn.commit()
            questionnaire_id = cursor.lastrowid
        
        # 记录操作日志
        OperationLogger.log(OperationLogger.CREATE_QUESTIONNAIRE, questionnaire_id, f'创建问卷: {name} - {questionnaire_type}')
        
        return jsonify({
            'success': True, 
            'id': questionnaire_id,
            'message': '问卷提交成功',
            'timestamp': datetime.now().isoformat()
        }), 201
        
    except ValidationError as e:
        response_data, status_code = validation_error(e.messages)
        return jsonify(response_data), status_code
    except Exception as e:
        response_data, status_code = server_error('问卷提交失败', str(e))
        return jsonify(response_data), status_code

# 获取所有问卷数据 - 增强版本，支持分页和高级搜索
@app.route('/api/questionnaires', methods=['GET'])
@login_required
def get_questionnaires():
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 20)), 100)  # 限制最大每页数量
        search = request.args.get('search', '').strip()
        
        # 高级筛选参数
        questionnaire_type = request.args.get('type', '').strip()
        grade_filter = request.args.get('grade', '').strip()
        date_from = request.args.get('date_from', '').strip()
        date_to = request.args.get('date_to', '').strip()
        sort_by = request.args.get('sort_by', 'created_at')  # 排序字段
        sort_order = request.args.get('sort_order', 'desc')  # 排序方向
        
        # 验证排序参数
        valid_sort_fields = ['id', 'name', 'type', 'grade', 'submission_date', 'created_at', 'updated_at']
        if sort_by not in valid_sort_fields:
            sort_by = 'created_at'
        
        if sort_order.lower() not in ['asc', 'desc']:
            sort_order = 'desc'
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            # 构建查询条件
            where_conditions = []
            params = []
            
            # 基本搜索 - 搜索姓名、类型、年级
            if search:
                where_conditions.append("(name LIKE ? OR type LIKE ? OR grade LIKE ?)")
                search_param = f"%{search}%"
                params.extend([search_param, search_param, search_param])
            
            # 问卷类型筛选
            if questionnaire_type:
                where_conditions.append("type = ?")
                params.append(questionnaire_type)
            
            # 年级筛选
            if grade_filter:
                where_conditions.append("grade = ?")
                params.append(grade_filter)
            
            # 日期范围筛选
            if date_from:
                where_conditions.append("DATE(created_at) >= ?")
                params.append(date_from)
            
            if date_to:
                where_conditions.append("DATE(created_at) <= ?")
                params.append(date_to)
            
            # 构建完整的WHERE子句
            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)
            
            # 获取总数
            count_query = f"SELECT COUNT(*) FROM questionnaires {where_clause}"
            cursor.execute(count_query, params)
            total_count = cursor.fetchone()[0]
            
            # 获取分页数据
            offset = (page - 1) * limit
            query = f"SELECT * FROM questionnaires {where_clause} ORDER BY {sort_by} {sort_order.upper()} LIMIT ? OFFSET ?"
            cursor.execute(query, params + [limit, offset])
            questionnaires = cursor.fetchall()
        
        result = []
        for q in questionnaires:
            # 解析data字段获取详细信息
            data = json.loads(q['data'])
            
            # 从data中提取性别、出生日期、家长联系信息、学校和老师信息
            gender = None
            birthdate = None
            parent_phone = None
            parent_wechat = None
            parent_email = None
            school = None
            teacher = None
            
            # 尝试从不同位置获取基本信息
            if 'basicInfo' in data and data['basicInfo']:
                basic_info = data['basicInfo']
                gender = basic_info.get('gender')
                birthdate = basic_info.get('birthdate') or basic_info.get('birth_date')
                parent_phone = basic_info.get('parent_phone')
                parent_wechat = basic_info.get('parent_wechat')
                parent_email = basic_info.get('parent_email')
                school = basic_info.get('school')
                teacher = basic_info.get('teacher')
            elif 'basic_info' in data and data['basic_info']:
                basic_info = data['basic_info']
                gender = basic_info.get('gender')
                birthdate = basic_info.get('birthdate') or basic_info.get('birth_date')
                parent_phone = basic_info.get('parent_phone')
                parent_wechat = basic_info.get('parent_wechat')
                parent_email = basic_info.get('parent_email')
                school = basic_info.get('school')
                teacher = basic_info.get('teacher')
            
            # 如果还没找到，尝试从顶级字段获取
            if not gender:
                gender = data.get('gender') or data.get('basic_info_gender')
            if not birthdate:
                birthdate = data.get('birthdate') or data.get('basic_info_birthdate') or data.get('birth_date')
            if not parent_phone:
                parent_phone = data.get('parent_phone') or data.get('basic_info_parent_phone')
            if not parent_wechat:
                parent_wechat = data.get('parent_wechat') or data.get('basic_info_parent_wechat')
            if not parent_email:
                parent_email = data.get('parent_email') or data.get('basic_info_parent_email')
            if not school:
                school = data.get('school') or data.get('basic_info_school')
            if not teacher:
                teacher = data.get('teacher') or data.get('basic_info_teacher')
            
            result.append({
                'id': q['id'],
                'type': q['type'],
                'name': q['name'],
                'grade': q['grade'],
                'gender': gender,
                'birthdate': birthdate,
                'submission_date': q['submission_date'],
                'created_at': q['created_at'],
                'updated_at': q['updated_at'],
                'parent_phone': parent_phone,
                'parent_wechat': parent_wechat,
                'parent_email': parent_email,
                'school': school,
                'teacher': teacher,
                'school_name': q['school_name'],
                'admission_date': q['admission_date'],
                'address': q['address'],
                'filler_name': q['filler_name'],
                'fill_date': q['fill_date'],
                'data': data
            })
        
        # 记录查询操作日志（仅在有搜索条件时）
        if search or questionnaire_type or grade_filter or date_from or date_to:
            search_details = {
                'search': search,
                'type': questionnaire_type,
                'grade': grade_filter,
                'date_from': date_from,
                'date_to': date_to,
                'results_count': len(result)
            }
            OperationLogger.log('SEARCH_QUESTIONNAIRES', None, f'搜索问卷: {json.dumps(search_details, default=str, ensure_ascii=False)}')
        
        return jsonify({
            'success': True,
            'data': result,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total_count,
                'pages': (total_count + limit - 1) // limit,
                'has_next': page < (total_count + limit - 1) // limit,
                'has_prev': page > 1
            },
            'filters': {
                'search': search,
                'type': questionnaire_type,
                'grade': grade_filter,
                'date_from': date_from,
                'date_to': date_to,
                'sort_by': sort_by,
                'sort_order': sort_order
            }
        })
    except Exception as e:
        response_data, status_code = server_error('获取问卷列表失败', str(e))
        return jsonify(response_data), status_code

# 获取筛选选项 - 用于高级搜索
@app.route('/api/questionnaires/filters', methods=['GET'])
@login_required
def get_filter_options():
    """获取可用的筛选选项"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # 获取所有可用的问卷类型
            cursor.execute("SELECT DISTINCT type FROM questionnaires WHERE type IS NOT NULL ORDER BY type")
            types = [row[0] for row in cursor.fetchall()]
            
            # 获取所有可用的年级
            cursor.execute("SELECT DISTINCT grade FROM questionnaires WHERE grade IS NOT NULL AND grade != '' ORDER BY grade")
            grades = [row[0] for row in cursor.fetchall()]
            
            # 获取日期范围
            cursor.execute("SELECT MIN(DATE(created_at)), MAX(DATE(created_at)) FROM questionnaires")
            date_range = cursor.fetchone()
            
            return jsonify({
                'success': True,
                'data': {
                    'types': types,
                    'grades': grades,
                    'date_range': {
                        'min': date_range[0],
                        'max': date_range[1]
                    },
                    'sort_options': [
                        {'value': 'created_at', 'label': '创建时间'},
                        {'value': 'updated_at', 'label': '更新时间'},
                        {'value': 'name', 'label': '姓名'},
                        {'value': 'type', 'label': '问卷类型'},
                        {'value': 'grade', 'label': '年级'},
                        {'value': 'submission_date', 'label': '提交日期'}
                    ]
                }
            })
    except Exception as e:
        response_data, status_code = server_error('获取筛选选项失败', str(e))
        return jsonify(response_data), status_code

# 获取单个问卷数据
@app.route('/api/questionnaires/<int:questionnaire_id>', methods=['GET'])
@login_required
def get_questionnaire(questionnaire_id):
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM questionnaires WHERE id = ?", (questionnaire_id,))
            q = cursor.fetchone()
        
        if not q:
            response_data, status_code = not_found_error('问卷')
            return jsonify(response_data), status_code
        
        result = {
            'success': True,
            'data': {
                'id': q['id'],
                'type': q['type'],
                'name': q['name'],
                'grade': q['grade'],
                'submission_date': q['submission_date'],
                'created_at': q['created_at'],
                'updated_at': q['updated_at'],
                'data': json.loads(q['data'])
            }
        }
        
        return jsonify(result)
    except Exception as e:
        response_data, status_code = server_error('获取问卷详情失败', str(e))
        return jsonify(response_data), status_code

# 更新问卷数据
@app.route('/api/questionnaires/<int:questionnaire_id>', methods=['PUT'])
@admin_required
def update_questionnaire(questionnaire_id):
    try:
        data = request.json
        print(f"[DEBUG] 接收到的原始数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        if not data:
            error_msg = '请求数据不能为空'
            print(f"[ERROR] {error_msg}")
            return jsonify(create_validation_error_response([error_msg])), 400
        
        # 获取原始问卷数据
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT data, type, name, grade, submission_date FROM questionnaires WHERE id = ?", (questionnaire_id,))
            result = cursor.fetchone()
            
            if not result:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'NOT_FOUND',
                        'message': '问卷不存在'
                    }
                }), 404
            
            original_data_str, original_type, original_name, original_grade, original_submission_date = result
            original_data = json.loads(original_data_str) if original_data_str else {}
        
        # 增量更新：合并原始数据和新数据
        merged_data = merge_questionnaire_data(original_data, data)
        print(f"[DEBUG] 合并后的数据: {json.dumps(merged_data, ensure_ascii=False, indent=2)}")
        
        # 数据标准化
        try:
            normalized_data = normalize_questionnaire_data(merged_data)
            print(f"[DEBUG] 标准化后的数据: {json.dumps(normalized_data, ensure_ascii=False, indent=2)}")
        except Exception as e:
            error_msg = f'数据标准化失败: {str(e)}'
            print(f"[ERROR] {error_msg}")
            return jsonify(create_validation_error_response([error_msg])), 400
        
        # 使用新的验证模块进行验证
        is_valid, validation_errors, validated_data = validate_questionnaire_with_schema(normalized_data)
        
        if not is_valid:
            error_msg = f'数据验证失败: {validation_errors}'
            print(f"[ERROR] {error_msg}")
            return jsonify(create_validation_error_response(validation_errors)), 400
        
        # 从验证后的数据中提取基本信息
        questionnaire_type = validated_data.get('type', original_type)
        basic_info = validated_data.get('basic_info', {})
        name = basic_info.get('name', original_name)
        grade = basic_info.get('grade', original_grade)
        submission_date = basic_info.get('submission_date', original_submission_date)
        
        updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 使用问题类型处理器进行最终处理
        final_data = process_complete_questionnaire(validated_data)
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE questionnaires SET type = ?, name = ?, grade = ?, submission_date = ?, updated_at = ?, data = ? WHERE id = ?",
                (questionnaire_type, name, grade, submission_date, updated_at, json.dumps(final_data, default=str, ensure_ascii=False), questionnaire_id)
            )
            conn.commit()
        
        # 记录操作日志
        OperationLogger.log(OperationLogger.UPDATE_QUESTIONNAIRE, questionnaire_id, f'增量更新问卷: {name} - {questionnaire_type}')
        
        return jsonify({
            'success': True,
            'message': '问卷更新成功',
            'timestamp': datetime.now().isoformat()
        })
    except ValidationError as e:
        return jsonify(create_validation_error_response(e.messages)), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': '更新问卷失败',
                'details': str(e)
            }
        }), 500

# 批量删除问卷
@app.route('/api/questionnaires/batch', methods=['DELETE'])
@admin_required
def batch_delete_questionnaires():
    try:
        data = request.json
        questionnaire_ids = data.get('ids', [])
        
        if not questionnaire_ids:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': '未提供问卷ID'
                }
            }), 400
        
        # 验证并转换ID格式
        try:
            # 尝试将所有ID转换为整数
            questionnaire_ids = [int(id) for id in questionnaire_ids]
            # 验证转换后的ID是否有效
            if not all(id > 0 for id in questionnaire_ids):
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'message': '问卷ID必须为正整数'
                    }
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': '问卷ID格式无效'
                }
            }), 400
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            # 首先检查要删除的问卷是否存在
            placeholders = ','.join(['?'] * len(questionnaire_ids))
            cursor.execute(f"SELECT id, name, type FROM questionnaires WHERE id IN ({placeholders})", questionnaire_ids)
            existing_questionnaires = cursor.fetchall()
            
            if not existing_questionnaires:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'NOT_FOUND',
                        'message': '未找到指定的问卷'
                    }
                }), 404
            
            # 执行批量删除
            cursor.execute(f"DELETE FROM questionnaires WHERE id IN ({placeholders})", questionnaire_ids)
            conn.commit()
            
            deleted_count = cursor.rowcount
            
            # 重新排序ID
            cursor.execute("SELECT id FROM questionnaires ORDER BY created_at")
            questionnaires = cursor.fetchall()
            
            for new_id, questionnaire in enumerate(questionnaires, 1):
                old_id = questionnaire['id']
                if old_id != new_id:
                    cursor.execute("UPDATE questionnaires SET id = ? WHERE id = ?", (new_id, old_id))
            
            conn.commit()
            
            # 重置自增计数器
            cursor.execute("UPDATE sqlite_sequence SET seq = (SELECT COUNT(*) FROM questionnaires) WHERE name = 'questionnaires'")
            conn.commit()
        
        # 记录操作日志
        questionnaire_names = [q['name'] for q in existing_questionnaires]
        OperationLogger.log(OperationLogger.BATCH_DELETE, None, f'批量删除问卷 {deleted_count} 条: {", ".join(questionnaire_names)}')
        
        return jsonify({
            'success': True,
            'message': f'成功删除 {deleted_count} 条问卷',
            'deleted_count': deleted_count,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': '批量删除失败',
                'details': str(e)
            }
        }), 500

# 删除问卷
@app.route('/api/questionnaires/<int:questionnaire_id>', methods=['DELETE'])
@admin_required
def delete_questionnaire(questionnaire_id):
    """删除指定问卷"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # 首先获取要删除的问卷信息用于日志记录
            cursor.execute("SELECT name, type, data FROM questionnaires WHERE id = ?", (questionnaire_id,))
            questionnaire_row = cursor.fetchone()
            
            if not questionnaire_row:
                response_data, status_code = not_found_error('问卷不存在')
                return jsonify(response_data), status_code
            
            # 提取问卷信息
            questionnaire_name = questionnaire_row['name'] or '未知'
            questionnaire_type = questionnaire_row['type'] or '未知'
            
            # 执行删除
            cursor.execute("DELETE FROM questionnaires WHERE id = ?", (questionnaire_id,))
            deleted_count = cursor.rowcount
            
            if deleted_count == 0:
                response_data, status_code = not_found_error('问卷不存在或已被删除')
                return jsonify(response_data), status_code
            
            # 重新排序ID - 保持连续性
            cursor.execute("SELECT id FROM questionnaires ORDER BY created_at")
            questionnaires = cursor.fetchall()
            
            for new_id, questionnaire in enumerate(questionnaires, 1):
                old_id = questionnaire['id']
                if old_id != new_id:
                    cursor.execute("UPDATE questionnaires SET id = ? WHERE id = ?", (new_id, old_id))
            
            conn.commit()
            
            # 重置自增计数器
            cursor.execute("UPDATE sqlite_sequence SET seq = (SELECT COUNT(*) FROM questionnaires) WHERE name = 'questionnaires'")
            conn.commit()
        
        # 记录操作日志
        OperationLogger.log(OperationLogger.DELETE_QUESTIONNAIRE, questionnaire_id, 
                     f'删除问卷: {questionnaire_name} - {questionnaire_type}')
        
        return jsonify({
            'success': True,
            'message': '问卷删除成功，数据已重新编号',
            'deleted_id': questionnaire_id,
            'reindexed': True,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        response_data, status_code = server_error('删除问卷失败', str(e))
        return jsonify(response_data), status_code

# ==================== 系统监控和统计功能 ====================

@app.route('/api/admin/statistics', methods=['GET'])
@login_required
def get_admin_statistics():
    """获取管理统计数据 - 增强版本"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # 基础统计数据
            cursor.execute("SELECT COUNT(*) FROM questionnaires")
            total_count = cursor.fetchone()[0]
            
            # 今日新增问卷数
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute("SELECT COUNT(*) FROM questionnaires WHERE DATE(created_at) = ?", (today,))
            today_count = cursor.fetchone()[0]
            
            # 本周新增问卷数
            cursor.execute("SELECT COUNT(*) FROM questionnaires WHERE DATE(created_at) >= DATE('now', '-7 days')")
            week_count = cursor.fetchone()[0]
            
            # 本月新增问卷数
            cursor.execute("SELECT COUNT(*) FROM questionnaires WHERE DATE(created_at) >= DATE('now', 'start of month')")
            month_count = cursor.fetchone()[0]
            
            # 按类型分组的统计
            cursor.execute("SELECT type, COUNT(*) FROM questionnaires GROUP BY type")
            type_stats = dict(cursor.fetchall())
            
            # 按年级分组的统计
            cursor.execute("SELECT grade, COUNT(*) FROM questionnaires WHERE grade IS NOT NULL GROUP BY grade")
            grade_stats = dict(cursor.fetchall())
            
            # 最近30天的提交趋势
            cursor.execute("""
                SELECT DATE(created_at) as date, COUNT(*) as count 
                FROM questionnaires 
                WHERE DATE(created_at) >= DATE('now', '-30 days')
                GROUP BY DATE(created_at)
                ORDER BY date
            """)
            trend_data = [{'date': row[0], 'count': row[1]} for row in cursor.fetchall()]
            
            # 每小时提交分布（今日）
            cursor.execute("""
                SELECT strftime('%H', created_at) as hour, COUNT(*) as count
                FROM questionnaires 
                WHERE DATE(created_at) = ?
                GROUP BY strftime('%H', created_at)
                ORDER BY hour
            """, (today,))
            hourly_stats = [{'hour': int(row[0]), 'count': row[1]} for row in cursor.fetchall()]
            
            # 用户活动统计
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(last_login) = ?", (today,))
            active_users_today = cursor.fetchone()[0]
            
            # 操作日志统计
            cursor.execute("SELECT COUNT(*) FROM operation_logs")
            total_operations = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM operation_logs WHERE DATE(created_at) = ?", (today,))
            operations_today = cursor.fetchone()[0]
            
            # 数据库大小统计
            cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
            db_size = cursor.fetchone()[0] if cursor.fetchone() else 0
            
        return jsonify({
            'success': True,
            'data': {
                'overview': {
                    'total_questionnaires': total_count,
                    'today_submissions': today_count,
                    'week_submissions': week_count,
                    'month_submissions': month_count,
                    'total_users': total_users,
                    'active_users_today': active_users_today,
                    'total_operations': total_operations,
                    'operations_today': operations_today,
                    'database_size': db_size
                },
                'distributions': {
                    'type_distribution': type_stats,
                    'grade_distribution': grade_stats
                },
                'trends': {
                    'submission_trend': trend_data,
                    'hourly_distribution': hourly_stats
                }
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': '获取统计数据失败',
                'details': str(e)
            }
        }), 500

@app.route('/api/admin/system/health', methods=['GET'])
@login_required
def system_health_check():
    """系统健康检查接口"""
    try:
        health_status = {
            'status': 'healthy',
            'checks': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # 数据库连接检查
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
            health_status['checks']['database'] = {
                'status': 'healthy',
                'message': '数据库连接正常'
            }
        except Exception as e:
            health_status['checks']['database'] = {
                'status': 'unhealthy',
                'message': f'数据库连接失败: {str(e)}'
            }
            health_status['status'] = 'unhealthy'
        
        # 磁盘空间检查
        try:
            import shutil
            total, used, free = shutil.disk_usage(os.path.dirname(DATABASE))
            free_percent = (free / total) * 100
            
            if free_percent > 10:
                health_status['checks']['disk_space'] = {
                    'status': 'healthy',
                    'message': f'磁盘空间充足 ({free_percent:.1f}% 可用)',
                    'free_space_gb': free // (1024**3),
                    'free_percent': round(free_percent, 1)
                }
            else:
                health_status['checks']['disk_space'] = {
                    'status': 'warning',
                    'message': f'磁盘空间不足 ({free_percent:.1f}% 可用)',
                    'free_space_gb': free // (1024**3),
                    'free_percent': round(free_percent, 1)
                }
                if health_status['status'] == 'healthy':
                    health_status['status'] = 'warning'
        except Exception as e:
            health_status['checks']['disk_space'] = {
                'status': 'unknown',
                'message': f'无法检查磁盘空间: {str(e)}'
            }
        
        # 内存使用检查
        try:
            import psutil
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            if memory_percent < 80:
                health_status['checks']['memory'] = {
                    'status': 'healthy',
                    'message': f'内存使用正常 ({memory_percent:.1f}%)',
                    'memory_percent': round(memory_percent, 1),
                    'available_gb': round(memory.available / (1024**3), 1)
                }
            elif memory_percent < 90:
                health_status['checks']['memory'] = {
                    'status': 'warning',
                    'message': f'内存使用较高 ({memory_percent:.1f}%)',
                    'memory_percent': round(memory_percent, 1),
                    'available_gb': round(memory.available / (1024**3), 1)
                }
                if health_status['status'] == 'healthy':
                    health_status['status'] = 'warning'
            else:
                health_status['checks']['memory'] = {
                    'status': 'critical',
                    'message': f'内存使用过高 ({memory_percent:.1f}%)',
                    'memory_percent': round(memory_percent, 1),
                    'available_gb': round(memory.available / (1024**3), 1)
                }
                health_status['status'] = 'critical'
        except ImportError:
            health_status['checks']['memory'] = {
                'status': 'unknown',
                'message': '需要安装 psutil 库来检查内存使用'
            }
        except Exception as e:
            health_status['checks']['memory'] = {
                'status': 'unknown',
                'message': f'无法检查内存使用: {str(e)}'
            }
        
        # 会话存储检查
        try:
            session_count = len([k for k in session.keys() if not k.startswith('_')])
            health_status['checks']['sessions'] = {
                'status': 'healthy',
                'message': f'会话系统正常 (当前会话项: {session_count})',
                'session_items': session_count
            }
        except Exception as e:
            health_status['checks']['sessions'] = {
                'status': 'warning',
                'message': f'会话系统异常: {str(e)}'
            }
            if health_status['status'] == 'healthy':
                health_status['status'] = 'warning'
        
        return jsonify({
            'success': True,
            'data': health_status
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': '系统健康检查失败',
                'details': str(e)
            }
        }), 500

@app.route('/api/admin/system/performance', methods=['GET'])
@login_required
def system_performance_metrics():
    """系统性能监控指标"""
    try:
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'uptime': time.time() - app.config.get('START_TIME', time.time()),
            'metrics': {}
        }
        
        # 数据库性能指标
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                
                # 数据库大小
                cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
                db_size_result = cursor.fetchone()
                db_size = db_size_result[0] if db_size_result else 0
                
                # 表统计
                cursor.execute("SELECT COUNT(*) FROM questionnaires")
                questionnaire_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM operation_logs")
                log_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM users")
                user_count = cursor.fetchone()[0]
                
                # 最近的操作频率
                cursor.execute("""
                    SELECT COUNT(*) FROM operation_logs 
                    WHERE created_at >= datetime('now', '-1 hour')
                """)
                operations_last_hour = cursor.fetchone()[0]
                
                metrics['metrics']['database'] = {
                    'size_bytes': db_size,
                    'size_mb': round(db_size / (1024*1024), 2),
                    'questionnaire_count': questionnaire_count,
                    'log_count': log_count,
                    'user_count': user_count,
                    'operations_last_hour': operations_last_hour
                }
        except Exception as e:
            metrics['metrics']['database'] = {
                'error': f'数据库指标获取失败: {str(e)}'
            }
        
        # 系统资源指标
        try:
            import psutil
            
            # CPU 使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 内存使用
            memory = psutil.virtual_memory()
            
            # 磁盘使用
            disk = psutil.disk_usage(os.path.dirname(DATABASE))
            
            metrics['metrics']['system'] = {
                'cpu_percent': round(cpu_percent, 1),
                'memory': {
                    'total_gb': round(memory.total / (1024**3), 2),
                    'available_gb': round(memory.available / (1024**3), 2),
                    'percent': round(memory.percent, 1)
                },
                'disk': {
                    'total_gb': round(disk.total / (1024**3), 2),
                    'free_gb': round(disk.free / (1024**3), 2),
                    'percent': round((disk.used / disk.total) * 100, 1)
                }
            }
        except ImportError:
            metrics['metrics']['system'] = {
                'error': '需要安装 psutil 库来获取系统指标'
            }
        except Exception as e:
            metrics['metrics']['system'] = {
                'error': f'系统指标获取失败: {str(e)}'
            }
        
        # 应用程序指标
        try:
            # 活跃会话数（简化统计）
            active_sessions = 1 if 'user_id' in session else 0
            
            # 最近错误统计
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM operation_logs 
                    WHERE operation LIKE '%ERROR%' 
                    AND created_at >= datetime('now', '-24 hours')
                """)
                errors_24h = cursor.fetchone()[0]
            
            metrics['metrics']['application'] = {
                'active_sessions': active_sessions,
                'errors_24h': errors_24h,
                'flask_env': app.config.get('ENV', 'unknown'),
                'debug_mode': app.debug
            }
        except Exception as e:
            metrics['metrics']['application'] = {
                'error': f'应用指标获取失败: {str(e)}'
            }
        
        return jsonify({
            'success': True,
            'data': metrics
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': '获取性能指标失败',
                'details': str(e)
            }
        }), 500

@app.route('/api/admin/system/realtime', methods=['GET'])
@login_required
def realtime_statistics():
    """实时统计数据接口"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # 最近1小时的活动
            cursor.execute("""
                SELECT COUNT(*) FROM questionnaires 
                WHERE created_at >= datetime('now', '-1 hour')
            """)
            submissions_last_hour = cursor.fetchone()[0]
            
            # 最近1小时的操作
            cursor.execute("""
                SELECT COUNT(*) FROM operation_logs 
                WHERE created_at >= datetime('now', '-1 hour')
            """)
            operations_last_hour = cursor.fetchone()[0]
            
            # 最近5分钟的活动
            cursor.execute("""
                SELECT COUNT(*) FROM questionnaires 
                WHERE created_at >= datetime('now', '-5 minutes')
            """)
            submissions_last_5min = cursor.fetchone()[0]
            
            # 最近的提交记录
            cursor.execute("""
                SELECT id, name, type, created_at 
                FROM questionnaires 
                ORDER BY created_at DESC 
                LIMIT 5
            """)
            recent_submissions = [
                {
                    'id': row[0],
                    'name': row[1],
                    'type': row[2],
                    'created_at': row[3]
                }
                for row in cursor.fetchall()
            ]
            
            # 最近的操作日志
            cursor.execute("""
                SELECT operation, created_at, details 
                FROM operation_logs 
                ORDER BY created_at DESC 
                LIMIT 5
            """)
            recent_operations = [
                {
                    'operation': row[0],
                    'created_at': row[1],
                    'details': json.loads(row[2]) if row[2] else {}
                }
                for row in cursor.fetchall()
            ]
        
        return jsonify({
            'success': True,
            'data': {
                'activity': {
                    'submissions_last_hour': submissions_last_hour,
                    'operations_last_hour': operations_last_hour,
                    'submissions_last_5min': submissions_last_5min
                },
                'recent': {
                    'submissions': recent_submissions,
                    'operations': recent_operations
                },
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': '获取实时统计失败',
                'details': str(e)
            }
        }), 500

# 获取操作日志
@app.route('/api/admin/logs', methods=['GET'])
@admin_required
def get_operation_logs():
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        operation_type = request.args.get('operation', '').strip()
        user_filter = request.args.get('user', '').strip()
        date_from = request.args.get('date_from', '').strip()
        date_to = request.args.get('date_to', '').strip()
        sensitive_only = request.args.get('sensitive_only', '').lower() == 'true'
        
        # 限制每页最大数量
        limit = min(limit, 200)
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            # 构建查询条件
            where_conditions = []
            params = []
            
            if operation_type:
                where_conditions.append("ol.operation LIKE ?")
                params.append(f"%{operation_type}%")
            
            if user_filter:
                where_conditions.append("u.username LIKE ?")
                params.append(f"%{user_filter}%")
            
            if date_from:
                where_conditions.append("DATE(ol.created_at) >= ?")
                params.append(date_from)
            
            if date_to:
                where_conditions.append("DATE(ol.created_at) <= ?")
                params.append(date_to)
            
            if sensitive_only:
                sensitive_ops = "', '".join(OperationLogger.SENSITIVE_OPERATIONS)
                where_conditions.append(f"ol.operation IN ('{sensitive_ops}')")
            
            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)
            
            # 获取总数
            count_query = f"""
                SELECT COUNT(*) 
                FROM operation_logs ol
                LEFT JOIN users u ON ol.user_id = u.id
                {where_clause}
            """
            cursor.execute(count_query, params)
            total_count = cursor.fetchone()[0]
            
            # 获取分页数据
            offset = (page - 1) * limit
            query = f"""
                SELECT ol.*, u.username 
                FROM operation_logs ol
                LEFT JOIN users u ON ol.user_id = u.id
                {where_clause}
                ORDER BY ol.created_at DESC
                LIMIT ? OFFSET ?
            """
            cursor.execute(query, params + [limit, offset])
            logs = cursor.fetchall()
        
        result = []
        for log in logs:
            # 解析详细信息
            details_data = {}
            try:
                if log['details']:
                    details_data = json.loads(log['details'])
            except:
                details_data = {'user_details': log['details']}
            
            # 判断是否为敏感操作
            is_sensitive = log['operation'] in OperationLogger.SENSITIVE_OPERATIONS
            
            log_entry = {
                'id': log['id'],
                'user_id': log['user_id'],
                'username': log['username'] or 'System',
                'operation': log['operation'],
                'target_id': log['target_id'],
                'created_at': log['created_at'],
                'is_sensitive': is_sensitive,
                'ip_address': details_data.get('ip_address', 'unknown'),
                'user_agent': details_data.get('user_agent', 'unknown')[:100] + '...' if len(details_data.get('user_agent', '')) > 100 else details_data.get('user_agent', 'unknown'),
                'request_path': details_data.get('request_path', 'unknown'),
                'request_method': details_data.get('request_method', 'unknown'),
                'user_details': details_data.get('user_details', ''),
                'raw_details': log['details']  # 保留原始详情用于详细查看
            }
            
            result.append(log_entry)
        
        # 记录日志查看操作
        OperationLogger.log('VIEW_LOGS', None, f'查看操作日志，页面: {page}, 过滤条件: {request.args}')
        
        return jsonify({
            'success': True,
            'data': result,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total_count,
                'pages': (total_count + limit - 1) // limit
            },
            'filters': {
                'operation_type': operation_type,
                'user_filter': user_filter,
                'date_from': date_from,
                'date_to': date_to,
                'sensitive_only': sensitive_only
            }
        })
        
    except Exception as e:
        OperationLogger.log('SYSTEM_ERROR', None, f'获取操作日志失败: {str(e)}')
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': '获取操作日志失败',
                'details': str(e)
            }
        }), 500

@app.route('/api/admin/logs/<int:log_id>', methods=['GET'])
@admin_required
def get_log_detail(log_id):
    """获取单个日志详情"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ol.*, u.username 
                FROM operation_logs ol
                LEFT JOIN users u ON ol.user_id = u.id
                WHERE ol.id = ?
            """, (log_id,))
            log = cursor.fetchone()
        
        if not log:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': '日志记录不存在'
                }
            }), 404
        
        # 解析详细信息
        details_data = {}
        try:
            if log['details']:
                details_data = json.loads(log['details'])
        except:
            details_data = {'user_details': log['details']}
        
        result = {
            'id': log['id'],
            'user_id': log['user_id'],
            'username': log['username'] or 'System',
            'operation': log['operation'],
            'target_id': log['target_id'],
            'created_at': log['created_at'],
            'is_sensitive': log['operation'] in OperationLogger.SENSITIVE_OPERATIONS,
            'details': details_data
        }
        
        # 记录查看日志详情的操作
        OperationLogger.log('VIEW_LOG_DETAIL', log_id, f'查看日志详情: {log["operation"]}')
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': '获取日志详情失败',
                'details': str(e)
            }
        }), 500

@app.route('/api/admin/logs/statistics', methods=['GET'])
@admin_required
def get_log_statistics():
    """获取日志统计信息"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # 总日志数
            cursor.execute("SELECT COUNT(*) FROM operation_logs")
            total_logs = cursor.fetchone()[0]
            
            # 今日日志数
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute("SELECT COUNT(*) FROM operation_logs WHERE DATE(created_at) = ?", (today,))
            today_logs = cursor.fetchone()[0]
            
            # 敏感操作数
            sensitive_ops = "', '".join(OperationLogger.SENSITIVE_OPERATIONS)
            cursor.execute(f"SELECT COUNT(*) FROM operation_logs WHERE operation IN ('{sensitive_ops}')")
            sensitive_logs = cursor.fetchone()[0]
            
            # 按操作类型统计
            cursor.execute("""
                SELECT operation, COUNT(*) as count 
                FROM operation_logs 
                GROUP BY operation 
                ORDER BY count DESC 
                LIMIT 10
            """)
            operation_stats = [{'operation': row[0], 'count': row[1]} for row in cursor.fetchall()]
            
            # 按用户统计
            cursor.execute("""
                SELECT u.username, COUNT(*) as count 
                FROM operation_logs ol
                LEFT JOIN users u ON ol.user_id = u.id
                WHERE u.username IS NOT NULL
                GROUP BY u.username 
                ORDER BY count DESC 
                LIMIT 10
            """)
            user_stats = [{'username': row[0], 'count': row[1]} for row in cursor.fetchall()]
            
            # 最近7天的活动趋势
            cursor.execute("""
                SELECT DATE(created_at) as date, COUNT(*) as count 
                FROM operation_logs 
                WHERE DATE(created_at) >= DATE('now', '-7 days')
                GROUP BY DATE(created_at)
                ORDER BY date
            """)
            activity_trend = [{'date': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        return jsonify({
            'success': True,
            'data': {
                'total_logs': total_logs,
                'today_logs': today_logs,
                'sensitive_logs': sensitive_logs,
                'operation_statistics': operation_stats,
                'user_statistics': user_stats,
                'activity_trend': activity_trend
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': '获取日志统计失败',
                'details': str(e)
            }
        }), 500

@app.route('/api/admin/logs/export', methods=['POST'])
@admin_required
def export_logs():
    """导出操作日志"""
    try:
        data = request.json or {}
        export_format = data.get('format', 'csv').lower()
        date_from = data.get('date_from', '')
        date_to = data.get('date_to', '')
        operation_filter = data.get('operation', '')
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            # 构建查询条件
            where_conditions = []
            params = []
            
            if date_from:
                where_conditions.append("DATE(ol.created_at) >= ?")
                params.append(date_from)
            
            if date_to:
                where_conditions.append("DATE(ol.created_at) <= ?")
                params.append(date_to)
            
            if operation_filter:
                where_conditions.append("ol.operation LIKE ?")
                params.append(f"%{operation_filter}%")
            
            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)
            
            # 获取数据
            query = f"""
                SELECT ol.*, u.username 
                FROM operation_logs ol
                LEFT JOIN users u ON ol.user_id = u.id
                {where_clause}
                ORDER BY ol.created_at DESC
                LIMIT 10000
            """
            cursor.execute(query, params)
            logs = cursor.fetchall()
        
        if export_format == 'csv':
            # 生成CSV
            output = StringIO()
            writer = csv.writer(output)
            
            # 写入标题行
            writer.writerow(['ID', '用户名', '操作类型', '目标ID', '创建时间', '详情'])
            
            # 写入数据行
            for log in logs:
                details_data = {}
                try:
                    if log['details']:
                        details_data = json.loads(log['details'])
                except:
                    details_data = {'user_details': log['details']}
                
                writer.writerow([
                    log['id'],
                    log['username'] or 'System',
                    log['operation'],
                    log['target_id'] or '',
                    log['created_at'],
                    details_data.get('user_details', '')
                ])
            
            # 记录导出操作
            OperationLogger.log('EXPORT_LOGS', None, f'导出操作日志，格式: {export_format}, 条数: {len(logs)}')
            
            # 返回CSV文件
            response = make_response(output.getvalue())
            response.headers['Content-Type'] = 'text/csv; charset=utf-8'
            response.headers['Content-Disposition'] = f'attachment; filename=operation_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            
            return response
        
        else:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': '不支持的导出格式'
                }
            }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': '导出日志失败',
                'details': str(e)
            }
        }), 500

# 获取支持的问题类型
@app.route('/api/question-types', methods=['GET'])
def get_supported_question_types():
    """获取系统支持的问题类型列表"""
    try:
        supported_types = question_processor.get_supported_types()
        
        # 为每种类型提供详细信息
        type_info = {
            'multiple_choice': {
                'name': '选择题',
                'description': '单选或多选题，用户从预设选项中选择答案',
                'required_fields': ['question', 'options', 'selected'],
                'optional_fields': ['can_speak']
            },
            'text_input': {
                'name': '填空题',
                'description': '文本输入题，用户填写文字答案',
                'required_fields': ['question', 'answer'],
                'optional_fields': ['max_length']
            }
        }
        
        result = []
        for type_key in supported_types:
            if type_key in type_info:
                result.append({
                    'type': type_key,
                    **type_info[type_key]
                })
        
        return jsonify({
            'success': True,
            'data': result,
            'total': len(result)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': '获取问题类型失败',
                'details': str(e)
            }
        }), 500

# 批量导出问卷数据 - 增强版本，支持 Excel 和 PDF
@app.route('/api/questionnaires/export', methods=['POST'])
@login_required
def batch_export_questionnaires():
    try:
        from export_utils import export_questionnaires, get_export_filename, get_content_type
        
        data = request.json
        questionnaire_ids = data.get('ids', [])
        export_format = data.get('format', 'csv').lower()
        include_details = data.get('include_details', True)
        
        if not questionnaire_ids:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': '请选择要导出的问卷'
                }
            }), 400
        
        # 验证导出格式
        supported_formats = ['csv', 'excel', 'xlsx', 'pdf', 'json']
        if export_format not in supported_formats:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': f'不支持的导出格式，支持: {", ".join(supported_formats)}'
                }
            }), 400
        
        # 获取问卷数据
        with get_db() as conn:
            cursor = conn.cursor()
            placeholders = ','.join(['?'] * len(questionnaire_ids))
            cursor.execute(f"SELECT * FROM questionnaires WHERE id IN ({placeholders}) ORDER BY created_at DESC", questionnaire_ids)
            questionnaires = cursor.fetchall()
        
        if not questionnaires:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': '未找到指定的问卷数据'
                }
            }), 404
        
        # 处理 JSON 格式（保持原有逻辑）
        if export_format == 'json':
            result = []
            for q in questionnaires:
                result.append({
                    'id': q['id'],
                    'type': q['type'],
                    'name': q['name'],
                    'grade': q['grade'],
                    'submission_date': q['submission_date'],
                    'created_at': q['created_at'],
                    'updated_at': q['updated_at'],
                    'data': json.loads(q['data'])
                })
            
            filename = get_export_filename('json', 'questionnaires_batch')
            response = make_response(json.dumps(result, default=str, ensure_ascii=False, indent=2))
            response.headers['Content-Disposition'] = f'attachment; filename={filename}'
            response.headers['Content-type'] = 'application/json; charset=utf-8'
            
            # 记录操作日志
            OperationLogger.log(OperationLogger.EXPORT_DATA, None, f'批量导出问卷 {len(questionnaires)} 条 (JSON格式)')
            
            return response
        
        # 使用新的导出工具处理其他格式
        try:
            file_content = export_questionnaires(questionnaires, export_format, include_details)
            filename = get_export_filename(export_format, 'questionnaires_batch')
            content_type = get_content_type(export_format)
            
            response = make_response(file_content)
            response.headers['Content-Disposition'] = f'attachment; filename={filename}'
            response.headers['Content-Type'] = content_type
            
            # 记录操作日志
            OperationLogger.log(OperationLogger.EXPORT_DATA, None, 
                         f'批量导出问卷 {len(questionnaires)} 条 ({export_format.upper()}格式)')
            
            return response
            
        except Exception as export_error:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'EXPORT_ERROR',
                    'message': f'导出失败: {str(export_error)}',
                    'details': str(export_error)
                }
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': '批量导出失败',
                'details': str(e)
            }
        }), 500

# 导出单个问卷数据 - 增强版本，支持多种格式
@app.route('/api/export/<int:questionnaire_id>', methods=['GET'])
@login_required
def export_questionnaire(questionnaire_id):
    try:
        from export_utils import export_questionnaires, get_export_filename, get_content_type
        
        # 获取导出格式参数
        export_format = request.args.get('format', 'csv').lower()
        include_details = request.args.get('include_details', 'true').lower() == 'true'
        
        # 验证导出格式
        supported_formats = ['csv', 'excel', 'xlsx', 'pdf', 'json']
        if export_format not in supported_formats:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': f'不支持的导出格式，支持: {", ".join(supported_formats)}'
                }
            }), 400
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM questionnaires WHERE id = ?", (questionnaire_id,))
            q = cursor.fetchone()
        
        if not q:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': '问卷不存在'
                }
            }), 404
        
        # 处理 JSON 格式（保持原有逻辑）
        if export_format == 'json':
            result = {
                'id': q['id'],
                'type': q['type'],
                'name': q['name'],
                'grade': q['grade'],
                'submission_date': q['submission_date'],
                'created_at': q['created_at'],
                'updated_at': q['updated_at'],
                'data': json.loads(q['data'])
            }
            
            filename = get_export_filename('json', f'questionnaire_{questionnaire_id}')
            response = make_response(json.dumps(result, default=str, ensure_ascii=False, indent=2))
            response.headers['Content-Disposition'] = f'attachment; filename={filename}'
            response.headers['Content-type'] = 'application/json; charset=utf-8'
            
            # 记录操作日志
            OperationLogger.log(OperationLogger.EXPORT_DATA, questionnaire_id, f'导出问卷 {questionnaire_id} (JSON格式)')
            
            return response
        
        # 使用新的导出工具处理其他格式
        try:
            questionnaires = [q]  # 包装成列表
            file_content = export_questionnaires(questionnaires, export_format, include_details)
            filename = get_export_filename(export_format, f'questionnaire_{questionnaire_id}')
            content_type = get_content_type(export_format)
            
            response = make_response(file_content)
            response.headers['Content-Disposition'] = f'attachment; filename={filename}'
            response.headers['Content-Type'] = content_type
            
            # 记录操作日志
            OperationLogger.log(OperationLogger.EXPORT_DATA, questionnaire_id, 
                         f'导出问卷 {questionnaire_id} ({export_format.upper()}格式)')
            
            return response
            
        except Exception as export_error:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'EXPORT_ERROR',
                    'message': f'导出失败: {str(export_error)}',
                    'details': str(export_error)
                }
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': '导出问卷失败',
                'details': str(e)
            }
        }), 500

# 高级导出功能 - 支持全量导出和自定义筛选
@app.route('/api/admin/export/advanced', methods=['POST'])
@admin_required
def advanced_export():
    """高级导出功能，支持全量导出和自定义筛选条件"""
    try:
        from export_utils import export_questionnaires, get_export_filename, get_content_type
        
        data = request.json or {}
        export_format = data.get('format', 'csv').lower()
        include_details = data.get('include_details', True)
        
        # 筛选条件
        filters = data.get('filters', {})
        date_from = filters.get('date_from', '')
        date_to = filters.get('date_to', '')
        questionnaire_type = filters.get('type', '')
        grade = filters.get('grade', '')
        name_search = filters.get('name_search', '')
        
        # 验证导出格式
        supported_formats = ['csv', 'excel', 'xlsx', 'pdf']
        if export_format not in supported_formats:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': f'不支持的导出格式，支持: {", ".join(supported_formats)}'
                }
            }), 400
        
        # 构建查询条件
        where_conditions = []
        params = []
        
        if date_from:
            where_conditions.append("DATE(created_at) >= ?")
            params.append(date_from)
        
        if date_to:
            where_conditions.append("DATE(created_at) <= ?")
            params.append(date_to)
        
        if questionnaire_type:
            where_conditions.append("type = ?")
            params.append(questionnaire_type)
        
        if grade:
            where_conditions.append("grade LIKE ?")
            params.append(f"%{grade}%")
        
        if name_search:
            where_conditions.append("name LIKE ?")
            params.append(f"%{name_search}%")
        
        # 构建完整查询
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        # 获取问卷数据
        with get_db() as conn:
            cursor = conn.cursor()
            query = f"SELECT * FROM questionnaires {where_clause} ORDER BY created_at DESC"
            cursor.execute(query, params)
            questionnaires = cursor.fetchall()
        
        if not questionnaires:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': '未找到符合条件的问卷数据'
                }
            }), 404
        
        # 检查导出数量限制
        max_export_limit = 1000  # 最大导出数量限制
        if len(questionnaires) > max_export_limit:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'EXPORT_LIMIT_EXCEEDED',
                    'message': f'导出数量超过限制，最多支持导出 {max_export_limit} 条记录，当前查询结果: {len(questionnaires)} 条'
                }
            }), 400
        
        # 执行导出
        try:
            file_content = export_questionnaires(questionnaires, export_format, include_details)
            filename = get_export_filename(export_format, 'questionnaires_advanced')
            content_type = get_content_type(export_format)
            
            response = make_response(file_content)
            response.headers['Content-Disposition'] = f'attachment; filename={filename}'
            response.headers['Content-Type'] = content_type
            
            # 记录操作日志
            filter_desc = []
            if date_from or date_to:
                filter_desc.append(f"日期: {date_from or '开始'} 至 {date_to or '结束'}")
            if questionnaire_type:
                filter_desc.append(f"类型: {questionnaire_type}")
            if grade:
                filter_desc.append(f"年级: {grade}")
            if name_search:
                filter_desc.append(f"姓名: {name_search}")
            
            filter_text = "; ".join(filter_desc) if filter_desc else "无筛选条件"
            
            OperationLogger.log(OperationLogger.EXPORT_DATA, None, 
                         f'高级导出问卷 {len(questionnaires)} 条 ({export_format.upper()}格式) - 筛选条件: {filter_text}')
            
            return response
            
        except Exception as export_error:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'EXPORT_ERROR',
                    'message': f'导出失败: {str(export_error)}',
                    'details': str(export_error)
                }
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': '高级导出失败',
                'details': str(e)
            }
        }), 500

# 获取导出预览信息
@app.route('/api/admin/export/preview', methods=['POST'])
@admin_required
def export_preview():
    """获取导出预览信息，显示将要导出的数据统计"""
    try:
        data = request.json or {}
        
        # 筛选条件
        filters = data.get('filters', {})
        date_from = filters.get('date_from', '')
        date_to = filters.get('date_to', '')
        questionnaire_type = filters.get('type', '')
        grade = filters.get('grade', '')
        name_search = filters.get('name_search', '')
        
        # 构建查询条件
        where_conditions = []
        params = []
        
        if date_from:
            where_conditions.append("DATE(created_at) >= ?")
            params.append(date_from)
        
        if date_to:
            where_conditions.append("DATE(created_at) <= ?")
            params.append(date_to)
        
        if questionnaire_type:
            where_conditions.append("type = ?")
            params.append(questionnaire_type)
        
        if grade:
            where_conditions.append("grade LIKE ?")
            params.append(f"%{grade}%")
        
        if name_search:
            where_conditions.append("name LIKE ?")
            params.append(f"%{name_search}%")
        
        # 构建完整查询
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        # 获取统计信息
        with get_db() as conn:
            cursor = conn.cursor()
            
            # 总数统计
            count_query = f"SELECT COUNT(*) FROM questionnaires {where_clause}"
            cursor.execute(count_query, params)
            total_count = cursor.fetchone()[0]
            
            # 按类型统计
            type_query = f"SELECT type, COUNT(*) FROM questionnaires {where_clause} GROUP BY type"
            cursor.execute(type_query, params)
            type_stats = dict(cursor.fetchall())
            
            # 按日期统计（最近7天）
            date_query = f"""
                SELECT DATE(created_at) as date, COUNT(*) 
                FROM questionnaires {where_clause} 
                GROUP BY DATE(created_at) 
                ORDER BY DATE(created_at) DESC 
                LIMIT 7
            """
            cursor.execute(date_query, params)
            date_stats = dict(cursor.fetchall())
        
        return jsonify({
            'success': True,
            'preview': {
                'total_count': total_count,
                'type_statistics': type_stats,
                'date_statistics': date_stats,
                'export_limit': 1000,
                'can_export': total_count <= 1000,
                'filters_applied': {
                    'date_from': date_from,
                    'date_to': date_to,
                    'type': questionnaire_type,
                    'grade': grade,
                    'name_search': name_search
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': '获取导出预览失败',
                'details': str(e)
            }
        }), 500

# Frankfurt Scale报告生成API
@app.route('/api/generate_frankfurt_report', methods=['POST'])
@login_required
def generate_frankfurt_report():
    """生成Frankfurt Scale选择性缄默筛查量表报告"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': '请求数据不能为空'
                }
            }), 400
        
        questionnaire_id = data.get('questionnaire_id')
        
        if not questionnaire_id:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_PARAMETERS',
                    'message': '缺少必要参数：questionnaire_id'
                }
            }), 400
        
        # 验证问卷是否存在并获取完整数据
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM questionnaires WHERE id = ?', (questionnaire_id,))
            questionnaire = cursor.fetchone()
            
            if not questionnaire:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'QUESTIONNAIRE_NOT_FOUND',
                        'message': '问卷不存在'
                    }
                }), 404
            
            # 获取列名
            columns = [description[0] for description in cursor.description]
            questionnaire_dict = dict(zip(columns, questionnaire))
            
            if questionnaire_dict['type'] != 'frankfurt_scale_selective_mutism':
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'INVALID_QUESTIONNAIRE_TYPE',
                        'message': '问卷类型不匹配，只支持frankfurt_scale_selective_mutism类型'
                    }
                }), 400
            
            # 从问卷数据生成报告数据
            report_data = generate_frankfurt_report_data(questionnaire_dict)
            
            # 生成报告HTML
            report_html = generate_frankfurt_report_html(report_data)
            
            # 保存报告到数据库
            report_json = json.dumps(report_data, ensure_ascii=False)
            cursor.execute(
                'UPDATE questionnaires SET report_data = ?, report_generated_at = ? WHERE id = ?',
                (report_json, datetime.now().isoformat(), questionnaire_id)
            )
            conn.commit()
            
            return jsonify({
                'success': True,
                'data': {
                    'questionnaire_id': questionnaire_id,
                    'report_html': report_html,
                    'report_data': report_data,
                    'generated_at': datetime.now().isoformat()
                }
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': '生成报告失败',
                'details': str(e)
            }
        }), 500

def generate_frankfurt_report_data(questionnaire_dict):
    """从问卷数据生成Frankfurt Scale报告数据"""
    try:
        # 解析问卷数据
        data = json.loads(questionnaire_dict.get('data', '{}'))
        basic_info = data.get('basic_info', {})
        questions = data.get('questions', [])
        
        # 初始化报告数据
        report_data = {
            'basic_info': {
                'name': basic_info.get('name', questionnaire_dict.get('name', '未知')),
                'gender': basic_info.get('gender', '未知'),
                'age': basic_info.get('age', '未知'),
                'birthdate': basic_info.get('birthdate', basic_info.get('birth_date', '未知'))
            },
            'scores': {
                'ds_total': 0,
                'ss_total': 0,
                'ds_average': 0,
                'ss_average': 0,
                'ss_school_total': 0,
                'ss_school_average': 0,
                'ss_public_total': 0,
                'ss_public_average': 0,
                'ss_home_total': 0,
                'ss_home_average': 0
            },
            'risk_assessment': {
                'overall': {
                    'level': '低风险',
                    'color': '#28a745',
                    'description': ''
                },
                'school': {
                    'level': '低风险',
                    'color': '#28a745',
                    'description': '',
                    'score': 0
                },
                'public': {
                    'level': '低风险',
                    'color': '#28a745',
                    'description': '',
                    'score': 0
                },
                'home': {
                    'level': '低风险',
                    'color': '#28a745',
                    'description': '',
                    'score': 0
                }
            },
            'interventions': [],
            'exposure_hierarchy': []
        }
        
        # 计算DS和SS得分
        ds_count = 0
        ss_count = 0
        ss_school_count = 0
        ss_public_count = 0
        ss_home_count = 0
        
        for question in questions:
            if isinstance(question, dict):
                section = question.get('section', '')
                selected = question.get('selected', [])
                
                # 获取选中的分数
                score = 0
                if selected and len(selected) > 0:
                    try:
                        score = int(selected[0])
                    except (ValueError, TypeError):
                        score = 0
                
                # 根据section字段判断是DS还是SS
                if section == 'DS':
                    report_data['scores']['ds_total'] += score
                    ds_count += 1
                elif section == 'SS_school':
                    report_data['scores']['ss_school_total'] += score
                    report_data['scores']['ss_total'] += score
                    ss_school_count += 1
                    ss_count += 1
                elif section == 'SS_public':
                    report_data['scores']['ss_public_total'] += score
                    report_data['scores']['ss_total'] += score
                    ss_public_count += 1
                    ss_count += 1
                elif section == 'SS_home':
                    report_data['scores']['ss_home_total'] += score
                    report_data['scores']['ss_total'] += score
                    ss_home_count += 1
                    ss_count += 1
        
        # 计算平均分
        if ds_count > 0:
            report_data['scores']['ds_average'] = round(report_data['scores']['ds_total'] / ds_count, 2)
        if ss_count > 0:
            report_data['scores']['ss_average'] = round(report_data['scores']['ss_total'] / ss_count, 2)
        if ss_school_count > 0:
            report_data['scores']['ss_school_average'] = round(report_data['scores']['ss_school_total'] / ss_school_count, 2)
        if ss_public_count > 0:
            report_data['scores']['ss_public_average'] = round(report_data['scores']['ss_public_total'] / ss_public_count, 2)
        if ss_home_count > 0:
            report_data['scores']['ss_home_average'] = round(report_data['scores']['ss_home_total'] / ss_home_count, 2)
        
        total_score = report_data['scores']['ds_total'] + report_data['scores']['ss_total']
        
        # 整体风险评估
        if total_score >= 30:
            report_data['risk_assessment']['overall'] = {
                'level': '高风险',
                'color': '#dc3545',
                'description': '建议立即寻求专业心理治疗师的帮助'
            }
        elif total_score >= 15:
            report_data['risk_assessment']['overall'] = {
                'level': '中等风险',
                'color': '#ffc107',
                'description': '建议学校心理咨询师介入，家长和教师需要密切配合'
            }
        else:
            report_data['risk_assessment']['overall'] = {
                'level': '低风险',
                'color': '#28a745',
                'description': '继续观察和支持，创造积极的交流环境'
            }
        
        # 学校环境风险评估
        school_score = report_data['scores']['ss_school_total']
        report_data['risk_assessment']['school']['score'] = school_score
        if school_score >= 20:
            report_data['risk_assessment']['school'].update({
                'level': '高风险',
                'color': '#dc3545',
                'description': '在学校环境中表现出严重的选择性缄默症状，需要学校心理咨询师立即介入'
            })
        elif school_score >= 10:
            report_data['risk_assessment']['school'].update({
                'level': '中等风险',
                'color': '#ffc107',
                'description': '在学校环境中有明显的交流困难，建议与老师密切合作制定支持计划'
            })
        else:
            report_data['risk_assessment']['school'].update({
                'level': '低风险',
                'color': '#28a745',
                'description': '在学校环境中表现相对良好，继续鼓励参与课堂活动'
            })
        
        # 公共场所/社区环境风险评估
        public_score = report_data['scores']['ss_public_total']
        report_data['risk_assessment']['public']['score'] = public_score
        if public_score >= 16:
            report_data['risk_assessment']['public'].update({
                'level': '高风险',
                'color': '#dc3545',
                'description': '在公共场所表现出严重的社交回避，需要系统性的暴露疗法'
            })
        elif public_score >= 8:
            report_data['risk_assessment']['public'].update({
                'level': '中等风险',
                'color': '#ffc107',
                'description': '在公共场所有一定的交流困难，建议逐步增加社区活动参与'
            })
        else:
            report_data['risk_assessment']['public'].update({
                'level': '低风险',
                'color': '#28a745',
                'description': '在公共场所表现较好，可以适当增加社交机会'
            })
        
        # 家庭环境风险评估
        home_score = report_data['scores']['ss_home_total']
        report_data['risk_assessment']['home']['score'] = home_score
        if home_score >= 16:
            report_data['risk_assessment']['home'].update({
                'level': '高风险',
                'color': '#dc3545',
                'description': '即使在家庭环境中也存在严重的交流障碍，建议家庭治疗介入'
            })
        elif home_score >= 8:
            report_data['risk_assessment']['home'].update({
                'level': '中等风险',
                'color': '#ffc107',
                'description': '在家庭环境中有一定的交流限制，建议家长学习支持性沟通技巧'
            })
        else:
            report_data['risk_assessment']['home'].update({
                'level': '低风险',
                'color': '#28a745',
                'description': '在家庭环境中表现良好，这是一个重要的支持基础'
            })
        
        # 生成综合干预建议
        interventions = []
        
        # 基于整体风险等级的建议
        if report_data['risk_assessment']['overall']['level'] == '高风险':
            interventions.extend([
                '立即寻求专业心理治疗师的帮助',
                '制定个性化的治疗计划',
                '家庭和学校需要密切配合',
                '考虑药物治疗的可能性'
            ])
        elif report_data['risk_assessment']['overall']['level'] == '中等风险':
            interventions.extend([
                '学校心理咨询师介入',
                '家长和教师密切配合',
                '创建支持性的交流环境',
                '定期评估进展情况'
            ])
        else:
            interventions.extend([
                '继续观察和支持',
                '创造积极的交流环境',
                '鼓励参与社交活动',
                '定期关注情况变化'
            ])
        
        # 基于学校环境的具体建议
        if report_data['risk_assessment']['school']['level'] == '高风险':
            interventions.extend([
                '学校环境：安排专门的心理支持老师',
                '学校环境：创建安全的表达空间',
                '学校环境：与同学建立伙伴支持系统'
            ])
        elif report_data['risk_assessment']['school']['level'] == '中等风险':
            interventions.extend([
                '学校环境：与班主任制定个性化支持计划',
                '学校环境：鼓励参与小组活动',
                '学校环境：提供非言语表达机会'
            ])
        
        # 基于公共场所的具体建议
        if report_data['risk_assessment']['public']['level'] == '高风险':
            interventions.extend([
                '社区环境：进行系统性暴露疗法',
                '社区环境：从熟悉的环境开始练习',
                '社区环境：家长陪同参与社区活动'
            ])
        elif report_data['risk_assessment']['public']['level'] == '中等风险':
            interventions.extend([
                '社区环境：逐步增加社区活动参与',
                '社区环境：选择舒适的社交场所',
                '社区环境：建立社区支持网络'
            ])
        
        # 基于家庭环境的具体建议
        if report_data['risk_assessment']['home']['level'] == '高风险':
            interventions.extend([
                '家庭环境：考虑家庭治疗',
                '家庭环境：改善家庭沟通模式',
                '家庭环境：创建无压力的表达空间'
            ])
        elif report_data['risk_assessment']['home']['level'] == '中等风险':
            interventions.extend([
                '家庭环境：家长学习支持性沟通技巧',
                '家庭环境：建立规律的家庭交流时间',
                '家庭环境：鼓励家庭内的表达尝试'
            ])
        
        report_data['interventions'] = interventions
        
        # 生成暴露层次
        report_data['exposure_hierarchy'] = [
            {'level': 1, 'activity': '在家中与亲密家人交谈', 'difficulty': '最容易'},
            {'level': 2, 'activity': '在熟悉环境中与朋友交谈', 'difficulty': '容易'},
            {'level': 3, 'activity': '在小组中发言', 'difficulty': '中等'},
            {'level': 4, 'activity': '在课堂上回答问题', 'difficulty': '困难'},
            {'level': 5, 'activity': '在陌生人面前讲话', 'difficulty': '最困难'}
        ]
        
        return report_data
        
    except Exception as e:
        # 返回默认报告数据
        return {
            'basic_info': {
                'name': questionnaire_dict.get('name', '未知'),
                'gender': '未知',
                'age': '未知',
                'birthdate': '未知'
            },
            'scores': {
                'ds_total': 0,
                'ss_total': 0,
                'ds_average': 0,
                'ss_average': 0
            },
            'risk_assessment': {
                'level': '无法评估',
                'color': '#6c757d',
                'description': f'数据解析错误: {str(e)}'
            },
            'interventions': ['请联系专业人员进行评估'],
            'exposure_hierarchy': []
        }

def generate_frankfurt_report_html(report_data):
    """生成Frankfurt Scale报告的HTML内容"""
    basic_info = report_data.get('basic_info', {})
    scores = report_data.get('scores', {})
    risk_assessment = report_data.get('risk_assessment', {})
    interventions = report_data.get('interventions', [])
    exposure_hierarchy = report_data.get('exposure_hierarchy', [])
    
    html = f"""
    <div class="frankfurt-report">
        <h2>Frankfurt Scale选择性缄默筛查量表 - 评估报告</h2>
        
        <div class="basic-info">
            <h3>基本信息</h3>
            <p><strong>姓名：</strong>{basic_info.get('name', '未填写')}</p>
            <p><strong>性别：</strong>{basic_info.get('gender', '未填写')}</p>
            <p><strong>年龄：</strong>{basic_info.get('age', '未填写')}</p>
            <p><strong>生日：</strong>{basic_info.get('birthdate', '未填写')}</p>
        </div>
        
        <div class="scores-summary">
            <h3>评分总结</h3>
            <div class="ds-scores">
                <h4>DS部分（诊断症状）</h4>
                <p><strong>总分：</strong>{scores.get('ds_total', 0)} (平均分: {scores.get('ds_average', 0)})</p>
            </div>
            <div class="ss-scores">
                <h4>SS部分（情境特异性）</h4>
                <p><strong>总分：</strong>{scores.get('ss_total', 0)} (平均分: {scores.get('ss_average', 0)})</p>
                <div class="ss-breakdown">
                    <p><strong>学校环境：</strong>{scores.get('ss_school_total', 0)} (平均分: {scores.get('ss_school_average', 0)})</p>
                    <p><strong>公共场所：</strong>{scores.get('ss_public_total', 0)} (平均分: {scores.get('ss_public_average', 0)})</p>
                    <p><strong>家庭环境：</strong>{scores.get('ss_home_total', 0)} (平均分: {scores.get('ss_home_average', 0)})</p>
                </div>
            </div>
        </div>
        
        <div class="risk-assessment">
            <h3>风险评估</h3>
            <div class="overall-risk">
                <h4>整体风险评估</h4>
                <p style="color: {risk_assessment.get('overall', {}).get('color', '#000')}; font-weight: bold;">
                    风险等级：{risk_assessment.get('overall', {}).get('level', '未知')}
                </p>
                <p>{risk_assessment.get('overall', {}).get('description', '')}</p>
            </div>
            <div class="detailed-risk">
                <h4>分环境风险评估</h4>
                <div class="school-risk">
                    <p><strong>学校环境：</strong>
                        <span style="color: {risk_assessment.get('school', {}).get('color', '#000')}; font-weight: bold;">
                            {risk_assessment.get('school', {}).get('level', '未知')}
                        </span>
                        (得分: {risk_assessment.get('school', {}).get('score', 0)})
                    </p>

                </div>
                <div class="public-risk">
                    <p><strong>公共场所：</strong>
                        <span style="color: {risk_assessment.get('public', {}).get('color', '#000')}; font-weight: bold;">
                            {risk_assessment.get('public', {}).get('level', '未知')}
                        </span>
                        (得分: {risk_assessment.get('public', {}).get('score', 0)})
                    </p>

                </div>
                <div class="home-risk">
                    <p><strong>家庭环境：</strong>
                        <span style="color: {risk_assessment.get('home', {}).get('color', '#000')}; font-weight: bold;">
                            {risk_assessment.get('home', {}).get('level', '未知')}
                        </span>
                        (得分: {risk_assessment.get('home', {}).get('score', 0)})
                    </p>

                </div>
            </div>
        </div>
        
        <div class="interventions">
            <h3>干预建议</h3>
            <ul>
    """
    
    for intervention in interventions:
        html += f"<li>{intervention}</li>"
    
    html += """
            </ul>
        </div>
        
        <div class="exposure-hierarchy">
            <h3>自主暴露层级</h3>
            <ol>
    """
    
    for item in exposure_hierarchy:
        html += f"<li>{item.get('activity', '')} (难度: {item.get('difficulty', '')})</li>"
    
    html += f"""
            </ol>
        </div>
        
        <div class="report-footer">
        </div>
    </div>
    """
    
    return html

# 注册统一错误处理器
register_error_handlers(app)

# 配置信息API - 提供给前端使用
@app.route('/api/config', methods=['GET'])
def get_config():
    """返回前端需要的配置信息"""
    return jsonify({
        'baseUrl': app.config['BASE_URL'],
        'environment': config_name,
        'debug': app.config.get('DEBUG', False)
    })

# 管理页面路由
@app.route('/admin')
@login_required
def admin_dashboard():
    return render_template('admin.html')

# 登录页面路由
@app.route('/login')
def login_page():
    # 如果已经登录，重定向到管理页面
    if 'user_id' in session:
        return redirect(url_for('admin_dashboard'))
    return render_template('login.html')

# config.js文件路由
@app.route('/config.js')
def config_js():
    """提供config.js配置文件"""
    return send_file('../html/config.js', mimetype='application/javascript')

@app.route('/html/FSCM/config.js')
def fscm_config_js():
    """提供FSCM目录下的config.js配置文件"""
    return send_file('../html/config.js', mimetype='application/javascript')

# 静态资源路由 - 本地开发环境使用Flask代理
@app.route('/local_assets/<path:filename>')
def serve_local_assets(filename):
    """提供html/local_assets目录下的静态资源"""
    return send_file(f'../html/local_assets/{filename}')

@app.route('/favicon.ico')
def favicon():
    """提供favicon"""
    return send_file('../html/favicon.ico')

# 静态文件代理路由 - 支持各种静态资源
@app.route('/image/<path:filename>')
def serve_images(filename):
    """提供html/image目录下的图片资源"""
    return send_file(f'../html/image/{filename}')

@app.route('/<path:filename>')
def serve_static_files(filename):
    """提供其他静态文件 - 仅在本地开发环境使用"""
    # 检查是否为静态文件扩展名
    static_extensions = ['.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', 
                        '.woff', '.woff2', '.ttf', '.eot', '.webp', '.json']
    
    if any(filename.lower().endswith(ext) for ext in static_extensions):
        try:
            # 首先尝试从html目录提供文件
            return send_file(f'../html/{filename}')
        except FileNotFoundError:
            # 如果html目录中没有，尝试从根目录
            try:
                return send_file(f'../{filename}')
            except FileNotFoundError:
                return "File not found", 404
    
    # 非静态文件返回404
    return "Not found", 404

# FSCM页面路由 - 根据环境动态设置路由
@app.route('/html/FSCM/')
@app.route('/FSCM/')
def fscm_page():
    """Frankfurt Scale选择性缄默筛查量表页面"""
    return send_file('../Frankfurt Scale of Selective Mutism - Integrated.html')

# 确保env-config.js和本地资源在FSCM路径下也能正确加载
@app.route('/FSCM/html/env-config.js')
def fscm_env_config():
    """在FSCM路径下提供env-config.js"""
    return send_file('../html/env-config.js')

# 确保本地资源在FSCM路径下也能正确加载
@app.route('/FSCM/html/local_assets/<path:filename>')
def fscm_local_assets(filename):
    """在FSCM路径下提供本地资源"""
    return send_file(f'../html/local_assets/{filename}')

# 首页路由 - html目录中的index.html作为入口页
@app.route('/')
def index():
    """首页 - 返回html目录中的index.html"""
    return send_file('../html/index.html')

# magic-wire页面路由
@app.route('/magic-wire')
def magic_wire():
    """Magic Wire页面"""
    return send_file('../html/magic-wire.html')

# study页面路由
@app.route('/study')
def study():
    """Study页面"""
    return send_file('../html/i5.html')

# 问卷引导页路由
@app.route('/guide')
def guide():
    """问卷引导页"""
    return send_file('../引导页.html')

# 6张表单页面路由
@app.route('/家长访谈表.html')
def parent_interview():
    """家长访谈表"""
    return send_file('../家长访谈表.html')

@app.route('/小学生交流评定表.html')
def student_communication():
    """小学生交流评定表"""
    return send_file('../小学生交流评定表.html')

@app.route('/青少年访谈表格.html')
def teen_interview():
    """青少年访谈表格"""
    return send_file('../青少年访谈表格.html')

@app.route('/说话习惯记录.html')
def speech_habit():
    """说话习惯记录"""
    return send_file('../说话习惯记录.html')

@app.route('/小学生报告表.html')
def student_report():
    """小学生报告表"""
    return send_file('../小学生报告表.html')

@app.route('/可能的SM维持因素清单.html')
def sm_factors():
    """可能的SM维持因素清单"""
    return send_file('../可能的SM维持因素清单.html')

if __name__ == '__main__':
    # 初始化数据库
    init_db()
    # 启动Flask应用
    app.run(debug=True, host='0.0.0.0', port=5002)
# ==================== 文件API路由 ====================

@app.route('/files/upload', methods=['GET'])
def get_upload_files():
    """获取上传目录文件列表"""
    try:
        import os
        upload_dir = '/home/ftptest/Downloader/upload'
        if not os.path.exists(upload_dir):
            return jsonify({'error': '上传目录不存在'}), 404
        
        files = []
        for filename in os.listdir(upload_dir):
            file_path = os.path.join(upload_dir, filename)
            if os.path.isfile(file_path):
                stat = os.stat(file_path)
                files.append({
                    'name': filename,
                    'size': stat.st_size,
                    'modified': stat.st_mtime
                })
        
        return jsonify({'files': files})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/files/successful', methods=['GET'])
def get_successful_files():
    """获取成功目录文件列表"""
    try:
        import os
        successful_dir = '/home/ftptest/Downloader/successful'
        if not os.path.exists(successful_dir):
            return jsonify({'error': '成功目录不存在'}), 404
        
        files = []
        for filename in os.listdir(successful_dir):
            file_path = os.path.join(successful_dir, filename)
            if os.path.isfile(file_path):
                stat = os.stat(file_path)
                files.append({
                    'name': filename,
                    'size': stat.st_size,
                    'modified': stat.st_mtime
                })
        
        return jsonify({'files': files})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/files/down', methods=['GET'])
def get_down_files():
    """获取下载目录文件列表"""
    try:
        import os
        down_dir = '/home/ftptest/Downloader/down'
        if not os.path.exists(down_dir):
            return jsonify({'error': '下载目录不存在'}), 404
        
        files = []
        for filename in os.listdir(down_dir):
            file_path = os.path.join(down_dir, filename)
            if os.path.isfile(file_path):
                stat = os.stat(file_path)
                files.append({
                    'name': filename,
                    'size': stat.st_size,
                    'modified': stat.st_mtime
                })
        
        return jsonify({'files': files})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
