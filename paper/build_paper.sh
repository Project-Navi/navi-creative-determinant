#!/usr/bin/env bash
# Build paper/creative_determinant.pdf in the pinned TeX Live environment.
#
# The committed PDF and the CI rebuild are both produced by this script, in the same Docker
# image (pinned by digest: texlive/texlive:TL2025-historic, a frozen TeX Live 2025 snapshot)
# with a fixed SOURCE_DATE_EPOCH, so the output is byte-for-byte reproducible and CI can require
# identity (scripts/check_paper_artifact.py). Change the image digest and the epoch only
# together with a rebuilt and recommitted PDF.
#
# Usage: paper/build_paper.sh [OUTPUT_DIR [FIGURE_DIR]]
#   OUTPUT_DIR  default paper/build (git-ignored)
#   FIGURE_DIR  where the stack figures cd_stack_{core,loop}.pdf are taken from; default paper/.
#               The paper workflow passes the directory that paper/build_figures.sh rendered and
#               checked against the committed figures.
# Needs: docker. The build runs as the calling user; nothing is written outside OUTPUT_DIR.
set -euo pipefail

IMAGE="texlive/texlive@sha256:f25ee2dcd00f58198f918064f4a1c8562410b33e84155bd55b02b419d73d9391"
EPOCH="1767225600"   # 2026-01-01T00:00:00Z: fixed PDF creation/modification date and trailer ID

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="${1:-$HERE/build}"
FIG="${2:-$HERE}"
mkdir -p "$OUT"
OUT="$(cd "$OUT" && pwd)"
cp "$HERE/creative_determinant.tex" "$HERE/cd_refs.bib" "$FIG/cd_stack_core.pdf" "$FIG/cd_stack_loop.pdf" "$OUT/"

docker run --rm \
  --user "$(id -u):$(id -g)" \
  --volume "$OUT:/work" \
  --workdir /work \
  --env "SOURCE_DATE_EPOCH=$EPOCH" \
  --env FORCE_SOURCE_DATE=1 \
  --env HOME=/tmp \
  --env TEXMFVAR=/tmp/texmf-var \
  --env TEXMFCONFIG=/tmp/texmf-config \
  "$IMAGE" \
  latexmk -pdf -interaction=nonstopmode -halt-on-error creative_determinant.tex

echo "built $OUT/creative_determinant.pdf"
