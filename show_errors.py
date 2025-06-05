#!/usr/bin/env python3
"""
错误日志提取和展示工具 - 彩色版
"""
import os
import sys
import re
import argparse
from pathlib import Path
from datetime import datetime
import traceback
from colorama import Fore, Back, Style, init

# 初始化colorama
init(autoreset=True)

def find_logs():
    """查找所有可能的日志文件"""
    log_patterns = [
        "./logs/*.log",              # 主日志目录
        "./*.log",                   # 当前目录日志
        "./douyin_ecom_analyzer/*.log",  # 应用目录日志
        "/tmp/*.log"                 # 临时目录
    ]

    log_files = []
    for pattern in log_patterns:
        log_files.extend(list(Path().glob(pattern)))

    return log_files

def extract_last_error(content):
    """提取最后一个完整的错误信息"""
    # 匹配错误模式
    error_patterns = [
        r"Traceback \(most recent call last\):.*?(?:\n.*?)+?\n(.*?Error:.*?)(?:\n|$)",  # Python标准错误
        r"(ERROR.*?Traceback.*?)(?=ERROR|\Z)",  # 日志格式错误
        r"(WARNING.*?SimHei)(?=WARNING|\Z)",  # 字体警告
        r"(AttributeError:.*?)(?=\n\n|\Z)",  # 属性错误
    ]

    for pattern in error_patterns:
        matches = list(re.finditer(pattern, content, re.DOTALL | re.MULTILINE))
        if matches:
            return matches[-1].group(0)  # 返回最后一个匹配

    return None

def extract_errors(content):
    """提取所有错误信息"""
    errors = []

    # 提取完整的错误栈
    traceback_pattern = r"Traceback \(most recent call last\):.*?(?:\n.*?)+?\n.*?Error:.*?(?:\n|$)"
    traceback_errors = re.findall(traceback_pattern, content, re.DOTALL | re.MULTILINE)
    errors.extend(traceback_errors)

    # 提取ERROR日志
    error_pattern = r"ERROR.*?(?:\n(?!ERROR).*?)*"
    error_logs = re.findall(error_pattern, content, re.DOTALL | re.MULTILINE)
    errors.extend([e for e in error_logs if e not in errors])

    # 提取WARNING日志
    warning_pattern = r"WARNING.*?(?:\n(?!WARNING|ERROR).*?)*"
    warning_logs = re.findall(warning_pattern, content, re.DOTALL | re.MULTILINE)

    # 过滤重复的字体警告，只保留一组代表性的
    font_warnings = [w for w in warning_logs if "Generic family 'sans-serif' not found" in w]
    if font_warnings:
        warnings_sample = "字体问题警告 (共出现 {} 次):\n{}".format(len(font_warnings), font_warnings[0].split('\n')[0])
        errors.append(warnings_sample)

    # 过滤其他警告
    other_warnings = [w for w in warning_logs if "Generic family 'sans-serif' not found" not in w and w not in errors]
    errors.extend(other_warnings)

    return errors

def highlight_code(text):
    """高亮显示代码行"""
    lines = text.split('\n')
    result = []

    for line in lines:
        if re.match(r'\s*File ".*", line \d+, in .*', line):
            # 文件路径行
            parts = re.match(r'(\s*File ")(.*)(".*)', line)
            if parts:
                line = parts.group(1) + Fore.CYAN + parts.group(2) + Fore.RESET + parts.group(3)
        elif re.match(r'\s*[a-zA-Z0-9_]+(\.[a-zA-Z0-9_]+)+\(.*\)', line):
            # 函数调用行
            line = Fore.YELLOW + line + Fore.RESET
        elif re.search(r'(Error|Exception|Warning):', line):
            # 错误行
            line = Fore.RED + Style.BRIGHT + line + Style.RESET_ALL

        result.append(line)

    return '\n'.join(result)

def colored_type(error_text):
    """为不同类型的错误添加颜色"""
    if "Error:" in error_text:
        header = f"{Fore.RED}{Style.BRIGHT}错误:{Style.RESET_ALL}"
    elif "WARNING" in error_text:
        header = f"{Fore.YELLOW}警告:{Style.RESET_ALL}"
    elif "INFO" in error_text:
        header = f"{Fore.BLUE}信息:{Style.RESET_ALL}"
    else:
        header = f"{Fore.WHITE}日志:{Style.RESET_ALL}"

    return header + " " + highlight_code(error_text)

def scan_for_errors(silent=False):
    """扫描所有日志文件中的错误"""
    log_files = find_logs()

    if not log_files:
        if not silent:
            print(f"{Fore.YELLOW}没有找到日志文件。请先运行应用程序生成日志。")
        return None

    all_errors = {}
    for log_file in log_files:
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()

            if content.strip():
                errors = extract_errors(content)
                if errors:
                    all_errors[log_file] = errors
        except Exception as e:
            if not silent:
                print(f"{Fore.RED}读取 {log_file} 时出错: {e}")

    return all_errors

