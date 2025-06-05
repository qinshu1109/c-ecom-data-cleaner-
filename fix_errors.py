#!/usr/bin/env python3
"""
修复抖音电商分析工具中的常见错误
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_environment():
    """检查环境并安装必要的包"""
    print("检查环境...")
    try:
        # 安装必要的依赖
        subprocess.run([sys.executable, "-m", "pip", "install",
                       "openpyxl", "matplotlib", "pandas", "streamlit",
                       "PyYAML", "seaborn"], check=True)
        print("依赖安装完成")
    except subprocess.CalledProcessError as e:
        print(f"安装依赖时出错: {e}")
        return False
    return True

def fix_font_issues():
    """修复字体问题"""
    print("修复中文字体问题...")

    # 检查matplotlib配置目录
    mpl_configdir = Path.home() / ".config" / "matplotlib"
    mpl_configdir.mkdir(parents=True, exist_ok=True)

    # 创建自定义样式文件
    mpl_style = mpl_configdir / "matplotlibrc"

    with open(mpl_style, "w", encoding="utf-8") as f:
        f.write("""
# 配置中文字体支持
font.family: sans-serif
font.sans-serif: Arial Unicode MS, DejaVu Sans, SimHei, Noto Sans CJK SC, Source Han Sans CN
axes.unicode_minus: False
        """)

    # 检查是否有 Noto 字体
    font_dir = Path.home() / ".fonts"
    font_dir.mkdir(exist_ok=True)

    print("字体配置完成")

    # 添加字体到代码中
    analyzer_file = Path("douyin_ecom_analyzer/analyzer.py")
    if analyzer_file.exists():
        with open(analyzer_file, "r", encoding="utf-8") as f:
            content = f.read()

        if "plt.rcParams['font.sans-serif']" not in content:
            add_font_config = """
# 设置通用字体支持
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False
"""
            with open(analyzer_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # 在import部分后添加
            for i, line in enumerate(lines):
                if "import" in line and i > 5:
                    lines.insert(i+1, add_font_config)
                    break

            with open(analyzer_file, "w", encoding="utf-8") as f:
                f.writelines(lines)

            print("已添加字体配置到analyzer.py")

    return True

def fix_excel_save_issue():
    """修复Excel保存问题"""
    print("修复Excel保存问题...")

    # 检查analyzer.py文件中的writer.save()并改为writer.close()
    analyzer_file = Path("douyin_ecom_analyzer/analyzer.py")
    if analyzer_file.exists():
        with open(analyzer_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 替换save为close
        if "writer.save()" in content:
            content = content.replace("writer.save()", "writer.close()")
            with open(analyzer_file, "w", encoding="utf-8") as f:
                f.write(content)
            print("已修复Excel保存问题: writer.save() → writer.close()")
        else:
            print("未发现Excel保存问题或已修复")
    else:
        print(f"找不到文件: {analyzer_file}")

    return True

def update_pandas_settings():
    """更新Pandas设置"""
    print("更新Pandas设置...")

    # 修改app.py中的Pandas配置
    app_file = Path("app.py")
    if app_file.exists():
        with open(app_file, "r", encoding="utf-8") as f:
            content = f.readlines()

        # 在导入部分后添加pandas配置
        for i, line in enumerate(content):
            if "import pandas as pd" in line:
                # 检查是否已有配置
                if i+1 < len(content) and "pd.set_option('io.excel.xlsx.writer', 'openpyxl')" in content[i+1]:
                    print("Pandas配置已存在")
                    break

                content.insert(i+1, "# 设置Excel引擎为openpyxl\npd.set_option('io.excel.xlsx.writer', 'openpyxl')\n")
                with open(app_file, "w", encoding="utf-8") as f:
                    f.writelines(content)
                print("已添加Pandas Excel配置")
                break
    else:
        print(f"找不到文件: {app_file}")

    return True

def main():
    print("开始修复抖音电商分析工具的常见错误...")

    if not check_environment():
        print("环境检查失败，请手动安装依赖")
        return

    fix_font_issues()
    fix_excel_save_issue()
    update_pandas_settings()

    print("\n所有修复完成！请重新启动应用: python run_web.py")

if __name__ == "__main__":
    main()
