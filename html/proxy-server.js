const http = require('http');
const https = require('https');
const url = require('url');

// 动态检测环境并设置目标URL
function getTargetBaseUrl() {
    // 在Node.js环境中，我们可以通过环境变量或其他方式来判断
    // 这里假设如果有PORT环境变量且为开发端口，则为本地环境
    const isDevelopment = process.env.NODE_ENV === 'development' || process.env.PORT === '5000';
    
    if (isDevelopment) {
        // 本地开发环境
        return 'http://localhost:5000';
    } else {
        // 生产环境 - 使用115.190.103.114 + 动态端口
        const targetPort = process.env.TARGET_PORT || '5000';
        return 'http://115.190.103.114:' + targetPort;
    }
}

const TARGET_BASE_URL = getTargetBaseUrl();
console.log('Proxy server target URL:', TARGET_BASE_URL);

// 创建代理服务器
const server = http.createServer((req, res) => {
    // 设置CORS头
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    
    // 处理预检请求
    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }
    
    // 解析目标URL
    const targetUrl = TARGET_BASE_URL + req.url;
    const parsedUrl = url.parse(targetUrl);
    
    const options = {
        hostname: parsedUrl.hostname,
        port: parsedUrl.port,
        path: parsedUrl.path,
        method: req.method,
        headers: {
            'Accept': 'application/json',
        }
    };
    
    const proxyReq = http.request(options, (proxyRes) => {
        // 转发响应头
        Object.keys(proxyRes.headers).forEach(key => {
            res.setHeader(key, proxyRes.headers[key]);
        });
        
        // 设置CORS头
        res.setHeader('Access-Control-Allow-Origin', '*');
        
        res.writeHead(proxyRes.statusCode);
        proxyRes.pipe(res);
    });
    
    proxyReq.on('error', (err) => {
        console.error('代理请求错误:', err);
        res.writeHead(500, { 'Content-Type': 'text/plain' });
        res.end('代理服务器错误: ' + err.message);
    });
    
    req.pipe(proxyReq);
});

const PORT = 5001;
server.listen(PORT, () => {
    console.log(`CORS代理服务器运行在 http://localhost:${PORT}`);
    console.log('代理目标:', TARGET_BASE_URL);
});