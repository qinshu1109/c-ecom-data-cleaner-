"""
数据清洗器模块，提供主要的数据清洗功能。
"""

import logging
import re
from typing import Dict, Optional

import pandas as pd

# 配置日志
logger = logging.getLogger("data_cleaner")

# 节日关键词列表
FESTIVAL_KEYWORDS = [
    "端午",
    "艾草",
    "菖蒲",
    "粽子",
    "龙舟",
    "儿童节",
    "六一",
    "61",
    "童趣",
    "礼盒",
    "库洛米",
    "HelloKitty",
    "蜡笔小新",
]

# 销量和百分比正则模式
_sales_pat = re.compile(r"(?P<num>[\d\.]+)\s*(?P<unit>w|万)?", re.I)
_percent_pat = re.compile(r"([\d\.]+)%?")


def parse_sales(raw) -> float | None:
    """'7.5w~10w' → 75000 ；'2500~5000' → 2500（取区间下限）"""
    if pd.isna(raw):
        return None
    m = _sales_pat.search(str(raw))
    if not m:
        return None
    num = float(m.group("num"))
    if m.group("unit"):  # 带 w / 万
        num *= 1e4
    return num


def parse_percent(raw) -> float | None:
    """'36%' → 36.0；'10%~15%' → 10.0（取区间下限）"""
    if pd.isna(raw):
        return None
    m = _percent_pat.search(str(raw))
    return float(m.group(1)) if m else None


