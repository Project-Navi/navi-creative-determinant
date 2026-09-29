#!/usr/bin/env python3
"""Validate an executed copy of ``notebooks/cd_pde_demo.ipynb``.

The notebook asserts its own numerical claims and prints ``CHECK PASSED: <claim>`` for each
one, then ``ALL_NOTEBOOK_CHECKS_PASSED`` at the end. This script rejects the executed notebook
if any of the following holds:

* a cell has an error output (a failed assertion or any exception);
* a code cell with source was not executed (no execution count);
* the text ``CHECK FAILED`` appears in any output;
* fewer than ``--min-checks`` ``CHECK PASSED`` lines were printed;
* the final marker ``ALL_NOTEBOOK_CHECKS_PASSED`` is missing, or appears in a cell before the
  last ``CHECK PASSED`` line;
* a required claim (``REQUIRED_CHECKS``, the notebook's essential scientific assertions) is
  missing or printed more than once, regardless of how many other checks passed.

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

# The essential claims of notebooks/cd_pde_demo.ipynb, by the exact name each check prints,
# listed in notebook order. Each must appear exactly once; losing any of them fails validation
# even if the count of other passed checks stays high. The list includes the convergence and
# residual checks the other claims depend on (a claim about a converged solve is vacuous
# without them), the Lean crosswalk facts of the triangle, and the 3D sign statements.
REQUIRED_CHECKS = [
    "FD eigenvalue equals the exact discrete formula",
    "FD eigenvalue is within O(h^2) of the continuum formula",
    "all 20 solves converged (residual-validated)",
    "every converged maximum respects the a = 0 discrete maximum-principle bound",
    "lambda_1 > 0: the zero branch (exact for a = 0)",
    "lambda_1 < 0: a positive branch",
    "iterates from the subsolution are nondecreasing",
    "iterates from the plateau are nonincreasing",
    "a clipped run returns the zero branch: not evidence of nonexistence",
    "second-order convergence of max Phi (ratios ~ 4)",
    "discrete residual at solver tolerance on every grid",
    "converse barrier identities hold analytically on the grid",
    "continuum converse: positive branch below the linear threshold (lambda_1 = +1/4, a = 1)",
    "continuum converse: the branch lies between the barriers v and 3/4",
    "collocation (a = 0) agrees with FD to 1e-5",
    "collocation (a = 0.5) agrees with FD to 1e-5",
    "residual at k = 1 is at tolerance",
    "every scaled field k != 1 has a residual above 1e-2",
    "wherever lambda_1 < 0 the solver found the positive branch (sufficiency, Theorem 3.16)",
    "both 2D solves converged with residual_2d < 1e-6",
    "positive case: lambda_1 < 0 and a positive branch",
    "collapsed case: lambda_1 > 0 and the zero solution",
    "triangle: L u = 2 and |grad u| = 2 at both interior vertices",
    "triangle: (0, 2, 2) is an exact solution",
    "triangle: energy(0,1,1) = -2 and lambda_1 = -1",
    "triangle: all hypotheses of exists_pos_graph hold",
    "proof constants match the Lean construction",
    "Jacobi iteration from eps*phi increases to (0, 2, 2)",
    "Jacobi iteration from the plateau decreases to (0, 2, 2)",
    "converse counterexample: positive solution with lambda_1 = +1/2",
    "graph bound 5/4 is attained, the continuum cap 1 is exceeded",
    "graph gradient sqrt(2) vs centered difference 0",
    "3D asymmetric anisotropic potential matches an independent assembly",
    "3D constant-coefficient eigenvalue matches the exact discrete formula",
    "3D: weak bump (lambda = 0.3) negative and strong bump (lambda = 1.5) positive discrete indicator",
    "3D near threshold: discrete indicator negative while the continuum value is positive",
]


def _output_text(output: dict) -> str:
    if output.get("output_type") == "stream":
        text = output.get("text", "")
        return "".join(text) if isinstance(text, list) else str(text)
    data = output.get("data", {}) if isinstance(output, dict) else {}
    text = data.get("text/plain", "")
    return "".join(text) if isinstance(text, list) else str(text)


def validate(
    path: str | pathlib.Path, min_checks: int = 30, required: list[str] | None = None
) -> tuple[bool, list[str]]:
    """Return ``(ok, messages)``; ``messages`` lists every violation found.

    ``required`` defaults to ``REQUIRED_CHECKS``; pass an empty list to validate a notebook
    that is not the project's demonstration notebook.
    """
    required_names = REQUIRED_CHECKS if required is None else list(required)
    nb = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    messages: list[str] = []
    passed = 0
    all_text: list[str] = []
    names: list[str] = []
    last_check_cell = -1
    marker_cell = -1
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
            for line in text.splitlines():
                if line.startswith(PASS_MARKER):
                    passed += 1
                    names.append(line[len(PASS_MARKER) :].lstrip(": ").strip())
                    last_check_cell = index
                if line.strip() == FINAL_MARKER:
                    marker_cell = index
            if FAIL_MARKER in text:
                messages.append(f"cell {index}: output contains {FAIL_MARKER}")
    joined = "\n".join(all_text)
    if FINAL_MARKER not in joined:
        messages.append(f"final marker {FINAL_MARKER} not found in any output")
    elif marker_cell < last_check_cell:
        messages.append(
            f"final marker appears in cell {marker_cell}, before the last check in cell {last_check_cell}"
        )
    if passed < min_checks:
        messages.append(f"only {passed} {PASS_MARKER} lines; at least {min_checks} checks required")
    for name in required_names:
        count = names.count(name)
        if count != 1:
            messages.append(
                f"required claim {'missing' if count == 0 else 'duplicated'} ({count}x): {name}"
            )
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
    parser.add_argument(
        "--no-required",
        action="store_true",
        help="do not require the project's essential claims (for notebooks other than cd_pde_demo)",
    )
    args = parser.parse_args(argv)
    ok, messages = validate(
        args.notebook, min_checks=args.min_checks, required=[] if args.no_required else None
    )
    for message in messages:
        print(message)
    print("NOTEBOOK VALID" if ok else "NOTEBOOK INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
