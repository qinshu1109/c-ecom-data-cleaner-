from __future__ import annotations
import io, yaml, re
import pandas as pd
import numpy as np
from pathlib import Path
from functools import lru_cache

_RULE_PATH = Path("filter_rules.yaml")

@lru_cache(maxsize=1)
def _load_rules(mtime: float | None = None) -> dict:
    # mtime 参数只为触发 lru_cache 失效
    with _RULE_PATH.open(encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_rules() -> dict:
    return _load_rules(_RULE_PATH.stat().st_mtime)

def filter_dataframe(df: pd.DataFrame, rules: dict | None = None) -> pd.DataFrame:
    r = rules or load_rules()
    
    # 创建副本避免修改原始数据
    df_copy = df.copy()
    
    # 确保数值列是数值类型
    numeric_cols = ["近7天销量值", "近30天销量值", "佣金比例值", "转化率值", "关联达人"]
    for col in numeric_cols:
        if col in df_copy.columns:
            df_copy[col] = pd.to_numeric(df_copy[col], errors='coerce').fillna(0)
    
    # 确保商品名称列是字符串类型
    if "商品名称" in df_copy.columns:
        df_copy["商品名称"] = df_copy["商品名称"].astype(str)

    # 构建过滤条件
    cond = pd.Series(True, index=df_copy.index)
    
    # 销量过滤
    if "近7天销量值" in df_copy.columns and "sales" in r and "last_7d_min" in r["sales"]:
        cond &= df_copy["近7天销量值"] >= r["sales"]["last_7d_min"]
    
    if "近30天销量值" in df_copy.columns and "sales" in r and "last_30d_min" in r["sales"]:
        cond &= df_copy["近30天销量值"] >= r["sales"]["last_30d_min"]
    
    # 佣金和转化率过滤
    if "佣金比例值" in df_copy.columns and "commission" in r:
        if "min_rate" in r["commission"] and "转化率值" in df_copy.columns and "zero_rate_conversion_min" in r["commission"]:
            # 佣金率高于最低要求 或 零佣金但转化率高
            cond &= (
                (df_copy["佣金比例值"] >= r["commission"]["min_rate"]) | 
                ((df_copy["佣金比例值"] == 0) & (df_copy["转化率值"] >= r["commission"]["zero_rate_conversion_min"]))
            )
    
    # 转化率过滤
    if "转化率值" in df_copy.columns and "conversion" in r and "min_rate" in r["conversion"]:
        cond &= df_copy["转化率值"] >= r["conversion"]["min_rate"]
    
    # KOL数量过滤
    if "关联达人" in df_copy.columns and "influencer" in r and "min_count" in r["influencer"]:
        cond &= df_copy["关联达人"] >= r["influencer"]["min_count"]
    
    # 类别黑名单过滤
    if "商品名称" in df_copy.columns and "categories" in r and "blacklist" in r["categories"] and r["categories"]["blacklist"]:
        blacklist_pattern = "|".join(r["categories"]["blacklist"])
        # 黑名单模式：排除包含黑名单关键词的商品
        cond &= ~df_copy["商品名称"].str.contains(blacklist_pattern, case=False, na=False)
    
    # 应用过滤条件并返回结果
    return df_copy.loc[cond].reset_index(drop=True) 