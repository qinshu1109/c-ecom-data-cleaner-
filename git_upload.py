#!/usr/bin/env python3
import subprocess
import os
import sys

def run_command(command):
    """执行命令并返回结果"""
    print(f"执行命令: {command}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            text=True,
            capture_output=True
        )
        print(f"命令输出: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"命令失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def init_git():
    """初始化Git仓库"""
    print("初始化Git仓库...")
    return run_command("git init")

def config_git():
    """配置Git用户信息"""
    print("配置Git用户信息...")
    run_command('git config --global user.name "Douyin Ecom User"')
    return run_command('git config --global user.email "douyinecom@example.com"')

def add_files():
    """添加所有文件到Git仓库"""
    print("添加文件到Git仓库...")
    return run_command("git add .")

def commit_changes():
    """提交更改"""
    print("提交更改...")
    return run_command('git commit -m "修复数据清洗与下载功能，解决str与float比较问题和BytesIO处理问题"')

def add_remote():
    """添加远程仓库"""
    print("添加远程仓库...")
    return run_command('git remote add origin https://github.com/qinshu1109/c-ecom-data-cleaner-.git')

def push_to_github():
    """推送到GitHub"""
    print("推送到GitHub main分支...")
    # 先创建main分支
    run_command('git branch -M main')
    return run_command('git push -u origin main')

def main():
    """主函数"""
    print("开始Git上传流程...")

    # 检查当前目录
    print(f"当前工作目录: {os.getcwd()}")

    # 执行Git操作
    if not init_git():
        print("初始化Git仓库失败，检查是否已经初始化...")

    if not config_git():
        print("配置Git用户信息失败，但将继续...")

    if not add_files():
        print("添加文件失败，退出...")
        return

    if not commit_changes():
        print("提交更改失败，退出...")
        return

    # 检查远程仓库是否已存在
    try:
        result = subprocess.run(
            "git remote -v",
            shell=True,
            check=False,
            text=True,
            capture_output=True
        )
        if "origin" not in result.stdout:
            if not add_remote():
                print("添加远程仓库失败，退出...")
                return
    except Exception as e:
        print(f"检查远程仓库时出错: {e}")
        if not add_remote():
            print("添加远程仓库失败，退出...")
            return

    if not push_to_github():
        print("推送到GitHub失败...")
        print("尝试使用凭证助手...")
        run_command('git config --global credential.helper store')
        push_to_github()

    print("Git上传流程完成！")

if __name__ == "__main__":
    main()
