# syntax=docker/dockerfile:1@sha256:ecfaec9ed6d810b56388c508f4121597bfbba70d41a6dfeee4d8cad5f295fc32

ARG JELLYFIN_VERSION=12.0@sha256:74f4d87d9cf262c52d62be6be265c0355c6a7e21d0477ab6c654a49a4f8b1fd4

FROM ghcr.io/jellyfin/jellyfin:${JELLYFIN_VERSION}

ARG UID=10001
ARG GID=10001

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get purge --yes gnupg gnupg2 gnupg-agent gpg gpg-agent dirmngr curl \
    && apt-get autoremove --yes \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -g $GID jellyfin \
    && useradd --create-home --home-dir /config --shell /usr/sbin/nologin -u $UID -g $GID -G video jellyfin \
    && mkdir -p /cache \
    && chown $UID:$GID /cache

WORKDIR /jellyfin

ENV JELLYFIN_DATA_DIR=/config \
    JELLYFIN_CACHE_DIR=/cache

# Exec form, one line: Dockerfile line continuations collapse a shell-form
# command into a single || chain that never sends the request.
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD ["/bin/bash", "-c", "exec 3<>/dev/tcp/127.0.0.1/8096 || exit 1; printf 'GET /health HTTP/1.0\\r\\nHost: localhost\\r\\n\\r\\n' >&3; IFS= read -r status <&3 || exit 1; [[ \"$status\" == *' 200 '* ]] || exit 1"]

USER jellyfin

VOLUME ["/config", "/cache"]
