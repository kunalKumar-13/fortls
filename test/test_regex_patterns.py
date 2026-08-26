from __future__ import annotations

import pytest

from fortls.regex_patterns import FortranRegularExpressions as FRegex
from fortls.regex_patterns import create_src_file_exts_regex


@pytest.mark.parametrize(
    "input_exts, input_files, matches",
    [
        (
            [],
            [
                "test.f",
                "test.F",
                "test.f90",
                "test.F90",
                "test.f03",
                "test.F03",
                "test.f18",
                "test.F18",
                "test.f77",
                "test.F77",
                "test.f95",
                "test.F95",
                "test.for",
                "test.FOR",
                "test.fpp",
                "test.FPP",
            ],
            [True] * 16,
        ),
        ([], ["test.ff", "test.f901", "test.f90.ff"], [False, False, False]),
        ([r"\.inc"], ["test.inc", "testinc", "test.inc2"], [True, False, False]),
        (["inc.*"], ["test.inc", "testinc", "test.inc2"], [True, True, True]),
        (["("], ["test.f90", "test.f90.ff"], [True, False]),
    ],
)
def test_src_file_exts(
    input_exts: list[str],
    input_files: list[str],
    matches: list[bool],
):
    regex = create_src_file_exts_regex(input_exts)
    results = [bool(regex.search(file)) for file in input_files]
    assert results == matches


@pytest.mark.parametrize(
    "line, matches",
    [
        # Real constructs, with and without a construct name.
        ("  block", True),
        ("  critical", True),
        ("  mylabel: block", True),
        ("  named: critical", True),
        ("  BLOCK", True),
        # Identifiers that merely start with the keyword. Regression test for
        # a `blocked_vector = ...` assignment being read as a BLOCK construct.
        ("  blocked_vector(1:2, 1) = 0", False),
        ("  block_size = 2", False),
        ("  blocks = 1", False),
        ("  criticality = 3", False),
    ],
)
def test_block_regex(line: str, matches: bool):
    assert bool(FRegex.BLOCK.match(line)) == matches


def test_block_regex_captures_construct_name():
    """The construct name is group(1) for both BLOCK and CRITICAL."""
    assert FRegex.BLOCK.match("  mylabel: block").group(1).strip() == "mylabel:"
    assert FRegex.BLOCK.match("  named: critical").group(1).strip() == "named:"
    assert FRegex.BLOCK.match("  block").group(1) is None
