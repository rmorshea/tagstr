from __future__ import annotations

from typing import Iterator

from tagstr.types import Thunk


def decode_raw(*args: str | Thunk) -> Iterator[str | Thunk]:
    """Decode raw strings and thunks."""
    for arg in args:
        if isinstance(arg, str):
            yield arg.encode("utf-8").decode("unicode-escape")
        else:
            yield arg


def format_value(arg: str | Thunk) -> str:
    """Format a value from a thunk or a string."""
    if isinstance(arg, str):
        return arg
    elif isinstance(arg, tuple) and len(arg) == 4:
        getvalue, _, conv, spec = arg
        value = getvalue()
        if conv == "r":
            value = repr(value)
        elif conv == "s":
            value = str(value)
        elif conv == "a":
            value = ascii(value)
        elif conv is None:
            pass
        else:
            raise ValueError(f"Bad conversion: {conv!r}")
        return format(value, spec if spec is not None else "")
    else:
        raise ValueError(f"Cannot format {arg!r} - expected a thunk or a string")
