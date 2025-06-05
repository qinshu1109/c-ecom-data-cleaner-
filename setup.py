from setuptools import setup, find_packages

with open("douyin_ecom_analyzer/requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="douyin_ecom_analyzer",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    author="抖音电商数据团队",
    author_email="example@domain.com",
    description="抖音电商数据批量处理和分析工具",
    keywords="抖音, 电商, 数据分析, 清洗",
    url="https://github.com/yourusername/douyin_ecom_analyzer",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    entry_points={
        "console_scripts": [
            "douyin-analyzer=douyin_ecom_analyzer.run:main",
        ],
    },
) 