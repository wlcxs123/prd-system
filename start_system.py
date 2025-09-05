#!/usr/bin/env python3
"""
问卷系统启动脚本
自动检查环境并启动系统
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python版本过低，需要Python 3.8或更高版本")
        print(f"当前版本: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
    return True

def check_virtual_env():
    """检查是否在虚拟环境中"""
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    if in_venv:
        print("✅ 已在虚拟环境中")
        return True
    else:
        print("⚠️  未检测到虚拟环境")
        print("建议创建虚拟环境:")
        print("  python -m venv venv")
        print("  # Windows: venv\\Scripts\\activate")
        print("  # Linux/Mac: source venv/bin/activate")
        return False

def check_dependencies():
    """检查依赖包"""
    requirements_file = Path("backend/requirements.txt")
    
    if not requirements_file.exists():
        print("❌ requirements.txt文件不存在")
        return False
    
    try:
        # 读取依赖列表
        with open(requirements_file, 'r') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        missing_packages = []
        
        for package in requirements:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"❌ 缺少依赖包: {', '.join(missing_packages)}")
            print("请运行: pip install -r backend/requirements.txt")
            return False
        
        print("✅ 所有依赖包已安装")
        return True
        
    except Exception as e:
        print(f"❌ 检查依赖包时出错: {e}")
        return False

def check_database():
    """检查数据库"""
    db_file = Path("backend/questionnaires.db")
    
    if not db_file.exists():
        print("⚠️  数据库文件不存在，正在初始化...")
        try:
            os.chdir("backend")
            result = subprocess.run([sys.executable, "init_db.py"], 
                                  capture_output=True, text=True)
            os.chdir("..")
            
            if result.returncode == 0:
                print("✅ 数据库初始化成功")
                return True
            else:
                print(f"❌ 数据库初始化失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ 数据库初始化异常: {e}")
            return False
    
    # 检查数据库完整性
    try:
        with sqlite3.connect(str(db_file)) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]
            
            if result == "ok":
                print("✅ 数据库完整性正常")
                return True
            else:
                print(f"❌ 数据库完整性检查失败: {result}")
                return False
                
    except Exception as e:
        print(f"❌ 数据库检查异常: {e}")
        return False

def start_server():
    """启动服务器"""
    print("\n🚀 启动问卷数据管理系统...")
    print("=" * 50)
    
    try:
        os.chdir("backend")
        
        # 设置环境变量
        env = os.environ.copy()
        env['FLASK_ENV'] = 'development'
        env['FLASK_DEBUG'] = '1'
        
        print("服务器启动中...")
        print("访问地址: http://localhost:5000")
        print("管理员账户: admin / admin123")
        print("按 Ctrl+C 停止服务器")
        print("=" * 50)
        
        # 启动Flask应用
        subprocess.run([sys.executable, "app.py"], env=env)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  服务器已停止")
    except Exception as e:
        print(f"\n❌ 启动服务器时出错: {e}")

def main():
    """主函数"""
    print("🔧 问卷数据管理系统 - 启动检查")
    print("=" * 50)
    
    # 检查环境
    checks = [
        ("Python版本", check_python_version),
        ("虚拟环境", check_virtual_env),
        ("依赖包", check_dependencies),
        ("数据库", check_database)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        print(f"\n检查 {check_name}...")
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("✅ 所有检查通过！")
        
        # 询问是否启动服务器
        try:
            response = input("\n是否启动服务器？(y/n): ").lower().strip()
            if response in ['y', 'yes', '是', '']:
                start_server()
            else:
                print("可以手动启动服务器:")
                print("  cd backend")
                print("  python app.py")
        except KeyboardInterrupt:
            print("\n\n操作已取消")
    else:
        print("❌ 环境检查未通过，请解决上述问题后重试")
        return False
    
    return True

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ 启动脚本异常: {e}")
        sys.exit(1)