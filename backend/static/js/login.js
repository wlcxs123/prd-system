/**
 * 问卷管理系统 - 登录页面 JavaScript
 * 实现登录表单验证、提交和状态管理功能
 */

// 登录管理类
class LoginManager {
    constructor() {
        this.loginForm = null;
        this.loginBtn = null;
        this.loading = null;
        this.alertContainer = null;
        this.usernameInput = null;
        this.passwordInput = null;
        
        // 初始化
        this.init();
    }
    
    /**
     * 初始化登录管理器
     */
    init() {
        // 等待DOM加载完成
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupElements());
        } else {
            this.setupElements();
        }
    }
    
    /**
     * 设置页面元素和事件监听器
     */
    setupElements() {
        // 获取页面元素
        this.loginForm = document.getElementById('loginForm');
        this.loginBtn = document.getElementById('loginBtn');
        this.loading = document.getElementById('loading');
        this.alertContainer = document.getElementById('alertContainer');
        this.usernameInput = document.getElementById('username');
        this.passwordInput = document.getElementById('password');
        
        // 检查必要元素是否存在
        if (!this.loginForm || !this.loginBtn) {
            console.error('登录页面必要元素未找到');
            return;
        }
        
        // 设置事件监听器
        this.setupEventListeners();
        
        // 检查登录状态
        this.checkAuthStatus();
        
        // 设置表单验证
        this.setupFormValidation();
    }
    
    /**
     * 设置事件监听器
     */
    setupEventListeners() {
        // 表单提交事件
        this.loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleLogin();
        });
        
        // 回车键登录
        document.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !this.loginBtn.disabled) {
                e.preventDefault();
                this.handleLogin();
            }
        });
        
        // 输入框实时验证
        if (this.usernameInput) {
            this.usernameInput.addEventListener('input', () => this.validateUsername());
            this.usernameInput.addEventListener('blur', () => this.validateUsername());
        }
        
        if (this.passwordInput) {
            this.passwordInput.addEventListener('input', () => this.validatePassword());
            this.passwordInput.addEventListener('blur', () => this.validatePassword());
        }
    }
    
    /**
     * 设置表单验证
     */
    setupFormValidation() {
        // 清除浏览器默认验证样式
        this.loginForm.setAttribute('novalidate', 'true');
    }
    
    /**
     * 验证用户名
     */
    validateUsername() {
        const username = this.usernameInput.value.trim();
        const isValid = username.length >= 2;
        
        this.setFieldValidation(this.usernameInput, isValid, 
            isValid ? '用户名格式正确' : '用户名至少需要2个字符');
        
        return isValid;
    }
    
    /**
     * 验证密码
     */
    validatePassword() {
        const password = this.passwordInput.value;
        const isValid = password.length >= 6;
        
        this.setFieldValidation(this.passwordInput, isValid,
            isValid ? '密码格式正确' : '密码至少需要6个字符');
        
        return isValid;
    }
    
    /**
     * 设置字段验证状态
     */
    setFieldValidation(field, isValid, message) {
        // 移除之前的验证类
        field.classList.remove('is-valid', 'is-invalid');
        
        // 移除之前的反馈信息
        const existingFeedback = field.parentNode.querySelector('.invalid-feedback, .valid-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }
        
        // 添加新的验证状态
        if (field.value.trim() !== '') {
            field.classList.add(isValid ? 'is-valid' : 'is-invalid');
            
            // 添加反馈信息
            const feedbackDiv = document.createElement('div');
            feedbackDiv.className = isValid ? 'valid-feedback' : 'invalid-feedback';
            feedbackDiv.textContent = message;
            field.parentNode.appendChild(feedbackDiv);
        }
    }
    
    /**
     * 检查登录状态
     */
    async checkAuthStatus() {
        try {
            const response = await fetch('/api/auth/status');
            const result = await response.json();
            
            if (result.success && result.authenticated) {
                // 已经登录，重定向到管理页面
                this.showAlert('您已登录，正在跳转到管理页面...', 'success');
                setTimeout(() => {
                    window.location.href = '/admin';
                }, 1000);
            }
        } catch (error) {
            console.log('检查登录状态失败:', error);
            // 不显示错误，因为可能是正常的未登录状态
        }
    }
    
    /**
     * 处理登录
     */
    async handleLogin() {
        // 获取表单数据
        const username = this.usernameInput.value.trim();
        const password = this.passwordInput.value;
        
        // 清除之前的错误信息
        this.clearAlerts();
        
        // 验证表单
        const isUsernameValid = this.validateUsername();
        const isPasswordValid = this.validatePassword();
        
        if (!isUsernameValid || !isPasswordValid) {
            this.showAlert('请检查输入信息', 'danger');
            return;
        }
        
        // 基本验证
        if (!username || !password) {
            this.showAlert('请输入用户名和密码', 'danger');
            return;
        }
        
        // 显示加载状态
        this.setLoadingState(true);
        
        try {
            // 发送登录请求
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username: username,
                    password: password
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showAlert('登录成功，正在跳转...', 'success');
                // 延迟跳转，让用户看到成功信息
                setTimeout(() => {
                    window.location.href = '/admin';
                }, 1500);
            } else {
                this.showAlert(result.error?.message || '登录失败', 'danger');
                this.setLoadingState(false);
                
                // 清空密码字段
                this.passwordInput.value = '';
                this.passwordInput.focus();
            }
        } catch (error) {
            console.error('登录请求失败:', error);
            this.showAlert('网络错误，请检查网络连接后重试', 'danger');
            this.setLoadingState(false);
        }
    }
    
    /**
     * 设置加载状态
     */
    setLoadingState(isLoading) {
        if (isLoading) {
            this.loginBtn.disabled = true;
            this.loginBtn.style.display = 'none';
            if (this.loading) {
                this.loading.style.display = 'block';
            }
            
            // 禁用输入框
            this.usernameInput.disabled = true;
            this.passwordInput.disabled = true;
        } else {
            this.loginBtn.disabled = false;
            this.loginBtn.style.display = 'block';
            if (this.loading) {
                this.loading.style.display = 'none';
            }
            
            // 启用输入框
            this.usernameInput.disabled = false;
            this.passwordInput.disabled = false;
        }
    }
    
    /**
     * 显示提示信息
     */
    showAlert(message, type = 'info') {
        if (!this.alertContainer) return;
        
        const alertClass = this.getAlertClass(type);
        const alertIcon = this.getAlertIcon(type);
        
        const alertHtml = `
            <div class="alert ${alertClass}">
                ${alertIcon} ${message}
            </div>
        `;
        
        this.alertContainer.innerHTML = alertHtml;
        
        // 自动隐藏成功消息
        if (type === 'success') {
            setTimeout(() => {
                this.clearAlerts();
            }, 3000);
        }
    }
    
    /**
     * 获取提示框样式类
     */
    getAlertClass(type) {
        const classes = {
            'success': 'alert-success',
            'danger': 'alert-danger',
            'warning': 'alert-warning',
            'info': 'alert-info'
        };
        return classes[type] || 'alert-info';
    }
    
    /**
     * 获取提示框图标
     */
    getAlertIcon(type) {
        const icons = {
            'success': '✓',
            'danger': '✗',
            'warning': '⚠',
            'info': 'ℹ'
        };
        return icons[type] || 'ℹ';
    }
    
    /**
     * 清除提示信息
     */
    clearAlerts() {
        if (this.alertContainer) {
            this.alertContainer.innerHTML = '';
        }
    }
}

