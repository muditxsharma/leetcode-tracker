from __future__ import annotations

import re
from typing import Optional, Tuple


def _parse_number_unit(s: str) -> Optional[Tuple[float, str]]:
    if not s:
        return None
    s = s.strip().lower()
    m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*([a-z]+)", s)
    if not m:
        return None
    return float(m.group(1)), m.group(2)


def runtime_ms(runtime_display: str) -> Optional[float]:
    parsed = _parse_number_unit(runtime_display)
    if not parsed:
        return None
    val, unit = parsed
    if unit == "ms":
        return val
    if unit == "s":
        return val * 1000.0
    return None


def memory_mb(memory_display: str) -> Optional[float]:
    parsed = _parse_number_unit(memory_display)
    if not parsed:
        return None
    val, unit = parsed
    if unit == "mb":
        return val
    if unit == "kb":
        return val / 1024.0
    if unit == "gb":
        return val * 1024.0
    return None