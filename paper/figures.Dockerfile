# The environment in which paper/build_figures.sh renders the stack diagram (paper/stack_figures.py).
#
# Graphviz sizes every node from the metrics of the fonts it finds and cairo embeds those fonts, so
# the four outputs are byte-reproducible only with fixed Graphviz, cairo, pango and font files. The
# base image is pinned by digest, every package comes from the Debian snapshot of the image's date,
# and the two brand fonts come from a fixed google/fonts commit, checked by SHA-256. A change here
# changes the rendered outputs: run `make -C paper` and rebuild the paper in the same commit.
FROM debian:forky-20260918-slim@sha256:7bb96d9b4ccd7f46f54853c258a56df0c6b628a63e65c2317959da18fd36932c

RUN printf 'Types: deb\nURIs: http://snapshot.debian.org/archive/debian/20260918T000000Z\nSuites: forky\nComponents: main\nSigned-By: /usr/share/keyrings/debian-archive-keyring.pgp\n' \
        > /etc/apt/sources.list.d/debian.sources \
    && apt-get -o Acquire::Check-Valid-Until=false update \
    && apt-get install -y --no-install-recommends graphviz python3 fonts-dejavu-core fonts-noto-core \
    && rm -rf /var/lib/apt/lists/*

# DM Sans (node and edge text) and Fraunces (cluster titles), SIL Open Font License 1.1. Noto Sans
# and DejaVu Sans above supply the Greek and mathematical glyphs these fonts lack.
ADD --chmod=644 --checksum=sha256:8cd08d97e89c24d0aa92edd2f0f4c8ee6195eee9b7c9f154865a58b02f0c1c0d \
    https://raw.githubusercontent.com/google/fonts/9710da1eacb3be272583c3224dcb70f9da6eadbb/ofl/dmsans/DMSans%5Bopsz,wght%5D.ttf \
    /usr/local/share/fonts/DMSans.ttf
ADD --chmod=644 --checksum=sha256:177ff6c0f14e5550a3c624247cd1189611d4eb65d000b14944c63d967958abbb \
    https://raw.githubusercontent.com/google/fonts/9710da1eacb3be272583c3224dcb70f9da6eadbb/ofl/fraunces/Fraunces%5BSOFT,WONK,opsz,wght%5D.ttf \
    /usr/local/share/fonts/Fraunces.ttf
RUN fc-cache -f
