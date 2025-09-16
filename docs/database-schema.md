# 数据库表结构文档

## 概述

本文档描述了问卷数据管理系统的完整数据库架构，包括所有表的结构、字段说明、索引和关系。

## 数据库配置

- **数据库类型**: SQLite
- **数据库文件**: `questionnaires.db`
- **字符编码**: UTF-8
- **开发环境路径**: `backend/questionnaires.db`
- **生产环境路径**: `/app/data/questionnaires.db` (可通过环境变量 `DATABASE_PATH` 配置)

## 表结构

### 1. questionnaires (问卷数据表)

**用途**: 存储所有问卷的数据和元信息

```sql
CREATE TABLE questionnaires (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,                    -- 问卷类型
    name TEXT,                            -- 填写人姓名
    gender TEXT,                          -- 性别
    birthdate TEXT,                       -- 出生日期
    grade TEXT,                           -- 年级
    school TEXT,                          -- 学校
    teacher TEXT,                         -- 老师
    parent_phone TEXT,                    -- 家长电话
    parent_wechat TEXT,                   -- 家长微信
    parent_email TEXT,                    -- 家长邮箱
    submission_date DATE,                 -- 提交日期
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 更新时间
    data TEXT NOT NULL,                   -- JSON格式的完整问卷数据
    report_data TEXT,                     -- 报告数据
    report_generated_at TIMESTAMP         -- 报告生成时间
);
```

#### 字段说明

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 主键，自增ID |
| type | TEXT | NOT NULL | 问卷类型（如：家长访谈表、小学生报告表等） |
| name | TEXT | - | 填写人姓名 |
| gender | TEXT | - | 性别（男/女） |
| birthdate | TEXT | - | 出生日期 |
| grade | TEXT | - | 年级信息 |
| school | TEXT | - | 学校名称 |
| teacher | TEXT | - | 老师姓名 |
| parent_phone | TEXT | - | 家长联系电话 |
| parent_wechat | TEXT | - | 家长微信号 |
| parent_email | TEXT | - | 家长邮箱地址 |
| submission_date | DATE | - | 问卷提交日期 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 记录创建时间 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 记录最后更新时间 |
| data | TEXT | NOT NULL | JSON格式存储的完整问卷数据 |
| report_data | TEXT | - | 生成的报告数据 |
| report_generated_at | TIMESTAMP | - | 报告生成时间 |

#### 常用查询示例

```sql
-- 查询所有家长访谈表
SELECT * FROM questionnaires WHERE type = '家长访谈表';

-- 按创建时间倒序查询最新10条记录
SELECT * FROM questionnaires ORDER BY created_at DESC LIMIT 10;

-- 查询特定学生的所有问卷
SELECT * FROM questionnaires WHERE name = '张三';

-- 统计各类型问卷数量
SELECT type, COUNT(*) as count FROM questionnaires GROUP BY type;
```

### 2. users (用户认证表)

**用途**: 存储系统用户信息和认证数据

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,        -- 用户名
    password_hash TEXT NOT NULL,          -- 密码哈希
    role TEXT DEFAULT 'admin',            -- 用户角色
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    last_login TIMESTAMP                  -- 最后登录时间
);
```

#### 字段说明

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 主键，自增ID |
| username | TEXT | UNIQUE, NOT NULL | 用户名，唯一 |
| password_hash | TEXT | NOT NULL | bcrypt加密的密码哈希 |
| role | TEXT | DEFAULT 'admin' | 用户角色（admin/user） |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 账户创建时间 |
| last_login | TIMESTAMP | - | 最后登录时间 |

#### 默认用户

系统初始化时会创建默认管理员账户：
- **用户名**: admin
- **密码**: admin123
- **角色**: admin

#### 常用查询示例

```sql
-- 验证用户登录
SELECT id, username, password_hash, role FROM users WHERE username = ?;

-- 更新最后登录时间
UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?;

-- 查询所有管理员
SELECT * FROM users WHERE role = 'admin';
```

### 3. operation_logs (操作日志表)

**用途**: 记录系统操作日志，用于审计和追踪

```sql
CREATE TABLE operation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,                      -- 操作用户ID
    operation TEXT NOT NULL,              -- 操作类型
    target_id INTEGER,                    -- 目标对象ID
    details TEXT,                         -- 操作详情
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 操作时间
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

