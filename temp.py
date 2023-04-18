import tagstr
from tagstr import Thunk, tag


@tag
def my_func(*args: Thunk | str) -> None:
    print(args)


name = "world"
my_func @ (f"Hello {name}!")