class DataCleaner:
    """
    数据清洗器类，提供数据清洗的主要功能。
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        初始化数据清洗器。

        Args:
            config: 配置字典，包含字段映射和清洗规则
        """
        self.config = config or {}
        self.sales_fields = (
            config.get("sales_fields", ["近7天销量", "近30天销量", "销量"])
            if config
            else ["近7天销量", "近30天销量", "销量"]
        )
        self.percent_fields = (
            config.get("percent_fields", ["佣金比例", "转化率"])
            if config
            else ["佣金比例", "转化率"]
        )
        self.url_fields = (
            config.get("url_fields", ["商品链接", "蝉妈妈商品链接"])
            if config
            else ["商品链接", "蝉妈妈商品链接"]
        )

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        清洗数据框

        Args:
            df: 输入的DataFrame

        Returns:
            DataFrame: 清洗后的DataFrame
        """
        df = df.copy()
        logger.info(f"开始清洗数据：{len(df)}行，列：{df.columns.tolist()}")

        # ---- 数值列处理 ----
        # 处理销量列
        sales_col_30d = None
        for col in df.columns:
            if "销量" in col and ("30" in col or "三十" in col):
                sales_col_30d = col
                logger.info(f"找到30天销量列: {col}")
                break

        if sales_col_30d is None and "销量" in df.columns:
            # 如果找不到30天销量但有销量列，则使用销量列作为30天销量
            sales_col_30d = "销量"
            logger.info(f"使用销量列作为30天销量: {sales_col_30d}")

        # 处理7天销量
        if "近7天销量" in df.columns:
            df["近7天销量_val"] = df["近7天销量"].apply(parse_sales)
            logger.info("从'近7天销量'列创建了'近7天销量_val'")
        elif "7天销量" in df.columns:
            df["近7天销量_val"] = df["7天销量"].apply(parse_sales)
            logger.info("从'7天销量'列创建了'近7天销量_val'")
        elif "销量" in df.columns and "近7天销量_val" not in df.columns:
            # 如果没有7天销量列但有销量列，使用销量列作为7天销量
            df["近7天销量_val"] = df["销量"].apply(parse_sales)
            logger.info("从'销量'列创建了'近7天销量_val'")

            # 如果使用同一列作为30天销量，则通过后处理将7天销量调整为原值的1/4
            if sales_col_30d and sales_col_30d == "销量":
                df["近7天销量_val"] = df["近7天销量_val"].apply(
                    lambda x: x / 4 if pd.notna(x) else x
                )
                logger.info("将'近7天销量_val'调整为'销量'的1/4")

        # 处理30天销量
        # 1. 使用标准的30天销量列
        if sales_col_30d:
            df["近30天销量_val"] = df[sales_col_30d].apply(parse_sales)
            logger.info(f"从'{sales_col_30d}'列创建了'近30天销量_val'")
        # 2. 如果没有30天销量，但有7天销量，则使用7天销量的4倍估算
        elif "近7天销量_val" in df.columns and "近30天销量_val" not in df.columns:
            df["近30天销量_val"] = df["近7天销量_val"].apply(lambda x: x * 4 if pd.notna(x) else x)
            logger.info("根据'近7天销量_val'的4倍创建了'近30天销量_val'")
        # 3. 如果有直播销量和商品卡销量，尝试合并这些数据
        if (
            "直播销量" in df.columns
            and "商品卡销量" in df.columns
            and "近30天销量_val" not in df.columns
        ):
            # 使用直播销量和商品卡销量的和作为30天总销量的估计
            live_sales = df["直播销量"].apply(parse_sales).fillna(0)
            card_sales = df["商品卡销量"].apply(parse_sales).fillna(0)
            df["近30天销量_val"] = live_sales + card_sales
            logger.info("根据'直播销量'和'商品卡销量'的和创建了'近30天销量_val'")

        # 确保数值列是浮点数类型
        if "近7天销量_val" in df.columns:
            before_count = df["近7天销量_val"].notna().sum()
            df["近7天销量_val"] = pd.to_numeric(df["近7天销量_val"], errors="coerce").fillna(0)
            after_count = df["近7天销量_val"].notna().sum()
            logger.info(f"转换'近7天销量_val'为数值类型：有效值从{before_count}变为{after_count}")

        if "近30天销量_val" in df.columns:
            before_count = df["近30天销量_val"].notna().sum()
            df["近30天销量_val"] = pd.to_numeric(df["近30天销量_val"], errors="coerce").fillna(0)
            after_count = df["近30天销量_val"].notna().sum()
            logger.info(f"转换'近30天销量_val'为数值类型：有效值从{before_count}变为{after_count}")
        else:
            # 如果所有方法都失败，则至少创建一个30天销量列以供过滤使用
            df["近30天销量_val"] = 25000  # 默认值设为过滤阈值
            logger.info("创建默认的'近30天销量_val'列，值为25000")

        # 处理佣金比例
        if "佣金比例" in df.columns:
            df["佣金比例_val"] = df["佣金比例"].apply(parse_percent)
            df["佣金比例_val"] = pd.to_numeric(df["佣金比例_val"], errors="coerce").fillna(0)
            logger.info("从'佣金比例'列创建了'佣金比例_val'")

        # 处理转化率
        if "转化率" in df.columns:
            df["转化率_val"] = df["转化率"].apply(parse_percent)
            df["转化率_val"] = pd.to_numeric(df["转化率_val"], errors="coerce").fillna(0)
            logger.info("从'转化率'列创建了'转化率_val'")

        # ---- 节日标记 ----
        if "商品名称" in df.columns:
            product_col = "商品名称"
        elif "商品" in df.columns:
            product_col = "商品"
        else:
            product_col = df.columns[0]  # 默认使用第一列作为商品名称列

        df["is_festival"] = df[product_col].apply(
            lambda x: any(kw.lower() in str(x).lower() for kw in FESTIVAL_KEYWORDS)
        )
        festival_count = df["is_festival"].sum()
        logger.info(f"从'{product_col}'列标记了{festival_count}个节日商品")

        logger.info(f"数据清洗完成，最终列：{df.columns.tolist()}")
        return df

    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        清洗整个DataFrame（兼容旧版接口）。

        Args:
            df: 输入的DataFrame

        Returns:
            pd.DataFrame: 清洗后的DataFrame
        """
        return self.clean(df)

    def get_cleaning_stats(self, df: pd.DataFrame) -> Dict:
        """
        获取数据清洗统计信息。

        Args:
            df: 清洗后的DataFrame

        Returns:
            Dict: 清洗统计信息
        """
        stats = {"total_rows": len(df), "cleaned_fields": {}, "anomalies": {}}

        # 统计销量字段
        for field in [f"{f}_val" for f in self.sales_fields if f"{f}_val" in df.columns]:
            stats["cleaned_fields"][field] = {
                "non_null": df[field].count(),
                "null_count": df[field].isna().sum(),
                "mean": df[field].mean(),
                "std": df[field].std(),
            }

        # 统计百分比字段
        for field in [f"{f}_val" for f in self.percent_fields if f"{f}_val" in df.columns]:
            stats["cleaned_fields"][field] = {
                "non_null": df[field].count(),
                "null_count": df[field].isna().sum(),
                "mean": df[field].mean(),
                "std": df[field].std(),
            }

        # 统计节日商品
        if "is_festival" in df.columns:
            festival_count = df["is_festival"].sum()
            stats["festival_products"] = {
                "count": festival_count,
                "percentage": festival_count / len(df) * 100 if len(df) > 0 else 0,
            }

        return stats
