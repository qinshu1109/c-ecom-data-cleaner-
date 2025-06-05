# Excel IO 安全规范

## 1. 写入规范

### 1.1 基本语法
- 使用 `with pd.ExcelWriter(path, engine="openpyxl") as writer:` 语法
- 统一设置 `index=False`，防止多余索引列
- 使用 `to_excel` 方法时指定 `sheet_name`

### 1.2 数据验证
- 写入前检查 DataFrame 内存使用
- 若 `df.memory_usage(deep=True).sum() > 250*1024*1024`，使用分块写入
- 验证数据类型和格式
- 处理特殊字符和空值

## 2. 读取规范

### 2.1 基本语法
- 使用 `pd.read_excel` 时指定 `engine="openpyxl"`
- 明确指定数据类型
- 处理缺失值
- 验证数据完整性

### 2.2 大数据处理
- 使用 `chunksize` 参数分块读取
- 及时释放内存
- 避免重复读取
- 使用迭代器处理

## 3. 错误处理

### 3.1 文件操作
- 检查文件是否存在
- 验证文件权限
- 处理文件锁定
- 备份重要数据

### 3.2 数据验证
- 检查数据类型
- 验证数据范围
- 处理异常值
- 记录错误日志

## 4. 性能优化

### 4.1 写入优化
- 使用 `openpyxl` 引擎
- 避免频繁写入
- 批量处理数据
- 优化内存使用

### 4.2 读取优化
- 只读取需要的列
- 使用适当的数据类型
- 避免重复读取
- 使用缓存机制

## 5. 安全措施

### 5.1 数据安全
- 加密敏感数据
- 验证数据来源
- 控制访问权限
- 记录操作日志

### 5.2 文件安全
- 定期备份
- 版本控制
- 访问控制
- 错误恢复

## 6. 最佳实践

### 6.1 代码示例
```python
def safe_write_excel(df: pd.DataFrame, path: str) -> None:
    """安全写入Excel文件
    
    Parameters
    ----------
    df : pd.DataFrame
        要写入的数据框
    path : str
        输出文件路径
    
    Raises
    ------
    ValueError
        当数据框内存使用超过250MB时
    """
    # 检查内存使用
    if df.memory_usage(deep=True).sum() > 250*1024*1024:
        raise ValueError("数据框太大，请使用分块写入")
    
    # 写入Excel
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="数据")
```

### 6.2 注意事项
- 避免在循环中频繁写入
- 及时关闭文件句柄
- 处理异常情况
- 保持代码简洁 