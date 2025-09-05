#!/usr/bin/env python3
"""
问卷数据管理系统启动脚本
"""

import os
import sys
from app import app, init_db

def main():
    """主函数"""
    print("=" * 50)
    print("问卷数据管理系统")
    print("=" * 50)
    
    # 检查数据库是否存在，如果不存在则初始化
    if not os.path.exists(app.config['DATABASE_PATH']):
        print("数据库不存在，正在初始化...")
        init_db()
        print("数据库初始化完成")
    
    # 获取运行参数
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    print(f"启动服务器...")
    print(f"地址: http://{host}:{port}")
    print(f"调试模式: {'开启' if debug else '关闭'}")
    print(f"数据库: {app.config['DATABASE_PATH']}")
    print("=" * 50)
    print("按 Ctrl+C 停止服务器")
    print()
    
    try:
        # 启动Flask应用
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=debug
        )
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"启动失败: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())