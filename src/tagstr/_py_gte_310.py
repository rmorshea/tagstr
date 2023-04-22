from __future__ import annotations

from typing import Iterator

from tagstr.types import Thunk


def decode_raw(*args: str | Thunk) -> Iterator[str | Thunk]:
    """Decode raw strings and thunks."""
    for arg in args:
        match arg:
            case str():
                yield arg.encode("utf-8").decode("unicode-escape")
            case _:
                yield arg


def format_value(arg: str | Thunk) -> str:
    """Format a value from a thunk or a string."""
    match arg:
        case str():
            return arg
        case getvalue, _, conv, spec:
            value = getvalue()
            match conv:
                case "r":
                    value = repr(value)
                case "s":
                    value = str(value)
                case "a":
                    value = ascii(value)
                case None:
                    pass
                case _:
                    raise ValueError(f"Bad conversion: {conv!r}")
            return format(value, spec if spec is not None else "")
        case _:
            raise ValueError(f"Cannot format {arg!r} - expected a thunk or a string")
