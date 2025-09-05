# 问卷数据管理系统 - 系统操作指南

## 目录
1. [系统安装部署](#系统安装部署)
2. [日常操作流程](#日常操作流程)
3. [数据管理操作](#数据管理操作)
4. [系统配置管理](#系统配置管理)
5. [备份与恢复](#备份与恢复)
6. [性能优化](#性能优化)
7. [安全管理](#安全管理)
8. [监控与维护](#监控与维护)

## 系统安装部署

### 环境要求
- **操作系统**: Linux (Ubuntu 18.04+) / Windows 10+ / macOS 10.14+
- **Python**: 3.8 或更高版本
- **内存**: 最低 2GB，推荐 4GB+
- **存储**: 最低 10GB 可用空间
- **网络**: 支持 HTTP/HTTPS 访问

### 安装步骤

#### 1. 下载源代码
```bash
git clone https://github.com/your-org/questionnaire-system.git
cd questionnaire-system
```

#### 2. 创建虚拟环境
```bash
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

#### 3. 安装依赖
```bash
pip install -r backend/requirements.txt
```

#### 4. 初始化数据库
```bash
cd backend
python init_db.py
```

#### 5. 创建管理员账户
```bash
python create_admin.py
```

#### 6. 启动服务
```bash
# 开发环境
python app.py

# 生产环境
gunicorn -c gunicorn.conf.py wsgi:app
```

### 配置文件说明

#### config.py (开发环境配置)
```python
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    DATABASE_URL = 'sqlite:///questionnaires.db'
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = 7200  # 2小时
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'static/uploads'
    
    # 导出配置
    EXPORT_FOLDER = 'static/exports'
    EXPORT_FORMATS = ['csv', 'excel', 'pdf']
    
    # 日志配置
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'logs/app.log'
```

#### config_production.py (生产环境配置)
```python
import os

class ProductionConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///questionnaires.db'
    
    # 安全配置
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # 性能配置
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1年
    
    # 日志配置
    LOG_LEVEL = 'WARNING'
    LOG_FILE = '/var/log/questionnaire-system/app.log'
```

## 日常操作流程

### 系统启动流程

1. **检查系统环境**
```bash
# 检查 Python 版本
python --version

# 检查虚拟环境
which python

# 检查依赖包
pip list
```

2. **启动数据库检查**
```bash
# 检查数据库文件
ls -la backend/questionnaires.db

# 测试数据库连接
python -c "import sqlite3; conn = sqlite3.connect('backend/questionnaires.db'); print('数据库连接正常'); conn.close()"
```

3. **启动 Web 服务**
```bash
cd backend

# 开发环境
python app.py

# 生产环境
gunicorn -c gunicorn.conf.py wsgi:app
```

4. **验证服务状态**
```bash
# 检查端口监听
netstat -tlnp | grep 5000

# 测试 HTTP 响应
curl -I http://localhost:5000
```

### 系统关闭流程

1. **优雅关闭服务**
```bash
# 发送 SIGTERM 信号
kill -TERM $(pgrep -f "gunicorn.*wsgi:app")

# 等待进程结束
sleep 5

# 强制关闭（如果需要）
kill -KILL $(pgrep -f "gunicorn.*wsgi:app")
```

2. **数据完整性检查**
```bash
# 检查数据库完整性
sqlite3 backend/questionnaires.db "PRAGMA integrity_check;"

# 检查日志文件
tail -n 50 logs/app.log
```

## 数据管理操作

### 问卷数据导入

#### 批量导入 CSV 数据
```python
import csv
import json
import sqlite3
from datetime import datetime

def import_csv_data(csv_file):
    """从 CSV 文件导入问卷数据"""
    conn = sqlite3.connect('questionnaires.db')
    cursor = conn.cursor()
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            # 构造问卷数据结构
            questionnaire_data = {
                'type': row.get('type', 'imported'),
                'basic_info': {
                    'name': row['name'],
                    'grade': row['grade'],
                    'submission_date': row['submission_date']
                },
                'questions': json.loads(row['questions_json']),
                'statistics': json.loads(row.get('statistics_json', '{}'))
            }
            
            # 插入数据库
            cursor.execute("""
                INSERT INTO questionnaires (type, name, grade, submission_date, data, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                questionnaire_data['type'],
                questionnaire_data['basic_info']['name'],
                questionnaire_data['basic_info']['grade'],
                questionnaire_data['basic_info']['submission_date'],
                json.dumps(questionnaire_data, ensure_ascii=False),
                datetime.now()
            ))
    
    conn.commit()
    conn.close()
    print(f"成功导入 {reader.line_num - 1} 条记录")

# 使用示例
import_csv_data('import_data.csv')
```

#### 数据格式转换
```python
def convert_old_format_to_new(old_data):
    """将旧格式数据转换为新格式"""
    new_format = {
        'type': old_data.get('questionnaire_type', 'unknown'),
        'basic_info': {
            'name': old_data.get('student_name', ''),
            'grade': old_data.get('grade', ''),
            'submission_date': old_data.get('date', '')
        },
        'questions': [],
        'statistics': {
            'total_score': old_data.get('total_score', 0),
            'completion_rate': 100
        }
    }
    
    # 转换问题格式
    for i, answer in enumerate(old_data.get('answers', [])):
        question = {
            'id': i + 1,
            'type': 'multiple_choice' if isinstance(answer, list) else 'text_input',
            'question': f"问题 {i + 1}",
            'answer': answer
        }
        new_format['questions'].append(question)
    
    return new_format
```

### 数据清理和维护

#### 清理重复数据
```python
def remove_duplicate_questionnaires():
    """清理重复的问卷数据"""
    conn = sqlite3.connect('questionnaires.db')
    cursor = conn.cursor()
    
    # 查找重复数据
    cursor.execute("""
        SELECT name, grade, submission_date, COUNT(*) as count
        FROM questionnaires
        GROUP BY name, grade, submission_date
        HAVING COUNT(*) > 1
    """)
    
    duplicates = cursor.fetchall()
    
    for name, grade, date, count in duplicates:
        print(f"发现重复数据: {name}, {grade}, {date} ({count} 条)")
        
        # 保留最新的记录，删除其他的
        cursor.execute("""
            DELETE FROM questionnaires
            WHERE name = ? AND grade = ? AND submission_date = ?
            AND id NOT IN (
                SELECT MAX(id) FROM questionnaires
                WHERE name = ? AND grade = ? AND submission_date = ?
            )
        """, (name, grade, date, name, grade, date))
    
    conn.commit()
    conn.close()
    print("重复数据清理完成")
```

#### 数据完整性检查
```python
def check_data_integrity():
    """检查数据完整性"""
    conn = sqlite3.connect('questionnaires.db')
    cursor = conn.cursor()
    
    issues = []
    
    # 检查必填字段
    cursor.execute("SELECT id FROM questionnaires WHERE name IS NULL OR name = ''")
    empty_names = cursor.fetchall()
    if empty_names:
        issues.append(f"发现 {len(empty_names)} 条记录缺少姓名")
    
    # 检查数据格式
    cursor.execute("SELECT id, data FROM questionnaires")
    for record_id, data_json in cursor.fetchall():
        try:
            data = json.loads(data_json)
            if not isinstance(data.get('questions'), list):
                issues.append(f"记录 {record_id} 的问题数据格式错误")
        except json.JSONDecodeError:
            issues.append(f"记录 {record_id} 的 JSON 数据格式错误")
    
    conn.close()
    
    if issues:
        print("数据完整性检查发现问题:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("数据完整性检查通过")
    
    return issues
```

### 数据统计分析

#### 生成统计报告
```python
def generate_statistics_report():
    """生成统计报告"""
    conn = sqlite3.connect('questionnaires.db')
    cursor = conn.cursor()
    
    report = {
        'summary': {},
        'type_distribution': {},
        'grade_distribution': {},
        'monthly_trend': {}
    }
    
    # 总体统计
    cursor.execute("SELECT COUNT(*) FROM questionnaires")
    report['summary']['total_count'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT name) FROM questionnaires")
    report['summary']['unique_students'] = cursor.fetchone()[0]
    
    # 按类型统计
    cursor.execute("""
        SELECT type, COUNT(*) as count
        FROM questionnaires
        GROUP BY type
        ORDER BY count DESC
    """)
    report['type_distribution'] = dict(cursor.fetchall())
    
    # 按年级统计
    cursor.execute("""
        SELECT grade, COUNT(*) as count
        FROM questionnaires
        GROUP BY grade
        ORDER BY count DESC
    """)
    report['grade_distribution'] = dict(cursor.fetchall())
    
    # 按月份统计
    cursor.execute("""
        SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as count
        FROM questionnaires
        GROUP BY month
        ORDER BY month
    """)
    report['monthly_trend'] = dict(cursor.fetchall())
    
    conn.close()
    
    # 输出报告
    print("=== 问卷数据统计报告 ===")
    print(f"总问卷数: {report['summary']['total_count']}")
    print(f"独立学生数: {report['summary']['unique_students']}")
    
    print("\n问卷类型分布:")
    for qtype, count in report['type_distribution'].items():
        print(f"  {qtype}: {count}")
    
    print("\n年级分布:")
    for grade, count in report['grade_distribution'].items():
        print(f"  {grade}: {count}")
    
    return report
```

## 系统配置管理

### 用户管理

#### 创建新用户
```python
import bcrypt
import sqlite3

def create_user(username, password, role='admin'):
    """创建新用户"""
    conn = sqlite3.connect('questionnaires.db')
    cursor = conn.cursor()
    
    # 检查用户是否已存在
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        print(f"用户 {username} 已存在")
        return False
    
    # 生成密码哈希
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    # 插入新用户
    cursor.execute("""
        INSERT INTO users (username, password_hash, role, created_at)
        VALUES (?, ?, ?, ?)
    """, (username, password_hash.decode('utf-8'), role, datetime.now()))
    
    conn.commit()
    conn.close()
    
    print(f"用户 {username} 创建成功")
    return True

# 使用示例
create_user('admin2', 'secure_password123', 'admin')
```

#### 重置用户密码
```python
def reset_user_password(username, new_password):
    """重置用户密码"""
    conn = sqlite3.connect('questionnaires.db')
    cursor = conn.cursor()
    
    # 生成新密码哈希
    password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    
    # 更新密码
    cursor.execute("""
        UPDATE users SET password_hash = ?, updated_at = ?
        WHERE username = ?
    """, (password_hash.decode('utf-8'), datetime.now(), username))
    
    if cursor.rowcount > 0:
        conn.commit()
        print(f"用户 {username} 密码重置成功")
        result = True
    else:
        print(f"用户 {username} 不存在")
        result = False
    
    conn.close()
    return result
```

### 系统参数配置

#### 配置管理脚本
```python
import json

class ConfigManager:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.get_default_config()
    
    def save_config(self):
        """保存配置文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def get_default_config(self):
        """获取默认配置"""
        return {
            'system': {
                'session_timeout': 7200,
                'max_file_size': 16777216,
                'allowed_file_types': ['.csv', '.xlsx', '.json']
            },
            'database': {
                'backup_interval': 86400,
                'cleanup_interval': 604800,
                'max_records': 100000
            },
            'export': {
                'max_records_per_export': 10000,
                'export_formats': ['csv', 'excel', 'pdf'],
                'export_timeout': 300
            }
        }
    
    def get(self, key, default=None):
        """获取配置值"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key, value):
        """设置配置值"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save_config()

# 使用示例
config = ConfigManager()
config.set('system.session_timeout', 3600)  # 设置会话超时为1小时
timeout = config.get('system.session_timeout', 7200)  # 获取会话超时设置
```

## 备份与恢复

### 自动备份脚本

```bash
#!/bin/bash
# auto_backup.sh

# 配置参数
BACKUP_DIR="/var/backups/questionnaire-system"
DB_FILE="/path/to/questionnaires.db"
STATIC_DIR="/path/to/static"
RETENTION_DAYS=30

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 生成时间戳
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 备份数据库
echo "开始备份数据库..."
sqlite3 "$DB_FILE" ".backup $BACKUP_DIR/questionnaires_$TIMESTAMP.db"

# 备份静态文件
echo "开始备份静态文件..."
tar -czf "$BACKUP_DIR/static_$TIMESTAMP.tar.gz" -C "$(dirname $STATIC_DIR)" "$(basename $STATIC_DIR)"

# 备份配置文件
echo "开始备份配置文件..."
tar -czf "$BACKUP_DIR/config_$TIMESTAMP.tar.gz" config.py config_production.py

# 创建备份清单
echo "创建备份清单..."
cat > "$BACKUP_DIR/backup_$TIMESTAMP.txt" << EOF
备份时间: $(date)
数据库文件: questionnaires_$TIMESTAMP.db
静态文件: static_$TIMESTAMP.tar.gz
配置文件: config_$TIMESTAMP.tar.gz
备份大小: $(du -sh $BACKUP_DIR/*$TIMESTAMP* | awk '{sum+=$1} END {print sum}')
EOF

# 清理过期备份
echo "清理过期备份..."
find "$BACKUP_DIR" -name "*_*.db" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*_*.tar.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*_*.txt" -mtime +$RETENTION_DAYS -delete

echo "备份完成: $TIMESTAMP"
```

### 数据恢复脚本

```bash
#!/bin/bash
# restore_backup.sh

if [ $# -ne 1 ]; then
    echo "使用方法: $0 <备份时间戳>"
    echo "示例: $0 20240115_143022"
    exit 1
fi

TIMESTAMP=$1
BACKUP_DIR="/var/backups/questionnaire-system"
RESTORE_DIR="/tmp/restore_$TIMESTAMP"

# 检查备份文件是否存在
if [ ! -f "$BACKUP_DIR/questionnaires_$TIMESTAMP.db" ]; then
    echo "错误: 备份文件不存在"
    exit 1
fi

# 创建恢复目录
mkdir -p "$RESTORE_DIR"

echo "开始恢复数据..."

# 停止服务
echo "停止服务..."
systemctl stop questionnaire-system

# 备份当前数据
echo "备份当前数据..."
cp questionnaires.db "questionnaires_backup_$(date +%Y%m%d_%H%M%S).db"

# 恢复数据库
echo "恢复数据库..."
cp "$BACKUP_DIR/questionnaires_$TIMESTAMP.db" questionnaires.db

# 恢复静态文件
if [ -f "$BACKUP_DIR/static_$TIMESTAMP.tar.gz" ]; then
    echo "恢复静态文件..."
    tar -xzf "$BACKUP_DIR/static_$TIMESTAMP.tar.gz" -C "$RESTORE_DIR"
    cp -r "$RESTORE_DIR/static"/* static/
fi

# 恢复配置文件
if [ -f "$BACKUP_DIR/config_$TIMESTAMP.tar.gz" ]; then
    echo "恢复配置文件..."
    tar -xzf "$BACKUP_DIR/config_$TIMESTAMP.tar.gz" -C "$RESTORE_DIR"
    # 注意: 配置文件恢复需要谨慎，可能需要手动检查
    echo "配置文件已解压到 $RESTORE_DIR，请手动检查后复制"
fi

# 验证数据完整性
echo "验证数据完整性..."
sqlite3 questionnaires.db "PRAGMA integrity_check;"

# 启动服务
echo "启动服务..."
systemctl start questionnaire-system

# 清理临时文件
rm -rf "$RESTORE_DIR"

echo "数据恢复完成"
```

## 性能优化

### 数据库优化

#### 索引优化
```sql
-- 创建常用查询的索引
CREATE INDEX IF NOT EXISTS idx_questionnaires_created_at ON questionnaires(created_at);
CREATE INDEX IF NOT EXISTS idx_questionnaires_type ON questionnaires(type);
CREATE INDEX IF NOT EXISTS idx_questionnaires_name ON questionnaires(name);
CREATE INDEX IF NOT EXISTS idx_questionnaires_grade ON questionnaires(grade);
CREATE INDEX IF NOT EXISTS idx_questionnaires_submission_date ON questionnaires(submission_date);

-- 复合索引
CREATE INDEX IF NOT EXISTS idx_questionnaires_type_date ON questionnaires(type, created_at);
CREATE INDEX IF NOT EXISTS idx_questionnaires_name_grade ON questionnaires(name, grade);

-- 操作日志索引
CREATE INDEX IF NOT EXISTS idx_operation_logs_user_id ON operation_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_operation_logs_created_at ON operation_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_operation_logs_operation ON operation_logs(operation);
```

#### 查询优化
```python
def get_questionnaires_optimized(page=1, per_page=20, filters=None):
    """优化的问卷查询函数"""
    conn = sqlite3.connect('questionnaires.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 构建查询条件
    where_conditions = []
    params = []
    
    if filters:
        if filters.get('name'):
            where_conditions.append("name LIKE ?")
            params.append(f"%{filters['name']}%")
        
        if filters.get('type'):
            where_conditions.append("type = ?")
            params.append(filters['type'])
        
        if filters.get('start_date'):
            where_conditions.append("submission_date >= ?")
            params.append(filters['start_date'])
        
        if filters.get('end_date'):
            where_conditions.append("submission_date <= ?")
            params.append(filters['end_date'])
    
    where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
    
    # 计算总数（使用索引）
    count_query = f"SELECT COUNT(*) FROM questionnaires WHERE {where_clause}"
    cursor.execute(count_query, params)
    total_count = cursor.fetchone()[0]
    
    # 分页查询（只查询必要字段）
    offset = (page - 1) * per_page
    query = f"""
        SELECT id, type, name, grade, submission_date, created_at
        FROM questionnaires
        WHERE {where_clause}
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    """
    
    cursor.execute(query, params + [per_page, offset])
    questionnaires = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        'questionnaires': questionnaires,
        'total_count': total_count,
        'page': page,
        'per_page': per_page,
        'total_pages': (total_count + per_page - 1) // per_page
    }
```

### 缓存策略

```python
from functools import wraps
import time
import json

class SimpleCache:
    def __init__(self):
        self.cache = {}
        self.timestamps = {}
    
    def get(self, key):
        if key in self.cache:
            return self.cache[key]
        return None
    
    def set(self, key, value, ttl=300):
        self.cache[key] = value
        self.timestamps[key] = time.time() + ttl
    
    def is_expired(self, key):
        if key not in self.timestamps:
            return True
        return time.time() > self.timestamps[key]
    
    def clear_expired(self):
        expired_keys = [k for k in self.timestamps if self.is_expired(k)]
        for key in expired_keys:
            self.cache.pop(key, None)
            self.timestamps.pop(key, None)

cache = SimpleCache()

def cached(ttl=300):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # 检查缓存
            if not cache.is_expired(cache_key):
                cached_result = cache.get(cache_key)
                if cached_result is not None:
                    return cached_result
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

# 使用示例
@cached(ttl=600)  # 缓存10分钟
def get_statistics():
    """获取统计数据（缓存版本）"""
    conn = sqlite3.connect('questionnaires.db')
    cursor = conn.cursor()
    
    # 执行统计查询
    stats = {}
    
    cursor.execute("SELECT COUNT(*) FROM questionnaires")
    stats['total_count'] = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT type, COUNT(*) as count
        FROM questionnaires
        GROUP BY type
    """)
    stats['type_distribution'] = dict(cursor.fetchall())
    
    conn.close()
    return stats
```

## 安全管理

### 安全配置检查

```python
def security_audit():
    """安全配置审计"""
    issues = []
    
    # 检查默认密码
    conn = sqlite3.connect('questionnaires.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE username = 'admin'")
    if cursor.fetchone():
        # 这里应该检查是否使用默认密码，但出于安全考虑不在代码中硬编码
        issues.append("请确认管理员账户未使用默认密码")
    
    # 检查文件权限
    import os
    import stat
    
    sensitive_files = [
        'questionnaires.db',
        'config.py',
        'config_production.py'
    ]
    
    for file_path in sensitive_files:
        if os.path.exists(file_path):
            file_stat = os.stat(file_path)
            mode = stat.filemode(file_stat.st_mode)
            if mode[7:] != '--':  # 其他用户有读写权限
                issues.append(f"文件 {file_path} 权限过于宽松: {mode}")
    
    # 检查日志文件
    log_files = ['logs/app.log', 'logs/error.log']
    for log_file in log_files:
        if os.path.exists(log_file):
            size = os.path.getsize(log_file)
            if size > 100 * 1024 * 1024:  # 100MB
                issues.append(f"日志文件 {log_file} 过大，可能包含敏感信息")
    
    conn.close()
    
    if issues:
        print("安全审计发现问题:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("安全审计通过")
    
    return issues
```

### 访问日志分析

```python
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta

def analyze_access_logs(log_file, days=7):
    """分析访问日志"""
    cutoff_date = datetime.now() - timedelta(days=days)
    
    ip_counter = Counter()
    endpoint_counter = Counter()
    error_counter = Counter()
    suspicious_ips = set()
    
    with open(log_file, 'r') as f:
        for line in f:
            # 解析日志行（假设是标准格式）
            match = re.match(r'(\S+) - - \[(.*?)\] "(\S+) (\S+) (\S+)" (\d+) (\d+)', line)
            if not match:
                continue
            
            ip, timestamp_str, method, endpoint, protocol, status, size = match.groups()
            
            # 解析时间戳
            try:
                timestamp = datetime.strptime(timestamp_str.split()[0], '%d/%b/%Y:%H:%M:%S')
                if timestamp < cutoff_date:
                    continue
            except ValueError:
                continue
            
            # 统计信息
            ip_counter[ip] += 1
            endpoint_counter[endpoint] += 1
            
            # 检查错误状态
            if status.startswith('4') or status.startswith('5'):
                error_counter[f"{status} {endpoint}"] += 1
            
            # 检查可疑活动
            if int(status) == 401:  # 未授权访问
                suspicious_ips.add(ip)
            
            # 检查频繁访问
            if ip_counter[ip] > 1000:  # 每天超过1000次请求
                suspicious_ips.add(ip)
    
    # 生成报告
    print(f"=== 访问日志分析报告 (最近 {days} 天) ===")
    
    print("\n访问最频繁的 IP:")
    for ip, count in ip_counter.most_common(10):
        print(f"  {ip}: {count} 次")
    
    print("\n访问最频繁的端点:")
    for endpoint, count in endpoint_counter.most_common(10):
        print(f"  {endpoint}: {count} 次")
    
    print("\n错误统计:")
    for error, count in error_counter.most_common(10):
        print(f"  {error}: {count} 次")
    
    if suspicious_ips:
        print("\n可疑 IP 地址:")
        for ip in suspicious_ips:
            print(f"  {ip} (访问次数: {ip_counter[ip]})")
    
    return {
        'ip_stats': dict(ip_counter),
        'endpoint_stats': dict(endpoint_counter),
        'error_stats': dict(error_counter),
        'suspicious_ips': list(suspicious_ips)
    }
```

## 监控与维护

### 系统监控脚本

```python
import psutil
import sqlite3
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

class SystemMonitor:
    def __init__(self, config):
        self.config = config
        self.alerts = []
    
    def check_disk_space(self):
        """检查磁盘空间"""
        disk_usage = psutil.disk_usage('/')
        usage_percent = (disk_usage.used / disk_usage.total) * 100
        
        if usage_percent > self.config.get('disk_threshold', 80):
            self.alerts.append(f"磁盘使用率过高: {usage_percent:.1f}%")
        
        return usage_percent
    
    def check_memory_usage(self):
        """检查内存使用"""
        memory = psutil.virtual_memory()
        
        if memory.percent > self.config.get('memory_threshold', 80):
            self.alerts.append(f"内存使用率过高: {memory.percent:.1f}%")
        
        return memory.percent
    
    def check_database_health(self):
        """检查数据库健康状态"""
        try:
            conn = sqlite3.connect('questionnaires.db', timeout=5)
            cursor = conn.cursor()
            
            # 检查数据库完整性
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]
            
            if result != 'ok':
                self.alerts.append(f"数据库完整性检查失败: {result}")
            
            # 检查数据库大小
            cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
            db_size = cursor.fetchone()[0]
            
            max_size = self.config.get('max_db_size', 1024 * 1024 * 1024)  # 1GB
            if db_size > max_size:
                self.alerts.append(f"数据库文件过大: {db_size / 1024 / 1024:.1f} MB")
            
            conn.close()
            return True
            
        except Exception as e:
            self.alerts.append(f"数据库连接失败: {str(e)}")
            return False
    
    def check_service_status(self):
        """检查服务状态"""
        try:
            import requests
            response = requests.get('http://localhost:5000/api/system/health', timeout=10)
            
            if response.status_code != 200:
                self.alerts.append(f"服务健康检查失败: HTTP {response.status_code}")
                return False
            
            health_data = response.json()
            if not health_data.get('success'):
                self.alerts.append("服务健康检查返回错误状态")
                return False
            
            return True
            
        except Exception as e:
            self.alerts.append(f"服务连接失败: {str(e)}")
            return False
    
    def send_alert_email(self):
        """发送告警邮件"""
        if not self.alerts:
            return
        
        email_config = self.config.get('email', {})
        if not email_config.get('enabled'):
            return
        
        subject = f"问卷系统监控告警 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        body = "检测到以下问题:\n\n" + "\n".join(f"- {alert}" for alert in self.alerts)
        
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = email_config['from']
        msg['To'] = email_config['to']
        
        try:
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            if email_config.get('use_tls'):
                server.starttls()
            if email_config.get('username'):
                server.login(email_config['username'], email_config['password'])
            
            server.send_message(msg)
            server.quit()
            
            print(f"告警邮件已发送: {len(self.alerts)} 个问题")
            
        except Exception as e:
            print(f"发送告警邮件失败: {e}")
    
    def run_monitoring(self):
        """运行监控检查"""
        print(f"开始系统监控检查 - {datetime.now()}")
        
        disk_usage = self.check_disk_space()
        memory_usage = self.check_memory_usage()
        db_healthy = self.check_database_health()
        service_healthy = self.check_service_status()
        
        print(f"磁盘使用率: {disk_usage:.1f}%")
        print(f"内存使用率: {memory_usage:.1f}%")
        print(f"数据库状态: {'正常' if db_healthy else '异常'}")
        print(f"服务状态: {'正常' if service_healthy else '异常'}")
        
        if self.alerts:
            print(f"发现 {len(self.alerts)} 个问题:")
            for alert in self.alerts:
                print(f"  - {alert}")
            
            self.send_alert_email()
        else:
            print("系统状态正常")

# 使用示例
monitor_config = {
    'disk_threshold': 80,
    'memory_threshold': 80,
    'max_db_size': 1024 * 1024 * 1024,  # 1GB
    'email': {
        'enabled': True,
        'smtp_server': 'smtp.example.com',
        'smtp_port': 587,
        'use_tls': True,
        'username': 'monitor@example.com',
        'password': 'password',
        'from': 'monitor@example.com',
        'to': 'admin@example.com'
    }
}

monitor = SystemMonitor(monitor_config)
monitor.run_monitoring()
```

### 定时任务配置

```bash
# crontab -e
# 添加以下定时任务

# 每小时运行系统监控
0 * * * * /path/to/venv/bin/python /path/to/system_monitor.py

# 每天凌晨2点备份数据
0 2 * * * /path/to/auto_backup.sh

# 每周日凌晨3点清理日志
0 3 * * 0 /path/to/cleanup_logs.sh

# 每天凌晨1点优化数据库
0 1 * * * /path/to/venv/bin/python -c "from maintenance import optimize_database; optimize_database()"

# 每月1号生成统计报告
0 0 1 * * /path/to/venv/bin/python -c "from statistics import generate_monthly_report; generate_monthly_report()"
```

---

*本指南最后更新时间: 2024年1月15日*