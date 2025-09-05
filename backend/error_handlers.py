"""
统一错误处理模块
实现标准化的错误响应格式和错误处理机制
"""

from flask import jsonify, request, session
from datetime import datetime
import traceback
import logging
import os

# 确保日志目录存在
os.makedirs('logs', exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/error.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class ErrorCodes:
    """错误代码常量"""
    # 验证错误
    VALIDATION_ERROR = 'VALIDATION_ERROR'
    REQUIRED_FIELD_MISSING = 'REQUIRED_FIELD_MISSING'
    INVALID_FORMAT = 'INVALID_FORMAT'
    
    # 认证和授权错误
    AUTH_REQUIRED = 'AUTH_REQUIRED'
    AUTH_ERROR = 'AUTH_ERROR'
    SESSION_EXPIRED = 'SESSION_EXPIRED'
    PERMISSION_DENIED = 'PERMISSION_DENIED'
    
    # 资源错误
    NOT_FOUND = 'NOT_FOUND'
    RESOURCE_EXISTS = 'RESOURCE_EXISTS'
    RESOURCE_LOCKED = 'RESOURCE_LOCKED'
    
    # 服务器错误
    SERVER_ERROR = 'SERVER_ERROR'
    DATABASE_ERROR = 'DATABASE_ERROR'
    NETWORK_ERROR = 'NETWORK_ERROR'
    
    # 业务逻辑错误
    BUSINESS_ERROR = 'BUSINESS_ERROR'
    OPERATION_FAILED = 'OPERATION_FAILED'
    INVALID_OPERATION = 'INVALID_OPERATION'

class ErrorMessages:
    """用户友好的错误消息"""
    
    # 中文错误消息映射
    MESSAGES = {
        ErrorCodes.VALIDATION_ERROR: '输入的数据格式不正确，请检查后重试',
        ErrorCodes.REQUIRED_FIELD_MISSING: '必填信息不完整，请补充后提交',
        ErrorCodes.INVALID_FORMAT: '数据格式不正确，请按要求填写',
        
        ErrorCodes.AUTH_REQUIRED: '请先登录后再进行操作',
        ErrorCodes.AUTH_ERROR: '用户名或密码错误，请重新输入',
        ErrorCodes.SESSION_EXPIRED: '登录已过期，请重新登录',
        ErrorCodes.PERMISSION_DENIED: '您没有权限执行此操作',
        
        ErrorCodes.NOT_FOUND: '请求的内容不存在或已被删除',
        ErrorCodes.RESOURCE_EXISTS: '该资源已存在，请勿重复创建',
        ErrorCodes.RESOURCE_LOCKED: '资源正在被其他用户使用，请稍后重试',
        
        ErrorCodes.SERVER_ERROR: '服务器暂时无法处理您的请求，请稍后重试',
        ErrorCodes.DATABASE_ERROR: '数据保存失败，请稍后重试',
        ErrorCodes.NETWORK_ERROR: '网络连接异常，请检查网络后重试',
        
        ErrorCodes.BUSINESS_ERROR: '操作失败，请检查输入信息',
        ErrorCodes.OPERATION_FAILED: '操作执行失败，请重试',
        ErrorCodes.INVALID_OPERATION: '当前操作不被允许'
    }
    
    @classmethod
    def get_message(cls, error_code, default_message=None):
        """获取用户友好的错误消息"""
        return cls.MESSAGES.get(error_code, default_message or '操作失败，请稍后重试')

class StandardErrorResponse:
    """标准错误响应格式"""
    
    @staticmethod
    def create_error_response(
        error_code, 
        message=None, 
        details=None, 
        status_code=400,
        user_message=None,
        retry_after=None,
        request_id=None
    ):
        """
        创建标准错误响应
        
        Args:
            error_code: 错误代码
            message: 技术错误消息
            details: 详细错误信息（列表或字符串）
            status_code: HTTP状态码
            user_message: 用户友好的错误消息
            retry_after: 重试间隔（秒）
            request_id: 请求ID（用于追踪）
        """
        
        # 生成请求ID用于错误追踪
        if not request_id:
            try:
                # 尝试从Flask请求上下文获取URL
                from flask import request
                url_part = str(request.url) if request else 'no-request'
            except (ImportError, RuntimeError):
                # 如果不在Flask上下文中，使用默认值
                url_part = 'no-request'
            
            request_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}-{hash(url_part + str(datetime.now().microsecond)) % 10000:04d}"
        
        # 获取用户友好的错误消息
        if not user_message:
            user_message = ErrorMessages.get_message(error_code, message)
        
        # 构建错误响应
        error_response = {
            'success': False,
            'error': {
                'code': error_code,
                'message': user_message,
                'technical_message': message,
                'request_id': request_id
            },
            'timestamp': datetime.now().isoformat()
        }
        
        # 添加详细错误信息
        if details:
            if isinstance(details, list):
                error_response['error']['details'] = details
            else:
                error_response['error']['details'] = [str(details)]
        
        # 添加重试信息
        if retry_after:
            error_response['retry_after'] = retry_after
        
        # 记录错误日志
        log_error(error_code, message, details, status_code, request_id)
        
        return error_response, status_code
    
    @staticmethod
    def validation_error(errors, message="数据验证失败"):
        """创建验证错误响应"""
        if isinstance(errors, dict):
            # 将嵌套的错误信息展平
            flat_errors = []
            def flatten_errors(errors, prefix=""):
                if isinstance(errors, dict):
                    for key, value in errors.items():
                        new_prefix = f"{prefix}.{key}" if prefix else key
                        flatten_errors(value, new_prefix)
                elif isinstance(errors, list):
                    for error in errors:
                        if isinstance(error, str):
                            flat_errors.append(f"{prefix}: {error}" if prefix else error)
                        else:
                            flatten_errors(error, prefix)
                else:
                    flat_errors.append(f"{prefix}: {errors}" if prefix else str(errors))
            
            flatten_errors(errors)
            errors = flat_errors
        elif not isinstance(errors, list):
            errors = [str(errors)]
        
        return StandardErrorResponse.create_error_response(
            ErrorCodes.VALIDATION_ERROR,
            message,
            errors,
            400,
            "请检查输入信息是否完整和正确"
        )
    
    @staticmethod
    def auth_error(message="认证失败"):
        """创建认证错误响应"""
        return StandardErrorResponse.create_error_response(
            ErrorCodes.AUTH_ERROR,
            message,
            status_code=401
        )
    
    @staticmethod
    def permission_error(message="权限不足"):
        """创建权限错误响应"""
        return StandardErrorResponse.create_error_response(
            ErrorCodes.PERMISSION_DENIED,
            message,
            status_code=403
        )
    
    @staticmethod
    def not_found_error(resource="资源", message=None):
        """创建资源不存在错误响应"""
        if not message:
            message = f"{resource}不存在"
        return StandardErrorResponse.create_error_response(
            ErrorCodes.NOT_FOUND,
            message,
            status_code=404
        )
    
    @staticmethod
    def server_error(message="服务器内部错误", details=None):
        """创建服务器错误响应"""
        return StandardErrorResponse.create_error_response(
            ErrorCodes.SERVER_ERROR,
            message,
            details,
            500,
            retry_after=30  # 建议30秒后重试
        )

