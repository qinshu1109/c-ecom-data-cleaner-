# 抖音电商数据分析工具

抖音电商数据批量处理和分析工具，为抖音电商运营团队提供高效的数据清洗、统计分析和可视化报表功能。

## 功能特点

- **批量数据清洗**：自动处理销量、佣金等特殊格式数据
- **数据验证**：自动验证URL有效性
- **描述统计**：生成全面的数据统计报表
- **数据可视化**：生成销量分布、佣金分布等分析图表
- **高性能处理**：支持5万行数据在3分钟内完成处理
- **双重界面**：同时支持命令行和Web界面两种使用方式

## 目录结构

```
douyin_ecom_analyzer/
├── data/                  # 数据相关模块
│   ├── __init__.py
│   └── sample_data.py     # 示例数据生成
├── __init__.py
├── app.py                 # Web应用界面
├── main.py                # 命令行入口
├── utils.py               # 数据清洗工具函数
├── analyzer.py            # 数据分析与可视化
├── run.py                 # 快速启动脚本
└── requirements.txt       # 项目依赖
```

## 安装使用

### 安装依赖

```bash
pip install -r douyin_ecom_analyzer/requirements.txt
```

### 使用方法

1. **生成示例数据**（可选）:

```bash
python -m douyin_ecom_analyzer.run sample --rows 1000
```

2. **命令行方式运行**:

```bash
python -m douyin_ecom_analyzer.run cli path/to/your/data.xlsx -o ./output
```

3. **Web界面方式运行**:

```bash
python -m douyin_ecom_analyzer.run web
```

打开浏览器访问 http://localhost:8501 使用Web界面。

## 数据字段说明

支持处理的主要数据字段：

| 字段 | 含义 | 典型值 | 备注 |
|------|------|--------|------|
| 近30天销量 | 最近30天销量区间 | `7.5w~10w` | 带w/万/k，取区间均值 |
| 佣金比例 | 商家设置佣金 | `20.00%` 或 `10%~15%` | 统一转0-1浮点 |
| 商品链接 | 抖音商品页 | `https://haohuo.douyin.com/...` | 需校验可访问 |
| 蝉妈妈商品链接 | 第三方分析页 | `https://www.chanmama.com/...` | 选填 |

## 输出结果

1. **Excel多表格报表**：包含原始数据、清洗后数据和统计分析结果
2. **可视化图表**：销量分布、佣金分布、相关性分析等PNG图表 