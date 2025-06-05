import pandas as pd
import numpy as np
import pytest
from pathlib import Path
import sys

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))

from cleaning.filter_engine import filter_dataframe, load_rules
from cleaning.converters import range_mid, commission_to_float, conversion_to_float

def test_range_mid():
    assert range_mid("7.5w~10w") == 87500
    assert range_mid("5000") == 5000
    assert range_mid("1.5万-2万") == 17500

def test_commission_to_float():
    assert commission_to_float("20.00%") == 0.2
    assert commission_to_float("10%~15%") == 0.125
    assert commission_to_float("5-10%") == 0.075

def test_conversion_to_float():
    assert conversion_to_float("15%") == 0.15
    assert conversion_to_float(0.2) == 0.2

def test_filter_dataframe():
    # 创建测试数据
    test_data = {
        "近7天销量值": [6000, 4000, 8000, 10000],
        "近30天销量值": [30000, 20000, 40000, 50000],
        "佣金比例值": [0.25, 0.15, 0, 0.3],
        "转化率值": [0.2, 0.1, 0.25, 0.16],
        "关联达人": [60, 40, 100, 30],
        "商品名称": ["测试商品", "端午文创商品", "普通商品", "艾草挂饰套装"]
    }
    
    df = pd.DataFrame(test_data)
    
    # 测试规则过滤
    rules = {
        "sales": {"last_7d_min": 5000, "last_30d_min": 25000},
        "commission": {"min_rate": 0.20, "zero_rate_conversion_min": 0.20},
        "conversion": {"min_rate": 0.15},
        "influencer": {"min_count": 50},
        "categories": {"blacklist": ["端午文创", "艾草挂饰"]}
    }
    
    filtered_df = filter_dataframe(df, rules)
    
    # 验证结果
    assert len(filtered_df) == 1
    assert filtered_df.iloc[0]["商品名称"] == "测试商品"

if __name__ == "__main__":
    test_range_mid()
    test_commission_to_float()
    test_conversion_to_float()
    test_filter_dataframe()
    print("所有测试通过!") 