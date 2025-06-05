import pandas as pd
import re
from typing import Union, Dict, Any
import yaml

def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """加载配置文件"""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def standardize_sales_range(value: str, config: Dict[str, Any]) -> float:
    """标准化销量范围数据"""
    if pd.isna(value) or value == "":
        return config["cleaning_rules"]["sales_range"]["default_value"]
    
    value = str(value).strip().lower()
    
    # 处理范围数据 (例如: "7.5w~10w")
    if "~" in value:
        min_val, max_val = value.split("~")
        min_val = convert_to_number(min_val, config)
        max_val = convert_to_number(max_val, config)
        return (min_val + max_val) / 2
    
    return convert_to_number(value, config)

def convert_to_number(value: str, config: Dict[str, Any]) -> float:
    """转换带单位的数据为数字"""
    value = value.strip().lower()
    unit_conversion = config["cleaning_rules"]["sales_range"]["unit_conversion"]
    
    for unit, multiplier in unit_conversion.items():
        if unit in value:
            return float(value.replace(unit, "")) * multiplier
    
    return float(value)

def standardize_percentage(value: str, config: Dict[str, Any]) -> float:
    """标准化百分比数据"""
    if pd.isna(value) or value == "":
        return config["cleaning_rules"]["percentage"]["default_value"]
    
    value = str(value).strip()
    
    # 处理范围数据 (例如: "10%~15%")
    if "~" in value:
        min_val, max_val = value.split("~")
        min_val = float(min_val.replace("%", "")) / 100
        max_val = float(max_val.replace("%", "")) / 100
        return round((min_val + max_val) / 2, config["cleaning_rules"]["percentage"]["decimal_places"])
    
    # 处理单个百分比
    return round(float(value.replace("%", "")) / 100, config["cleaning_rules"]["percentage"]["decimal_places"])

def validate_url(url: str, config: Dict[str, Any]) -> str:
    """验证URL链接"""
    if pd.isna(url) or url == "":
        return config["cleaning_rules"]["url_validation"]["default_value"]
    
    url = str(url).strip()
    allowed_domains = config["cleaning_rules"]["url_validation"]["allowed_domains"]
    
    # 检查URL格式
    if not re.match(r"^https?://", url):
        url = "https://" + url
    
    # 检查域名
    for domain in allowed_domains:
        if domain in url:
            return url
    
    return config["cleaning_rules"]["url_validation"]["default_value"]

def clean_dataframe(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    """清洗整个数据框"""
    df_clean = df.copy()
    
    # 处理销量数据
    for field in config["sales_fields"]:
        if field in df_clean.columns:
            df_clean[field] = df_clean[field].astype(str).apply(
                lambda x: standardize_sales_range(x, config)
            )
    
    # 处理百分比数据
    for field in config["percent_fields"]:
        if field in df_clean.columns:
            df_clean[field] = df_clean[field].astype(str).apply(
                lambda x: standardize_percentage(x, config)
            )
    
    # 处理URL数据
    for field in config["url_fields"]:
        if field in df_clean.columns:
            df_clean[field] = df_clean[field].astype(str).apply(
                lambda x: validate_url(x, config)
            )
    
    return df_clean

def detect_anomalies(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    """检测异常值"""
    anomalies = pd.DataFrame()
    
    # 销量异常检测
    for field in config["analysis"]["sales_metrics"]:
        if field in df.columns:
            mean = df[field].mean()
            std = df[field].std()
            threshold = 3  # 3个标准差
            
            field_anomalies = df[
                (df[field] > mean + threshold * std) |
                (df[field] < mean - threshold * std)
            ][[field]]
            
            if not field_anomalies.empty:
                anomalies = pd.concat([anomalies, field_anomalies], axis=1)
    
    return anomalies 