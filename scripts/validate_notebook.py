#!/usr/bin/env python3
"""Validate an executed copy of ``notebooks/cd_pde_demo.ipynb``.

The notebook asserts its own numerical claims and prints ``CHECK PASSED: <claim>`` for each
one, then ``ALL_NOTEBOOK_CHECKS_PASSED`` at the end. This script rejects the executed notebook
if any of the following holds:

* a cell has an error output (a failed assertion or any exception);
* a code cell with source was not executed (no execution count);
* the text ``CHECK FAILED`` appears in any output;
* fewer than ``--min-checks`` ``CHECK PASSED`` lines were printed;
* the final marker ``ALL_NOTEBOOK_CHECKS_PASSED`` is missing.

Counting output cells is not a validation; this script does not do it. Exit status 0 means
every condition above was checked and none failed.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

FINAL_MARKER = "ALL_NOTEBOOK_CHECKS_PASSED"
PASS_MARKER = "CHECK PASSED"
FAIL_MARKER = "CHECK FAILED"


def _output_text(output: dict) -> str:
    if output.get("output_type") == "stream":
        text = output.get("text", "")
        return "".join(text) if isinstance(text, list) else str(text)
    data = output.get("data", {}) if isinstance(output, dict) else {}
    text = data.get("text/plain", "")
    return "".join(text) if isinstance(text, list) else str(text)


def validate(path: str | pathlib.Path, min_checks: int = 30) -> tuple[bool, list[str]]:
    """Return ``(ok, messages)``; ``messages`` lists every violation found."""
    nb = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    messages: list[str] = []
    passed = 0
    all_text: list[str] = []
    for index, cell in enumerate(nb.get("cells", [])):
        if cell.get("cell_type") != "code":
            continue
        source = cell.get("source", "")
        source = "".join(source) if isinstance(source, list) else str(source)
        if not source.strip():
            continue
        if cell.get("execution_count") is None:
            messages.append(f"cell {index}: code cell not executed")
        for output in cell.get("outputs", []):
            if output.get("output_type") == "error":
                messages.append(
                    f"cell {index}: error output {output.get('ename', '?')}: {output.get('evalue', '')}"
                )
            text = _output_text(output)
            all_text.append(text)
            passed += sum(1 for line in text.splitlines() if line.startswith(PASS_MARKER))
            if FAIL_MARKER in text:
                messages.append(f"cell {index}: output contains {FAIL_MARKER}")
    joined = "\n".join(all_text)
    if FINAL_MARKER not in joined:
        messages.append(f"final marker {FINAL_MARKER} not found in any output")
    if passed < min_checks:
        messages.append(f"only {passed} {PASS_MARKER} lines; at least {min_checks} checks required")
    ok = not messages
    messages.append(f"{passed} passed checks counted")
    return ok, messages


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("notebook", help="path to the executed notebook")
    parser.add_argument(
        "--min-checks", type=int, default=30, help="minimum number of CHECK PASSED lines"
    )
    args = parser.parse_args(argv)
    ok, messages = validate(args.notebook, min_checks=args.min_checks)
    for message in messages:
        print(message)
    print("NOTEBOOK VALID" if ok else "NOTEBOOK INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
