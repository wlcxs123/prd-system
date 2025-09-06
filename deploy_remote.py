#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
远程服务器自动部署脚本

功能：
- 通过SSH连接到远程服务器
- 自动部署项目到指定目录
- 支持备份和回滚
- 自动启动服务

使用方法：
python deploy_remote.py
"""

import os
import sys
import subprocess
import tarfile
import tempfile
from datetime import datetime
import paramiko
from scp import SCPClient
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deploy.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 服务器配置
SERVER_CONFIG = {
    'hostname': '115.190.103.114',
    'username': 'root',
    'password': 'LKziTP2FWjbdv87AuUHJ',
    'port': 22,
    'deploy_dir': '/usr/share/nginx-after',
    'backup_dir': '/usr/share/nginx-after-backup'
}

# 项目配置
PROJECT_CONFIG = {
    'local_dir': os.path.dirname(os.path.abspath(__file__)),
    'project_name': 'prd-system',
    'exclude_patterns': [
        '__pycache__',
        '*.pyc',
        '.git',
        '.env',
        'venv',
        'node_modules',
        '*.log',
        '.DS_Store',
        'Thumbs.db'
    ]
}

class RemoteDeployer:
    def __init__(self):
        self.ssh_client = None
        self.scp_client = None
        
    def connect(self):
        """连接到远程服务器"""
        try:
            logger.info(f"正在连接到服务器 {SERVER_CONFIG['hostname']}...")
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            self.ssh_client.connect(
                hostname=SERVER_CONFIG['hostname'],
                username=SERVER_CONFIG['username'],
                password=SERVER_CONFIG['password'],
                port=SERVER_CONFIG['port'],
                timeout=30
            )
            
            self.scp_client = SCPClient(self.ssh_client.get_transport())
            logger.info("SSH连接成功！")
            return True
            
        except Exception as e:
            logger.error(f"SSH连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        if self.scp_client:
            self.scp_client.close()
        if self.ssh_client:
            self.ssh_client.close()
        logger.info("已断开SSH连接")
    
    def execute_command(self, command, check_exit_code=True, timeout=30):
        """在远程服务器执行命令"""
        try:
            logger.info(f"执行命令: {command}")
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            
            # 检查是否是nohup后台命令
            is_nohup_command = 'nohup' in command and '&' in command
            
            if is_nohup_command:
                # 对于nohup命令，立即返回成功，不等待输出
                logger.info("nohup后台命令已提交")
                return True, "", ""
            else:
                # 普通命令正常等待
                stdout.channel.settimeout(timeout)
                exit_code = stdout.channel.recv_exit_status()
                
                output = stdout.read().decode('utf-8')
                error = stderr.read().decode('utf-8')
                
                if check_exit_code and exit_code != 0:
                    logger.error(f"命令执行失败 (退出码: {exit_code}): {error}")
                    return False, output, error
                
                if output:
                    logger.info(f"命令输出: {output.strip()}")
                
                return True, output, error
            
        except Exception as e:
            logger.error(f"执行命令失败: {e}")
            return False, "", str(e)
    
    def create_backup(self):
        """创建备份"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"backup_{timestamp}"
        backup_path = f"{SERVER_CONFIG['backup_dir']}/{backup_name}"
        
        logger.info("正在创建备份...")
        
        # 创建备份目录
        success, _, _ = self.execute_command(f"mkdir -p {SERVER_CONFIG['backup_dir']}")
        if not success:
            return False, None
        
        # 检查部署目录是否存在
        success, _, _ = self.execute_command(f"test -d {SERVER_CONFIG['deploy_dir']}", check_exit_code=False)
        if success:
            # 备份现有部署
            success, _, _ = self.execute_command(f"cp -r {SERVER_CONFIG['deploy_dir']} {backup_path}")
            if success:
                logger.info(f"备份创建成功: {backup_path}")
                return True, backup_path
            else:
                logger.error("备份创建失败")
                return False, None
        else:
            logger.info("部署目录不存在，跳过备份")
            return True, None
    
    def create_archive(self):
        """创建项目压缩包"""
        logger.info("正在创建项目压缩包...")
        
        # 创建临时文件
        temp_file = tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False)
        temp_file.close()
        
        try:
            with tarfile.open(temp_file.name, 'w:gz') as tar:
                for root, dirs, files in os.walk(PROJECT_CONFIG['local_dir']):
                    # 过滤排除的目录
                    dirs[:] = [d for d in dirs if not any(
                        d.startswith(pattern.rstrip('*')) for pattern in PROJECT_CONFIG['exclude_patterns']
                    )]
                    
                    for file in files:
                        # 过滤排除的文件
                        if any(
                            file.endswith(pattern.lstrip('*')) or file.startswith(pattern.rstrip('*'))
                            for pattern in PROJECT_CONFIG['exclude_patterns']
                        ):
                            continue
                        
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, PROJECT_CONFIG['local_dir'])
                        tar.add(file_path, arcname=arcname)
            
            logger.info(f"项目压缩包创建成功: {temp_file.name}")
            return temp_file.name
            
        except Exception as e:
            logger.error(f"创建压缩包失败: {e}")
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
            return None
    
    def upload_and_extract(self, archive_path):
        """上传并解压项目"""
        remote_archive = f"/tmp/deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
        
        try:
            logger.info("正在上传项目文件...")
            self.scp_client.put(archive_path, remote_archive)
            logger.info("文件上传成功")
            
            # 创建部署目录
            success, _, _ = self.execute_command(f"mkdir -p {SERVER_CONFIG['deploy_dir']}")
            if not success:
                return False
            
            # 清理旧文件
            success, _, _ = self.execute_command(f"rm -rf {SERVER_CONFIG['deploy_dir']}/*")
            if not success:
                return False
            
            # 解压文件
            logger.info("正在解压项目文件...")
            success, _, _ = self.execute_command(
                f"tar -xzf {remote_archive} -C {SERVER_CONFIG['deploy_dir']}"
            )
            if not success:
                return False
            
            # 清理临时文件
            self.execute_command(f"rm -f {remote_archive}")
            
            logger.info("项目文件部署成功")
            return True
            
        except Exception as e:
            logger.error(f"上传和解压失败: {e}")
            return False
    
    def setup_environment(self):
        """设置环境"""
        logger.info("正在设置环境...")
        
        commands = [
            # 进入部署目录
            f"cd {SERVER_CONFIG['deploy_dir']}",
            
            # 检查Python环境
            "python3 --version || echo 'Python3 not found'",
            
            # 安装Python依赖（如果存在requirements.txt）
            f"cd {SERVER_CONFIG['deploy_dir']}/backend && if [ -f requirements.txt ]; then pip3 install -r requirements.txt; fi",
            
            # 设置权限
            f"chmod +x {SERVER_CONFIG['deploy_dir']}/backend/*.py",
            f"chmod +x {SERVER_CONFIG['deploy_dir']}/backend/*.sh",
            
            # 创建日志目录
            f"mkdir -p {SERVER_CONFIG['deploy_dir']}/logs",
        ]
        
        for cmd in commands:
            success, output, error = self.execute_command(cmd, check_exit_code=False)
            if not success and "not found" not in error.lower():
                logger.warning(f"命令可能失败: {cmd}")
        
        logger.info("环境设置完成")
        return True
    
    def start_services(self):
        """启动服务"""
        logger.info("正在启动服务...")
        
        # 停止可能运行的服务
        self.execute_command("pkill -f 'python.*app.py' || true", check_exit_code=False)
        
        # 使用nohup启动应用，避免SSH连接影响
        start_cmd = f"cd {SERVER_CONFIG['deploy_dir']}/backend && nohup python3 app.py > ../logs/app.log 2>&1 &"
        success, output, _ = self.execute_command(start_cmd, check_exit_code=False, timeout=10)
        
        if success:
            logger.info("服务启动命令已执行")
            # 等待服务启动
            import time
            time.sleep(5)
            
            # 检查进程是否运行
            success, output, _ = self.execute_command("pgrep -f 'python.*app.py' || echo 'No process found'", check_exit_code=False)
            if "No process found" not in output and output.strip():
                logger.info("服务运行正常")
                logger.info(f"进程ID: {output.strip()}")
                
                # 检查日志文件
                log_success, log_output, _ = self.execute_command(f"tail -5 {SERVER_CONFIG['deploy_dir']}/logs/app.log 2>/dev/null || echo 'Log file not found'", check_exit_code=False)
                if log_success and "Log file not found" not in log_output:
                    logger.info(f"应用日志: {log_output.strip()}")
                return True
            else:
                logger.warning("服务可能未正常启动，尝试检查日志")
                # 检查日志文件
                log_success, log_output, _ = self.execute_command(f"tail -10 {SERVER_CONFIG['deploy_dir']}/logs/app.log 2>/dev/null || echo 'Log file not found'", check_exit_code=False)
                if log_success and "Log file not found" not in log_output:
                    logger.info(f"应用日志: {log_output.strip()}")
                return False
        else:
            logger.error("服务启动失败")
            return False
    
    def health_check(self):
        """健康检查"""
        logger.info("正在进行健康检查...")
        
        # 检查端口是否监听
        success, output, _ = self.execute_command("netstat -tlnp | grep :8081 || ss -tlnp | grep :8081", check_exit_code=False)
        if success and output.strip():
            logger.info("端口8081正在监听")
            
            # 尝试HTTP请求
            success, output, _ = self.execute_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:8081/health || echo 'curl failed'", check_exit_code=False)
            if "200" in output:
                logger.info("健康检查通过")
                return True
            else:
                logger.warning(f"健康检查失败，HTTP状态码: {output}")
        else:
            logger.warning("端口8081未在监听")
        
        return False
    
    def rollback(self, backup_path):
        """回滚到备份"""
        if not backup_path:
            logger.error("没有可用的备份进行回滚")
            return False
        
        logger.info(f"正在回滚到备份: {backup_path}")
        
        # 停止服务
        self.execute_command("pkill -f 'python.*app.py' || true", check_exit_code=False)
        
        # 恢复备份
        success, _, _ = self.execute_command(f"rm -rf {SERVER_CONFIG['deploy_dir']}")
        if not success:
            return False
        
        success, _, _ = self.execute_command(f"mv {backup_path} {SERVER_CONFIG['deploy_dir']}")
        if success:
            logger.info("回滚成功")
            return True
        else:
            logger.error("回滚失败")
            return False
    
    def deploy(self):
        """执行完整部署流程"""
        backup_path = None
        archive_path = None
        
        try:
            # 连接服务器
            if not self.connect():
                return False
            
            # 创建备份
            success, backup_path = self.create_backup()
            if not success:
                logger.error("备份创建失败，部署终止")
                return False
            
            # 创建项目压缩包
            archive_path = self.create_archive()
            if not archive_path:
                logger.error("项目压缩包创建失败，部署终止")
                return False
            
            # 上传并解压
            if not self.upload_and_extract(archive_path):
                logger.error("文件上传失败，开始回滚")
                if backup_path:
                    self.rollback(backup_path)
                return False
            
            # 设置环境
            if not self.setup_environment():
                logger.error("环境设置失败，开始回滚")
                if backup_path:
                    self.rollback(backup_path)
                return False
            
            # 启动服务
            if not self.start_services():
                logger.error("服务启动失败，开始回滚")
                if backup_path:
                    self.rollback(backup_path)
                return False
            
            # 健康检查
            if not self.health_check():
                logger.warning("健康检查失败，但部署已完成")
            
            logger.info("🎉 部署成功完成！")
            logger.info(f"应用访问地址: http://{SERVER_CONFIG['hostname']}:8081")
            
            return True
            
        except Exception as e:
            logger.error(f"部署过程中发生错误: {e}")
            if backup_path:
                logger.info("尝试回滚...")
                self.rollback(backup_path)
            return False
            
        finally:
            # 清理临时文件
            if archive_path and os.path.exists(archive_path):
                os.unlink(archive_path)
            
            # 断开连接
            self.disconnect()

