#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSH连接脚本
用于连接到远程服务器并执行命令
"""

import paramiko
import sys
import time
from typing import Optional

class SSHConnection:
    def __init__(self, hostname: str, username: str, password: str, port: int = 22):
        """
        初始化SSH连接参数
        
        Args:
            hostname: 服务器地址
            username: 用户名
            password: 密码
            port: SSH端口，默认22
        """
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.client = None
        
    def connect(self) -> bool:
        """
        建立SSH连接
        
        Returns:
            bool: 连接成功返回True，失败返回False
        """
        try:
            print(f"正在连接到 {self.hostname}:{self.port}...")
            
            # 创建SSH客户端
            self.client = paramiko.SSHClient()
            
            # 自动添加主机密钥（生产环境建议手动管理）
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # 建立连接
            self.client.connect(
                hostname=self.hostname,
                username=self.username,
                password=self.password,
                port=self.port,
                timeout=30
            )
            
            print("✅ SSH连接成功建立！")
            return True
            
        except paramiko.AuthenticationException:
            print("❌ 认证失败：用户名或密码错误")
            return False
        except paramiko.SSHException as e:
            print(f"❌ SSH连接错误：{e}")
            return False
        except Exception as e:
            print(f"❌ 连接失败：{e}")
            return False
    
    def execute_command(self, command: str) -> Optional[str]:
        """
        执行远程命令
        
        Args:
            command: 要执行的命令
            
        Returns:
            str: 命令输出结果，失败返回None
        """
        if not self.client:
            print("❌ 未建立SSH连接")
            return None
            
        try:
            print(f"执行命令: {command}")
            stdin, stdout, stderr = self.client.exec_command(command)
            
            # 获取输出
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            
            if error:
                print(f"错误输出: {error}")
                
            return output if output else error
            
        except Exception as e:
            print(f"执行命令失败：{e}")
            return None
    
    def get_system_info(self) -> None:
        """获取系统基本信息"""
        commands = [
            "uname -a",
            "whoami",
            "pwd",
            "df -h",
            "free -h"
        ]
        
        print("\n" + "="*50)
        print("系统信息")
        print("="*50)
        
        for cmd in commands:
            result = self.execute_command(cmd)
            if result:
                print(f"{cmd}: {result.strip()}")
            time.sleep(0.5)
    
    def close(self):
        """关闭SSH连接"""
        if self.client:
            self.client.close()
            print("🔌 SSH连接已关闭")

def main():
    """主函数"""
    # 连接参数
    HOST = "115.190.103.114"  # 服务器地址
    USERNAME = "root"         # 用户名
    PASSWORD = "LKziTP2FWjbdv87AuUHJ"  # 密码
    PORT = 22                 # SSH端口
    
    # 创建SSH连接实例
    ssh = SSHConnection(HOST, USERNAME, PASSWORD, PORT)
    
    try:
        # 建立连接
        if not ssh.connect():
            sys.exit(1)
        
        # 获取系统信息
        ssh.get_system_info()
        
        # 交互式命令执行
        print("\n" + "="*50)
        print("交互式命令模式")
        print("输入 'exit' 退出, 'info' 获取系统信息")
        print("="*50)
        
        while True:
            command = input("\n请输入命令: ").strip()
            
            if command.lower() == 'exit':
                break
            elif command.lower() == 'info':
                ssh.get_system_info()
                continue
            elif not command:
                continue
                
            result = ssh.execute_command(command)
            if result:
                print("输出:")
                print(result)
    
    except KeyboardInterrupt:
        print("\n🛑 用户中断")
    except Exception as e:
        print(f"❌ 发生错误：{e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    main()