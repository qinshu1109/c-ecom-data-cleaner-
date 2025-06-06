#!/usr/bin/env python3
"""
通过GitHub API上传文件到仓库
使用方法:
1. 设置环境变量GITHUB_TOKEN为你的GitHub Personal Access Token
2. 运行脚本: python github_upload.py
"""

import os
import base64
import json
import requests
from pathlib import Path

# 仓库信息
REPO_OWNER = "qinshu1109"
REPO_NAME = "c-ecom-data-cleaner-"
BRANCH = "main"

# 获取GitHub Token
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    print("错误: 未设置GITHUB_TOKEN环境变量")
    print("请创建一个Personal Access Token: https://github.com/settings/tokens")
    print("然后设置环境变量: export GITHUB_TOKEN=your_token")
    exit(1)

# API基础URL
API_BASE = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"

# 设置请求头
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def create_repo_if_not_exists():
    """如果仓库不存在，则创建仓库"""
    print(f"检查仓库 {REPO_OWNER}/{REPO_NAME} 是否存在...")

    # 检查仓库是否存在
    response = requests.get(
        f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}",
        headers=HEADERS
    )

    if response.status_code == 404:
        print(f"仓库不存在，正在创建...")

        # 创建仓库
        create_response = requests.post(
            "https://api.github.com/user/repos",
            headers=HEADERS,
            json={
                "name": REPO_NAME,
                "description": "抖音电商数据分析工具",
                "private": False,
                "auto_init": True
            }
        )

        if create_response.status_code not in [201, 200]:
            print(f"创建仓库失败: {create_response.status_code}")
            print(create_response.json())
            return False

        print("仓库创建成功！")
        return True

    elif response.status_code == 200:
        print("仓库已存在，继续上传文件...")
        return True

    else:
        print(f"检查仓库时发生错误: {response.status_code}")
        print(response.json())
        return False

def get_file_list():
    """获取要上传的文件列表"""
    excluded_dirs = [".git", ".pytest_cache", "__pycache__", ".ruff_cache", "node_modules", ".cursor"]
    excluded_files = [".DS_Store", ".gitignore", "git_upload.py", "github_upload.py"]

    files_to_upload = []

    for path in Path(".").rglob("*"):
        # 排除目录
        if path.is_dir():
            continue

        # 排除特定目录下的文件
        if any(excluded in path.parts for excluded in excluded_dirs):
            continue

        # 排除特定文件
        if path.name in excluded_files:
            continue

        files_to_upload.append(str(path))

    return files_to_upload

def upload_file(file_path):
    """上传单个文件到GitHub"""
    print(f"上传文件: {file_path}")

    try:
        # 读取文件内容
        with open(file_path, 'rb') as file:
            content = file.read()

        # Base64编码文件内容
        content_encoded = base64.b64encode(content).decode('utf-8')

        # 构建API请求
        url = f"{API_BASE}/contents/{file_path}"
        data = {
            "message": f"上传文件: {file_path}",
            "content": content_encoded,
            "branch": BRANCH
        }

        # 发送API请求
        response = requests.put(url, headers=HEADERS, json=data)

        # 检查响应
        if response.status_code in [201, 200]:
            print(f"✅ 文件 {file_path} 上传成功！")
            return True
        else:
            print(f"❌ 文件 {file_path} 上传失败: {response.status_code}")
            print(response.json())
            return False

    except Exception as e:
        print(f"❌ 上传文件 {file_path} 时出错: {e}")
        return False

def main():
    """主函数"""
    print("开始上传文件到GitHub仓库...")

    # 检查/创建仓库
    if not create_repo_if_not_exists():
        print("仓库准备失败，退出...")
        return

    # 获取文件列表
    files = get_file_list()
    print(f"找到 {len(files)} 个文件需要上传")

    # 优先上传重要文件
    priority_files = ["README.md", "requirements.txt", "app.py", "run_web.py", "filter_rules.yaml"]
    for priority_file in priority_files:
        if priority_file in files:
            files.remove(priority_file)
            upload_file(priority_file)

    # 上传其余文件
    success_count = 0
    for file in files:
        if upload_file(file):
            success_count += 1

    # 总结
    print("\n上传完成！")
    print(f"成功上传: {success_count + len([f for f in priority_files if Path(f).exists()])} 个文件")
    print(f"失败: {len(files) + len(priority_files) - success_count - len([f for f in priority_files if Path(f).exists()])} 个文件")
    print(f"\n仓库地址: https://github.com/{REPO_OWNER}/{REPO_NAME}")

if __name__ == "__main__":
    main()
