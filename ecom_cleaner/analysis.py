import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from typing import Tuple, Dict, Any
import yaml

def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """加载配置文件"""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def generate_sales_analysis(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    """生成销量分析报告"""
    analysis = pd.DataFrame()

    for field in config["analysis"]["sales_metrics"]:
        if field in df.columns:
            stats = df[field].describe()
            stats.name = field
            analysis = pd.concat([analysis, stats], axis=1)

    return analysis

def generate_conversion_analysis(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    """生成转化率分析报告"""
    analysis = pd.DataFrame()

    for field in config["analysis"]["conversion_metrics"]:
        if field in df.columns:
            stats = df[field].describe()
            stats.name = field
            analysis = pd.concat([analysis, stats], axis=1)

    return analysis

def create_visualization(df: pd.DataFrame, config: Dict[str, Any]) -> BytesIO:
    """创建数据可视化"""
    # 设置图表样式
    plt.style.use('seaborn')
    colors = config["analysis"]["visualization"]["chart_colors"]

    # 创建图表
    fig, axes = plt.subplots(2, 2, figsize=(
        config["output"]["visualization"]["size"]["width"],
        config["output"]["visualization"]["size"]["height"]
    ))

    # 销量分布图
    sns.histplot(data=df, x=config["analysis"]["sales_metrics"][0],
                ax=axes[0,0], color=colors[0])
    axes[0,0].set_title("近30天销量分布")

    # 销售额分布图
    sns.histplot(data=df, x=config["analysis"]["sales_metrics"][1],
                ax=axes[0,1], color=colors[1])
    axes[0,1].set_title("近30天销售额分布")

    # 转化率分布图
    sns.histplot(data=df, x=config["analysis"]["conversion_metrics"][0],
                ax=axes[1,0], color=colors[2])
    axes[1,0].set_title("转化率分布")

    # 佣金比例分布图
    sns.histplot(data=df, x=config["analysis"]["conversion_metrics"][1],
                ax=axes[1,1], color=colors[3])
    axes[1,1].set_title("佣金比例分布")

    plt.tight_layout()

    # 保存图表到内存
    img_data = BytesIO()
    plt.savefig(img_data, format=config["output"]["visualization"]["format"],
                dpi=config["output"]["visualization"]["dpi"],
                bbox_inches="tight")
    img_data.seek(0)

    return img_data

def generate_excel_report(df: pd.DataFrame, sales_analysis: pd.DataFrame,
                         conversion_analysis: pd.DataFrame,
                         anomalies: pd.DataFrame,
                         config: Dict[str, Any]) -> bytes:
    """
    生成Excel报表

    Args:
        df: 清洗后的数据
        sales_analysis: 销量分析
        conversion_analysis: 转化率分析
        anomalies: 异常数据
        config: 配置字典

    Returns:
        bytes: Excel报表的字节数据
    """
    excel_data = BytesIO()

    with pd.ExcelWriter(excel_data, engine="openpyxl") as writer:
        # 清洗后的数据
        df.to_excel(writer, sheet_name=config["output"]["excel"]["sheets"][0]["name"],
                   index=False)

        # 销量分析
        sales_analysis.to_excel(writer, sheet_name=config["output"]["excel"]["sheets"][1]["name"])

        # 转化率分析
        conversion_analysis.to_excel(writer, sheet_name=config["output"]["excel"]["sheets"][2]["name"])

        # 异常值检测
        anomalies.to_excel(writer, sheet_name=config["output"]["excel"]["sheets"][3]["name"])

    excel_data.seek(0)
    return excel_data.getvalue()

def analyze_and_report(df: pd.DataFrame) -> Tuple[bytes, bytes]:
    """
    执行完整的数据分析和报表生成

    Args:
        df: 清洗后的DataFrame

    Returns:
        Tuple[bytes, bytes]: (Excel报表字节数据, 可视化图表字节数据)
    """
    config = load_config()

    # 生成分析报告
    sales_analysis = generate_sales_analysis(df, config)
    conversion_analysis = generate_conversion_analysis(df, config)

    # 检测异常值
    from . import cleaning
    anomalies = pd.DataFrame()

    # 生成可视化
    visualization = create_visualization(df, config)

    # 生成Excel报表
    excel_report = generate_excel_report(df, sales_analysis,
                                       conversion_analysis, anomalies, config)

    return excel_report, visualization.getvalue()
