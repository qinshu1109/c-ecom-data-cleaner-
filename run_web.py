#!/usr/bin/env python
"""
抖音电商数据分析工具 - Web界面启动脚本
"""
import os
import sys
import subprocess

if __name__ == "__main__":
    # 获取app.py的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(current_dir, 'douyin_ecom_analyzer', 'app.py')
    
    print("正在启动抖音电商数据分析工具 Web界面...")
    
    # 使用streamlit运行，指定端口为8080
    cmd = [sys.executable, '-m', 'streamlit', 'run', 
           app_path, 
           '--server.port', '8080',
           '--server.address', '0.0.0.0']
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n已停止Web服务")
    except Exception as e:
        print(f"启动失败: {str(e)}")
        print("\n请确保已安装所需依赖:")
        print("pip install -r douyin_ecom_analyzer/requirements.txt")
        sys.exit(1) 