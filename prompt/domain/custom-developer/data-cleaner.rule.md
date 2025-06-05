# 电商数据清洗工具规则

## 1. 技术架构

### 1.1 技术选型
| 层次 | 组件 | 说明 |
|------|------|------|
| 界面 | Streamlit | 纯Python实现的Web界面 |
| 业务逻辑 | cleaning/ | 数据清洗核心模块 |
| 分析报表 | analysis/ | 数据分析和可视化 |
| 打包发布 | PyInstaller | 生成可执行文件 |

### 1.2 目录结构
```
ecom_cleaner/
├── app.py                # Streamlit 入口（UI 只写渲染）
├── cleaning/             # 业务包
│   ├── __init__.py
│   ├── rules.py          # 正则/枚举等纯逻辑
│   ├── converters.py     # 通用字段转换
│   ├── cleaner.py        # DataFrame→DataFrame 清洗主函数
│   └── validator.py      # URL/link/空值校验
├── analysis/
│   ├── __init__.py
│   ├── stats.py          # 描述统计
│   ├── viz.py            # plotly 画图
│   └── report.py         # 写 Excel & PNG
├── assets/               # UI 资源（logo / css）
│   └── ui_style.css
├── config.yaml           # 字段映射 + 阈值
├── pyproject.toml        # ruff+black+mypy 统一配置
├── requirements.txt
├── build/                # 打包脚本
│   ├── build_win.ps1     # PyInstaller Windows
│   └── post_build.py     # 补充复制资产
├── tests/
│   ├── __init__.py
│   ├── test_cleaner.py
│   └── test_stats.py
├── .github/              # CI/CD
│   └── workflows/
│       └── ci.yml
└── .cursor/
    └── rules/
        ├── architecture.mdc
        ├── lint.mdc
        ├── streamlit_ui.mdc
        ├── excel_io.mdc
        └── bug-triage.mdc
```

## 2. 核心功能

### 2.1 数据清洗规则
- 销量数据标准化（7.5w~10w → 87500）
- 百分比数据标准化（20.00% → 0.2）
- URL链接验证
- 数据格式统一化

### 2.2 数据分析功能
- 描述性统计
- 数据分布可视化
- 多维度分析
- 异常值检测

### 2.3 报表输出
- Excel多sheet报表
- 可视化图表
- 一键导出功能

## 3. 代码规范

### 3.1 架构规范
- app.py 仅负责 Streamlit UI 实现，不包含业务逻辑
- cleaning/ 包负责数据清洗相关功能
- analysis/ 包负责数据分析和可视化功能
- 业务逻辑必须按功能模块分离
- 避免跨层直接调用
- 保持单一职责原则

### 3.2 代码质量
- 使用 ruff + black 进行代码格式化
- 行宽限制为 100 字符
- 使用 f-string 进行字符串格式化
- 禁止使用 print，改用 logging
- 所有公开函数必须使用完整的 type-hint
- 使用 numpy-docstring 风格编写文档

### 3.3 Excel IO 安全规范
- 使用 `with pd.ExcelWriter(path, engine="openpyxl")` 语法
- 统一设置 `index=False`
- 写入前检查文件大小
- 检查 DataFrame 内存使用
- 验证数据完整性
- 处理特殊字符和格式

## 4. 使用流程

### 4.1 运营使用步骤
1. 双击启动程序
2. 上传Excel文件
3. 点击清洗按钮
4. 下载分析结果

### 4.2 配置修改
- 通过config.yaml修改字段映射
- 自定义清洗规则
- 调整分析维度

## 5. 扩展功能

### 5.1 数据源扩展
- 支持多文件批量处理
- 支持实时数据流
- 支持API数据接入

### 5.2 分析功能扩展
- 自定义分析维度
- 高级统计分析
- 预测模型集成

### 5.3 输出扩展
- 邮件自动推送
- 钉钉消息通知
- 数据大屏展示

## 6. 安全与性能

### 6.1 数据安全
- 本地化部署
- 数据加密传输
- 访问权限控制

### 6.2 性能优化
- 大数据量处理优化
- 内存使用优化
- 并行处理支持

## 7. 维护与更新

### 7.1 版本管理
- 功能迭代记录
- 问题修复记录
- 用户反馈处理

### 7.2 文档支持
- 使用手册
- 开发文档
- 常见问题解答

## 8. 配置文件示例

```yaml
sales_fields: ["近30天销量", "周销量", "近1年销量"]
percent_fields: ["佣金比例", "转化率", "30天转化率"]
url_fields: ["商品链接", "蝉妈妈商品链接", "抖音商品链接"]

# 阈值&预警
warn:
  high_commission: 0.5      # >50%
  zero_sales_high_revenue: true
``` 