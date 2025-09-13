// 通用环境配置文件
// 为html文件夹中的所有页面提供统一的环境判断和URL配置
// 支持从不同路径加载（如/FSCM/路径）

(function(global) {
    'use strict';
    
    // 环境检测函数 - 增强版，支持不同路径下的加载
    function detectEnvironment() {
        // 使用与后端app.py一致的本地环境判断逻辑
        const isLocal = location.hostname === 'localhost' || 
                       location.hostname === '127.0.0.1' || 
                       location.hostname === '' ||
                       location.hostname === '0.0.0.0';
        
        const currentPort = location.port || (location.protocol === 'https:' ? '443' : '80');
        const protocol = location.protocol;
        const hostname = location.hostname;
        
        return {
            isLocal: isLocal,
            hostname: hostname,
            port: currentPort,
            protocol: protocol,
            fullHost: location.host
        };
    }
    
    // 获取当前脚本路径，用于处理不同路径下的加载情况
    function getScriptPath() {
        // 尝试获取当前正在执行的脚本元素
        const scripts = document.getElementsByTagName('script');
        let scriptPath = '';
        
        // 遍历所有脚本标签，查找env-config.js
        for (let i = 0; i < scripts.length; i++) {
            const src = scripts[i].src;
            if (src && src.indexOf('env-config.js') !== -1) {
                // 提取脚本所在的路径
                const urlObj = new URL(src);
                const pathParts = urlObj.pathname.split('/');
                
                // 移除脚本文件名
                pathParts.pop();
                
                // 重建路径
                scriptPath = pathParts.join('/');
                break;
            }
        }
        
        return scriptPath;
    }
    
    // URL生成器
    function createUrlGenerator(env) {
        // 获取脚本路径，用于处理不同路径下的加载
        const scriptPath = getScriptPath();
        
        // 根据环境设置基础URL
        const baseUrl = env.isLocal ? 'http://127.0.0.1:5002' : `http://115.190.103.114:8080/html`;
        
        // 确保在不同路径下加载时能正确处理资源路径
        // 如果是本地环境且脚本路径不为空，则使用脚本路径作为基础路径
        const adjustedBaseUrl = env.isLocal && scriptPath ? scriptPath : baseUrl;
        
        return {
            // 基础URL
            base: adjustedBaseUrl,
            
            // API URL生成器
            api: function(endpoint) {
                return adjustedBaseUrl + (endpoint.startsWith('/') ? endpoint : '/' + endpoint);
            },
            
            // 页面URL生成器
            page: function(path) {
                return adjustedBaseUrl + (path.startsWith('/') ? path : '/' + path);
            },
            
            // 图片资源URL生成器
            image: function(imagePath) {
                const cleanPath = imagePath.startsWith('/') ? imagePath : '/' + imagePath;
                return adjustedBaseUrl + '/image' + cleanPath;
            },
            
            // 静态资源URL生成器
            asset: function(assetPath) {
                const cleanPath = assetPath.startsWith('/') ? assetPath : '/' + assetPath;
                return baseUrl + cleanPath;
            },
            
            // 完整URL生成器（用于外部链接）
            full: function(path) {
                const cleanPath = path.startsWith('/') ? path : '/' + path;
                return baseUrl + cleanPath;
            }
        };
    }
    
    // 初始化环境配置
    function initEnvConfig() {
        const env = detectEnvironment();
        const urls = createUrlGenerator(env);
        
        const config = {
            // 环境信息
            environment: env,
            
            // URL生成器
            urls: urls,
            
            // 便捷属性
            baseUrl: urls.base,
            isLocal: env.isLocal,
            
            // 日志函数
            log: function(message, data) {
                console.log(`[EnvConfig] ${message}`, data || '');
            },
            
            // 获取环境描述
            getEnvDescription: function() {
                return env.isLocal ? '本地开发环境' : `生产环境 (${env.hostname}:${env.port})`;
            }
        };
        
        // 输出环境信息 - 增加脚本路径信息用于调试
        config.log('环境检测完成', {
            environment: config.getEnvDescription(),
            baseUrl: config.baseUrl,
            scriptPath: getScriptPath(),
            hostname: env.hostname,
            port: env.port,
            isLocal: env.isLocal,
            currentPath: window.location.pathname
        });
        
        return config;
    }
    
    // 创建全局配置对象
    const ENV_CONFIG = initEnvConfig();
    
    // 导出到全局作用域
    if (typeof module !== 'undefined' && module.exports) {
        // Node.js环境
        module.exports = ENV_CONFIG;
    } else {
        // 浏览器环境
        global.ENV_CONFIG = ENV_CONFIG;
        
        // 兼容性：也提供一些常用的全局变量
        global.baseUrl = ENV_CONFIG.baseUrl;
        global.isLocalEnv = ENV_CONFIG.isLocal;
        
        // 触发配置就绪事件
        if (typeof document !== 'undefined') {
            document.addEventListener('DOMContentLoaded', function() {
                const event = new CustomEvent('envConfigReady', {
                    detail: ENV_CONFIG
                });
                document.dispatchEvent(event);
            });
        }
    }
    
})(typeof window !== 'undefined' ? window : global);