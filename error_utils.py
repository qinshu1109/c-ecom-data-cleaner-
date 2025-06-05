#!/usr/bin/env python3
"""
错误日志查看和管理工具
"""
import os
import sys
from pathlib import Path
import argparse
import re
from datetime import datetime

def setup_logging():
    """设置日志目录"""
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    return logs_dir

def list_log_files(logs_dir):
    """列出所有日志文件"""
    log_files = list(logs_dir.glob("*.log"))
    if not log_files:
        print("没有找到日志文件")
        return []

    print("可用日志文件:")
    for i, log_file in enumerate(log_files, 1):
        size = log_file.stat().st_size / 1024  # 转为KB
        mtime = datetime.fromtimestamp(log_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        print(f"{i}. {log_file.name} ({size:.1f}KB) - 最后修改: {mtime}")

    return log_files

def extract_errors(log_file, pattern=None):
    """提取日志文件中的错误"""
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取错误和回溯
    error_pattern = r'(ERROR.*?(?:Traceback.*?(?:\n.*?)+?\n.*?Error.*?))'
    if pattern:
        error_pattern = pattern

    errors = re.findall(error_pattern, content, re.DOTALL | re.MULTILINE)
    return errors

def view_log(log_file, show_errors_only=False, export_path=None):
    """查看日志文件内容"""
    if show_errors_only:
        errors = extract_errors(log_file)
        if not errors:
            print(f"在 {log_file} 中没有发现错误")
            return

        content = "\n\n" + "\n\n".join(errors)
    else:
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()

    if export_path:
        with open(export_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"日志已导出到 {export_path}")
    else:
        print("\n" + "="*50)
        print(f"日志文件: {log_file}")
        print("="*50)
        print(content)

def search_log(log_file, search_term):
    """在日志中搜索关键词"""
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.readlines()

    matches = []
    for i, line in enumerate(content):
        if search_term.lower() in line.lower():
            start = max(0, i-2)
            end = min(len(content), i+3)
            context = ''.join(content[start:end])
            matches.append((i+1, context))

    if not matches:
        print(f"在 {log_file} 中没有找到 '{search_term}'")
    else:
        print(f"在 {log_file} 中找到 {len(matches)} 处匹配:")
        for line_num, context in matches:
            print(f"\n--- 行 {line_num} ---\n{context}")

def main():
    parser = argparse.ArgumentParser(description='错误日志查看和管理工具')
    parser.add_argument('--list', action='store_true', help='列出所有日志文件')
    parser.add_argument('--view', type=str, help='查看指定日志文件内容')
    parser.add_argument('--errors', action='store_true', help='只显示错误和回溯')
    parser.add_argument('--search', type=str, help='搜索关键词')
    parser.add_argument('--export', type=str, help='导出日志到文件')

    args = parser.parse_args()
    logs_dir = setup_logging()

    if args.list or (not args.view and not args.search):
        list_log_files(logs_dir)
        return

    if args.view:
        log_path = logs_dir / args.view if not os.path.exists(args.view) else Path(args.view)
        if not log_path.exists():
            log_files = list_log_files(logs_dir)
            try:
                index = int(args.view) - 1
                if 0 <= index < len(log_files):
                    log_path = log_files[index]
                else:
                    print(f"无效的索引: {args.view}")
                    return
            except ValueError:
                print(f"找不到日志文件: {args.view}")
                return

        if args.search:
            search_log(log_path, args.search)
        else:
            view_log(log_path, args.errors, args.export)

if __name__ == "__main__":
    main()
