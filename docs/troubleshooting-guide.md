# 问卷数据管理系统 - 故障排除指南

## 目录
1. [常见问题诊断](#常见问题诊断)
2. [登录相关问题](#登录相关问题)
3. [数据提交问题](#数据提交问题)
4. [系统性能问题](#系统性能问题)
5. [数据库问题](#数据库问题)
6. [导出功能问题](#导出功能问题)
7. [网络连接问题](#网络连接问题)
8. [浏览器兼容性问题](#浏览器兼容性问题)
9. [系统维护](#系统维护)
10. [错误日志分析](#错误日志分析)

## 常见问题诊断

### 问题诊断流程
1. **确认问题现象**: 详细记录错误信息和操作步骤
2. **检查系统状态**: 确认服务是否正常运行
3. **查看错误日志**: 分析系统日志获取详细信息
4. **尝试基础解决方案**: 重启服务、清除缓存等
5. **深入分析**: 检查配置文件、数据库状态等
6. **联系技术支持**: 如果问题仍未解决

### 快速诊断命令
```bash
# 检查服务状态
ps aux | grep python
netstat -tlnp | grep 5000

# 检查日志
tail -f logs/error.log
tail -f logs/access.log

# 检查磁盘空间
df -h

# 检查内存使用
free -h
```

## 登录相关问题

### 问题1: 无法登录系统

**症状**: 输入正确的用户名和密码后仍然无法登录

**可能原因**:
- 会话配置问题
- 数据库连接失败
- 密码哈希验证错误
- Cookie 被禁用

**解决方案**:

1. **检查用户账户**:
```python
# 在 Python 控制台中执行
import sqlite3
conn = sqlite3.connect('backend/questionnaires.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM users WHERE username = 'admin'")
result = cursor.fetchone()
print(result)
```

2. **重置管理员密码**:
```python
import bcrypt
import sqlite3

# 生成新密码哈希
new_password = "admin123"
password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

# 更新数据库
conn = sqlite3.connect('backend/questionnaires.db')
cursor = conn.cursor()
cursor.execute("UPDATE users SET password_hash = ? WHERE username = 'admin'", 
               (password_hash.decode('utf-8'),))
conn.commit()
conn.close()
```

3. **检查会话配置**:
```python
# 在 app.py 中确认会话配置
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SESSION_TYPE'] = 'filesystem'
```

### 问题2: 登录后立即退出

**症状**: 登录成功后页面自动跳转到登录页面

**可能原因**:
- 会话存储问题
- 时区设置错误
- 浏览器 Cookie 设置问题

**解决方案**:

1. **清除浏览器缓存和 Cookie**
2. **检查会话目录权限**:
```bash
ls -la flask_session/
chmod 755 flask_session/
```

3. **检查系统时间**:
```bash
date
# 如果时间不正确，同步时间
ntpdate -s time.nist.gov
```

### 问题3: 会话超时过快

**症状**: 短时间内会话就过期，需要重新登录

**解决方案**:
```python
# 在 app.py 中调整会话超时时间
from datetime import timedelta
app.permanent_session_lifetime = timedelta(hours=8)  # 8小时超时
```

## 数据提交问题

### 问题1: 问卷提交失败

**症状**: 点击提交按钮后显示错误信息或无响应

**诊断步骤**:

1. **检查浏览器控制台**:
   - 按 F12 打开开发者工具
   - 查看 Console 标签页的错误信息
   - 查看 Network 标签页的请求状态

2. **检查数据格式**:
```javascript
// 在浏览器控制台中验证数据格式
console.log(JSON.stringify(questionnaireData, null, 2));
```

3. **检查后端日志**:
```bash
tail -f logs/error.log
```

**常见解决方案**:

1. **数据验证错误**:
```javascript
// 确保必填字段不为空
if (!data.basic_info.name.trim()) {
    alert("姓名不能为空");
    return;
}
```

2. **网络请求超时**:
```javascript
// 增加请求超时时间
fetch('/api/questionnaires', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data),
    timeout: 30000  // 30秒超时
})
```

### 问题2: 数据保存不完整

**症状**: 部分问题的答案没有保存

**解决方案**:

1. **检查数据结构**:
```javascript
// 验证所有问题都有答案
data.questions.forEach((question, index) => {
    if (question.type === 'multiple_choice' && !question.selected) {
        console.error(`第${index + 1}题未选择答案`);
    }
    if (question.type === 'text_input' && !question.answer) {
        console.error(`第${index + 1}题答案为空`);
    }
});
```

2. **增加数据完整性检查**:
```python
# 在后端添加更严格的验证
def validate_questionnaire_data(data):
    errors = []
    
    if not data.get('basic_info', {}).get('name'):
        errors.append("姓名不能为空")
    
    questions = data.get('questions', [])
    for i, question in enumerate(questions):
        if question.get('type') == 'multiple_choice':
            if not question.get('selected'):
                errors.append(f"第{i+1}题未选择答案")
        elif question.get('type') == 'text_input':
            if not question.get('answer', '').strip():
                errors.append(f"第{i+1}题答案不能为空")
    
    return errors
```

## 系统性能问题

### 问题1: 系统响应缓慢

**症状**: 页面加载时间过长，操作响应延迟

**诊断步骤**:

1. **检查系统资源使用**:
```bash
# CPU 使用率
top -p $(pgrep -f "python.*app.py")

# 内存使用
ps aux | grep python | awk '{print $6}' | awk '{sum+=$1} END {print sum/1024 "MB"}'

# 磁盘 I/O
iostat -x 1 5
```

2. **检查数据库性能**:
```python
import sqlite3
import time

conn = sqlite3.connect('backend/questionnaires.db')
cursor = conn.cursor()

# 测试查询性能
start_time = time.time()
cursor.execute("SELECT COUNT(*) FROM questionnaires")
result = cursor.fetchone()
end_time = time.time()

print(f"查询耗时: {end_time - start_time:.2f}秒")
print(f"记录数量: {result[0]}")
```

**解决方案**:

1. **优化数据库查询**:
```sql
-- 添加索引
CREATE INDEX idx_questionnaires_created_at ON questionnaires(created_at);
CREATE INDEX idx_questionnaires_type ON questionnaires(type);
CREATE INDEX idx_questionnaires_name ON questionnaires(name);
```

2. **实现分页查询**:
```python
def get_questionnaires_paginated(page=1, per_page=20):
    offset = (page - 1) * per_page
    cursor.execute("""
        SELECT * FROM questionnaires 
        ORDER BY created_at DESC 
        LIMIT ? OFFSET ?
    """, (per_page, offset))
    return cursor.fetchall()
```

3. **启用缓存**:
```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@cache.cached(timeout=300)  # 缓存5分钟
def get_statistics():
    # 统计数据查询
    pass
```

### 问题2: 内存使用过高

**症状**: 系统内存占用持续增长，可能导致系统崩溃

**解决方案**:

1. **检查内存泄漏**:
```python
import gc
import psutil
import os

def check_memory_usage():
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    print(f"内存使用: {memory_info.rss / 1024 / 1024:.2f} MB")
    print(f"对象数量: {len(gc.get_objects())}")
```

2. **优化数据处理**:
```python
# 避免一次性加载大量数据
def process_large_dataset():
    cursor.execute("SELECT COUNT(*) FROM questionnaires")
    total_count = cursor.fetchone()[0]
    
    batch_size = 1000
    for offset in range(0, total_count, batch_size):
        cursor.execute("""
            SELECT * FROM questionnaires 
            LIMIT ? OFFSET ?
        """, (batch_size, offset))
        
        batch_data = cursor.fetchall()
        # 处理批次数据
        process_batch(batch_data)
        
        # 清理内存
        del batch_data
        gc.collect()
```

## 数据库问题

### 问题1: 数据库连接失败

**症状**: 系统启动时报数据库连接错误

**诊断步骤**:
```bash
# 检查数据库文件是否存在
ls -la backend/questionnaires.db

# 检查文件权限
ls -la backend/questionnaires.db

# 检查数据库完整性
sqlite3 backend/questionnaires.db "PRAGMA integrity_check;"
```

**解决方案**:

1. **重新初始化数据库**:
```bash
cd backend
python init_db.py
```

2. **修复权限问题**:
```bash
chmod 664 backend/questionnaires.db
chown www-data:www-data backend/questionnaires.db
```

### 问题2: 数据库锁定

**症状**: 操作时出现 "database is locked" 错误

**解决方案**:

1. **检查锁定进程**:
```bash
lsof backend/questionnaires.db
```

2. **强制解锁**:
```python
import sqlite3

# 使用 WAL 模式避免锁定
conn = sqlite3.connect('backend/questionnaires.db')
conn.execute('PRAGMA journal_mode=WAL;')
conn.close()
```

3. **实现连接池**:
```python
import sqlite3
from contextlib import contextmanager

@contextmanager
def get_db_connection():
    conn = None
    try:
        conn = sqlite3.connect('backend/questionnaires.db', timeout=30)
        conn.row_factory = sqlite3.Row
        yield conn
    finally:
        if conn:
            conn.close()
```

## 导出功能问题

### 问题1: 导出文件生成失败

**症状**: 点击导出按钮后没有生成文件或下载失败

**诊断步骤**:

1. **检查导出目录权限**:
```bash
ls -la backend/static/exports/
mkdir -p backend/static/exports/
chmod 755 backend/static/exports/
```

2. **检查依赖库**:
```bash
pip list | grep -E "(pandas|openpyxl|reportlab)"
```

**解决方案**:

1. **安装缺失的依赖**:
```bash
pip install pandas openpyxl reportlab
```

2. **检查导出逻辑**:
```python
import os
import pandas as pd

def export_to_excel(data, filename):
    try:
        # 确保导出目录存在
        export_dir = 'backend/static/exports'
        os.makedirs(export_dir, exist_ok=True)
        
        # 生成文件路径
        filepath = os.path.join(export_dir, filename)
        
        # 导出数据
        df = pd.DataFrame(data)
        df.to_excel(filepath, index=False)
        
        return filepath
    except Exception as e:
        print(f"导出失败: {e}")
        return None
```

### 问题2: 导出文件格式错误

**症状**: 导出的文件无法正常打开或格式不正确

**解决方案**:

1. **CSV 格式问题**:
```python
import csv
import io

def export_to_csv(data):
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_ALL)
    
    # 写入 BOM 以支持中文
    output.write('\ufeff')
    
    # 写入表头
    if data:
        writer.writerow(data[0].keys())
        
        # 写入数据
        for row in data:
            writer.writerow(row.values())
    
    return output.getvalue()
```

2. **Excel 格式问题**:
```python
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

def export_to_excel_advanced(data, filename):
    wb = Workbook()
    ws = wb.active
    ws.title = "问卷数据"
    
    # 设置表头样式
    header_font = Font(bold=True)
    center_alignment = Alignment(horizontal='center')
    
    if data:
        # 写入表头
        headers = list(data[0].keys())
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = header_font
            cell.alignment = center_alignment
        
        # 写入数据
        for row_idx, row_data in enumerate(data, 2):
            for col_idx, value in enumerate(row_data.values(), 1):
                ws.cell(row=row_idx, column=col_idx, value=value)
    
    wb.save(filename)
```

## 网络连接问题

### 问题1: API 请求失败

**症状**: 前端无法连接到后端 API

**诊断步骤**:

1. **检查服务状态**:
```bash
curl -I http://localhost:5000/api/auth/status
```

2. **检查防火墙设置**:
```bash
# Ubuntu/Debian
ufw status
ufw allow 5000

# CentOS/RHEL
firewall-cmd --list-ports
firewall-cmd --add-port=5000/tcp --permanent
```

3. **检查端口占用**:
```bash
netstat -tlnp | grep 5000
lsof -i :5000
```

**解决方案**:

1. **配置 CORS**:
```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000'])
```

2. **检查网络配置**:
```python
# 确保服务监听所有接口
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

### 问题2: 请求超时

**症状**: 请求发送后长时间无响应，最终超时

**解决方案**:

1. **增加超时时间**:
```javascript
// 前端请求超时设置
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), 30000);

fetch('/api/questionnaires', {
    method: 'POST',
    signal: controller.signal,
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
}).finally(() => {
    clearTimeout(timeoutId);
});
```

2. **优化后端处理**:
```python
from flask import request
import threading

def process_large_request():
    # 异步处理大量数据
    def background_task():
        # 处理逻辑
        pass
    
    thread = threading.Thread(target=background_task)
    thread.start()
    
    return {"status": "processing", "message": "请求正在处理中"}
```

## 浏览器兼容性问题

### 问题1: 旧版浏览器不支持

**症状**: 在旧版本浏览器中功能异常或页面显示错误

**解决方案**:

1. **添加 Polyfill**:
```html
<!-- 在 HTML 头部添加 -->
<script src="https://polyfill.io/v3/polyfill.min.js?features=fetch,Promise,Array.from"></script>
```

2. **兼容性检查**:
```javascript
// 检查浏览器支持
function checkBrowserSupport() {
    const features = {
        fetch: typeof fetch !== 'undefined',
        promise: typeof Promise !== 'undefined',
        localStorage: typeof Storage !== 'undefined'
    };
    
    const unsupported = Object.keys(features).filter(key => !features[key]);
    
    if (unsupported.length > 0) {
        alert(`您的浏览器不支持以下功能: ${unsupported.join(', ')}\n请升级浏览器或使用现代浏览器。`);
        return false;
    }
    
    return true;
}
```

### 问题2: 移动端显示问题

**症状**: 在移动设备上页面布局错乱或功能不可用

**解决方案**:

1. **响应式设计**:
```css
/* 移动端适配 */
@media (max-width: 768px) {
    .questionnaire-table {
        font-size: 14px;
    }
    
    .form-group input {
        width: 100%;
        box-sizing: border-box;
    }
    
    .btn {
        padding: 12px 20px;
        font-size: 16px;
    }
}
```

2. **触摸事件支持**:
```javascript
// 支持触摸设备
function addTouchSupport() {
    if ('ontouchstart' in window) {
        document.addEventListener('touchstart', function() {}, {passive: true});
    }
}
```

## 系统维护

### 定期维护任务

1. **清理过期日志**:
```bash
#!/bin/bash
# cleanup_logs.sh

# 删除30天前的日志文件
find logs/ -name "*.log" -mtime +30 -delete

# 压缩7天前的日志文件
find logs/ -name "*.log" -mtime +7 -exec gzip {} \;
```

2. **数据库优化**:
```python
import sqlite3

def optimize_database():
    conn = sqlite3.connect('backend/questionnaires.db')
    
    # 分析表结构
    conn.execute('ANALYZE')
    
    # 清理碎片
    conn.execute('VACUUM')
    
    # 重建索引
    conn.execute('REINDEX')
    
    conn.close()
    print("数据库优化完成")
```

3. **备份数据**:
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups"
DB_FILE="backend/questionnaires.db"

mkdir -p $BACKUP_DIR

# 备份数据库
cp $DB_FILE "$BACKUP_DIR/questionnaires_$DATE.db"

# 压缩备份文件
gzip "$BACKUP_DIR/questionnaires_$DATE.db"

# 删除30天前的备份
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "备份完成: questionnaires_$DATE.db.gz"
```

### 监控脚本

```bash
#!/bin/bash
# monitor.sh

# 检查服务状态
if ! pgrep -f "python.*app.py" > /dev/null; then
    echo "$(date): 服务未运行，正在重启..." >> logs/monitor.log
    cd backend && python app.py &
fi

# 检查磁盘空间
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "$(date): 磁盘使用率过高: ${DISK_USAGE}%" >> logs/monitor.log
fi

# 检查内存使用
MEMORY_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ $MEMORY_USAGE -gt 80 ]; then
    echo "$(date): 内存使用率过高: ${MEMORY_USAGE}%" >> logs/monitor.log
fi
```

## 错误日志分析

### 常见错误模式

1. **数据库错误**:
```
ERROR: database is locked
ERROR: no such table: questionnaires
ERROR: UNIQUE constraint failed
```

2. **认证错误**:
```
ERROR: Invalid username or password
ERROR: Session expired
ERROR: Unauthorized access
```

3. **数据验证错误**:
```
ERROR: Validation failed for field 'name'
ERROR: Missing required field 'questions'
ERROR: Invalid question type
```

### 日志分析工具

```python
import re
from collections import Counter
from datetime import datetime

def analyze_error_log(log_file):
    """分析错误日志"""
    error_patterns = {
        'database': r'database.*error|sqlite.*error',
        'validation': r'validation.*failed|invalid.*field',
        'authentication': r'unauthorized|login.*failed|session.*expired',
        'network': r'connection.*refused|timeout|network.*error'
    }
    
    error_counts = Counter()
    
    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            for error_type, pattern in error_patterns.items():
                if re.search(pattern, line, re.IGNORECASE):
                    error_counts[error_type] += 1
                    break
    
    print("错误统计:")
    for error_type, count in error_counts.most_common():
        print(f"  {error_type}: {count}")
    
    return error_counts

# 使用示例
analyze_error_log('logs/error.log')
```

## 联系技术支持

如果以上解决方案都无法解决问题，请联系技术支持团队：

**联系方式**:
- 邮箱: support@questionnaire-system.com
- 电话: 400-123-4567
- 在线支持: 工作日 9:00-18:00

**提供信息**:
1. 详细的错误描述和重现步骤
2. 错误截图或日志文件
3. 系统环境信息（操作系统、浏览器版本等）
4. 最近的系统变更记录

---

*本指南最后更新时间: 2024年1月15日*