// 工具函数
const LoginUtils = {
    /**
     * 检查密码强度
     */
    checkPasswordStrength(password) {
        let strength = 0;
        const checks = {
            length: password.length >= 8,
            lowercase: /[a-z]/.test(password),
            uppercase: /[A-Z]/.test(password),
            numbers: /\d/.test(password),
            symbols: /[^A-Za-z0-9]/.test(password)
        };
        
        strength = Object.values(checks).filter(Boolean).length;
        
        return {
            score: strength,
            checks: checks,
            level: strength < 2 ? 'weak' : strength < 4 ? 'medium' : 'strong'
        };
    },
    
    /**
     * 格式化错误信息
     */
    formatErrorMessage(error) {
        const errorMessages = {
            'AUTH_ERROR': '用户名或密码错误',
            'VALIDATION_ERROR': '输入信息格式不正确',
            'NETWORK_ERROR': '网络连接失败，请稍后重试',
            'SERVER_ERROR': '服务器错误，请联系管理员'
        };
        
        return errorMessages[error.code] || error.message || '未知错误';
    }
};

// 页面加载完成后初始化登录管理器
let loginManager;
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        loginManager = new LoginManager();
    });
} else {
    loginManager = new LoginManager();
}

// 导出到全局作用域（用于调试）
window.LoginManager = LoginManager;
window.LoginUtils = LoginUtils;