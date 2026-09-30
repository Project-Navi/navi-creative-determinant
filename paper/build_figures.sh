#!/usr/bin/env bash
# Render the stack diagram in the pinned environment and install or check the four outputs.
#
# paper/stack_figures.py renders paper/cd_stack.dot as the docs SVG (committed twice, next to the
# source and under docs/assets) and as the two paper figure PDFs. The outputs depend on the source,
# the renderer, Graphviz and the fonts, so they are rendered in the image built from
# paper/figures.Dockerfile, which pins all of them. The checkout is mounted read-only and the
# renderer writes into an empty directory, without network access.
#
# Usage: paper/build_figures.sh check [OUTPUT_DIR]   render into OUTPUT_DIR (created if absent,
#                                                    must be empty; default: a temporary
#                                                    directory) and require each committed output
#                                                    to be byte-identical to its render
#        paper/build_figures.sh update               render and copy the outputs into place
# Needs: docker.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$HERE")"
OUTPUTS=(paper/cd_stack.svg docs/assets/cd-stack.svg paper/cd_stack_core.pdf paper/cd_stack_loop.pdf)

mode="${1:-}"
if [[ $mode != check && $mode != update ]]; then
  echo "usage: paper/build_figures.sh check [OUTPUT_DIR] | update" >&2
  exit 2
fi

if [[ $mode == check && -n "${2:-}" ]]; then
  OUT="$2"
  mkdir -p "$OUT"
  if [[ -n "$(ls -A "$OUT")" ]]; then
    echo "$OUT is not empty" >&2
    exit 2
  fi
  OUT="$(cd "$OUT" && pwd)"
else
  OUT="$(mktemp -d)"
  trap 'rm -r "$OUT"' EXIT
fi

TAG="cd-stack-figures:$(sha256sum "$HERE/figures.Dockerfile" | cut -c1-16)"
docker build --quiet --tag "$TAG" - < "$HERE/figures.Dockerfile" > /dev/null

docker run --rm --network none \
  --user "$(id -u):$(id -g)" \
  --volume "$ROOT:/src:ro" \
  --volume "$OUT:/out" \
  --env HOME=/tmp \
  "$TAG" \
  python3 /src/paper/stack_figures.py --out /out

if [[ $mode == update ]]; then
  for f in "${OUTPUTS[@]}"; do
    cp "$OUT/$f" "$ROOT/$f"
  done
  echo "rendered and installed ${OUTPUTS[*]}"
  exit 0
fi

stale=0
for f in "${OUTPUTS[@]}"; do
  if cmp -s "$OUT/$f" "$ROOT/$f"; then
    echo "identical  $f"
  else
    echo "DIFFERS    $f"
    stale=1
  fi
done
if ((stale)); then
  echo "the committed stack diagram outputs are not the render of the current source, renderer and environment; run make -C paper" >&2
  exit 1
fi