def display_error_summary(all_errors, max_errors=3):
    """显示错误摘要"""
    if not all_errors:
        print(f"{Fore.GREEN}没有发现错误！")
        return

    print(f"\n{Fore.CYAN}{Style.BRIGHT}{'='*20} 错误摘要 {'='*20}{Style.RESET_ALL}")

    total_errors = sum(len(errors) for errors in all_errors.values())
    print(f"在 {len(all_errors)} 个日志文件中发现了 {total_errors} 个错误/警告\n")

    for log_file, errors in all_errors.items():
        print(f"{Fore.CYAN}文件: {log_file} ({len(errors)} 个问题){Style.RESET_ALL}")

        # 显示前max_errors个错误
        for i, error in enumerate(errors[:max_errors]):
            # 获取错误的第一行作为摘要
            first_line = error.split('\n')[0]
            print(f"  {i+1}. {colored_type(first_line)}")

        if len(errors) > max_errors:
            print(f"  ...以及 {len(errors) - max_errors} 个更多问题")

        print()

    print(f"{Fore.CYAN}{Style.BRIGHT}{'='*50}{Style.RESET_ALL}")
    print(f"使用 {Fore.YELLOW}--details <日志文件> <错误索引>{Style.RESET_ALL} 查看详细错误信息")

def display_error_details(log_file, error_index):
    """显示特定错误的详细信息"""
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()

        errors = extract_errors(content)
        if not errors:
            print(f"{Fore.YELLOW}在 {log_file} 中没有找到错误")
            return

        if error_index < 0 or error_index >= len(errors):
            print(f"{Fore.YELLOW}错误索引超出范围，应在 0-{len(errors)-1} 之间")
            return

        error = errors[error_index]

        print(f"\n{Fore.CYAN}{Style.BRIGHT}{'='*20} 错误详情 {'='*20}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}文件: {log_file}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}错误 #{error_index+1}/{len(errors)}{Style.RESET_ALL}\n")

        print(colored_type(error))

        print(f"\n{Fore.CYAN}{Style.BRIGHT}{'='*50}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}可能的解决方法:{Style.RESET_ALL}")

        # 根据错误类型提供可能的解决方法
        if "AttributeError: 'XlsxWriter' object has no attribute 'save'" in error:
            print("  1. 使用 writer.close() 替代 writer.save()")
            print("  2. 将Excel引擎从'xlsxwriter'改为'openpyxl'")
            print("  3. 运行 ./fix_errors.py 自动修复")
        elif "Generic family 'sans-serif' not found" in error:
            print("  1. 安装SimHei字体")
            print("  2. 使用替代字体: DejaVu Sans, Arial Unicode MS")
            print("  3. 运行 ./fix_errors.py 自动修复字体问题")
        else:
            print("  请检查错误消息，修复相应的代码问题")

    except Exception as e:
        print(f"{Fore.RED}显示错误详情时出错: {e}")

def main():
    parser = argparse.ArgumentParser(description='彩色错误日志分析工具')
    parser.add_argument('--summary', action='store_true', help='显示所有日志文件的错误摘要')
    parser.add_argument('--details', nargs=2, metavar=('LOG_FILE', 'ERROR_INDEX'), help='显示特定错误的详细信息')
    parser.add_argument('--last', action='store_true', help='显示最后一个错误')
    parser.add_argument('--scan', action='store_true', help='扫描所有日志文件')

    args = parser.parse_args()

    if args.details:
        log_file = args.details[0]
        try:
            error_index = int(args.details[1])
            display_error_details(log_file, error_index)
        except ValueError:
            print(f"{Fore.RED}错误索引必须是数字")
    elif args.last:
        # 显示最后一个错误
        all_errors = scan_for_errors(silent=True)
        if all_errors:
            # 找到最后修改的日志文件
            last_log = max(all_errors.keys(), key=lambda p: p.stat().st_mtime)
            errors = all_errors[last_log]
            if errors:
                print(f"\n{Fore.CYAN}{Style.BRIGHT}{'='*20} 最后一个错误 {'='*20}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}文件: {last_log}{Style.RESET_ALL}\n")
                print(colored_type(errors[-1]))
        else:
            print(f"{Fore.YELLOW}没有找到错误")
    elif args.scan or args.summary:
        all_errors = scan_for_errors()
        if all_errors:
            display_error_summary(all_errors)
    else:
        # 默认行为：显示摘要
        all_errors = scan_for_errors()
        if all_errors:
            display_error_summary(all_errors)
        else:
            parser.print_help()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}操作已取消")
    except Exception as e:
        print(f"{Fore.RED}错误: {e}")
        print(f"{Fore.RED}{traceback.format_exc()}")
