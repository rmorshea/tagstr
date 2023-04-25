from __future__ import annotations

import pytest
from tagstr.utils import decode_raw, format_value


def test_decode_raw():
    """Test that decode_raw decodes unicode escape characters"""
    assert list(decode_raw("a\\u00f1")) == ["añ"]
    assert list(decode_raw("a\\u00f1", "b\\u00f1")) == ["añ", "bñ"]


def test_decode_raw_ignores_thunks():
    """Test that decode_raw ignores thunks"""
    thunk = (lambda: None, "a", None, None)
    assert list(decode_raw(thunk)) == [thunk]


def test_format_value():
    # ignore string
    assert format_value("a") == "a"

    # handle string formatting
    assert format_value((lambda: "a", "expr", None, None)) == "a"
    assert format_value((lambda: "a", "expr", "r", None)) == "'a'"
    assert format_value((lambda: "a", "expr", "s", None)) == "a"
    assert format_value((lambda: "a", "expr", "a", None)) == "'a'"
    assert format_value((lambda: "a", "expr", "a", "5")) == "'a'  "

    # numeric tests
    assert format_value((lambda: 1, "expr", None, None)) == "1"
    assert format_value((lambda: 1, "expr", None, ".2f")) == "1.00"


def test_format_invalid_value():
    with pytest.raises(ValueError):
        format_value(1)
    # check bad formatting character
    with pytest.raises(ValueError):
        format_value((lambda: 1, "expr", "not-a-formatting-character", None))