#### 字段说明

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 主键，自增ID |
| user_id | INTEGER | FOREIGN KEY | 操作用户ID，关联users表 |
| operation | TEXT | NOT NULL | 操作类型（LOGIN/LOGOUT/CREATE/UPDATE/DELETE等） |
| target_id | INTEGER | - | 操作目标的ID（如问卷ID） |
| details | TEXT | - | 操作详细信息 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 操作时间 |

#### 操作类型说明

| 操作类型 | 说明 |
|----------|------|
| LOGIN | 用户登录 |
| LOGOUT | 用户登出 |
| AUTO_LOGOUT | 会话超时自动登出 |
| CREATE | 创建问卷 |
| UPDATE | 更新问卷 |
| DELETE | 删除问卷 |
| VIEW | 查看问卷 |
| EXPORT | 导出数据 |
| BATCH_DELETE | 批量删除 |

#### 常用查询示例

```sql
-- 查询用户操作历史
SELECT ol.*, u.username 
FROM operation_logs ol 
LEFT JOIN users u ON ol.user_id = u.id 
WHERE ol.user_id = ? 
ORDER BY ol.created_at DESC;

-- 查询最近24小时的操作日志
SELECT * FROM operation_logs 
WHERE created_at >= datetime('now', '-1 day') 
ORDER BY created_at DESC;

-- 统计各类操作数量
SELECT operation, COUNT(*) as count 
FROM operation_logs 
GROUP BY operation;
```

## 数据库维护

### 备份策略

1. **自动备份**: 系统支持定时自动备份
2. **手动备份**: 管理员可通过后台手动创建备份
3. **备份文件**: 存储在 `/app/backups/` 目录下

### 性能优化

#### 建议索引

```sql
-- 问卷表索引
CREATE INDEX idx_questionnaires_type ON questionnaires(type);
CREATE INDEX idx_questionnaires_created_at ON questionnaires(created_at);
CREATE INDEX idx_questionnaires_name ON questionnaires(name);
CREATE INDEX idx_questionnaires_submission_date ON questionnaires(submission_date);

-- 操作日志表索引
CREATE INDEX idx_operation_logs_user_id ON operation_logs(user_id);
CREATE INDEX idx_operation_logs_created_at ON operation_logs(created_at);
CREATE INDEX idx_operation_logs_operation ON operation_logs(operation);
```

### 数据清理

#### 清理旧日志

```sql
-- 删除30天前的操作日志
DELETE FROM operation_logs 
WHERE created_at < datetime('now', '-30 days');
```

## 数据迁移

系统支持数据库结构的自动迁移，当添加新字段时会自动执行 `ALTER TABLE` 语句。

### 迁移脚本

- `init_db.py`: 初始化数据库和创建表结构
- `migrate_db.py`: 数据库迁移脚本
- `check_db.py`: 检查数据库状态

## 故障排除

### 常见问题

1. **数据库文件权限问题**
   ```bash
   chmod 664 questionnaires.db
   chown www-data:www-data questionnaires.db
   ```

2. **数据库锁定问题**
   ```bash
   lsof questionnaires.db  # 查看占用进程
   ```

3. **数据库损坏**
   ```sql
   PRAGMA integrity_check;
   ```

### 恢复操作

```bash
# 从备份恢复
cp /app/backups/questionnaires_YYYYMMDD_HHMMSS.db questionnaires.db

# 重新初始化数据库
python init_db.py
```

## 安全注意事项

1. **密码安全**: 使用bcrypt进行密码哈希
2. **SQL注入防护**: 使用参数化查询
3. **会话管理**: 实现会话超时机制
4. **访问控制**: 基于角色的权限控制
5. **数据备份**: 定期备份重要数据

## 更新日志

- **v1.0**: 初始版本，基础表结构
- **v1.1**: 添加家长联系方式字段
- **v1.2**: 添加性别、出生日期、学校、老师字段
- **v1.3**: 添加报告生成相关字段
- **v1.4**: 优化索引和性能