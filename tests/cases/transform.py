"""Defines transformation test cases

Test cases are of the form:

    actual = expression
    expected = expression
    assert "description"
"""

actual = func @ "hello"
expected = func @ "hello"
assert "no transformation for non-format string"

actual = func @ f"hello"
expected = func ( 'hello', )
assert "transformation for format string"

actual = func @ f"hello {name}"
expected = func ( 'hello ',(lambda:(name),'name',None,None), )
assert "handle simple interpolated value"

actual = func @ f"hello {name}!"
expected = func ( 'hello ',(lambda:(name),'name',None,None),'!', )
assert "handle simple interpolated value with end string"

actual = (
    func @ f"hello"
)
expected = (
    func ( 'hello', )
)
assert "handle format string in parentheses"

actual = func @ f"""
hello
"""
expected = func ( '\nhello\n', )\
\

assert "multi-line format string"

actual = func @ f"hello" + "something-else"
expected = func ( 'hello', )+"something-else"

assert "handle op after format string"

actual = func @ f"""
hello
""" + "something-else"
expected = func ( '\nhello\n', )\
\
    + "something-else"

assert "handle op after multi-line format string"
