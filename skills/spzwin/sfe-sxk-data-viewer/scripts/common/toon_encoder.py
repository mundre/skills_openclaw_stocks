"""
TOON (Token-Oriented Object Notation) Encoder

A zero-dependency Python implementation fully compliant with TOON spec v3.0.

【核心用途解说】
此序列化引擎的本质，是专门建立一条将臃肿的 JSON（或多层嵌套的 Python dict/list）结构，转化为面向人工大语言模型（LLM）的高密度浓缩协议通道。
它的核心目标聚焦于【断崖式的削减大模型 Token 损耗】。依靠识别与动态压缩统一表头（类似 CSV 表格内联提取），结合 YAML 的层级树特质，该模块能在确保数据上下文明义 100% 不受损的前提下，精简掉所有的废弃闭合括号及引号符号，平均可帮你的 API 系统为单个语境输入节省极大量的 Token 从而实现极致降本提效。
"""

import re
import json
import math
from datetime import datetime, date
from typing import Any, Iterator, Tuple, List

# Validation patterns matching TS implementation
NUMERIC_LIKE_PATTERN = re.compile(r"^-?\d+(?:\.\d+)?(?:e[+-]?\d+)?$", re.IGNORECASE)
LEADING_ZERO_PATTERN = re.compile(r"^0\d+$")
VALID_UNQUOTED_KEY_PATTERN = re.compile(r"^[A-Za-z_][\w.]*$")


def _is_valid_unquoted_key(key: str) -> bool:
    """Checks if a key can be safely used without quotes."""
    return bool(VALID_UNQUOTED_KEY_PATTERN.match(key))


def _is_safe_unquoted(value: str, delimiter: str) -> bool:
    """Determines if a string value can be safely encoded without quotes."""
    if not value or value != value.strip():
        return False

    val_lower = value.lower()
    if val_lower in ("true", "false", "null"):
        return False

    if NUMERIC_LIKE_PATTERN.match(value) or LEADING_ZERO_PATTERN.match(value):
        return False

    if ":" in value or '"' in value or "\\" in value:
        return False

    if any(ch in value for ch in ("[", "]", "{", "}")):
        return False

    if any(ch in value for ch in ("\n", "\r", "\t")):
        return False

    if delimiter in value:
        return False

    if value.startswith("-"):
        return False

    return True


def _escape_string(val: str) -> str:
    """
    Safely escapes string matching JSON specification exactly (e.g. control characters).
    Uses standard library json.dumps to stringify and slices off the bounding quotes.
    """
    return json.dumps(val, ensure_ascii=False)[1:-1]


def normalize_value(value: Any, strip_html_style: bool = False) -> Any:
    """
    Normalizes complex Python types into strict JSON equivalents (Primitives, Lists, Dicts, None).
    Matches the TypeScript implementation's robust tracking for edge cases like NaNs and Sets.
    """
    if value is None:
        return None
    if isinstance(value, str):
        if strip_html_style:
            # Safely remove style="..." or style='...' attributes from HTML tags to save tokens
            value = re.sub(r'(?i)\s*style\s*=\s*(["\']).*?\1', "", value)
        return value
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        if isinstance(value, float):
            # NaN and Infinity map to null in standard JSON
            if math.isnan(value) or math.isinf(value):
                return None
        return value
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, (list, tuple, set, frozenset)):
        return [normalize_value(v, strip_html_style) for v in value]
    if isinstance(value, dict):
        return {str(k): normalize_value(v, strip_html_style) for k, v in value.items()}

    # Graceful fallback for custom objects implementing a toJSON serialization target hook
    if hasattr(value, "toJSON") and callable(value.toJSON):
        return normalize_value(value.toJSON(), strip_html_style)
    if hasattr(value, "to_json") and callable(value.to_json):
        return normalize_value(value.to_json(), strip_html_style)

    # Silent fallback for unreadable items like functions, mimicking JSON's drop behavior
    return None


def _is_primitive(val: Any) -> bool:
    return val is None or isinstance(val, (bool, int, float, str))


def _encode_primitive(val: Any, delimiter: str) -> str:
    if val is None:
        return "null"
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, str):
        if _is_safe_unquoted(val, delimiter):
            return val
        return f'"{_escape_string(val)}"'
    return str(val)


