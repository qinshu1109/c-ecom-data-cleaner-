import sys
from pathlib import Path

import pandas as pd

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))

# 从douyin_ecom_analyzer包中导入
from douyin_ecom_analyzer.cleaning.converters import range_mid, commission_to_float, conversion_to_float
from douyin_ecom_analyzer.cleaning.filter_engine import filter_dataframe

def test_range_mid():
    assert range_mid("7.5w~10w") == 87500
    assert range_mid("5000") == 5000
    assert range_mid("1.5万-2万") == 17500

def test_commission_to_float():
    assert commission_to_float("20.00%") == 0.2
    assert commission_to_float("10%~15%") == 0.125
    # 使用近似相等而不是精确相等来解决浮点数精度问题
    result = commission_to_float("5-10%")
    assert abs(result - 0.075) < 1e-10

def test_conversion_to_float():
    assert conversion_to_float("15%") == 0.15
    assert conversion_to_float(0.2) == 0.2

def test_filter_dataframe():
    # 创建测试数据
    data = {
        "商品名称": ["优质商品A", "低价商品B", "黑名单商品"],
        "近7天销量值": [6000, 3000, 10000],
        "近30天销量值": [30000, 15000, 50000],
        "佣金比例值": [0.2, 0.1, 0.3],
        "转化率值": [0.25, 0.1, 0.05],
        "关联达人": [60, 30, 10]
    }
    df = pd.DataFrame(data)

    # 创建测试规则
    rules = {
        "sales": {
            "last_7d_min": 5000,
            "last_30d_min": 20000
        },
        "commission": {
            "min_rate": 0.15,
            "zero_rate_conversion_min": 0.2
        },
        "conversion": {
            "min_rate": 0.15
        },
        "influencer": {
            "min_count": 50
        },
        "categories": {
            "blacklist": ["黑名单"]
        }
    }

    # 应用过滤规则
    filtered_df = filter_dataframe(df, rules)

    # 检查结果：应该只有第一行符合条件
    assert len(filtered_df) == 1
    assert filtered_df.iloc[0]["商品名称"] == "优质商品A"

if __name__ == "__main__":
    test_range_mid()
    test_commission_to_float()
    test_conversion_to_float()
    test_filter_dataframe()
    print("所有测试通过!")
