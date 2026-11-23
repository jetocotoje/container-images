# syntax=docker/dockerfile:1@sha256:572cebbc2b15e6f84c077742952674889cb63cd5e9b80abdffcbe587b6f19183

ARG RUST_BASE=docker.io/library/rust:1.100.0-slim-trixie@sha256:6f14b2b4b278ec0d50aa1d69541c304ce0f95e0f6268487aa9924af1c2e9aebe
ARG GO_BASE=docker.io/library/golang:1.27.4-trixie@sha256:f18c3d73a184fb0582828510722e723b63a93f7188d11dd223d9be6f6880e65d
ARG DEBIAN_BASE=docker.io/library/debian:trixie-slim@sha256:a72b4433de1cf7d6bae0c4cee74d0547f58601a643b3375f070c51600d63b6b2

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
    && DEBIAN_FRONTEND=noninteractive apt-get upgrade --yes \
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
