#!/usr/bin/env python
"""
启动抖音电商数据分析工具

用法:
1. 命令行模式: python run.py cli input.xlsx
2. Web界面模式: python run.py web
"""

import sys
import os
import argparse
import subprocess
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('douyin_runner')

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='抖音电商数据分析工具启动器')
    
    parser.add_argument(
        'mode', 
        choices=['cli', 'web', 'sample'],
        help='运行模式: cli=命令行, web=Web界面, sample=生成样例数据'
    )
    
    parser.add_argument(
        'input_file', 
        nargs='?',
        help='输入Excel文件路径 (仅CLI模式需要)'
    )
    
    parser.add_argument(
        '-o', '--output', 
        default='./output',
        help='输出目录路径'
    )
    
    parser.add_argument(
        '--rows', 
        type=int,
        default=500,
        help='样例数据行数 (仅sample模式需要)'
    )
    
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_args()
    
    # 获取当前脚本所在目录作为基础路径
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    try:
        if args.mode == 'cli':
            # 检查命令行模式所需的参数
            if not args.input_file:
                logger.error("CLI模式需要提供输入文件路径")
                return 1
                
            # 运行命令行模式
            from douyin_ecom_analyzer.main import main as cli_main
            
            # 修改sys.argv以符合main.py的参数格式
            sys.argv = [
                'main.py', 
                args.input_file,
                '--output', args.output
            ]
            
            return cli_main()
            
        elif args.mode == 'web':
            # 运行Web界面
            logger.info("启动Web界面...")
            import streamlit
            
            # 获取app.py的完整路径
            app_path = os.path.join(base_dir, 'app.py')
            
            # 使用子进程运行streamlit
            cmd = [sys.executable, '-m', 'streamlit', 'run', app_path]
            subprocess.run(cmd)
            
            return 0
            
        elif args.mode == 'sample':
            # 生成样例数据
            logger.info(f"生成{args.rows}行样例数据...")
            
            # 导入样例数据生成模块
            from douyin_ecom_analyzer.data.sample_data import generate_sample_data
            
            # 设置输出文件路径
            sample_file = os.path.join(os.path.dirname(base_dir), 'data', 'douyin_sample_data.xlsx')
            os.makedirs(os.path.dirname(sample_file), exist_ok=True)
            
            # 生成样例数据
            generate_sample_data(args.rows, sample_file)
            
            logger.info(f"样例数据已生成: {sample_file}")
            return 0
            
    except Exception as e:
        logger.exception(f"运行过程中发生错误: {str(e)}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main()) 