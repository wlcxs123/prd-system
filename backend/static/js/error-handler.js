/**
 * 统一前端错误处理组件
 * 提供标准化的错误显示、网络重试机制和用户友好的错误提示
 */

class ErrorHandler {
    constructor() {
        this.retryAttempts = 3;
        this.retryDelay = 1000; // 1秒
        this.maxRetryDelay = 10000; // 最大10秒
        this.networkTimeout = 30000; // 30秒超时
        
        // 初始化错误提示容器
        this.initErrorContainer();
        
        // 绑定全局错误处理
        this.bindGlobalErrorHandlers();
    }
    
    /**
     * 初始化错误提示容器
     */
    initErrorContainer() {
        // 等待DOM加载完成
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initErrorContainer());
            return;
        }
        
        // 创建错误提示容器
        if (!document.getElementById('error-container')) {
            const container = document.createElement('div');
            container.id = 'error-container';
            container.className = 'error-container';
            container.innerHTML = `
                <style>
                    .error-container {
                        position: fixed;
                        top: 20px;
                        right: 20px;
                        z-index: 10000;
                        max-width: 400px;
                    }
                    
                    .error-toast {
                        background: #fff;
                        border-radius: 8px;
                        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                        margin-bottom: 10px;
                        padding: 16px;
                        border-left: 4px solid #dc3545;
                        animation: slideIn 0.3s ease-out;
                        position: relative;
                        max-height: 200px;
                        overflow-y: auto;
                    }
                    
                    .error-toast.success {
                        border-left-color: #28a745;
                    }
                    
                    .error-toast.warning {
                        border-left-color: #ffc107;
                    }
                    
                    .error-toast.info {
                        border-left-color: #17a2b8;
                    }
                    
                    .error-toast-header {
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        margin-bottom: 8px;
                        font-weight: bold;
                        color: #333;
                    }
                    
                    .error-toast-close {
                        background: none;
                        border: none;
                        font-size: 18px;
                        cursor: pointer;
                        color: #999;
                        padding: 0;
                        width: 20px;
                        height: 20px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    }
                    
                    .error-toast-close:hover {
                        color: #333;
                    }
                    
                    .error-toast-body {
                        color: #666;
                        line-height: 1.4;
                    }
                    
                    .error-toast-details {
                        margin-top: 8px;
                        padding: 8px;
                        background: #f8f9fa;
                        border-radius: 4px;
                        font-size: 12px;
                        color: #666;
                        max-height: 100px;
                        overflow-y: auto;
                    }
                    
                    .error-toast-actions {
                        margin-top: 12px;
                        display: flex;
                        gap: 8px;
                    }
                    
                    .error-toast-btn {
                        padding: 4px 12px;
                        border: 1px solid #ddd;
                        background: #fff;
                        border-radius: 4px;
                        cursor: pointer;
                        font-size: 12px;
                        transition: all 0.2s;
                    }
                    
                    .error-toast-btn:hover {
                        background: #f8f9fa;
                    }
                    
                    .error-toast-btn.primary {
                        background: #007bff;
                        color: white;
                        border-color: #007bff;
                    }
                    
                    .error-toast-btn.primary:hover {
                        background: #0056b3;
                    }
                    
                    .retry-indicator {
                        display: inline-block;
                        margin-left: 8px;
                        font-size: 12px;
                        color: #666;
                    }
                    
                    .loading-spinner {
                        display: inline-block;
                        width: 12px;
                        height: 12px;
                        border: 2px solid #f3f3f3;
                        border-top: 2px solid #007bff;
                        border-radius: 50%;
                        animation: spin 1s linear infinite;
                        margin-right: 6px;
                    }
                    
                    @keyframes slideIn {
                        from {
                            transform: translateX(100%);
                            opacity: 0;
                        }
                        to {
                            transform: translateX(0);
                            opacity: 1;
                        }
                    }
                    
                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                </style>
            `;
            document.body.appendChild(container);
        }
    }
    
    /**
     * 绑定全局错误处理
     */
    bindGlobalErrorHandlers() {
        // 处理未捕获的JavaScript错误
        window.addEventListener('error', (event) => {
            this.showError('JavaScript错误', event.message, 'error', {
                details: `文件: ${event.filename}, 行: ${event.lineno}, 列: ${event.colno}`
            });
        });
        
        // 处理Promise拒绝
        window.addEventListener('unhandledrejection', (event) => {
            this.showError('网络请求失败', '请检查网络连接后重试', 'error', {
                details: event.reason
            });
        });
    }
    
    /**
     * 显示错误提示
     */
    showError(title, message, type = 'error', options = {}) {
        const container = document.getElementById('error-container');
        if (!container) return;
        
        const toast = document.createElement('div');
        toast.className = `error-toast ${type}`;
        
        const toastId = 'toast-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        toast.id = toastId;
        
        let actionsHtml = '';
        if (options.retry) {
            actionsHtml += `<button class="error-toast-btn primary" onclick="errorHandler.retry('${toastId}')">重试</button>`;
        }
        if (options.details) {
            actionsHtml += `<button class="error-toast-btn" onclick="errorHandler.toggleDetails('${toastId}')">详情</button>`;
        }
        
        toast.innerHTML = `
            <div class="error-toast-header">
                <span>${title}</span>
                <button class="error-toast-close" onclick="errorHandler.closeToast('${toastId}')">&times;</button>
            </div>
            <div class="error-toast-body">${message}</div>
            ${options.details ? `<div class="error-toast-details" id="${toastId}-details" style="display: none;">${this.formatDetails(options.details)}</div>` : ''}
            ${actionsHtml ? `<div class="error-toast-actions">${actionsHtml}</div>` : ''}
        `;
        
        container.appendChild(toast);
        
        // 存储重试信息
        if (options.retry) {
            toast.retryFunction = options.retry;
        }
        
        // 自动关闭（除非是错误类型）
        if (type !== 'error') {
            setTimeout(() => {
                this.closeToast(toastId);
            }, options.autoClose || 5000);
        }
        
        return toastId;
    }
    
    /**
     * 显示成功提示
     */
    showSuccess(message, options = {}) {
        return this.showError('成功', message, 'success', options);
    }
    
    /**
     * 显示警告提示
     */
    showWarning(message, options = {}) {
        return this.showError('警告', message, 'warning', options);
    }
    
    /**
     * 显示信息提示
     */
    showInfo(message, options = {}) {
        return this.showError('提示', message, 'info', options);
    }
    
    /**
     * 关闭提示
     */
    closeToast(toastId) {
        const toast = document.getElementById(toastId);
        if (toast) {
            toast.style.animation = 'slideIn 0.3s ease-out reverse';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }
    }
    
    /**
     * 切换详情显示
     */
    toggleDetails(toastId) {
        const details = document.getElementById(toastId + '-details');
        if (details) {
            details.style.display = details.style.display === 'none' ? 'block' : 'none';
        }
    }
    
    /**
     * 重试操作
     */
    retry(toastId) {
        const toast = document.getElementById(toastId);
        if (toast && toast.retryFunction) {
            // 显示重试状态
            const retryBtn = toast.querySelector('.error-toast-btn.primary');
            if (retryBtn) {
                retryBtn.innerHTML = '<span class="loading-spinner"></span>重试中...';
                retryBtn.disabled = true;
            }
            
            // 执行重试
            toast.retryFunction().finally(() => {
                this.closeToast(toastId);
            });
        }
    }
    
    /**
     * 格式化详情信息
     */
    formatDetails(details) {
        if (typeof details === 'string') {
            return details;
        } else if (Array.isArray(details)) {
            return details.join('<br>');
        } else if (typeof details === 'object') {
            return JSON.stringify(details, null, 2);
        }
        return String(details);
    }
    
    /**
     * 处理API响应错误
     */
    handleApiError(response, originalRequest = null) {
        if (!response) {
            return this.showError('网络错误', '无法连接到服务器，请检查网络连接', 'error', {
                retry: originalRequest ? () => this.retryRequest(originalRequest) : null
            });
        }
        
        // 尝试解析错误响应
        return response.json().then(errorData => {
            const error = errorData.error || {};
            const title = this.getErrorTitle(error.code);
            const message = error.message || '操作失败，请稍后重试';
            const details = error.details || error.technical_message;
            
            return this.showError(title, message, 'error', {
                details: details,
                retry: originalRequest && this.shouldRetry(error.code) ? 
                    () => this.retryRequest(originalRequest) : null
            });
        }).catch(() => {
            // 无法解析响应，显示通用错误
            return this.showError('服务器错误', `HTTP ${response.status}: ${response.statusText}`, 'error', {
                retry: originalRequest ? () => this.retryRequest(originalRequest) : null
            });
        });
    }
    
    /**
     * 获取错误标题
     */
    getErrorTitle(errorCode) {
        const titles = {
            'VALIDATION_ERROR': '输入错误',
            'AUTH_REQUIRED': '需要登录',
            'AUTH_ERROR': '登录失败',
            'SESSION_EXPIRED': '登录过期',
            'PERMISSION_DENIED': '权限不足',
            'NOT_FOUND': '内容不存在',
            'SERVER_ERROR': '服务器错误',
            'NETWORK_ERROR': '网络错误',
            'DATABASE_ERROR': '数据错误'
        };
        return titles[errorCode] || '操作失败';
    }
    
    /**
     * 判断是否应该重试
     */
    shouldRetry(errorCode) {
        const retryableCodes = ['SERVER_ERROR', 'NETWORK_ERROR', 'DATABASE_ERROR'];
        return retryableCodes.includes(errorCode);
    }
    
    /**
     * 带重试机制的网络请求
     */
    async fetchWithRetry(url, options = {}, retryCount = 0) {
        // 设置超时
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.networkTimeout);
        
        const requestOptions = {
            ...options,
            signal: controller.signal
        };
        
        try {
            const response = await fetch(url, requestOptions);
            clearTimeout(timeoutId);
            
            // 如果响应成功，直接返回
            if (response.ok) {
                return response;
            }
            
            // 如果是客户端错误（4xx），不重试
            if (response.status >= 400 && response.status < 500) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            // 服务器错误（5xx），可以重试
            if (retryCount < this.retryAttempts) {
                const delay = Math.min(this.retryDelay * Math.pow(2, retryCount), this.maxRetryDelay);
                await this.sleep(delay);
                return this.fetchWithRetry(url, options, retryCount + 1);
            }
            
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            
        } catch (error) {
            clearTimeout(timeoutId);
            
            // 网络错误或超时，可以重试
            if ((error.name === 'AbortError' || error.name === 'TypeError') && retryCount < this.retryAttempts) {
                const delay = Math.min(this.retryDelay * Math.pow(2, retryCount), this.maxRetryDelay);
                await this.sleep(delay);
                return this.fetchWithRetry(url, options, retryCount + 1);
            }
            
            throw error;
        }
    }
    
    /**
     * 重试请求
     */
    async retryRequest(originalRequest) {
        try {
            const response = await this.fetchWithRetry(originalRequest.url, originalRequest.options);
            
            if (response.ok) {
                this.showSuccess('操作成功');
                
                // 如果有成功回调，执行它
                if (originalRequest.onSuccess) {
                    const data = await response.json();
                    originalRequest.onSuccess(data);
                }
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
            
        } catch (error) {
            this.showError('重试失败', error.message, 'error');
        }
    }
    
    /**
     * 睡眠函数
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    /**
     * 包装fetch请求，自动处理错误
     */
    async request(url, options = {}) {
        try {
            const response = await this.fetchWithRetry(url, options);
            
            if (!response.ok) {
                await this.handleApiError(response, { url, options });
                return null;
            }
            
            return response;
            
        } catch (error) {
            this.showError('网络请求失败', error.message, 'error', {
                retry: () => this.retryRequest({ url, options })
            });
            return null;
        }
    }
    
    /**
     * 便捷的POST请求方法
     */
    async post(url, data, options = {}) {
        const requestOptions = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            body: JSON.stringify(data),
            ...options
        };
        
        return this.request(url, requestOptions);
    }
    
    /**
     * 便捷的GET请求方法
     */
    async get(url, options = {}) {
        return this.request(url, { method: 'GET', ...options });
    }
    
    /**
     * 便捷的PUT请求方法
     */
    async put(url, data, options = {}) {
        const requestOptions = {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            body: JSON.stringify(data),
            ...options
        };
        
        return this.request(url, requestOptions);
    }
    
    /**
     * 便捷的DELETE请求方法
     */
    async delete(url, options = {}) {
        return this.request(url, { method: 'DELETE', ...options });
    }
}

// 创建全局错误处理器实例
const errorHandler = new ErrorHandler();

// 导出给其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ErrorHandler;
}