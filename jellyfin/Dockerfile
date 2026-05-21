# renovate: datasource=github-releases depName=jellyfin/jellyfin
ARG JELLYFIN_VERSION=10.11.9@sha256:ef4d95143a5475d1ba4d9a6983342cac300044d676a30648b7d0e0688961712a
ARG TARGETARCH

FROM --platform=linux/${TARGETARCH} ghcr.io/jellyfin/jellyfin:${JELLYFIN_VERSION}

ARG UID=10001
ARG GID=10001

RUN apt-get update \
    && apt-get purge --yes gnupg gnupg2 gnupg-agent gpg gpg-agent dirmngr curl \
    && apt-get autoremove --yes \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -g $GID jellyfin && \
    useradd --create-home --home-dir /config --shell /bin/bash -u $UID -g $GID -G video jellyfin && \
    mkdir -p /cache && \
    chown $UID:$GID /cache

WORKDIR /jellyfin

ENV JELLYFIN_DATA_DIR=/config \
    JELLYFIN_CACHE_DIR=/cache

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD bash -c ' \
    exec 3<>/dev/tcp/127.0.0.1/8096 || exit 1 \
    printf "GET /health HTTP/1.0\r\nHost: localhost\r\n\r\n" >&3 \
    IFS= read -r status <&3 || exit 1 \
    echo "$status" | grep -q " 200 " || exit 1 \
  '

USER jellyfin

VOLUME ["/config", "/cache"]