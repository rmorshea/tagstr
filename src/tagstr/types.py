from __future__ import annotations

from typing import Any, Callable, Protocol, TypeVar, Union

Thunk = tuple[Callable[[], Any], str, Union[str, None], Union[str, None]]
"""
A "thunk" is a tuple contianing the following:

1. getvalue: a callable that returns the value to be formatted
2. raw: the raw string that was used to create the thunk
3. conv: the conversion character (e.g. "r", "s", "a")
4. formatspec: the format specification (e.g. ".2f")

TODO: thunks likely should like be a namedtuple in the future.
"""


T_co = TypeVar("T_co", covariant=True)


class TagFunc(Protocol[T_co]):
    def __call__(self, *args: str | Thunk) -> T_co:
        ...
