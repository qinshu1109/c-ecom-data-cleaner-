# 抖音电商数据分析工具

## 项目概述
为抖音电商运营团队提供"批量数据清洗 + 描述统计 + 可视化"一键工具。
运营同事每月导出约**50,000行·30列**的Excel，本工具可在**3分钟内**完成清洗并生成报表。

## 主要功能
1. **数据清洗**：自动处理销量、佣金等特殊格式数据
2. **数据过滤**：根据多维度条件过滤不符合要求的商品数据
3. **高价值商品**：自动计算价值分数并筛选Top50高价值商品

## 安装方法

### 依赖项
- Python 3.8+
- pandas
- numpy
- streamlit
- matplotlib
- openpyxl

### 快速安装
```bash
git clone https://github.com/qinshu1109/c-ecom-data-cleaner-.git
cd c-ecom-data-cleaner-
pip install -r requirements.txt
```

## 使用方法

### 运行Web界面
```bash
python run_web.py
```
Web界面将在 http://localhost:8501 启动。

### 数据要求
支持的数据字段包括:

| 字段 | 含义 | 典型值 | 备注 |
|------|------|--------|------|
| 近30天销量 | 最近30天销量区间 | `7.5w~10w` | 带w/万/k，取区间均值 |
| 佣金比例 | 商家设置佣金 | `20.00%` 或 `10%~15%` | 统一转0-1浮点 |
| 商品名称 | 商品名称 | - | 用于类别过滤 |
| 商品链接 | 抖音商品页 | `https://haohuo.douyin.com/...` | - |

## 过滤规则配置
过滤规则保存在`filter_rules.yaml`文件中，可以根据需要进行调整。

## 项目结构
```
.
├── app.py                         # Streamlit应用入口
├── run_web.py                     # Web应用启动脚本
├── filter_rules.yaml              # 过滤规则配置
├── douyin_ecom_analyzer/          # 核心功能模块
│   ├── cleaning/                  # 数据清洗模块
│   │   ├── converters.py          # 数据格式转换
│   │   └── filter_engine.py       # 过滤引擎
├── tests/                         # 测试用例
│   └── test_filter.py             # 过滤功能测试
```

## 联系方式
有任何问题或建议，请联系项目维护者。
