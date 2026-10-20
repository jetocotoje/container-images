# syntax=docker/dockerfile:1@sha256:4edf897a3ffa55b89f906fc8cc78afdb3f1834cc9c7083565e611a8a7d5fe99e

ARG RUST_BASE=docker.io/library/rust:1.99.1-slim-trixie@sha256:4df2ae8cfdfebdfc13a65da7f253b73d68983dc0339f2719bc17a279c913b13d
ARG GO_BASE=docker.io/library/golang:1.27.3-trixie@sha256:1896654cfc5c2b5ad74c07f29cb36f5d2d1cbed42e3054070fbfe444e521e83c
ARG DEBIAN_BASE=docker.io/library/debian:trixie-slim@sha256:a29215f6a35e51e22adffa17f89e9d2ef06214e64a2bad10d765c46aea49f11f

FROM ${RUST_BASE} AS ssync

# renovate: datasource=github-tags depName=fosskar/ssync extractVersion=^v(?<version>.+)$
ARG SSYNC_VERSION=0.20.2

RUN cargo install --locked --root /out \
        --git https://github.com/fosskar/ssync --tag "v${SSYNC_VERSION}" ssync

FROM ${GO_BASE} AS age

# renovate: datasource=github-tags depName=FiloSottile/age extractVersion=^v(?<version>.+)$
ARG AGE_VERSION=1.3.2

RUN CGO_ENABLED=0 GOBIN=/out/bin go install -trimpath -ldflags="-s -w" "filippo.io/age/cmd/...@v${AGE_VERSION}"

FROM ${DEBIAN_BASE}

ARG UID=10001
ARG GID=10001

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
        ca-certificates \
        catatonit \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid "$GID" ssync \
    && useradd --uid "$UID" --gid "$GID" --home-dir /var/lib/ssync --no-create-home --shell /usr/sbin/nologin ssync \
    && install -d -o "$UID" -g "$GID" -m 0700 /var/lib/ssync

COPY --from=ssync /out/bin/ssync /usr/local/bin/ssync
COPY --from=age /out/bin/age /out/bin/age-keygen /usr/local/bin/

ENV HOME=/var/lib/ssync \
    MALLOC_ARENA_MAX=2

USER $UID:$GID

ENTRYPOINT ["/usr/bin/catatonit", "--", "/usr/local/bin/ssync"]
CMD ["daemon"]
