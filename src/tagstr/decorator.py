from __future__ import annotations
from typing import Generic, TypeVar, Protocol, Callable, Any

T = TypeVar("T")


class tag(Generic[T]):
    def __init__(self, func: TagFunc[T]) -> None:
        self.func = func

    def __matmul__(self, other: str) -> T:
        raise NotImplementedError(
            "Usages of tag @ f'...' must be transpiled - "
            "tagstr encoding may not have been registered."
        )

    def __call__(self, *args: str | Thunk) -> T:
        return self.func(*args)


class TagFunc(Protocol[T]):
    def __call__(self, *args: Thunk) -> T:
        ...


Thunk = tuple[
    Callable[[], Any],  # getvalue
    str,  # raw
    str | None,  # conv
    str | None,  # formatspec
]
