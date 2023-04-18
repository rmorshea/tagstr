import tagstr


@tagstr.tagfunc
def my_func(*args: tagstr.Thunk | str) -> None:
    print(args)


name = "world"
my_func @ (f"Hello {name}!")
