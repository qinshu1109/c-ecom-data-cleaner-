from __future__ import annotations
import io, yaml, re
import pandas as pd
from pathlib import Path
from functools import lru_cache

_RULE_PATH = Path("filter_rules.yaml")

@lru_cache(maxsize=1)
def _load_rules(mtime: float | None = None) -> dict:
    # mtime 参数只为触发 lru_cache 失效
    with _RULE_PATH.open(encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_rules() -> dict:
    return _load_rules(_RULE_PATH.stat().st_mtime)

def filter_dataframe(df: pd.DataFrame, rules: dict | None = None) -> pd.DataFrame:
    r = rules or load_rules()

    cond = (
        (df["近7天销量值"]   >= r["sales"]["last_7d_min"])
      & (df["近30天销量值"] >= r["sales"]["last_30d_min"])
      & (
            (df["佣金比例值"] >= r["commission"]["min_rate"])
          | ((df["佣金比例值"] == 0) & (df["转化率值"] >= r["commission"]["zero_rate_conversion_min"]))
        )
      & (df["转化率值"] >= r["conversion"]["min_rate"])
      & (df["关联达人"] >= r["influencer"]["min_count"])
      & ~df["商品名称"].str.contains("|".join(r["categories"]["blacklist"]), case=False, na=False)
    )
    return df.loc[cond].reset_index(drop=True) 