#!/usr/bin/env python
"""
抖音电商数据分析工具 - 测试脚本
用于检查所有必要的依赖是否正确安装和导入
"""

import logging

# 设置日志记录
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("test_app")


def test_imports():
    """测试所有必需的模块导入"""
    logger.info("开始测试导入...")

    # 测试基础库
    try:
        import numpy

        logger.info("✓ numpy 导入成功")
    except ImportError as e:
        logger.error(f"✗ numpy 导入失败: {e}")

    try:
        import pandas

        logger.info("✓ pandas 导入成功")
    except ImportError as e:
        logger.error(f"✗ pandas 导入失败: {e}")

    try:
        import matplotlib
        import matplotlib.pyplot as plt

        logger.info("✓ matplotlib 导入成功")
    except ImportError as e:
        logger.error(f"✗ matplotlib 导入失败: {e}")

    try:
        import streamlit

        logger.info("✓ streamlit 导入成功")
    except ImportError as e:
        logger.error(f"✗ streamlit 导入失败: {e}")

    try:
        import plotly.express

        logger.info("✓ plotly 导入成功")
    except ImportError as e:
        logger.error(f"✗ plotly 导入失败: {e}")

    try:
        import yaml

        logger.info("✓ yaml 导入成功")
    except ImportError as e:
        logger.error(f"✗ yaml 导入失败: {e}")

    try:
        import tqdm

        logger.info("✓ tqdm 导入成功")
    except ImportError as e:
        logger.error(f"✗ tqdm 导入失败: {e}")

    # 测试项目模块
    try:
        from douyin_ecom_analyzer.cleaning.converters import commission_to_float, range_mid

        logger.info("✓ 清洗模块导入成功")
    except ImportError as e:
        logger.error(f"✗ 清洗模块导入失败: {e}")

    try:
        from douyin_ecom_analyzer.filter_engine import FilterEngine

        logger.info("✓ 过滤引擎导入成功")
    except ImportError as e:
        logger.error(f"✗ 过滤引擎导入失败: {e}")


def main():
    """主函数"""
    print("抖音电商数据分析工具 - 测试脚本")
    print("===============================")

    # 测试导入
    test_imports()

    print("\n测试完成！")


if __name__ == "__main__":
    main()
