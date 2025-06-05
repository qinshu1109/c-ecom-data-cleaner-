import streamlit as st
import pandas as pd
import numpy as np
import os
import time
import logging
import base64
from io import BytesIO
from datetime import datetime

# 导入项目模块 - 修改为完整包路径
from douyin_ecom_analyzer.utils import clean_dataframe
from douyin_ecom_analyzer.analyzer import DouyinAnalyzer
from douyin_ecom_analyzer.filter_engine import FilterEngine

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

def get_file_download_link(file_path, link_text):
    """生成文件下载链接"""
    with open(file_path, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    filename = os.path.basename(file_path)
    return f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">{link_text}</a>'

def get_excel_download_link(df, filename, sheet_name='Sheet1'):
    """生成Excel文件下载链接"""
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name=sheet_name, index=False)
    writer.save()
    b64 = base64.b64encode(output.getvalue()).decode()
    return f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">{filename}</a>'

def main():
    """主函数"""
    # 侧边栏配置
    st.sidebar.header("配置")
    skip_url_check = st.sidebar.checkbox("跳过URL有效性检查", value=True, 
                                        help="启用此选项可加快处理速度，但会跳过链接验证")
    
    apply_filters = st.sidebar.checkbox("应用过滤规则", value=False,
                                       help="启用此选项将根据filter_rules.yaml中的规则过滤数据")
    
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 上传文件部分
    st.header("1. 上传Excel文件")
    uploaded_file = st.file_uploader("选择抖音电商数据Excel文件", type=["xlsx", "xls"])
    
    if uploaded_file is not None:
        # 显示进度信息
        progress_container = st.empty()
        progress_bar = st.progress(0)
        info = st.empty()
        
        try:
            # 读取Excel文件
            progress_container.text("正在读取Excel文件...")
            df = pd.read_excel(uploaded_file)
            info.info(f"成功读取数据: {df.shape[0]}行 x {df.shape[1]}列")
            progress_bar.progress(20)
            
            # 显示原始数据预览
            st.header("2. 原始数据预览")
            st.write(df.head())
            
            # 数据清洗
            progress_container.text("正在清洗数据...")
            start_time = time.time()
            cleaned_df = clean_dataframe(df)
            cleaning_time = time.time() - start_time
            progress_bar.progress(40)
            info.info(f"数据清洗完成，耗时: {cleaning_time:.2f}秒")
            
            # 显示清洗后的数据预览
            st.header("3. 清洗后数据预览")
            st.write(cleaned_df.head())
            
            # 应用过滤规则（如果启用）
            filtered_df = cleaned_df
            filter_stats = None
            
            if apply_filters:
                progress_container.text("正在应用过滤规则...")
                try:
                    # 初始化过滤引擎
                    filter_engine = FilterEngine()
                    # 应用过滤规则
                    filtered_df, filter_stats = filter_engine.filter_data(cleaned_df)
                    progress_bar.progress(60)
                    
                    # 显示过滤报告
                    st.header("4. 过滤结果")
                    st.subheader("过滤统计")
                    st.write(f"原始数据量: {filter_stats['原始数据量']}")
                    st.write(f"过滤后数据量: {filter_stats['过滤后数据量']}")
                    st.write(f"过滤率: {filter_stats['过滤率']}")
                    
                    st.subheader("过滤详情")
                    for reason, count in filter_stats.get("过滤详情", {}).items():
                        st.write(f"- {reason}: {count}项")
                    
                    # 显示过滤后的数据预览
                    st.subheader("过滤后数据预览")
                    st.write(filtered_df.head())
                    
                except Exception as e:
                    st.error(f"应用过滤规则时发生错误: {str(e)}")
                    logger.exception("过滤错误")
                    # 出错时使用清洗后的数据继续
                    filtered_df = cleaned_df
            
            # 数据分析
            progress_container.text("正在分析数据...")
            analyzer = DouyinAnalyzer(filtered_df, output_dir)
            results = analyzer.run_all_analyses()
            progress_bar.progress(90)
            
            # 展示分析结果
            result_header = "5. 分析结果" if apply_filters else "4. 分析结果"
            st.header(result_header)
            
            # 创建两列布局
            col1, col2 = st.columns(2)
            
            # 销量分析
            if results['sales'] and 'plot_path' in results['sales']:
                with col1:
                    st.subheader("销量分析")
                    st.image(results['sales']['plot_path'])
            
            # 佣金分析
            if results['commission'] and 'plot_path' in results['commission']:
                with col2:
                    st.subheader("佣金分析")
                    st.image(results['commission']['plot_path'])
            
            # 相关性分析
            if results['correlation'] and 'plot_path' in results['correlation']:
                st.subheader("相关性分析")
                st.image(results['correlation']['plot_path'])
            
            # URL有效性分析
            if results['url_validation'] and 'plot_path' in results['url_validation']:
                st.subheader("URL有效性分析")
                st.image(results['url_validation']['plot_path'])
            
            # 下载报告
            download_header = "6. 下载报告" if apply_filters else "5. 下载报告"
            st.header(download_header)
            
            excel_report = results.get('excel_report')
            if excel_report:
                st.markdown(get_file_download_link(excel_report, "下载Excel报表"), unsafe_allow_html=True)
                
                # 如果应用了过滤规则，生成过滤报告
                if apply_filters and filter_stats:
                    filter_report_path = os.path.join(output_dir, f'filter_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md')
                    filter_engine.generate_filter_report(filter_stats, filter_report_path)
                    st.markdown(get_file_download_link(filter_report_path, "下载过滤报告"), unsafe_allow_html=True)
                
                progress_container.text("处理完成!")
                progress_bar.progress(100)
                
                # 显示总耗时
                total_time = time.time() - start_time
                st.success(f"所有处理已完成，总耗时: {total_time:.2f}秒")
                
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
        
        1. **数据清洗**: 自动处理销量、佣金等特殊格式数据，验证URL有效性
        2. **数据过滤**: 根据配置规则过滤不符合要求的商品数据
        3. **数据分析**: 生成销量分布、佣金分布等分析图表
        4. **报表生成**: 创建多Sheet的Excel报表，包含原始数据和分析结果
        
        ### 数据要求
        支持的数据字段包括:
        
        | 字段 | 含义 | 典型值 | 备注 |
        |------|------|--------|------|
        | 近30天销量 | 最近30天销量区间 | `7.5w~10w` | 带w/万/k，取区间均值 |
        | 佣金比例 | 商家设置佣金 | `20.00%` 或 `10%~15%` | 统一转0-1浮点 |
        | 商品链接 | 抖音商品页 | `https://haohuo.douyin.com/...` | 需校验可访问 |
        | 蝉妈妈商品链接 | 第三方分析页 | `https://www.chanmama.com/...` | 选填 |
        """)

if __name__ == "__main__":
    main() 