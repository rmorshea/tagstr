from __future__ import annotations
from typing import Generic, TypeVar, Protocol

from tagstr.utils import Thunk

T = TypeVar("T")


class tagfunc(Generic[T]):
    def __init__(self, func: TagFunc[T]) -> None:
        self.func = func

    def __matmul__(self, other: str) -> T:
        raise NotImplementedError(
            "Usages of `tag @ f'string'` must be transpiled - is there an "
            "`import tagstr` statement placed at the top of your file?"
        )

    def __call__(self, *args: str | Thunk) -> T:
        return self.func(*args)


class TagFunc(Protocol[T]):
    def __call__(self, *args: Thunk) -> T:
        ...
