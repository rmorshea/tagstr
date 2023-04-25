from __future__ import annotations

from pathlib import Path
from typing import TypedDict

HERE = Path(__file__).parent


class Case(TypedDict, total=False):
    given: str
    expect: str
    message: str


def parse_cases(name: str) -> list[Case]:
    source = (HERE / f"{name}.case.py").read_text()
    source_lines = source.splitlines()

    locations: list[_CaseLoc] = []
    for index, line in enumerate(source_lines):
        if line.startswith("# GIVEN:"):
            locations.append({"given": index})
        elif line.startswith("# EXPECT:"):
            assert "given" in locations[-1] and "expect" not in locations[-1]
            locations[-1]["expect"] = index
        elif line.startswith("# END"):
            assert "expect" in locations[-1] and "end" not in locations[-1]
            locations[-1]["end"] = index

    cases: list[Case] = []
    for loc in locations:
        given_line = loc['given']
        expect_line = loc['expect']
        end_line = loc['end']

        given = "\n".join(source_lines[given_line + 1 : expect_line])
        expect = "\n".join(source_lines[expect_line + 1 : end_line])

        given_msg = source_lines[given_line][1:].strip()
        expect_msg = source_lines[expect_line][1:].strip()
        message = f"\n{given_msg}\n{expect_msg}"
        cases.append({"given": given, "expect": expect, "message": message})

    return cases


class _CaseLoc(TypedDict, total=False):
    given: int
    expect: int
    end: int
