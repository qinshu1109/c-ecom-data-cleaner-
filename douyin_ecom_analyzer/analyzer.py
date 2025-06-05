import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime
import logging
import io

# 设置通用字体支持
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Bitstream Vera Sans', 'Arial', 'Liberation Sans', 'sans-serif']  # 使用更通用的字体设置
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 配置日志
logger = logging.getLogger('douyin_analyzer')

class DouyinAnalyzer:
    """抖音电商数据分析器"""

    def __init__(self, df, output_dir='./output'):
        """
        初始化分析器

        Args:
            df: 清洗后的DataFrame
            output_dir: 输出目录
        """
        self.df = df
        self.output_dir = output_dir

        # 初始化分析结果属性
        self.category_counts = None
        self.commission_pivot = None
        self.conversion_counts = None

        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)

        # 当前时间戳（用于文件命名）
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    def generate_summary_stats(self):
        """
        生成描述性统计数据

        Returns:
            DataFrame: 统计摘要
        """
        # 识别数值列
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()

        # 基本统计量
        summary = self.df[numeric_cols].describe()

        # 添加中位数等其他统计量
        for col in numeric_cols:
            summary.loc['中位数', col] = self.df[col].median()
            summary.loc['非空值数', col] = self.df[col].count()
            summary.loc['空值数', col] = self.df[col].isna().sum()
            summary.loc['空值比例', col] = self.df[col].isna().mean()

        return summary

    def sales_analysis(self):
        """销量分析"""
        if '近30天销量_清洗' not in self.df.columns:
            logger.warning("缺少销量数据，跳过销量分析")
            return None

        # 销量分布统计
        sales_data = self.df['近30天销量_清洗'].dropna()

        if len(sales_data) == 0:
            logger.warning("有效销量数据为空，跳过销量分析")
            return None

        # 创建销量区间
        sales_bins = [0, 1000, 5000, 10000, 50000, 100000, float('inf')]
        sales_labels = ['<1k', '1k-5k', '5k-1w', '1w-5w', '5w-10w', '>10w']

        self.df['销量区间'] = pd.cut(
            self.df['近30天销量_清洗'],
            bins=sales_bins,
            labels=sales_labels
        )

        # 统计各区间商品数量
        sales_counts = self.df['销量区间'].value_counts().sort_index()

        # 创建图表
        plt.figure(figsize=(12, 6))
        ax = sales_counts.plot(kind='bar', color='skyblue')

        plt.title('商品销量分布')
        plt.xlabel('销量区间')
        plt.ylabel('商品数量')
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        # 添加数据标签
        for i, v in enumerate(sales_counts):
            ax.text(i, v + 5, str(v), ha='center')

        # 保存图表
        plot_path = os.path.join(self.output_dir, f'sales_distribution_{self.timestamp}.png')
        plt.tight_layout()
        plt.savefig(plot_path, dpi=300)
        plt.close()

        return {
            'plot_path': plot_path,
            'data': sales_counts
        }

    def commission_analysis(self):
        """佣金分析"""
        if '佣金比例_清洗' not in self.df.columns:
            logger.warning("缺少佣金数据，跳过佣金分析")
            return None

        # 佣金比例分布统计
        commission_data = self.df['佣金比例_清洗'].dropna()

        if len(commission_data) == 0:
            logger.warning("有效佣金数据为空，跳过佣金分析")
            return None

        # 创建佣金比例区间
        commission_bins = [0, 0.05, 0.1, 0.15, 0.2, 0.3, 1.0]
        commission_labels = ['0-5%', '5-10%', '10-15%', '15-20%', '20-30%', '>30%']

        self.df['佣金区间'] = pd.cut(
            self.df['佣金比例_清洗'],
            bins=commission_bins,
            labels=commission_labels
        )

        # 统计各区间商品数量
        commission_counts = self.df['佣金区间'].value_counts().sort_index()

        # 创建图表
        plt.figure(figsize=(12, 6))
        ax = commission_counts.plot(kind='bar', color='salmon')

        plt.title('商品佣金比例分布')
        plt.xlabel('佣金区间')
        plt.ylabel('商品数量')
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        # 添加数据标签
        for i, v in enumerate(commission_counts):
            ax.text(i, v + 5, str(v), ha='center')

        # 保存图表
        plot_path = os.path.join(self.output_dir, f'commission_distribution_{self.timestamp}.png')
        plt.tight_layout()
        plt.savefig(plot_path, dpi=300)
        plt.close()

        return {
            'plot_path': plot_path,
            'data': commission_counts
        }

    def correlation_analysis(self):
        """相关性分析"""
        # 获取数值列
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()

        if len(numeric_cols) < 2:
            logger.warning("数值列不足，跳过相关性分析")
            return None

        # 计算相关系数
        corr_matrix = self.df[numeric_cols].corr()

        # 创建热力图
        plt.figure(figsize=(12, 10))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)

        plt.title('数值特征相关性分析')

        # 保存图表
        plot_path = os.path.join(self.output_dir, f'correlation_heatmap_{self.timestamp}.png')
        plt.tight_layout()
        plt.savefig(plot_path, dpi=300)
        plt.close()

        return {
            'plot_path': plot_path,
            'data': corr_matrix
        }

    def url_validation_analysis(self):
        """URL有效性分析"""
        # 查找URL验证结果列
        url_valid_cols = [col for col in self.df.columns if col.endswith('_有效')]

        if not url_valid_cols:
            logger.warning("未找到URL验证结果，跳过URL分析")
            return None

        # 统计各URL的有效率
        valid_rates = {}
        for col in url_valid_cols:
            original_col = col.replace('_有效', '')
            total = self.df[original_col].notna().sum()
            valid = self.df[col].sum()

            if total > 0:
                valid_rates[original_col] = {
                    '有效数': valid,
                    '总数': total,
                    '有效率': valid / total
                }

        if not valid_rates:
            logger.warning("无有效的URL验证结果，跳过URL分析")
            return None

        # 创建图表
        labels = list(valid_rates.keys())
        valid_counts = [data['有效数'] for data in valid_rates.values()]
        invalid_counts = [data['总数'] - data['有效数'] for data in valid_rates.values()]

        plt.figure(figsize=(12, 6))

        x = np.arange(len(labels))
        width = 0.35

        plt.bar(x, valid_counts, width, label='有效链接', color='green')
        plt.bar(x, invalid_counts, width, bottom=valid_counts, label='无效链接', color='red')

        plt.title('URL有效性分析')
        plt.ylabel('链接数量')
        plt.xticks(x, labels)
        plt.legend()

        # 添加百分比标签
        for i, (label, data) in enumerate(valid_rates.items()):
            plt.text(
                i, data['总数'] / 2,
                f"{data['有效率']:.1%}",
                ha='center', va='center',
                color='white', fontweight='bold'
            )

        # 保存图表
        plot_path = os.path.join(self.output_dir, f'url_validation_{self.timestamp}.png')
        plt.tight_layout()
        plt.savefig(plot_path, dpi=300)
        plt.close()

        return {
            'plot_path': plot_path,
            'data': valid_rates
        }

    def generate_excel_report(self):
        """生成Excel报表"""
        # 创建一个BytesIO对象，保存Excel
        output = io.BytesIO()

        # 创建ExcelWriter对象
        writer = pd.ExcelWriter(output, engine='openpyxl')

        # 写入不同的sheet
        self.df.to_excel(writer, sheet_name='原始数据', index=False)

        # 类别分布
        if self.category_counts is not None:
            self.category_counts.to_excel(writer, sheet_name='类别分布')

        # 佣金分布
        if self.commission_pivot is not None:
            self.commission_pivot.to_excel(writer, sheet_name='佣金分布')

        # 转化率分布
        if self.conversion_counts is not None:
            self.conversion_counts.to_excel(writer, sheet_name='转化率分布')

        # 关闭writer，获取输出
        writer.close()  # 修改这里，从save()改为close()

        # 返回输出
        output.seek(0)
        return output

    def run_all_analyses(self):
        """
        运行所有分析并生成报告

        Returns:
            dict: 包含所有分析结果和文件路径的字典
        """
        results = {}

        # 运行各项分析
        results['sales'] = self.sales_analysis()
        results['commission'] = self.commission_analysis()
        results['correlation'] = self.correlation_analysis()
        results['url_validation'] = self.url_validation_analysis()

        # 生成Excel报表
        results['excel_report'] = self.generate_excel_report()

        return results
