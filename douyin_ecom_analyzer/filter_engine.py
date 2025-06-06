"""
过滤引擎
"""

import logging
from pathlib import Path

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
            "sales": {"last_7d_min": 5000, "last_30d_min": 20000},
            "commission": {"min_rate": 0.15, "zero_rate_conversion_min": 0.2},
            "conversion": {"min_rate": 0.15},
            "influencer": {"min_count": 50},
            "categories": {"blacklist": ["端午文创", "艾草挂饰", "儿童节礼盒", "高复购烟具"]},
        }

    def filter_data(self, df):
        """
        过滤数据

        Args:
            df: 输入的DataFrame

        Returns:
            tuple: (过滤后的DataFrame, 过滤统计信息)
        """
        stats = {"原始数据量": len(df), "过滤后数据量": 0, "过滤率": 0, "过滤详情": {}}

        # 创建副本避免修改原始数据
        df_filtered = df.copy()

        # 应用各种过滤规则
        for filter_name, filter_func in self._get_filter_functions().items():
            if filter_name in self.rules:
                df_before = df_filtered.copy()
                df_filtered = filter_func(df_filtered, self.rules[filter_name])
                filtered_count = len(df_before) - len(df_filtered)

                if filtered_count > 0:
                    stats["过滤详情"][filter_name] = filtered_count

        # 更新统计信息
        stats["过滤后数据量"] = len(df_filtered)
        stats["过滤率"] = (
            f"{(1 - len(df_filtered) / stats['原始数据量']) * 100:.2f}%"
            if stats["原始数据量"] > 0
            else "0%"
        )

        return df_filtered, stats

    def _get_filter_functions(self):
        """获取过滤函数字典"""
        return {
            "sales": self._filter_by_sales,
            "commission": self._filter_by_commission,
            "conversion": self._filter_by_conversion,
            "influencer": self._filter_by_influencer,
            "categories": self._filter_by_categories,
        }

    def _filter_by_sales(self, df, rules):
        """根据销量过滤"""
        if not rules:
            return df

        result = df.copy()

        # 7天销量过滤
        if "last_7d_min" in rules and "近7天销量_清洗" in result.columns:
            result = result[result["近7天销量_清洗"] >= rules["last_7d_min"]]

        # 30天销量过滤
        if "last_30d_min" in rules and "近30天销量_清洗" in result.columns:
            result = result[result["近30天销量_清洗"] >= rules["last_30d_min"]]

        return result

    def _filter_by_commission(self, df, rules):
        """根据佣金过滤"""
        if not rules or "佣金比例_清洗" not in df.columns:
            return df

        result = df.copy()

        # 最低佣金率
        if "min_rate" in rules:
            # 零佣金但高转化率的特例
            if "zero_rate_conversion_min" in rules and "转化率_清洗" in result.columns:
                mask = (result["佣金比例_清洗"] >= rules["min_rate"]) | (
                    (result["佣金比例_清洗"] == 0)
                    & (result["转化率_清洗"] >= rules["zero_rate_conversion_min"])
                )
                result = result[mask]
            else:
                result = result[result["佣金比例_清洗"] >= rules["min_rate"]]

        return result

    def _filter_by_conversion(self, df, rules):
        """根据转化率过滤"""
        if not rules or "转化率_清洗" not in df.columns:
            return df

        result = df.copy()

        # 最低转化率
        if "min_rate" in rules:
            result = result[result["转化率_清洗"] >= rules["min_rate"]]

        return result

    def _filter_by_influencer(self, df, rules):
        """根据KOL数量过滤"""
        if not rules or "关联达人" not in df.columns:
            return df

        result = df.copy()

        # 最低KOL数量
        if "min_count" in rules:
            result = result[result["关联达人"] >= rules["min_count"]]

        return result

    def _filter_by_categories(self, df, rules):
        """根据类别过滤"""
        if not rules or "商品名称" not in df.columns or not rules.get("blacklist"):
            return df

        result = df.copy()

        # 黑名单过滤
        for keyword in rules["blacklist"]:
            result = result[~result["商品名称"].str.contains(keyword, case=False, na=False)]

        return result

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
