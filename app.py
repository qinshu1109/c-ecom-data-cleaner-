import streamlit as st
import pandas as pd
import numpy as np
import io
import os
from pathlib import Path
import logging
import time
import yaml

# 导入项目模块
from cleaning.converters import range_mid, commission_to_float, conversion_to_float
from cleaning.filter_engine import filter_dataframe, load_rules

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('douyin_app')

# 设置页面配置
st.set_page_config(
    page_title="抖音电商数据分析工具",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 应用标题
st.title("抖音电商数据分析工具")
st.markdown("---")

def clean_dataframe(df, cfg=None):
    """
    数据清洗函数
    
    Args:
        df: 原始DataFrame
        cfg: 配置参数
    
    Returns:
        DataFrame: 清洗后的DataFrame
    """
    df_clean = df.copy()
    
    # 处理销量数据
    if '近7天销量' in df_clean.columns:
        df_clean['近7天销量_清洗'] = df_clean['近7天销量'].astype(str).apply(range_mid)
        df_clean['近7天销量值'] = df_clean['近7天销量_清洗']
    
    if '近30天销量' in df_clean.columns:
        df_clean['近30天销量_清洗'] = df_clean['近30天销量'].astype(str).apply(range_mid)
        df_clean['近30天销量值'] = df_clean['近30天销量_清洗']
    
    # 处理佣金数据
    if '佣金比例' in df_clean.columns:
        df_clean['佣金比例_清洗'] = df_clean['佣金比例'].astype(str).apply(commission_to_float)
        df_clean['佣金比例值'] = df_clean['佣金比例_清洗']
    
    # 处理转化率
    if '转化率' in df_clean.columns:
        df_clean['转化率_清洗'] = df_clean['转化率'].astype(str).apply(conversion_to_float)
        df_clean['转化率值'] = df_clean['转化率_清洗']
    
    # 确保关联达人列存在
    if '关联达人' in df_clean.columns:
        if df_clean['关联达人'].dtype == 'object':
            df_clean['关联达人'] = pd.to_numeric(df_clean['关联达人'], errors='coerce').fillna(0)
    
    # 确保价格列存在
    if '价格' in df_clean.columns:
        if df_clean['价格'].dtype == 'object':
            df_clean['价格'] = pd.to_numeric(df_clean['价格'], errors='coerce').fillna(0)
        df_clean['price'] = df_clean['价格']
    
    return df_clean

def main():
    """主函数"""
    # 侧边栏配置
    st.sidebar.header("配置")
    
    # 专家模式选项
    expert_mode = st.sidebar.checkbox("专家模式: 手动调阈值", value=False)
    
    # 如果启用专家模式，显示滑块调整过滤规则
    rules_gui = None
    if expert_mode:
        st.sidebar.subheader("过滤阈值设置")
        
        # 销量阈值
        last_7d_min = st.sidebar.slider("7天最低销量", 1000, 10000, 5000, 500)
        last_30d_min = st.sidebar.slider("30天最低销量", 10000, 50000, 25000, 1000)
        
        # 佣金阈值
        min_commission_rate = st.sidebar.slider("最低佣金比例", 0.05, 0.5, 0.20, 0.01, format="%.2f")
        zero_rate_min_conversion = st.sidebar.slider("零佣金最低转化率", 0.05, 0.5, 0.20, 0.01, format="%.2f")
        
        # 转化率阈值
        min_conversion_rate = st.sidebar.slider("最低转化率", 0.05, 0.5, 0.15, 0.01, format="%.2f")
        
        # KOL数量阈值
        min_influencer_count = st.sidebar.slider("最低KOL数量", 10, 200, 50, 5)
        
        # 类别黑名单
        try:
            with open("filter_rules.yaml", "r", encoding="utf-8") as f:
                default_rules = yaml.safe_load(f)
                default_blacklist = default_rules.get("categories", {}).get("blacklist", [])
        except:
            default_blacklist = ["端午文创", "艾草挂饰", "儿童节礼盒", "库洛米", "HelloKitty", "高复购烟具", "过滤烟嘴"]
        
        blacklist_input = st.sidebar.text_area(
            "类别黑名单（每行一个）", 
            value="\n".join(default_blacklist)
        )
        blacklist = [item.strip() for item in blacklist_input.split("\n") if item.strip()]
        
        # 构建自定义规则
        rules_gui = {
            "sales": {
                "last_7d_min": last_7d_min,
                "last_30d_min": last_30d_min
            },
            "commission": {
                "min_rate": min_commission_rate,
                "zero_rate_conversion_min": zero_rate_min_conversion
            },
            "conversion": {
                "min_rate": min_conversion_rate
            },
            "influencer": {
                "min_count": min_influencer_count
            },
            "categories": {
                "blacklist": blacklist
            }
        }
    
    # 上传文件部分
    st.header("1. 上传Excel文件")
    uploaded_file = st.file_uploader("选择抖音电商数据Excel文件", type=["xlsx", "xls"])
    
    if uploaded_file is not None:
        try:
            # 读取Excel文件
            df_raw = pd.read_excel(uploaded_file)
            st.success(f"成功读取数据: {df_raw.shape[0]}行 x {df_raw.shape[1]}列")
            
            # 显示原始数据预览
            st.header("2. 原始数据预览")
            st.dataframe(df_raw.head())
            
            # 清洗按钮
            if st.button("🚀 开始清洗并分析", type="primary"):
                # 显示进度信息
                progress = st.progress(0)
                status = st.empty()
                
                # 清洗数据
                start_time = time.time()
                status.info("正在清洗数据...")
                df_clean = clean_dataframe(df_raw)
                progress.progress(25)
                
                # 显示清洗后的数据预览
                st.header("3. 清洗后数据预览")
                st.dataframe(df_clean.head())
                
                # 应用过滤规则
                status.info("正在应用过滤规则...")
                df_filt = filter_dataframe(df_clean, rules_gui)
                progress.progress(50)
                
                # 计算价值分数
                status.info("正在计算商品价值分数...")
                df_filt["value_score"] = (
                    df_filt["近30天销量值"] * df_filt["佣金比例值"] * df_filt["price"]
                )
                
                # 选择Top50
                top50 = df_filt.nlargest(50, "value_score").reset_index(drop=True)
                progress.progress(75)
                
                # 显示过滤结果
                st.header("4. 过滤结果")
                st.write(f"原始数据量: {len(df_raw)}行")
                st.write(f"清洗后数据量: {len(df_clean)}行")
                st.write(f"过滤后数据量: {len(df_filt)}行")
                st.write(f"过滤率: {(1 - len(df_filt) / len(df_clean)) * 100:.2f}%")
                
                # 显示Top50
                st.header("5. Top 50 高价值商品")
                st.dataframe(top50, height=600)
                
                # 提供下载
                towrite = io.BytesIO()
                top50.to_excel(towrite, index=False, engine="openpyxl")
                towrite.seek(0)
                
                st.download_button(
                    "📥 下载 Top50", 
                    data=towrite.getvalue(),
                    file_name="top50.xlsx", 
                    key="dl-top50"
                )
                
                # 完成
                progress.progress(100)
                status.success(f"处理完成！总耗时: {time.time() - start_time:.2f}秒")
                
        except Exception as e:
            st.error(f"处理过程中发生错误: {str(e)}")
            logger.exception("处理错误")
    
    else:
        # 未上传文件时显示使用说明
        st.info("请上传Excel文件开始分析")
        
        st.header("使用说明")
        st.markdown("""
        ### 功能介绍
        本工具为抖音电商运营团队提供一键式数据清洗和分析功能:
        
        1. **数据清洗**: 自动处理销量、佣金等特殊格式数据
        2. **数据过滤**: 根据多维度条件过滤不符合要求的商品数据
        3. **高价值商品**: 自动计算价值分数并筛选Top50高价值商品
        
        ### 数据要求
        支持的数据字段包括:
        
        | 字段 | 含义 | 典型值 | 备注 |
        |------|------|--------|------|
        | 近30天销量 | 最近30天销量区间 | `7.5w~10w` | 带w/万/k，取区间均值 |
        | 佣金比例 | 商家设置佣金 | `20.00%` 或 `10%~15%` | 统一转0-1浮点 |
        | 商品名称 | 商品名称 | - | 用于类别过滤 |
        | 商品链接 | 抖音商品页 | `https://haohuo.douyin.com/...` | - |
        """)

if __name__ == "__main__":
    main() 