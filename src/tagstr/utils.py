from typing import Callable, Any, Iterator

# TODO: thunks likely should have a "tuple-like object with named attributes"
# (so namedtuples) as seen in the os module. This will enable future expansion.
# Of course such named attribute support can also be done in the future!

Thunk = tuple[
    Callable[[], Any],  # getvalue
    str,  # raw
    str | None,  # conv
    str | None,  # formatspec
]


def decode_raw(*args: str | Thunk) -> Iterator[str | Thunk]:
    """Decode raw strings and thunks."""
    for arg in args:
        if isinstance(arg, str):
            yield arg.encode("utf-8").decode("unicode-escape")
        else:
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
