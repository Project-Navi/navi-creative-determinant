# Contributing to Creative Determinant

Thank you for your interest in contributing to the Creative Determinant (CD) framework. The full contributing guide, covering the kinds of contributions we want, how to propose them, the contribution standards and licensing, lives at <https://docs.projectnavi.ai/navi-creative-determinant/how-to/contributing/>.

Four things to know before opening a pull request:

1. **uv only.** Install with `uv sync`; do not use `pip`.
2. **Run the tests.** `uv run pytest tests/ -v` must pass; the tests validate mathematical claims, so a failure after a change to `src/cd/` means the math is wrong, not the test.
3. **Conventional commits and branch names.** Commit titles are `<type>: <description>` (`feat`, `fix`, `refactor`, `test`, `chore`, `docs`, `ci`, `perf`) and branches are `<type>/<slug>`.
4. **Label mathematical claims.** Mark every result as **Theorem**, **Conjecture**, **Heuristic** or **Observation (numerical)**, and be explicit about what is proved, what is conditional and what is interpretation.
