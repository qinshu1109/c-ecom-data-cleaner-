import os
import sys
import argparse
import pandas as pd
import logging
from datetime import datetime
import time
from tqdm import tqdm

# 导入项目模块 - 修改为完整包路径
from douyin_ecom_analyzer.utils import clean_dataframe
from douyin_ecom_analyzer.analyzer import DouyinAnalyzer
from douyin_ecom_analyzer.filter_engine import FilterEngine

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('douyin_main')

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='抖音电商数据分析工具')
    
    parser.add_argument(
        'input_file', 
        help='输入Excel文件路径'
    )
    
    parser.add_argument(
        '-o', '--output', 
        default='./output',
        help='输出目录路径'
    )
    
    parser.add_argument(
        '--sheet', 
        default=0,
        help='要处理的Excel表格名称或索引'
    )
    
    parser.add_argument(
        '--no-url-check',
        action='store_true',
        help='跳过URL有效性检查'
    )
    
    parser.add_argument(
        '--apply-filters',
        action='store_true',
        help='应用filter_rules.yaml中的过滤规则'
    )
    
    parser.add_argument(
        '--rules',
        help='自定义过滤规则文件路径'
    )
    
    return parser.parse_args()

def main():
    """主函数"""
    start_time = time.time()
    
    # 解析命令行参数
    args = parse_args()
    
    # 检查输入文件
    if not os.path.exists(args.input_file):
        logger.error(f"文件不存在: {args.input_file}")
        return 1
    
    logger.info(f"开始处理文件: {args.input_file}")
    
    try:
        # 读取Excel文件
        logger.info("正在读取Excel文件...")
        df = pd.read_excel(args.input_file, sheet_name=args.sheet)
        logger.info(f"成功读取数据: {df.shape[0]}行 x {df.shape[1]}列")
        
        # 打印原始数据列名
        logger.info(f"原始数据列: {', '.join(df.columns)}")
        
        # 清洗数据
        logger.info("正在清洗数据...")
        if args.no_url_check:
            logger.info("已禁用URL检查")
        
        cleaned_df = clean_dataframe(df)
        logger.info(f"数据清洗完成: {cleaned_df.shape[0]}行 x {cleaned_df.shape[1]}列")
        
        # 应用过滤规则（如果启用）
        filtered_df = cleaned_df
        filter_stats = None
        
        if args.apply_filters:
            logger.info("正在应用过滤规则...")
            
            # 初始化过滤引擎
            filter_engine = FilterEngine(args.rules)
            
            # 应用过滤
            filtered_df, filter_stats = filter_engine.filter_data(cleaned_df)
            
            # 输出过滤结果
            logger.info(f"过滤前数据量: {filter_stats['原始数据量']}")
            logger.info(f"过滤后数据量: {filter_stats['过滤后数据量']}")
            logger.info(f"过滤率: {filter_stats['过滤率']}")
            
            for reason, count in filter_stats.get("过滤详情", {}).items():
                logger.info(f"- {reason}: {count}项")
            
            # 生成过滤报告
            filter_report_path = os.path.join(args.output, f'filter_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md')
            filter_engine.generate_filter_report(filter_stats, filter_report_path)
            logger.info(f"过滤报告已保存: {filter_report_path}")
        
        # 创建分析器
        analyzer = DouyinAnalyzer(filtered_df, args.output)
        
        # 运行分析
        logger.info("正在进行数据分析...")
        results = analyzer.run_all_analyses()
        
        # 输出结果
        excel_report = results.get('excel_report')
        if excel_report:
            logger.info(f"报表生成完成: {excel_report}")
        
        for analysis_type, result in results.items():
            if analysis_type != 'excel_report' and result and 'plot_path' in result:
                logger.info(f"{analysis_type}分析完成: {result['plot_path']}")
        
        end_time = time.time()
        logger.info(f"处理完成! 总耗时: {end_time - start_time:.2f}秒")
        
        return 0
        
    except Exception as e:
        logger.exception(f"处理过程中发生错误: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 