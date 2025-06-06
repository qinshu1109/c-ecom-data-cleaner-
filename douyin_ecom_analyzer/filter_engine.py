"""
过滤引擎
"""

import logging
from pathlib import Path

import pandas as pd
import yaml

# 配置日志
logger = logging.getLogger("filter_engine")

# 默认规则文件路径
DEFAULT_RULES_PATH = Path("filter_rules.yaml")


class FilterEngine:
    """
    数据过滤引擎，根据规则过滤数据
    """

    def __init__(self, rules_path=None):
        """
        初始化过滤引擎

        Args:
            rules_path: 规则文件路径，默认为filter_rules.yaml
        """
        self.rules_path = Path(rules_path) if rules_path else DEFAULT_RULES_PATH
        self.rules = self._load_rules()

    def _load_rules(self):
        """加载过滤规则"""
        try:
            if self.rules_path.exists():
                with open(self.rules_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f)
            else:
                logger.warning(f"规则文件 {self.rules_path} 不存在，使用默认规则")
                return self._get_default_rules()
        except Exception as e:
            logger.error(f"加载规则失败: {e}")
            return self._get_default_rules()

    def _get_default_rules(self):
        """获取默认规则"""
        return {
            "sales": {"last_7d_min": 5000, "last_30d_min": 25000},
            "commission": {"min_rate": 20, "zero_rate_conversion_min": 20},  # 百分比单位
            "conversion": {"min_rate": 15},  # 百分比单位
            "influencer": {"min_count": 50},
        }

    def apply_rules(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        执行五维过滤规则，返回合规行，自动处理缺失列

        Args:
            df: 输入的DataFrame，需要包含*_val列

        Returns:
            DataFrame: 过滤后的DataFrame
        """
        # 创建副本
        df_filtered = df.copy()

        # 记录初始行数
        initial_count = len(df_filtered)
        logger.info(f"开始过滤，初始数据量: {initial_count}行")

        # 确保必要的列存在
        required_cols = [
            "近7天销量_val",
            "近30天销量_val",
            "佣金比例_val",
            "转化率_val",
            "关联达人",
            "is_festival",
        ]

        # 检查并添加缺失列
        for col in required_cols:
            if col not in df_filtered.columns:
                if col == "is_festival":
                    df_filtered[col] = False
                    logger.info(f"添加缺失列: {col} (默认值: False)")
                elif col == "关联达人":
                    # 关联达人使用固定值100替代
                    df_filtered[col] = 100
                    logger.info(f"添加缺失列: {col} (默认值: 100)")
                elif col.endswith("_val"):
                    # 对于数值列，使用合理的默认值
                    if "销量" in col:
                        default_val = 10000 if "30" in col else 5000
                    elif "佣金" in col:
                        default_val = 20
                    elif "转化" in col:
                        default_val = 15
                    else:
                        default_val = 0
                    df_filtered[col] = default_val
                    logger.info(f"添加缺失列: {col} (默认值: {default_val})")

        # 确保所有_val列都是数值类型
        for col in df_filtered.columns:
            if col.endswith("_val") and df_filtered[col].dtype == object:
                df_filtered[col] = pd.to_numeric(df_filtered[col], errors="coerce").fillna(0)
                logger.info(f"转换列 {col} 为数值类型")

        # 获取规则值（可从配置中动态获取）
        sales_7d_min = self.rules.get("sales", {}).get("last_7d_min", 5000)
        sales_30d_min = self.rules.get("sales", {}).get("last_30d_min", 25000)
        min_influencer = self.rules.get("influencer", {}).get("min_count", 50)
        min_commission = self.rules.get("commission", {}).get("min_rate", 20)
        zero_rate_conversion = self.rules.get("commission", {}).get("zero_rate_conversion_min", 20)
        min_conversion = self.rules.get("conversion", {}).get("min_rate", 15)

        # 1) 销量过滤 (7天销量 ≥ 5000, 30天销量 ≥ 25000)
        try:
            before_count = len(df_filtered)
            df_filtered = df_filtered[df_filtered["近7天销量_val"] >= sales_7d_min]
            logger.info(
                f"7天销量过滤 (≥{sales_7d_min}): 过滤掉 {before_count - len(df_filtered)}行"
            )

            before_count = len(df_filtered)
            df_filtered = df_filtered[df_filtered["近30天销量_val"] >= sales_30d_min]
            logger.info(
                f"30天销量过滤 (≥{sales_30d_min}): 过滤掉 {before_count - len(df_filtered)}行"
            )
        except Exception as e:
            logger.warning(f"销量过滤出错: {e}")

        # 2) 关联达人过滤 (关联达人 ≥ 50)
        try:
            before_count = len(df_filtered)
            df_filtered = df_filtered[df_filtered["关联达人"] >= min_influencer]
            logger.info(
                f"关联达人过滤 (≥{min_influencer}): 过滤掉 {before_count - len(df_filtered)}行"
            )
        except Exception as e:
            logger.warning(f"关联达人过滤出错: {e}")

        # 3) 佣金和转化率过滤
        # ((佣金 ≥ 20% & 转化率 ≥ 15%) | (佣金 = 0% & 转化率 ≥ 20%))
        try:
            before_count = len(df_filtered)
            cond_commission = (
                (df_filtered["佣金比例_val"] >= min_commission)
                & (df_filtered["转化率_val"] >= min_conversion)
            ) | (
                (df_filtered["佣金比例_val"] == 0)
                & (df_filtered["转化率_val"] >= zero_rate_conversion)
            )
            df_filtered = df_filtered[cond_commission]
            logger.info(f"佣金转化率过滤: 过滤掉 {before_count - len(df_filtered)}行")
        except Exception as e:
            logger.warning(f"佣金转化率过滤出错: {e}")

        # 4) 节日商品过滤
        try:
            before_count = len(df_filtered)
            df_filtered = df_filtered[~df_filtered["is_festival"]]
            logger.info(f"节日商品过滤: 过滤掉 {before_count - len(df_filtered)}行")
        except Exception as e:
            logger.warning(f"节日商品过滤出错: {e}")

        logger.info(f"过滤完成，从 {initial_count} 行减少到 {len(df_filtered)} 行")
        return df_filtered

    def filter_data(self, df):
        """
        过滤数据（兼容旧接口）

        Args:
            df: 输入的DataFrame

        Returns:
            tuple: (过滤后的DataFrame, 过滤统计信息)
        """
        stats = {"原始数据量": len(df), "过滤后数据量": 0, "过滤率": 0, "过滤详情": {}}
        df_filtered = df.copy()  # 默认值，避免未定义变量

        # 尝试使用新方法过滤
        try:
            # 记录输入数据的列
            logger.info(f"输入数据列: {df.columns.tolist()}")

            # 检查是否包含新的*_val列
            has_val_cols = all(
                col in df.columns
                for col in ["近7天销量_val", "近30天销量_val", "佣金比例_val", "转化率_val"]
            )

            logger.info(f"是否包含所有_val列: {has_val_cols}")
            if not has_val_cols:
                missing = [
                    col
                    for col in ["近7天销量_val", "近30天销量_val", "佣金比例_val", "转化率_val"]
                    if col not in df.columns
                ]
                logger.warning(f"缺少以下_val列: {missing}")
                # 即使缺少某些列，仍然使用新的过滤方法
                logger.info("尽管缺少某些列，仍然使用新的过滤方法")

            # 使用新方法过滤 - 总是使用新方法，不再回退到旧方法
            logger.info("使用新的过滤方法")
            df_before = df.copy()
            df_filtered = self.apply_rules(df)
            logger.info(f"过滤前: {len(df_before)}行, 过滤后: {len(df_filtered)}行")

            # 更新统计信息
            # 根据日志计算各环节过滤数量
            sales_7d_min = self.rules.get("sales", {}).get("last_7d_min", 5000)
            sales_30d_min = self.rules.get("sales", {}).get("last_30d_min", 25000)

            try:
                # 计算销量过滤数量
                if "近7天销量_val" in df.columns and "近30天销量_val" in df.columns:
                    mask_7d = df["近7天销量_val"] >= sales_7d_min
                    mask_30d = df["近30天销量_val"] >= sales_30d_min
                    sales_filtered = len(df) - len(df[mask_7d & mask_30d])

                    # 计算佣金/转化率过滤数量
                    min_commission = self.rules.get("commission", {}).get("min_rate", 20)
                    min_conversion = self.rules.get("conversion", {}).get("min_rate", 15)
                    zero_rate_conversion = self.rules.get("commission", {}).get(
                        "zero_rate_conversion_min", 20
                    )

                    if "佣金比例_val" in df.columns and "转化率_val" in df.columns:
                        cond_commission = (
                            (df["佣金比例_val"] >= min_commission)
                            & (df["转化率_val"] >= min_conversion)
                        ) | ((df["佣金比例_val"] == 0) & (df["转化率_val"] >= zero_rate_conversion))

                        commission_filtered = len(df[mask_7d & mask_30d]) - len(
                            df[mask_7d & mask_30d & cond_commission]
                        )

                        # 计算节日商品过滤数量
                        if "is_festival" in df.columns:
                            festival_filtered = len(
                                df[mask_7d & mask_30d & cond_commission & df["is_festival"]]
                            )
                            stats["过滤详情"]["节日商品"] = festival_filtered

                        stats["过滤详情"]["佣金或转化率不达标"] = commission_filtered

                    stats["过滤详情"]["销量不达标"] = sales_filtered
                else:
                    # 无法详细统计时使用总体统计
                    stats["过滤详情"]["总过滤数量"] = len(df) - len(df_filtered)
            except Exception as e:
                logger.warning(f"统计详情计算错误: {e}")
                # 无法详细统计时使用总体统计
                stats["过滤详情"]["总过滤数量"] = len(df) - len(df_filtered)

        except Exception as e:
            logger.exception(f"过滤失败: {e}")
            df_filtered = df.copy()
            stats["过滤详情"]["过滤错误"] = str(e)

        # 更新统计信息
        stats["过滤后数据量"] = len(df_filtered)
        stats["过滤率"] = (
            f"{(1 - len(df_filtered) / stats['原始数据量']) * 100:.2f}%"
            if stats["原始数据量"] > 0
            else "0%"
        )

        return df_filtered, stats

    def generate_filter_report(self, stats, output_path=None):
        """
        生成过滤报告

        Args:
            stats: 过滤统计信息
            output_path: 输出路径

        Returns:
            str: 报告内容
        """
        report = f"""# 数据过滤报告

## 基本统计
- 原始数据量: {stats["原始数据量"]}
- 过滤后数据量: {stats["过滤后数据量"]}
- 过滤率: {stats["过滤率"]}

## 过滤详情
"""

        for reason, count in stats.get("过滤详情", {}).items():
            report += f"- {reason}: {count}项\n"

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report)

        return report
