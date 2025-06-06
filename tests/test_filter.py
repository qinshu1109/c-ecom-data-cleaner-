import sys
from pathlib import Path

import pandas as pd

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))

# 从douyin_ecom_analyzer包和ecom_cleaner包导入
from douyin_ecom_analyzer.filter_engine import FilterEngine
from ecom_cleaner.cleaning.cleaner import DataCleaner, parse_percent, parse_sales


def test_parse_sales():
    # 测试销量解析
    assert parse_sales("7.5w~10w") == 75000
    assert parse_sales("5000") == 5000
    assert parse_sales("1.5万") == 15000


def test_parse_percent():
    # 测试百分比解析
    assert parse_percent("20.00%") == 20.0
    assert parse_percent("10%~15%") == 10.0  # 取区间下限
    assert parse_percent("5-10%") == 5.0


def test_cleaner():
    # 测试数据清洗器
    data = {
        "商品名称": ["优质商品A", "儿童节礼盒", "端午文创"],
        "近7天销量": ["7.5w~10w", "6000~7500", "3w"],
        "近30天销量": ["25w~30w", "3w~5w", "12w"],
        "佣金比例": ["36%", "25%", "0%"],
        "转化率": ["10%~15%", "20%~25%", "30%"],
        "关联达人": [100, 60, 30],
    }
    df = pd.DataFrame(data)

    cleaner = DataCleaner()
    cleaned_df = cleaner.clean(df)

    # 验证清洗结果
    assert cleaned_df["近7天销量_val"].iloc[0] == 75000
    assert cleaned_df["近30天销量_val"].iloc[0] == 250000
    assert cleaned_df["佣金比例_val"].iloc[0] == 36.0
    assert cleaned_df["转化率_val"].iloc[0] == 10.0
    assert cleaned_df["is_festival"].iloc[1] == True
    assert cleaned_df["is_festival"].iloc[2] == True
    assert cleaned_df["is_festival"].iloc[0] == False


def test_filter_rules():
    # 测试过滤规则
    data = {
        "商品名称": ["优质商品A", "低价商品B", "儿童节礼盒", "零佣金高转化率"],
        "近7天销量": ["7.5w~10w", "6000~7500", "3w", "8w"],
        "近30天销量": ["25w~30w", "3w~5w", "12w", "27w"],
        "佣金比例": ["36%", "25%", "30%", "0%"],
        "转化率": ["16%", "10%", "15%", "30%"],
        "关联达人": [100, 30, 60, 80],
    }
    df = pd.DataFrame(data)

    # 清洗数据
    cleaner = DataCleaner()
    cleaned_df = cleaner.clean(df)

    # 应用过滤规则
    filter_engine = FilterEngine()
    filtered_df = filter_engine.apply_rules(cleaned_df)

    # 验证过滤结果
    assert len(filtered_df) == 2  # 只有两条记录满足所有条件
    assert "优质商品A" in filtered_df["商品名称"].values
    assert "零佣金高转化率" in filtered_df["商品名称"].values

    # 确认被过滤掉的原因
    # "低价商品B" - 销量不达标、关联达人少
    # "儿童节礼盒" - 节日商品被过滤


def test_complete_flow():
    # 测试完整流程
    data = {
        "商品名称": ["优质商品A", "低价商品B", "儿童节礼盒", "零佣金高转化率"],
        "近7天销量": ["7.5w~10w", "6000~7500", "3w", "8w"],
        "近30天销量": ["25w~30w", "3w~5w", "12w", "27w"],
        "佣金比例": ["36%", "25%", "30%", "0%"],
        "转化率": ["16%", "10%", "15%", "30%"],
        "关联达人": [100, 30, 60, 80],
    }
    df = pd.DataFrame(data)

    # 清洗数据
    cleaner = DataCleaner()
    cleaned_df = cleaner.clean(df)

    # 应用过滤规则
    filter_engine = FilterEngine()
    filtered_df, stats = filter_engine.filter_data(cleaned_df)

    # 验证结果
    assert stats["原始数据量"] == 4
    assert stats["过滤后数据量"] == 2
    assert "销量不达标" in stats["过滤详情"]
    assert "节日商品" in stats["过滤详情"]


if __name__ == "__main__":
    test_parse_sales()
    test_parse_percent()
    test_cleaner()
    test_filter_rules()
    test_complete_flow()
    print("所有测试通过!")
