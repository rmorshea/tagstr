from __future__ import annotations

from pathlib import Path

import pytest
from tagstr.transform import transform_string

from tests.cases import Case, parse_cases

case_file = Path(__file__).parent / "cases" / "transform.py"


@pytest.mark.parametrize("case", parse_cases("transform"))
def test_transform(case: Case) -> None:
    given = transform_string(case["given"])
    expect = case["expect"]
    assert given == expect, case["message"]
