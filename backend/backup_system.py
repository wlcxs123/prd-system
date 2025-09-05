#!/usr/bin/env python3
"""
自动备份系统
用于定期备份数据库和重要文件
"""

import os
import sys
import sqlite3
import shutil
import gzip
import json
import schedule
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path

class BackupSystem:
    """备份系统类"""
    
    def __init__(self, config=None):
        self.config = config or self.load_config()
        self.setup_logging()
        
    def load_config(self):
        """加载备份配置"""
        return {
            'database_path': os.environ.get('DATABASE_PATH', 'questionnaires.db'),
            'backup_path': os.environ.get('BACKUP_PATH', './backups'),
            'retention_days': int(os.environ.get('BACKUP_RETENTION_DAYS', '30')),
            'compress': os.environ.get('BACKUP_COMPRESS', 'true').lower() == 'true',
            'include_logs': os.environ.get('BACKUP_INCLUDE_LOGS', 'true').lower() == 'true',
            'log_path': os.environ.get('LOG_PATH', './logs'),
            'static_path': os.environ.get('STATIC_PATH', './static'),
            'templates_path': os.environ.get('TEMPLATES_PATH', './templates'),
        }
    
    def setup_logging(self):
        """设置日志"""
        log_dir = os.path.join(self.config['backup_path'], 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(log_dir, 'backup.log')),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def create_backup(self):
        """创建完整备份"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = os.path.join(self.config['backup_path'], f'backup_{timestamp}')
            os.makedirs(backup_dir, exist_ok=True)
            
            self.logger.info(f"开始创建备份: {backup_dir}")
            
            # 备份数据库
            db_backup_path = self.backup_database(backup_dir, timestamp)
            
            # 备份日志文件
            if self.config['include_logs']:
                self.backup_logs(backup_dir)
            
            # 备份静态文件和模板
            self.backup_static_files(backup_dir)
            
            # 创建备份清单
            manifest = self.create_manifest(backup_dir, timestamp)
            
            # 压缩备份（如果启用）
            if self.config['compress']:
                compressed_path = self.compress_backup(backup_dir)
                if compressed_path:
                    shutil.rmtree(backup_dir)  # 删除未压缩的目录
                    backup_path = compressed_path
                else:
                    backup_path = backup_dir
            else:
                backup_path = backup_dir
            
            self.logger.info(f"备份创建完成: {backup_path}")
            
            # 清理旧备份
            self.cleanup_old_backups()
            
            return backup_path
            
        except Exception as e:
            self.logger.error(f"创建备份失败: {e}")
            return None
    
    def backup_database(self, backup_dir, timestamp):
        """备份数据库"""
        db_path = self.config['database_path']
        
        if not os.path.exists(db_path):
            self.logger.warning(f"数据库文件不存在: {db_path}")
            return None
        
        try:
            # 创建数据库备份目录
            db_backup_dir = os.path.join(backup_dir, 'database')
            os.makedirs(db_backup_dir, exist_ok=True)
            
            # 复制数据库文件
            db_backup_path = os.path.join(db_backup_dir, f'questionnaires_{timestamp}.db')
            shutil.copy2(db_path, db_backup_path)
            
            # 导出数据为 JSON（便于跨平台恢复）
            json_backup_path = os.path.join(db_backup_dir, f'questionnaires_{timestamp}.json')
            self.export_database_to_json(db_path, json_backup_path)
            
            # 创建数据库统计信息
            stats_path = os.path.join(db_backup_dir, f'stats_{timestamp}.json')
            self.create_database_stats(db_path, stats_path)
            
            self.logger.info(f"数据库备份完成: {db_backup_path}")
            return db_backup_path
            
        except Exception as e:
            self.logger.error(f"数据库备份失败: {e}")
            return None
    
    def export_database_to_json(self, db_path, json_path):
        """将数据库导出为 JSON 格式"""
        try:
            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                export_data = {
                    'export_time': datetime.now().isoformat(),
                    'tables': {}
                }
                
                # 获取所有表名
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                for table in tables:
                    cursor.execute(f"SELECT * FROM {table}")
                    rows = cursor.fetchall()
                    export_data['tables'][table] = [dict(row) for row in rows]
                
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)
                
                self.logger.info(f"数据库 JSON 导出完成: {json_path}")
                
        except Exception as e:
            self.logger.error(f"数据库 JSON 导出失败: {e}")
    
    def create_database_stats(self, db_path, stats_path):
        """创建数据库统计信息"""
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                stats = {
                    'backup_time': datetime.now().isoformat(),
                    'database_size': os.path.getsize(db_path),
                    'tables': {}
                }
                
                # 获取表统计信息
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    stats['tables'][table] = {'row_count': count}
                
                with open(stats_path, 'w', encoding='utf-8') as f:
                    json.dump(stats, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"创建数据库统计信息失败: {e}")
    
    def backup_logs(self, backup_dir):
        """备份日志文件"""
        log_path = self.config['log_path']
        
        if not os.path.exists(log_path):
            self.logger.warning(f"日志目录不存在: {log_path}")
            return
        
        try:
            log_backup_dir = os.path.join(backup_dir, 'logs')
            shutil.copytree(log_path, log_backup_dir, ignore=shutil.ignore_patterns('*.tmp'))
            self.logger.info(f"日志备份完成: {log_backup_dir}")
            
        except Exception as e:
            self.logger.error(f"日志备份失败: {e}")
    
    def backup_static_files(self, backup_dir):
        """备份静态文件和模板"""
        paths_to_backup = [
            ('static', self.config['static_path']),
            ('templates', self.config['templates_path'])
        ]
        
        for name, path in paths_to_backup:
            if os.path.exists(path):
                try:
                    backup_path = os.path.join(backup_dir, name)
                    shutil.copytree(path, backup_path)
                    self.logger.info(f"{name} 备份完成: {backup_path}")
                except Exception as e:
                    self.logger.error(f"{name} 备份失败: {e}")
    
    def create_manifest(self, backup_dir, timestamp):
        """创建备份清单"""
        try:
            manifest = {
                'backup_time': datetime.now().isoformat(),
                'timestamp': timestamp,
                'version': '1.0',
                'files': []
            }
            
            # 遍历备份目录，记录所有文件
            for root, dirs, files in os.walk(backup_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, backup_dir)
                    file_size = os.path.getsize(file_path)
                    
                    manifest['files'].append({
                        'path': rel_path,
                        'size': file_size,
                        'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                    })
            
            manifest_path = os.path.join(backup_dir, 'manifest.json')
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"备份清单创建完成: {manifest_path}")
            return manifest_path
            
        except Exception as e:
            self.logger.error(f"创建备份清单失败: {e}")
            return None
    
    def compress_backup(self, backup_dir):
        """压缩备份目录"""
        try:
            compressed_path = f"{backup_dir}.tar.gz"
            
            import tarfile
            with tarfile.open(compressed_path, 'w:gz') as tar:
                tar.add(backup_dir, arcname=os.path.basename(backup_dir))
            
            self.logger.info(f"备份压缩完成: {compressed_path}")
            return compressed_path
            
        except Exception as e:
            self.logger.error(f"备份压缩失败: {e}")
            return None
    
    def cleanup_old_backups(self):
        """清理过期备份"""
        try:
            backup_path = self.config['backup_path']
            retention_days = self.config['retention_days']
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            deleted_count = 0
            
            for item in os.listdir(backup_path):
                item_path = os.path.join(backup_path, item)
                
                # 跳过非备份文件
                if not (item.startswith('backup_') or item.endswith('.tar.gz')):
                    continue
                
                # 检查文件/目录的修改时间
                if os.path.getmtime(item_path) < cutoff_date.timestamp():
                    try:
                        if os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                        else:
                            os.remove(item_path)
                        
                        deleted_count += 1
                        self.logger.info(f"删除过期备份: {item}")
                        
                    except Exception as e:
                        self.logger.error(f"删除过期备份失败 {item}: {e}")
            
            if deleted_count > 0:
                self.logger.info(f"清理完成，删除了 {deleted_count} 个过期备份")
            
        except Exception as e:
            self.logger.error(f"清理过期备份失败: {e}")
    
    def restore_backup(self, backup_path):
        """恢复备份"""
        try:
            self.logger.info(f"开始恢复备份: {backup_path}")
            
            # 检查备份文件/目录是否存在
            if not os.path.exists(backup_path):
                raise FileNotFoundError(f"备份文件不存在: {backup_path}")
            
            # 如果是压缩文件，先解压
            if backup_path.endswith('.tar.gz'):
                extract_dir = backup_path.replace('.tar.gz', '')
                
                import tarfile
                with tarfile.open(backup_path, 'r:gz') as tar:
                    tar.extractall(os.path.dirname(backup_path))
                
                backup_dir = extract_dir
            else:
                backup_dir = backup_path
            
            # 读取备份清单
            manifest_path = os.path.join(backup_dir, 'manifest.json')
            if os.path.exists(manifest_path):
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                self.logger.info(f"备份清单: {len(manifest['files'])} 个文件")
            
            # 恢复数据库
            db_backup_path = os.path.join(backup_dir, 'database')
            if os.path.exists(db_backup_path):
                self.restore_database(db_backup_path)
            
            self.logger.info("备份恢复完成")
            return True
            
        except Exception as e:
            self.logger.error(f"恢复备份失败: {e}")
            return False
    
    def restore_database(self, db_backup_path):
        """恢复数据库"""
        try:
            # 查找数据库备份文件
            db_files = [f for f in os.listdir(db_backup_path) if f.endswith('.db')]
            
            if not db_files:
                raise FileNotFoundError("未找到数据库备份文件")
            
            # 使用最新的备份文件
            db_file = sorted(db_files)[-1]
            source_path = os.path.join(db_backup_path, db_file)
            target_path = self.config['database_path']
            
            # 备份当前数据库
            if os.path.exists(target_path):
                backup_current = f"{target_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(target_path, backup_current)
                self.logger.info(f"当前数据库已备份到: {backup_current}")
            
            # 恢复数据库
            shutil.copy2(source_path, target_path)
            self.logger.info(f"数据库恢复完成: {target_path}")
            
        except Exception as e:
            self.logger.error(f"数据库恢复失败: {e}")
            raise

def run_scheduled_backup():
    """运行定时备份"""
    backup_system = BackupSystem()
    backup_system.create_backup()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='问卷数据管理系统备份工具')
    parser.add_argument('--backup', action='store_true', help='创建备份')
    parser.add_argument('--restore', help='恢复备份（指定备份路径）')
    parser.add_argument('--schedule', action='store_true', help='启动定时备份服务')
    parser.add_argument('--cleanup', action='store_true', help='清理过期备份')
    parser.add_argument('--interval', type=int, default=24, help='备份间隔（小时）')
    
    args = parser.parse_args()
    
    backup_system = BackupSystem()
    
    if args.backup:
        backup_path = backup_system.create_backup()
        if backup_path:
            print(f"备份创建成功: {backup_path}")
        else:
            print("备份创建失败")
            sys.exit(1)
    
    elif args.restore:
        success = backup_system.restore_backup(args.restore)
        if success:
            print("备份恢复成功")
        else:
            print("备份恢复失败")
            sys.exit(1)
    
    elif args.cleanup:
        backup_system.cleanup_old_backups()
        print("过期备份清理完成")
    
    elif args.schedule:
        print(f"启动定时备份服务，间隔: {args.interval} 小时")
        
        # 设置定时任务
        schedule.every(args.interval).hours.do(run_scheduled_backup)
        
        # 立即执行一次备份
        run_scheduled_backup()
        
        # 运行定时任务
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main()