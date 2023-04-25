import pytest
from tagstr.decorator import tagfunc


def test_no_implemented_error():
    @tagfunc
    def some_func():
        pass

    with pytest.raises(NotImplementedError):
        # note this is not an f-string
        some_func @ "some string"
