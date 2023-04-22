import sys

if sys.version_info < (3, 10):
    from tagstr._py_lt_310 import decode_raw, format_value
else:
    from tagstr._py_gte_310 import decode_raw, format_value

__all__ = ["format_value", "decode_raw"]
