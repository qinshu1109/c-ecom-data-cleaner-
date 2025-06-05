"""
数据转换器模块，提供各种数据格式的转换功能。
"""

import re
from functools import lru_cache
from typing import Union, Optional
import numpy as np
import pandas as pd
import requests
from urllib.parse import urlparse


def parse_sales_to_float(raw: Union[str, int, float, None]) -> Optional[float]:
    """
    将各种销量格式转换为浮点数。

    Args:
        raw: 销量数据，可以是字符串、整数、浮点数或None

    Returns:
        Optional[float]: 转换后的浮点数，如果输入无效则返回None

    Examples:
        >>> parse_sales_to_float('1.2万')
        12000.0
        >>> parse_sales_to_float('3,500+')
        3500.0
        >>> parse_sales_to_float('nan')
        None
    """
    if pd.isna(raw):
        return None
    if isinstance(raw, (int, float)):
        return float(raw)

    s = str(raw).strip().rstrip('+')          # 去掉末尾 '+'
    if s.endswith('万') or s.endswith('w'):
        num = re.sub(r'[^\d\.]', '', s[:-1])  # '1.2万' → '1.2'
        return float(num) * 10_000
    # 普通数字，去掉逗号
    num = re.sub(r'[^\d\.]', '', s)
    return float(num) if num else None


def parse_percent_to_float(raw: Union[str, int, float, None]) -> Optional[float]:
    """
    将百分比格式转换为浮点数。

    Args:
        raw: 百分比数据，可以是字符串、整数、浮点数或None

    Returns:
        Optional[float]: 转换后的浮点数，如果输入无效则返回None

    Examples:
        >>> parse_percent_to_float('36.0%')
        0.36
        >>> parse_percent_to_float('12%')
        0.12
        >>> parse_percent_to_float(0.15)
        0.15
    """
    if pd.isna(raw):
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    s = str(raw).strip().rstrip('%')
    return float(s) / 100.0


@lru_cache(maxsize=1024)
def range_to_mean(range_str: str) -> float:
    """
    将销量区间转换为均值。

    Args:
        range_str: 销量区间字符串，如 "7.5w~10w"

    Returns:
        float: 区间均值，如 87500.0

    Examples:
        >>> range_to_mean("7.5w~10w")
        87500.0
        >>> range_to_mean("1k~2k")
        1500.0
    """
    # 移除所有空格
    range_str = range_str.replace(" ", "")

    # 提取数字和单位
    pattern = r"([\d.]+)([k万w])?~([\d.]+)([k万w])?"
    match = re.match(pattern, range_str)

    if not match:
        raise ValueError(f"Invalid range format: {range_str}")

    # 解析数字和单位
    start_num, start_unit, end_num, end_unit = match.groups()
    start_num = float(start_num)
    end_num = float(end_num)

    # 统一单位转换
    unit_map = {
        'k': 1000,
        '万': 10000,
        'w': 10000,
        None: 1
    }

    # 转换到统一单位
    start_value = start_num * unit_map.get(start_unit, 1)
    end_value = end_num * unit_map.get(end_unit, 1)

    # 计算均值
    return (start_value + end_value) / 2


@lru_cache(maxsize=1024)
def percent_to_float(percent_str: str) -> float:
    """
    将百分比字符串转换为浮点数。

    Args:
        percent_str: 百分比字符串，如 "20.00%" 或 "10%~15%"

    Returns:
        float: 转换后的浮点数，如 0.2 或 0.125

    Examples:
        >>> percent_to_float("20.00%")
        0.2
        >>> percent_to_float("10%~15%")
        0.125
    """
    # 移除所有空格
    percent_str = percent_str.replace(" ", "")

    # 处理区间
    if "~" in percent_str:
        pattern = r"([\d.]+)%?~([\d.]+)%?"
        match = re.match(pattern, percent_str)
        if not match:
            raise ValueError(f"Invalid percent range format: {percent_str}")

        start, end = map(float, match.groups())
        return (start + end) / 200  # 除以200是因为要转换为0-1范围

    # 处理单个百分比
    else:
        pattern = r"([\d.]+)%"
        match = re.match(pattern, percent_str)
        if not match:
            raise ValueError(f"Invalid percent format: {percent_str}")

        return float(match.group(1)) / 100


@lru_cache(maxsize=1024)
def validate_url(url: str) -> Union[str, float]:
    """
    验证URL是否可访问，返回有效URL或np.nan。

    Args:
        url: 要验证的URL字符串

    Returns:
        Union[str, float]: 如果URL有效则返回URL，否则返回np.nan

    Examples:
        >>> validate_url("https://haohuo.douyin.com/123")
        "https://haohuo.douyin.com/123"
        >>> validate_url("invalid-url")
        nan
    """
    if not url or not isinstance(url, str):
        return np.nan

    # 检查URL格式
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            return np.nan
    except:
        return np.nan

    # 检查URL可访问性
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        if response.status_code == 200:
            return url
    except:
        pass

    return np.nan
