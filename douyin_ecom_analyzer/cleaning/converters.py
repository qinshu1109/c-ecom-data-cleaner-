import re
import numpy as np
from typing import Union, List

def _to_num(token: str) -> float:
    token = token.replace("万", "w")
    if "w" in token.lower():
        return float(token.lower().replace("w", "")) * 1e4
    return float(token)

def range_mid(text: str) -> float:
    """'7.5w~10w' → 87500；'5000' → 5000"""
    parts = re.split(r"[~\-]", str(text))
    nums = [_to_num(p) for p in parts]
    return float(np.mean(nums))

# 佣金比例转换（百分比转小数）
def commission_to_float(text: str) -> float:
    """'20.00%' → 0.2；'10%~15%' → 0.125"""
    # 移除百分号
    text = str(text).replace('%', '')
    # 检查是否为区间
    if '~' in text or '-' in text:
        separator = '~' if '~' in text else '-'
        parts = text.split(separator)
        rates = [float(p)/100 for p in parts]
        return float(np.mean(rates))
    else:
        return float(text)/100

# 转化率转换
def conversion_to_float(text: Union[str, float]) -> float:
    """转化率转浮点数"""
    # 如果是百分比格式
    if isinstance(text, str) and '%' in text:
        return float(text.replace('%', ''))/100
    return float(text)
