// 全局配置文件
var CONFIG = {
    // 基础URL配置 - 从服务器端动态获取
    BASE_URL: '',  // 将在初始化时从服务器获取
    
    // 临时基础URL配置 - 用于获取配置信息
    TEMP_BASE_URL: (function() {
        // 检测当前环境
        var isLocal = location.hostname === 'localhost' || location.hostname === '127.0.0.1' || location.hostname === '';
        
        if (isLocal) {
            // 本地开发环境 - 使用5002端口
            return 'http://127.0.0.1:5002';
        } else {
            // 生产环境 - 使用115.190.103.114（默认HTTP端口）
            return 'http://115.190.103.114';
        }
    })(),
    
    // API端点配置
    API: {
        SUBMIT: '/api/submit',
        QUESTIONNAIRES: '/api/questionnaires',
        AUTH: {
            LOGIN: '/api/auth/login',
            LOGOUT: '/api/auth/logout',
            STATUS: '/api/auth/status',
            REFRESH: '/api/auth/refresh',
            EXTEND: '/api/auth/extend'
        },
        ADMIN: {
            STATISTICS: '/api/admin/statistics',
            LOGS: '/api/admin/logs',
            EXPORT: '/api/admin/export',
            HEALTH: '/api/admin/system/health',
            PERFORMANCE: '/api/admin/system/performance',
            REALTIME: '/api/admin/system/realtime'
        }
    },
    
    // 页面路径配置
    PAGES: {
        LOGIN: '/login',
        ADMIN: '/admin',
        HOME: '/'
    },
    
    // 获取完整URL的辅助函数
    getApiUrl: function(endpoint) {
        return this.BASE_URL + endpoint;
    },
    
    getPageUrl: function(page) {
        return this.BASE_URL + page;
    },
    
    // 初始化配置 - 从服务器获取baseUrl
    init: async function() {
        try {
            const response = await fetch(this.TEMP_BASE_URL + '/api/config');
            if (response.ok) {
                const config = await response.json();
                this.BASE_URL = config.baseUrl;
                this.ENVIRONMENT = config.environment;
                this.DEBUG = config.debug;
                console.log('CONFIG initialized:', {
                    baseUrl: this.BASE_URL,
                    environment: this.ENVIRONMENT,
                    debug: this.DEBUG
                });
            } else {
                console.warn('Failed to fetch config from server, using fallback');
                this.BASE_URL = this.TEMP_BASE_URL;
            }
        } catch (error) {
            console.warn('Error fetching config from server:', error);
            this.BASE_URL = this.TEMP_BASE_URL;
        }
        
        // 触发配置初始化完成事件
        if (typeof window !== 'undefined') {
            window.dispatchEvent(new Event('configReady'));
            console.log('configReady event dispatched');
        }
    }
};

// 如果在Node.js环境中，导出配置
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}

// 如果在浏览器环境中，将配置添加到全局对象
if (typeof window !== 'undefined') {
    window.CONFIG = CONFIG;
}