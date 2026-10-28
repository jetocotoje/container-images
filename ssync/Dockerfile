# syntax=docker/dockerfile:1@sha256:4edf897a3ffa55b89f906fc8cc78afdb3f1834cc9c7083565e611a8a7d5fe99e

ARG RUST_BASE=docker.io/library/rust:1.99.1-slim-trixie@sha256:45afd9478205dcdf7f98b099019fee773a33644cf69ac0a3b862eb31d2a1ccef
ARG GO_BASE=docker.io/library/golang:1.27.3-trixie@sha256:7b072c590a326b9d2a43b165ae247f6e8eafff32e1ad154ab97139e89f053be9
ARG DEBIAN_BASE=docker.io/library/debian:trixie-slim@sha256:89c1ea91e897f0fe0a3731595330bc45b8bdef4047464a07116f891a94054b31

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
