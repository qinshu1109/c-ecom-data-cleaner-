import streamlit as st
import pandas as pd
from cleaning import clean_dataframe, load_config
from analysis import analyze_and_report
import yaml

# 页面配置
st.set_page_config(
    page_title="电商数据清洗工具",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 标题和说明
st.title("📊 电商运营数据一键清洗与分析")
st.markdown("""
这个工具可以帮助你快速清洗和分析电商运营数据，支持以下功能：
- 数据清洗：标准化销量、百分比、URL等数据
- 数据分析：生成描述性统计和可视化图表
- 异常检测：自动识别异常数据
- 一键导出：生成Excel报表和可视化图表
""")

# 侧边栏配置
with st.sidebar:
    st.header("⚙️ 配置选项")
    
    # 加载配置文件
    config = load_config()
    
    # 显示当前配置
    st.subheader("当前配置")
    st.json({
        "销量字段": config["sales_fields"],
        "百分比字段": config["percent_fields"],
        "URL字段": config["url_fields"]
    })

# 文件上传
uploaded_file = st.file_uploader(
    "请选择要处理的Excel文件",
    type=["xlsx", "xls"],
    help="支持.xlsx和.xls格式的文件"
)

if uploaded_file is not None:
    try:
        # 读取数据
        df_raw = pd.read_excel(uploaded_file)
        st.success(f"✅ 成功读取数据：{df_raw.shape[0]} 行 × {df_raw.shape[1]} 列")
        
        # 显示数据预览
        with st.expander("📋 数据预览", expanded=True):
            st.dataframe(df_raw.head())
        
        # 清洗按钮
        if st.button("🚀 开始清洗并生成报表", type="primary"):
            with st.spinner("🔄 正在处理数据，请稍候..."):
                # 数据清洗
                df_clean = clean_dataframe(df_raw, config)
                
                # 生成报表
                excel_bytes, fig_bytes = analyze_and_report(df_clean)
                
                # 显示处理结果
                st.success("✨ 数据处理完成！")
                
                # 显示清洗后的数据预览
                with st.expander("📋 清洗后数据预览", expanded=True):
                    st.dataframe(df_clean.head())
                
                # 下载按钮
                st.download_button(
                    label="📥 下载Excel报表",
                    data=excel_bytes,
                    file_name="电商数据分析报表.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                # 显示可视化图表
                st.image(fig_bytes, caption="数据分布可视化", use_column_width=True)
                
    except Exception as e:
        st.error(f"❌ 处理数据时出错：{str(e)}")
        st.error("请确保上传的文件格式正确，并包含所需的数据字段。")

# 页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>📊 电商数据清洗工具 | 版本 1.0.0</p>
    <p>如有问题，请联系技术支持</p>
</div>
""", unsafe_allow_html=True) 