def main():
    """主函数"""
    print("="*60)
    print("🚀 远程服务器自动部署脚本")
    print(f"📡 目标服务器: {SERVER_CONFIG['hostname']}")
    print(f"📁 部署目录: {SERVER_CONFIG['deploy_dir']}")
    print("="*60)
    
    # 检查依赖
    try:
        import paramiko
        import scp
    except ImportError as e:
        logger.error(f"缺少依赖包: {e}")
        logger.info("请安装依赖: pip install paramiko scp")
        return False
    
    # 确认部署
    try:
        confirm = input("\n确认开始部署？(y/N): ").strip().lower()
        if confirm not in ['y', 'yes']:
            logger.info("部署已取消")
            return False
    except KeyboardInterrupt:
        logger.info("\n部署已取消")
        return False
    
    # 执行部署
    deployer = RemoteDeployer()
    success = deployer.deploy()
    
    if success:
        print("\n" + "="*60)
        print("✅ 部署成功完成！")
        print(f"🌐 应用地址: http://{SERVER_CONFIG['hostname']}:8081")
        print(f"📋 健康检查: http://{SERVER_CONFIG['hostname']}:8081/health")
        print("📝 查看日志: tail -f /usr/share/nginx-after/logs/app.log")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ 部署失败！")
        print("📝 请查看日志文件 deploy.log 获取详细信息")
        print("="*60)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)