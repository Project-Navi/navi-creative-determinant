---
name: bump-cd-formalization
description: Fetch the latest commit on Project-Navi/cd-formalization main, show the commit log between the current submodule pin and upstream HEAD, update the submodule pointer, and draft a conventional-commit message summarising the bump. Use when the Lean 4 submodule needs updating.
disable-model-invocation: true
---

# Bump cd_formalization submodule

Automates the workflow for updating the Lean 4 formalization submodule pointer and writing a descriptive commit message.

## Workflow

1. **Confirm submodule is initialised.** If `cd_formalization/` is empty, run `git submodule update --init --recursive` first.

2. **Fetch upstream:**
   ```bash
   git -C cd_formalization fetch
   ```
   The submodule's remote is usually `origin`; if a different name is configured, adjust accordingly.

3. **Compute the diff range:**
   ```bash
   current=$(git -C cd_formalization rev-parse HEAD)
   target=$(git -C cd_formalization rev-parse origin/main)
   echo "Current: $current"
   echo "Target:  $target"
   git -C cd_formalization log --oneline "$current..$target"
   ```

4. **Summarise the commit log** by theme:
   - proof changes (new theorems, refactors, `sorry` removed/added)
   - API changes in Lean definitions (signatures of `SemioticContext`, `PdeInfra`, etc.)
   - axiom surface changes (anything touching `CdFormal/Axioms.lean` or `PdeInfra`)
   - docs / CI / infrastructure

5. **Flag material changes prominently.** If the diff includes any of:
   - New `sorry` in Lean files (regression from zero-sorry status)
   - Added or removed `PdeInfra` axioms
   - Renamed or removed public lemmas/theorems referenced from this parent repo
   stop and confirm with the user before bumping.

6. **Present to user.** Show:
   - Old SHA → New SHA
   - Commit count
   - Themed summary
   - Any red flags
   Wait for explicit confirmation.

7. **On confirmation, bump the pointer:**
   ```bash
   git -C cd_formalization checkout "$target"
   git add cd_formalization
   ```

8. **Draft commit message:**
   ```
   chore: bump cd_formalization submodule <short-old>..<short-new>

   Includes <N> upstream commits:
   - <theme 1>: <bullet summary>
   - <theme 2>: <bullet summary>
   ```
   Do NOT auto-commit; hand the staged change back to the user to review and commit.

## Safety rails

- Never bump to a commit not reachable from `origin/main` upstream.
- Never `--force` anything in the submodule.
- Never bump across a change that adds `sorry` to Lean files without explicit user acknowledgement.
- Never bump if the submodule has uncommitted local modifications — surface them and stop.
- If the parent repo has its own uncommitted changes, don't stage them alongside the submodule bump — keep the chore PR single-purpose.

## Example output

```
Current submodule pointer: d6587dbf (docs: add badges to README)
Upstream main:             eb9364ad (Merge pull request #8 from proof-golf-aristotle)

20 commits between pins. Themes:
  • proof golf: 4 commits refactoring algebraic lemmas (no new sorry)
  • CI/infra:   6 commits — unified org ruleset, scorecard fix, pre-commit SHA pinning
  • docs:       7 commits — Zensical site scaffold, README badges, CLAUDE.md
  • housekeeping: 3 commits — CODEOWNERS, brand CSS vendoring

No axiom surface changes detected. No new sorry. Safe to bump.

Proceed? (y/n)
```
