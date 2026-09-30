# Contributing to Creative Determinant

The full contributing guide is at <https://docs.projectnavi.ai/navi-creative-determinant/how-to/contributing/>.

Before opening a pull request:

1. **uv only.** Install with `uv sync`; do not use `pip`.
2. **Run the tests.** `uv run pytest tests/ -v` must pass. Never weaken a test to get a pass; the rule for a failing test is in [tests/README.md](tests/README.md#when-a-test-fails).
3. **Conventional commits and branch names.** Commit titles are `<type>: <description>` (`feat`, `fix`, `refactor`, `test`, `chore`, `docs`, `ci`, `perf`) and branches are `<type>/<slug>`.
4. **Label mathematical claims.** Mark every result as **Theorem**, **Conjecture**, **Heuristic** or **Observation (numerical)**, and be explicit about what is proved, what is conditional and what is interpretation.