def log_error(error_code, message, details, status_code, request_id):
    """记录错误日志"""
    try:
        # 获取请求信息（如果在Flask上下文中）
        try:
            from flask import request, session
            user_id = session.get('user_id', 'anonymous')
            username = session.get('username', 'anonymous')
            ip_address = request.remote_addr or 'unknown'
            user_agent = request.headers.get('User-Agent', 'unknown')[:200]
            request_method = request.method
            request_path = request.path
            request_args = dict(request.args)
        except (ImportError, RuntimeError):
            # 如果不在Flask上下文中，使用默认值
            user_id = 'system'
            username = 'system'
            ip_address = 'unknown'
            user_agent = 'unknown'
            request_method = 'unknown'
            request_path = 'unknown'
            request_args = {}
        
        # 构建日志信息
        log_data = {
            'request_id': request_id,
            'error_code': error_code,
            'error_message': message,  # 避免与logging的message字段冲突
            'error_details': details,
            'status_code': status_code,
            'user_id': user_id,
            'username': username,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'request_method': request_method,
            'request_path': request_path,
            'request_args': request_args,
            'timestamp': datetime.now().isoformat()
        }
        
        # 记录到日志文件
        if status_code >= 500:
            logger.error(f"Server Error [{request_id}]: {message}", extra=log_data)
        elif status_code >= 400:
            logger.warning(f"Client Error [{request_id}]: {message}", extra=log_data)
        else:
            logger.info(f"Error [{request_id}]: {message}", extra=log_data)
            
    except Exception as e:
        # 记录日志失败不应该影响主要功能
        logger.error(f"Failed to log error: {e}")

