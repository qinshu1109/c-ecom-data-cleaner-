"""
数据清洗器模块，提供主要的数据清洗功能。
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union
from concurrent.futures import ThreadPoolExecutor
from .converters import range_to_mean, percent_to_float, validate_url


class DataCleaner:
    """
    数据清洗器类，提供数据清洗的主要功能。
    """

    def __init__(self, config: Dict):
        """
        初始化数据清洗器。

        Args:
            config: 配置字典，包含字段映射和清洗规则
        """
        self.config = config
        self.sales_fields = config.get("sales_fields", [])
        self.percent_fields = config.get("percent_fields", [])
        self.url_fields = config.get("url_fields", [])

    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        清洗整个DataFrame。

        Args:
            df: 输入的DataFrame

        Returns:
            pd.DataFrame: 清洗后的DataFrame
        """
        # 创建副本避免修改原始数据
        df_clean = df.copy()
        
        # 并行处理各个字段
        with ThreadPoolExecutor() as executor:
            # 清洗销量字段
            for field in self.sales_fields:
                if field in df_clean.columns:
                    df_clean[field] = executor.submit(
                        self._clean_sales_field, df_clean[field]
                    ).result()
            
            # 清洗百分比字段
            for field in self.percent_fields:
                if field in df_clean.columns:
                    df_clean[field] = executor.submit(
                        self._clean_percent_field, df_clean[field]
                    ).result()
            
            # 清洗URL字段
            for field in self.url_fields:
                if field in df_clean.columns:
                    df_clean[field] = executor.submit(
                        self._clean_url_field, df_clean[field]
                    ).result()
        
        return df_clean

    def _clean_sales_field(self, series: pd.Series) -> pd.Series:
        """
        清洗销量字段。

        Args:
            series: 销量数据序列

        Returns:
            pd.Series: 清洗后的销量数据
        """
        return series.apply(
            lambda x: range_to_mean(x) if pd.notna(x) else np.nan
        )

    def _clean_percent_field(self, series: pd.Series) -> pd.Series:
        """
        清洗百分比字段。

        Args:
            series: 百分比数据序列

        Returns:
            pd.Series: 清洗后的百分比数据
        """
        return series.apply(
            lambda x: percent_to_float(x) if pd.notna(x) else np.nan
        )

    def _clean_url_field(self, series: pd.Series) -> pd.Series:
        """
        清洗URL字段。

        Args:
            series: URL数据序列

        Returns:
            pd.Series: 清洗后的URL数据
        """
        return series.apply(
            lambda x: validate_url(x) if pd.notna(x) else np.nan
        )

    def get_cleaning_stats(self, df: pd.DataFrame) -> Dict:
        """
        获取数据清洗统计信息。

        Args:
            df: 清洗后的DataFrame

        Returns:
            Dict: 清洗统计信息
        """
        stats = {
            "total_rows": len(df),
            "cleaned_fields": {},
            "anomalies": {}
        }
        
        # 统计销量字段
        for field in self.sales_fields:
            if field in df.columns:
                stats["cleaned_fields"][field] = {
                    "non_null": df[field].count(),
                    "null_count": df[field].isna().sum(),
                    "mean": df[field].mean(),
                    "std": df[field].std()
                }
        
        # 统计百分比字段
        for field in self.percent_fields:
            if field in df.columns:
                stats["cleaned_fields"][field] = {
                    "non_null": df[field].count(),
                    "null_count": df[field].isna().sum(),
                    "mean": df[field].mean(),
                    "std": df[field].std()
                }
        
        # 统计URL字段
        for field in self.url_fields:
            if field in df.columns:
                stats["cleaned_fields"][field] = {
                    "non_null": df[field].count(),
                    "null_count": df[field].isna().sum(),
                    "valid_urls": df[field].notna().sum()
                }
        
        return stats 