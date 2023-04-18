"""Defines transformation test cases

Test cases are of the form:

    actual = expression
    expected = expression
    assert actual == expected, "description"
"""
import tagstr

actual = func @ "hello"
expected = func @ "hello"
assert actual == expected, "check no transformation for non-format string"

actual = func @ f"hello"
expected = func ( 'hello', )
assert actual == expected, "check transformation for format string"
