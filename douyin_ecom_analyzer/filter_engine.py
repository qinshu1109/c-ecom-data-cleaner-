import os
import yaml
import pandas as pd
import logging

# 配置日志
logger = logging.getLogger('douyin_filter')

class FilterEngine:
    """数据过滤引擎，根据规则对数据进行筛选"""
    
    def __init__(self, rules_file=None):
        """
        初始化过滤引擎
        
        Args:
            rules_file: 规则文件路径，如果为None则使用默认路径
        """
        if rules_file is None:
            # 使用默认规则文件路径
            self.rules_file = os.path.join(os.getcwd(), 'filter_rules.yaml')
        else:
            self.rules_file = rules_file
            
        self.rules = self._load_rules()
        logger.info(f"已加载过滤规则: {self.rules_file}")
    
    def _load_rules(self):
        """加载过滤规则"""
        try:
            with open(self.rules_file, 'r', encoding='utf-8') as f:
                rules = yaml.safe_load(f)
            return rules
        except Exception as e:
            logger.error(f"加载规则文件失败: {str(e)}")
            # 返回空规则
            return {}
    
    def filter_data(self, df):
        """
        根据规则过滤数据
        
        Args:
            df: 包含商品数据的DataFrame
        
        Returns:
            DataFrame: 过滤后的DataFrame
            dict: 过滤统计信息
        """
        if not self.rules:
            logger.warning("没有可用的过滤规则，返回原始数据")
            return df, {"无过滤": len(df)}
        
        # 创建副本避免修改原始数据
        filtered_df = df.copy()
        original_count = len(filtered_df)
        
        # 过滤统计
        stats = {
            "原始数据量": original_count,
            "过滤详情": {}
        }
        
        # 应用销量过滤
        if 'sales' in self.rules:
            sales_rules = self.rules['sales']
            
            # 7天销量过滤
            if 'last_7d_min' in sales_rules and '近7天销量_清洗' in filtered_df.columns:
                min_sales = sales_rules['last_7d_min']
                before_count = len(filtered_df)
                filtered_df = filtered_df[filtered_df['近7天销量_清洗'] >= min_sales]
                after_count = len(filtered_df)
                stats["过滤详情"]["7天销量低于" + str(min_sales)] = before_count - after_count
                
            # 30天销量过滤
            if 'last_30d_min' in sales_rules and '近30天销量_清洗' in filtered_df.columns:
                min_sales = sales_rules['last_30d_min']
                before_count = len(filtered_df)
                filtered_df = filtered_df[filtered_df['近30天销量_清洗'] >= min_sales]
                after_count = len(filtered_df)
                stats["过滤详情"]["30天销量低于" + str(min_sales)] = before_count - after_count
        
        # 应用佣金过滤
        if 'commission' in self.rules:
            commission_rules = self.rules['commission']
            
            # 最低佣金率
            if 'min_rate' in commission_rules and '佣金比例_清洗' in filtered_df.columns:
                min_rate = commission_rules['min_rate']
                before_count = len(filtered_df)
                filtered_df = filtered_df[filtered_df['佣金比例_清洗'] >= min_rate]
                after_count = len(filtered_df)
                stats["过滤详情"]["佣金率低于" + str(min_rate)] = before_count - after_count
            
            # 零佣金但转化率高的特例
            if ('zero_rate_conversion_min' in commission_rules and 
                '佣金比例_清洗' in filtered_df.columns and 
                '转化率' in filtered_df.columns):
                
                min_conversion = commission_rules['zero_rate_conversion_min']
                # 找出佣金为0但转化率高的商品
                zero_commission_high_conversion = (
                    (filtered_df['佣金比例_清洗'] == 0) & 
                    (filtered_df['转化率'] >= min_conversion)
                )
                # 添加回过滤结果
                if zero_commission_high_conversion.any():
                    zero_comm_df = df[zero_commission_high_conversion].copy()
                    filtered_df = pd.concat([filtered_df, zero_comm_df])
                    stats["过滤详情"]["零佣金高转化率例外"] = len(zero_comm_df)
        
        # 应用转化率过滤
        if 'conversion' in self.rules and 'conversion' in self.rules:
            conversion_rules = self.rules['conversion']
            
            if 'min_rate' in conversion_rules and '转化率' in filtered_df.columns:
                min_rate = conversion_rules['min_rate']
                before_count = len(filtered_df)
                filtered_df = filtered_df[filtered_df['转化率'] >= min_rate]
                after_count = len(filtered_df)
                stats["过滤详情"]["转化率低于" + str(min_rate)] = before_count - after_count
        
        # 应用KOL数量过滤
        if 'influencer' in self.rules:
            influencer_rules = self.rules['influencer']
            
            if 'min_count' in influencer_rules and 'KOL数量' in filtered_df.columns:
                min_count = influencer_rules['min_count']
                before_count = len(filtered_df)
                filtered_df = filtered_df[filtered_df['KOL数量'] >= min_count]
                after_count = len(filtered_df)
                stats["过滤详情"]["KOL数量少于" + str(min_count)] = before_count - after_count
        
        # 应用类别白名单
        if 'categories' in self.rules and 'whitelist' in self.rules['categories']:
            categories = self.rules['categories']['whitelist']
            
            if categories and '类目' in filtered_df.columns:
                before_count = len(filtered_df)
                # 创建类目匹配条件
                category_mask = filtered_df['类目'].isin(categories)
                # 应用白名单过滤
                whitelist_df = filtered_df[category_mask].copy()
                
                # 计算过滤掉的类目数量
                stats["过滤详情"]["非白名单类目"] = before_count - len(whitelist_df)
                filtered_df = whitelist_df
        
        # 添加过滤后总量
        stats["过滤后数据量"] = len(filtered_df)
        stats["过滤率"] = f"{(1 - len(filtered_df) / original_count) * 100:.2f}%" if original_count > 0 else "0%"
        
        return filtered_df, stats
    
    def generate_filter_report(self, stats, output_file=None):
        """
        生成过滤报告
        
        Args:
            stats: 过滤统计信息
            output_file: 输出文件路径
        
        Returns:
            str: 报告文本
        """
        report = []
        report.append("# 数据过滤报告")
        report.append(f"原始数据量: {stats['原始数据量']}")
        report.append(f"过滤后数据量: {stats['过滤后数据量']}")
        report.append(f"过滤率: {stats['过滤率']}")
        
        report.append("\n## 过滤详情")
        for reason, count in stats.get("过滤详情", {}).items():
            report.append(f"- {reason}: {count}项")
        
        report_text = "\n".join(report)
        
        # 如果指定了输出文件，保存报告
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report_text)
                logger.info(f"过滤报告已保存到: {output_file}")
            except Exception as e:
                logger.error(f"保存过滤报告失败: {str(e)}")
        
        return report_text 