def _encode_key(key: Any) -> str:
    k_str = str(key)
    if _is_valid_unquoted_key(k_str):
        return k_str
    return f'"{_escape_string(k_str)}"'


def _is_tabular_array(arr: List[Any]) -> Tuple[bool, List[str]]:
    if not arr or not isinstance(arr[0], dict):
        return False, []
    first_keys = list(arr[0].keys())
    if not first_keys:
        return False, []

    for item in arr:
        if not isinstance(item, dict):
            return False, []
        if len(item) != len(first_keys):
            return False, []
        for k in first_keys:
            if k not in item or not _is_primitive(item[k]):
                return False, []
    return True, first_keys


def _indent_line(depth: int, content: str, indent_size: int) -> str:
    return (" " * (depth * indent_size)) + content


def _format_header(length: int, key=None, fields=None, delimiter: str = ",") -> str:
    header = ""
    if key is not None:
        header += _encode_key(key)

    header += f"[{length}"
    if delimiter != ",":
        header += delimiter
    header += "]"

    if fields:
        enc_fields = [_encode_key(f) for f in fields]
        header += f"{{{delimiter.join(enc_fields)}}}"

    header += ":"
    return header


def _encode_dict(
    obj: dict, depth: int, indent_size: int, delimiter: str
) -> Iterator[str]:
    for k, v in obj.items():
        yield from _encode_kv(k, v, depth, indent_size, delimiter)


def _encode_kv(
    key: Any, value: Any, depth: int, indent_size: int, delimiter: str
) -> Iterator[str]:
    enc_k = _encode_key(key)
    if _is_primitive(value):
        yield _indent_line(
            depth, f"{enc_k}: {_encode_primitive(value, delimiter)}", indent_size
        )
    elif isinstance(value, list):
        if len(value) == 0:
            yield _indent_line(
                depth, _format_header(0, key=key, delimiter=delimiter), indent_size
            )
        elif all(_is_primitive(v) for v in value):
            joined = delimiter.join(_encode_primitive(v, delimiter) for v in value)
            yield _indent_line(
                depth,
                f"{_format_header(len(value), key=key, delimiter=delimiter)} {joined}",
                indent_size,
            )
        else:
            is_tabular, headers = _is_tabular_array(value)
            if is_tabular:
                yield _indent_line(
                    depth,
                    _format_header(
                        len(value), key=key, fields=headers, delimiter=delimiter
                    ),
                    indent_size,
                )
                for item in value:
                    joined = delimiter.join(
                        _encode_primitive(item[h], delimiter) for h in headers
                    )
                    yield _indent_line(depth + 1, joined, indent_size)
            else:
                yield _indent_line(
                    depth,
                    _format_header(len(value), key=key, delimiter=delimiter),
                    indent_size,
                )
                for item in value:
                    yield from _encode_list_item(
                        item, depth + 1, indent_size, delimiter
                    )
    elif isinstance(value, dict):
        yield _indent_line(depth, f"{enc_k}:", indent_size)
        if value:
            yield from _encode_dict(value, depth + 1, indent_size, delimiter)


