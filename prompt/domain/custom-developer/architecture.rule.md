# 电商数据清洗工具架构总则

## 1. 分层约定

### 1.1 文件职责
- `app.py` 仅负责 Streamlit UI 实现，不包含业务逻辑
- `cleaning.py` 负责数据清洗相关功能
- `analysis.py` 负责数据分析和可视化功能

### 1.2 代码组织
- 业务逻辑必须按功能模块分离
- 避免跨层直接调用
- 保持单一职责原则

## 2. 类型与注释规范

### 2.1 类型提示
- 所有公开函数必须使用完整的 type-hint
- 使用 typing 模块的类型注解
- 复杂类型使用 TypeVar 和 Generic

### 2.2 文档规范
- 使用 numpy-docstring 风格
- 必须包含参数说明和返回值类型
- 复杂逻辑需要添加示例代码

## 3. 性能优化准则

### 3.1 数据处理
- 避免使用 `df.apply(lambda ...)` 进行行级循环
- 优先使用向量化操作
- 大数据量使用 `pd.Series.map`
- 单次读取超过 80k 行时使用 `chunksize`

### 3.2 内存管理
- 及时释放大型 DataFrame
- 使用 `del` 清理临时变量
- 避免不必要的数据复制

## 4. 依赖管理

### 4.1 允许的依赖
- pandas >= 2.2
- openpyxl
- matplotlib
- plotly
- pyyaml

### 4.2 禁止的依赖
- seaborn
- 其他未明确允许的包

## 5. 代码风格规范

### 5.1 格式化规则
- 使用 ruff + black 配置
- 行宽限制为 100 字符
- 使用 f-string 进行字符串格式化
- 禁止使用 print，改用 logging

### 5.2 异常处理
- 必须显式捕获具体异常类型
- 禁止使用裸异常 `except:`
- 异常信息必须明确且可追踪

## 6. Excel IO 安全规范

### 6.1 写入规范
- 使用 `with pd.ExcelWriter(path, engine="openpyxl")` 语法
- 统一设置 `index=False`
- 写入前检查文件大小

### 6.2 数据验证
- 检查 DataFrame 内存使用
- 验证数据完整性
- 处理特殊字符和格式

## 7. 测试规范

### 7.1 测试覆盖
- 新增或修改公共函数必须添加测试
- 测试文件命名：`tests/test_xxx.py`
- 确保 `pytest -q` 全部通过

### 7.2 测试场景
- 标准输入测试
- 边界值测试
- 性能测试（5万行数据）
- 异常情况测试

## 8. 调试规范

### 8.1 错误追踪
- 定位报错文件和行号
- 检查最近三次提交的 diff
- 回溯变量覆盖情况

### 8.2 数据调试
- 使用 `clean_dataframe` 处理脏数据
- 打印样例数据（5条）
- 记录调试日志

## 9. 版本控制

### 9.1 提交规范
- 清晰的提交信息
- 相关的代码变更
- 测试用例更新

### 9.2 分支管理
- 功能分支命名规范
- 代码审查流程
- 合并策略 