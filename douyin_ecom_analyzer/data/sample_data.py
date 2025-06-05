"""
示例数据生成脚本，用于测试和演示
"""

import pandas as pd
import numpy as np
import random
import os

def generate_sample_data(rows=100, output_file=None):
    """
    生成示例抖音电商数据
    
    Args:
        rows: 生成的行数
        output_file: 输出文件路径，如果不提供则只返回DataFrame不保存
    
    Returns:
        DataFrame: 生成的示例数据
    """
    # 随机种子，确保可重复性
    np.random.seed(42)
    random.seed(42)
    
    # 创建销量数据
    sales_formats = [
        lambda: f"{random.randint(1, 9)}.{random.randint(1, 9)}w~{random.randint(10, 20)}w",
        lambda: f"{random.randint(1, 99)}k-{random.randint(100, 999)}k",
        lambda: f"{random.randint(100, 999)}-{random.randint(1000, 9999)}",
        lambda: f"{random.randint(1, 9)}万-{random.randint(10, 20)}万",
        lambda: f"{random.randint(1, 50)}w" if random.random() < 0.5 else f"{random.randint(1, 50)}万"
    ]
    
    # 创建佣金数据
    commission_formats = [
        lambda: f"{random.randint(5, 30)}.{random.randint(0, 99):02d}%",
        lambda: f"{random.randint(5, 15)}%~{random.randint(16, 30)}%",
        lambda: f"{random.randint(5, 30)}%"
    ]
    
    # 生成商品数据
    data = {
        "商品ID": [f"item_{i:06d}" for i in range(1, rows+1)],
        "商品名称": [f"测试商品{i}" for i in range(1, rows+1)],
        "近30天销量": [random.choice(sales_formats)() for _ in range(rows)],
        "佣金比例": [random.choice(commission_formats)() for _ in range(rows)],
        "商品链接": [f"https://haohuo.douyin.com/goods/{random.randint(10000, 99999)}" for _ in range(rows)],
        "蝉妈妈商品链接": [f"https://www.chanmama.com/goods/{random.randint(10000, 99999)}" if random.random() < 0.8 else "" for _ in range(rows)],
        "商品价格": [round(random.uniform(9.9, 999.9), 2) for _ in range(rows)],
        "类目": [random.choice(["服装", "美妆", "食品", "家居", "电子", "母婴"]) for _ in range(rows)],
        "店铺名称": [f"店铺{random.randint(1, 100)}" for _ in range(rows)],
        "是否天猫": [random.choice(["是", "否"]) for _ in range(rows)],
        "近30日访客数": [random.randint(1000, 100000) for _ in range(rows)],
        "近30日浏览量": [random.randint(2000, 200000) for _ in range(rows)],
        "商品评分": [round(random.uniform(3.0, 5.0), 1) for _ in range(rows)],
    }
    
    # 创建DataFrame
    df = pd.DataFrame(data)
    
    # 添加一些空值
    for col in df.columns:
        mask = np.random.random(size=len(df)) < 0.05  # 5%的概率为空
        df.loc[mask, col] = np.nan
    
    # 保存到Excel文件
    if output_file:
        # 确保目录存在
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        df.to_excel(output_file, index=False)
        print(f"示例数据已生成并保存到: {output_file}")
    
    return df

if __name__ == "__main__":
    # 生成示例数据并保存
    sample_file = os.path.join(os.path.dirname(__file__), "douyin_sample_data.xlsx")
    generate_sample_data(500, sample_file) 