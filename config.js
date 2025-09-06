// 全局配置文件
const CONFIG = {
    // 基础URL配置
    BASE_URL: 'http://115.190.103.114:8081',
    
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