def _encode_list_item(
    value: Any, depth: int, indent_size: int, delimiter: str
) -> Iterator[str]:
    if _is_primitive(value):
        yield _indent_line(
            depth, f"- {_encode_primitive(value, delimiter)}", indent_size
        )
    elif isinstance(value, list):
        if all(_is_primitive(v) for v in value):
            joined = delimiter.join(_encode_primitive(v, delimiter) for v in value)
            yield _indent_line(
                depth,
                f"- {_format_header(len(value), delimiter=delimiter)} {joined}",
                indent_size,
            )
        else:
            yield _indent_line(
                depth,
                f"- {_format_header(len(value), delimiter=delimiter)}",
                indent_size,
            )
            for item in value:
                yield from _encode_list_item(item, depth + 1, indent_size, delimiter)
    elif isinstance(value, dict):
        if not value:
            yield _indent_line(depth, "- ", indent_size)
            return

        entries = list(value.items())
        first_k, first_v = entries[0]
        enc_first_k = _encode_key(first_k)

        if isinstance(first_v, list) and len(first_v) > 0:
            tabular, headers = _is_tabular_array(first_v)
            if tabular:
                yield _indent_line(
                    depth,
                    f"- {_format_header(len(first_v), key=first_k, fields=headers, delimiter=delimiter)}",
                    indent_size,
                )
                for item in first_v:
                    joined = delimiter.join(
                        _encode_primitive(item[h], delimiter) for h in headers
                    )
                    yield _indent_line(depth + 2, joined, indent_size)
                if len(entries) > 1:
                    rest_dict = dict(entries[1:])
                    yield from _encode_dict(
                        rest_dict, depth + 1, indent_size, delimiter
                    )
                return

        if _is_primitive(first_v):
            yield _indent_line(
                depth,
                f"- {enc_first_k}: {_encode_primitive(first_v, delimiter)}",
                indent_size,
            )
        elif isinstance(first_v, list):
            if len(first_v) == 0:
                yield _indent_line(
                    depth,
                    f"- {enc_first_k}{_format_header(0, delimiter=delimiter)}",
                    indent_size,
                )
            elif all(_is_primitive(v) for v in first_v):
                joined = delimiter.join(
                    _encode_primitive(v, delimiter) for v in first_v
                )
                yield _indent_line(
                    depth,
                    f"- {enc_first_k}{_format_header(len(first_v), delimiter=delimiter)} {joined}",
                    indent_size,
                )
            else:
                yield _indent_line(
                    depth,
                    f"- {enc_first_k}{_format_header(len(first_v), delimiter=delimiter)}",
                    indent_size,
                )
                for item in first_v:
                    yield from _encode_list_item(
                        item, depth + 2, indent_size, delimiter
                    )
        elif isinstance(first_v, dict):
            yield _indent_line(depth, f"- {enc_first_k}:", indent_size)
            if first_v:
                yield from _encode_dict(first_v, depth + 2, indent_size, delimiter)

        if len(entries) > 1:
            rest_dict = dict(entries[1:])
            yield from _encode_dict(rest_dict, depth + 1, indent_size, delimiter)


def encode_lines(
    data: Any, indent: int = 2, delimiter: str = ",", strip_html_style: bool = False
) -> Iterator[str]:
    """
    Core generator returning lines instead of full string.
    Suitable for streaming large inputs.
    """
    # 1. Normalize strictly to JSON limits matching TS behavior
    data = normalize_value(data, strip_html_style)

    if _is_primitive(data):
        enc_val = _encode_primitive(data, delimiter)
        if enc_val:
            yield enc_val
    elif isinstance(data, list):
        if not data:
            yield _format_header(0, delimiter=delimiter)
        elif all(_is_primitive(v) for v in data):
            joined = delimiter.join(_encode_primitive(v, delimiter) for v in data)
            yield f"{_format_header(len(data), delimiter=delimiter)} {joined}"
        else:
            is_tabular, headers = _is_tabular_array(data)
            if is_tabular:
                yield _format_header(len(data), fields=headers, delimiter=delimiter)
                for item in data:
                    joined = delimiter.join(
                        _encode_primitive(item[h], delimiter) for h in headers
                    )
                    yield _indent_line(1, joined, indent)
            else:
                yield _format_header(len(data), delimiter=delimiter)
                for item in data:
                    yield from _encode_list_item(item, 1, indent, delimiter)
    elif isinstance(data, dict):
        yield from _encode_dict(data, 0, indent, delimiter)


def encode(
    data: Any, indent: int = 2, delimiter: str = ",", strip_html_style: bool = False
) -> str:
    """
    Encodes a Python value (dict, list, primitive) into a TOON formatted string.

    【主入口方法解说】
    接收包含复杂嵌套结构的 Python 变量体系（如原生的 json 解析对象）。通过内部深度优先的生成器矩阵和结构对齐，
    将其最终吐出为能够直接硬编码嵌入给 GPT/Claude/Gemini 等大模型 Prompt 阅读的 TOON 语境化压缩多行字符实体。
    此方法正是所有后续省 Token 转换流的总开关。

    【兼容性处理】
    如果传入的数据已经是字符串且不是明显的 JSON 结构（Dict 或 List），则原样返回，确保接口在高频调用下的稳健性。
    """
    if isinstance(data, str) and not (
        data.strip().startswith("{") or data.strip().startswith("[")
    ):
        return data

    return "\n".join(encode_lines(data, indent, delimiter, strip_html_style))