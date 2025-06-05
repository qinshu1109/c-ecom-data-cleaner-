import re
import pandas as pd
import numpy as np
import requests
from tqdm import tqdm
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('douyin_cleaner')

def clean_sales_volume(value):
    """
    清洗销量数据，处理带w/万/k的格式和区间
    
    Args:
        value: 原始销量值，如 "7.5w~10w", "3k-5k", "2000-3000"
    
    Returns:
        float: 转换后的销量数值（区间取均值）
    """
    if pd.isna(value) or value == '':
        return np.nan
    
    # 转为字符串
    value = str(value).lower().replace('，', ',').replace(' ', '')
    
    # 检查是否为区间
    if '~' in value or '-' in value or ',' in value:
        separator = '~' if '~' in value else '-' if '-' in value else ','
        parts = value.split(separator)
        
        # 处理每个部分并取均值
        clean_parts = []
        for part in parts:
            clean_parts.append(parse_number_with_unit(part))
        
        return sum(clean_parts) / len(clean_parts)
    else:
        return parse_number_with_unit(value)

def parse_number_with_unit(value):
    """解析带单位的数字"""
    if pd.isna(value) or value == '':
        return np.nan
    
    value = str(value).lower().strip()
    
    # 提取数字和单位
    match = re.search(r'([\d.]+)([wk万千]?)', value)
    if not match:
        try:
            return float(value)
        except ValueError:
            return np.nan
    
    number, unit = match.groups()
    number = float(number)
    
    # 根据单位转换
    if unit in ['w', '万']:
        return number * 10000
    elif unit in ['k', '千']:
        return number * 1000
    else:
        return number

def clean_commission_rate(value):
    """
    清洗佣金比例，统一转为0-1之间的浮点数
    
    Args:
        value: 原始佣金值，如 "20.00%", "10%~15%"
    
    Returns:
        float: 转换后的佣金比例（区间取均值）
    """
    if pd.isna(value) or value == '':
        return np.nan
    
    value = str(value).replace(' ', '')
    
    # 移除百分号
    value = value.replace('%', '')
    
    # 检查是否为区间
    if '~' in value or '-' in value:
        separator = '~' if '~' in value else '-'
        parts = value.split(separator)
        try:
            rates = [float(part) for part in parts]
            avg_rate = sum(rates) / len(rates)
            return avg_rate / 100  # 转为小数
        except ValueError:
            return np.nan
    else:
        try:
            return float(value) / 100  # 转为小数
        except ValueError:
            return np.nan

def validate_url(url, timeout=2):
    """
    验证URL是否可访问
    
    Args:
        url: 要验证的URL
        timeout: 超时时间（秒）
    
    Returns:
        bool: URL是否有效
    """
    if pd.isna(url) or not isinstance(url, str):
        return False
    
    # 验证URL格式
    if not url.startswith(('http://', 'https://')):
        return False
    
    try:
        # 发送HEAD请求检查URL是否可访问
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        return response.status_code < 400
    except requests.RequestException:
        return False

def batch_validate_urls(df, url_columns, max_workers=10):
    """
    批量验证DataFrame中的URL
    
    Args:
        df: 包含URL的DataFrame
        url_columns: URL列名列表
        max_workers: 并行处理的最大工作线程数
    
    Returns:
        DataFrame: 添加了URL验证结果的DataFrame
    """
    from concurrent.futures import ThreadPoolExecutor
    
    result_df = df.copy()
    
    for col in url_columns:
        if col not in df.columns:
            logger.warning(f"列 {col} 不存在，跳过验证")
            continue
        
        valid_col = f"{col}_有效"
        result_df[valid_col] = False
        
        urls = df[col].dropna().tolist()
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(tqdm(
                executor.map(validate_url, urls),
                total=len(urls),
                desc=f"验证 {col}"
            ))
        
        # 将结果填回DataFrame
        valid_dict = dict(zip(urls, results))
        result_df.loc[df[col].notna(), valid_col] = df.loc[df[col].notna(), col].map(valid_dict)
    
    return result_df

def clean_dataframe(df):
    """
    清洗整个DataFrame
    
    Args:
        df: 原始DataFrame
    
    Returns:
        DataFrame: 清洗后的DataFrame
    """
    # 创建副本避免修改原始数据
    cleaned_df = df.copy()
    
    # 基本清洗：去除前后空格，替换特殊字符等
    for col in cleaned_df.columns:
        if cleaned_df[col].dtype == 'object':
            cleaned_df[col] = cleaned_df[col].astype(str).str.strip()
    
    # 特定字段清洗
    if '近30天销量' in cleaned_df.columns:
        cleaned_df['近30天销量_清洗'] = cleaned_df['近30天销量'].apply(clean_sales_volume)
    
    if '佣金比例' in cleaned_df.columns:
        cleaned_df['佣金比例_清洗'] = cleaned_df['佣金比例'].apply(clean_commission_rate)
    
    # 验证URL列
    url_columns = [col for col in cleaned_df.columns if '链接' in col]
    if url_columns:
        cleaned_df = batch_validate_urls(cleaned_df, url_columns)
    
    return cleaned_df 