def register_error_handlers(app):
    """注册全局错误处理器"""
    
    @app.errorhandler(400)
    def handle_bad_request(e):
        """处理400错误"""
        return jsonify(*StandardErrorResponse.create_error_response(
            ErrorCodes.VALIDATION_ERROR,
            "请求格式不正确",
            str(e),
            400
        ))
    
    @app.errorhandler(401)
    def handle_unauthorized(e):
        """处理401错误"""
        return jsonify(*StandardErrorResponse.auth_error("需要登录认证"))
    
    @app.errorhandler(403)
    def handle_forbidden(e):
        """处理403错误"""
        return jsonify(*StandardErrorResponse.permission_error("访问被拒绝"))
    
    @app.errorhandler(404)
    def handle_not_found(e):
        """处理404错误"""
        return jsonify(*StandardErrorResponse.not_found_error("页面或资源"))
    
    @app.errorhandler(405)
    def handle_method_not_allowed(e):
        """处理405错误"""
        return jsonify(*StandardErrorResponse.create_error_response(
            ErrorCodes.INVALID_OPERATION,
            "请求方法不被允许",
            str(e),
            405
        ))
    
    @app.errorhandler(429)
    def handle_too_many_requests(e):
        """处理429错误（请求过多）"""
        return jsonify(*StandardErrorResponse.create_error_response(
            ErrorCodes.OPERATION_FAILED,
            "请求过于频繁",
            "请稍后再试",
            429,
            retry_after=60
        ))
    
    @app.errorhandler(500)
    def handle_internal_server_error(e):
        """处理500错误"""
        # 记录详细的错误堆栈
        error_details = traceback.format_exc()
        return jsonify(*StandardErrorResponse.server_error(
            "服务器内部错误",
            error_details if app.debug else None
        ))
    
    @app.errorhandler(502)
    def handle_bad_gateway(e):
        """处理502错误"""
        return jsonify(*StandardErrorResponse.create_error_response(
            ErrorCodes.NETWORK_ERROR,
            "网关错误",
            str(e),
            502,
            retry_after=30
        ))
    
    @app.errorhandler(503)
    def handle_service_unavailable(e):
        """处理503错误"""
        return jsonify(*StandardErrorResponse.create_error_response(
            ErrorCodes.SERVER_ERROR,
            "服务暂时不可用",
            str(e),
            503,
            retry_after=60
        ))
    
    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        """处理未捕获的异常"""
        error_details = traceback.format_exc()
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        
        return jsonify(*StandardErrorResponse.server_error(
            f"未处理的异常: {str(e)}",
            error_details if app.debug else None
        ))

# 便捷函数，用于在视图函数中快速创建错误响应
def validation_error(errors, message="数据验证失败"):
    """快速创建验证错误响应"""
    return StandardErrorResponse.validation_error(errors, message)

def auth_error(message="认证失败"):
    """快速创建认证错误响应"""
    return StandardErrorResponse.auth_error(message)

def permission_error(message="权限不足"):
    """快速创建权限错误响应"""
    return StandardErrorResponse.permission_error(message)

def not_found_error(resource="资源", message=None):
    """快速创建资源不存在错误响应"""
    return StandardErrorResponse.not_found_error(resource, message)

def server_error(message="服务器内部错误", details=None):
    """快速创建服务器错误响应"""
    return StandardErrorResponse.server_error(message, details)

def business_error(message, details=None):
    """快速创建业务逻辑错误响应"""
    return StandardErrorResponse.create_error_response(
        ErrorCodes.BUSINESS_ERROR,
        message,
        details,
        400
    )