from __future__ import annotations

import ast
from pathlib import Path
from typing import TypedDict


class Case(TypedDict, total=False):
    actual: str
    expected: str
    message: str


def parse_cases(file: Path | str) -> list[Case]:
    cases: list[Case] = []
    source = Path(file).read_text()
    source_lines = source.splitlines()

    loc: _CaseLoc = {}
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign):
            assert "message" not in loc
            assert len(node.targets) == 1
            assert isinstance(node.targets[0], ast.Name)

            target_1 = node.targets[0].id

            assert target_1 not in loc, f"More than one {target_1} in a case"

            assert target_1 in ("actual", "expected")
            loc[target_1] = (
                (node.value.lineno, node.value.col_offset),
                (node.value.end_lineno, node.value.end_col_offset),
            )

        elif isinstance(node, ast.Assert):
            assert "actual" in loc and "expected" in loc, "Missing actual or expected"
            a_start, a_end = loc["actual"]
            a_start_line, a_start_col = a_start
            a_end_line, a_end_col = a_end

            a_lines = source_lines[a_start_line - 1 : a_end_line]
            a_slice_end = len(a_lines[-1]) - a_end_col or None
            actual_src = "\n".join(a_lines)[a_start_col:a_slice_end]

            e_start, e_end = loc["expected"]
            e_start_line, e_start_col = e_start
            e_end_line, e_end_col = e_end

            e_lines = source_lines[e_start_line - 1 : e_end_line]
            e_slice_end = len(e_lines[-1]) - e_end_col or None
            expected_src = "\n".join(e_lines)[e_start_col:e_slice_end]

            cases.append(
                {
                    "actual": actual_src,
                    "expected": expected_src,
                    "message": node.msg.s,
                }
            )
            loc = {}
    return cases


class _CaseLoc(TypedDict, total=False):
    actual: tuple[int, int]
    expected: tuple[int, int]
