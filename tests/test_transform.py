from __future__ import annotations

import pytest
from pathlib import Path

from tagstr.transform import transform_string
from tests.case_utils import parse_cases, Case

case_file = Path(__file__).parent / "cases" / "transform.py"


@pytest.mark.parametrize("case", parse_cases(case_file))
def test_transform(case: Case) -> None:
    actual = transform_string(case["actual"])
    expected = case["expected"]
    assert actual == expected, case["message"]
