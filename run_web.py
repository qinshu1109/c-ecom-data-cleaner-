#!/usr/bin/env python
"""
抖音电商数据分析工具 - Web界面启动脚本
"""
import os
import logging
import sys
from pathlib import Path
import subprocess

# 创建logs目录
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# 设置日志输出到文件
log_file = logs_dir / "app_error.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# 将标准错误也重定向到文件
error_log = logs_dir / "stderr.log"
sys.stderr = open(error_log, "w", encoding="utf-8")

if __name__ == "__main__":
    # 获取app.py的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(current_dir, 'douyin_ecom_analyzer', 'app.py')

    print("正在启动抖音电商数据分析工具 Web界面...")
    print(f"日志将保存到: {log_file} 和 {error_log}")

    # 使用streamlit运行，指定端口为8080
    cmd = [sys.executable, '-m', 'streamlit', 'run',
           app_path,
           '--server.port', '8080',
           '--server.address', '0.0.0.0']

    try:
        # 解决matplotlib中文字体问题
        import matplotlib
        matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS', 'sans-serif']
        matplotlib.rcParams['axes.unicode_minus'] = False

        # 修复Excel保存问题
        import pandas as pd
        pd.options.io.excel.writer = "openpyxl"

        # 启动应用
        import streamlit.web.cli as stcli
        import sys

        sys.argv = ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
        sys.exit(stcli.main())
    except Exception as e:
        logging.exception("启动失败")
        with open(logs_dir / "startup_error.log", "w", encoding="utf-8") as f:
            f.write(f"启动错误: {str(e)}\n")
        print(f"启动失败，详细错误已保存到 {logs_dir}/startup_error.log")
        sys.exit(1)
