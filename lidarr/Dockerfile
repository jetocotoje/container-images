# syntax=docker/dockerfile:1

ARG DEBIAN_BASE=docker.io/library/debian:trixie-slim@sha256:26f98ccd92fd0a44d6928ce8ff8f4921b4d2f535bfa07555ee5d18f61429cf0c

FROM --platform=$BUILDPLATFORM ${DEBIAN_BASE} AS fetch

# renovate: datasource=custom.servarr-nightly depName=lidarr versioning=loose
ARG LIDARR_VERSION=3.1.2.4928
ARG LIDARR_BRANCH=nightly
ARG TARGETARCH

WORKDIR /work

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        jq \
    && rm -rf /var/lib/apt/lists/*

RUN case "${TARGETARCH}" in \
        amd64) lidarr_arch='x64' ;; \
        arm64) lidarr_arch='arm64' ;; \
        *) echo "Unsupported TARGETARCH: ${TARGETARCH}" >&2; exit 1 ;; \
    esac \
    && release_json="$(curl --fail --show-error --silent --location --retry 5 --retry-delay 2 --retry-all-errors "https://lidarr.servarr.com/v1/update/${LIDARR_BRANCH}/changes?os=linux&runtime=netcore&arch=${lidarr_arch}")" \
    && package_url="$(printf '%s' "${release_json}" | jq -er --arg version "${LIDARR_VERSION}" 'first(.[] | select(.version == $version)) | .url')" \
    && package_hash="$(printf '%s' "${release_json}" | jq -er --arg version "${LIDARR_VERSION}" 'first(.[] | select(.version == $version)) | .hash')" \
    && mkdir -p /out/bin \
    && curl --fail --show-error --silent --location --retry 5 --retry-delay 2 --retry-all-errors "${package_url}" -o /tmp/lidarr.tar.gz \
    && printf '%s  %s\n' "${package_hash}" "/tmp/lidarr.tar.gz" | sha256sum -c - \
    && tar xzf /tmp/lidarr.tar.gz -C /out/bin --strip-components=1 \
    && rm -rf /out/bin/Lidarr.Update /out/bin/fpcalc /tmp/lidarr.tar.gz \
    && printf "UpdateMethod=docker\nBranch=%s\nPackageVersion=%s\n" "${LIDARR_BRANCH}" "${LIDARR_VERSION}" > /out/package_info

FROM ${DEBIAN_BASE}

ENV DOTNET_EnableDiagnostics=0 \
    HOME=/config

WORKDIR /app

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates \
        catatonit \
        ffmpeg \
        libchromaprint-tools \
        libcurl4t64 \
        libgcc-s1 \
        libicu76 \
        libsqlite3-0 \
        libssl3t64 \
        libstdc++6 \
        tzdata \
        zlib1g \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 lidarr \
    && useradd --uid 10001 --gid 10001 --home-dir /config --no-create-home --shell /usr/sbin/nologin lidarr \
    && install -d -o 10001 -g 10001 /config /config/tmp

ENV TMPDIR=/config/tmp

COPY --from=fetch /out/bin/ /app/bin/
COPY --from=fetch /out/package_info /app/package_info
COPY --chmod=755 entrypoint.sh /entrypoint.sh

USER 10001:10001
WORKDIR /config
VOLUME ["/config"]

ENTRYPOINT ["/usr/bin/catatonit", "--", "/entrypoint.sh"]
