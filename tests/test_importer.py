# tagstr: on


def test_simple_conversion():
    def raw(*args):
        values = []
        for a in args:
            if isinstance(a, str):
                values.append(a)
            else:
                getvalue, raw, format, convert = a
                values.append((getvalue(), raw, format, convert))
        return values

    result = raw @ f"{1} {2} {3}"

    assert result == [
        (1, "1", None, None),
        " ",
        (2, "2", None, None),
        " ",
        (3, "3", None, None),
    ]
