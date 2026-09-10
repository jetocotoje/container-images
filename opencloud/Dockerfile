# syntax=docker/dockerfile:1@sha256:ecfaec9ed6d810b56388c508f4121597bfbba70d41a6dfeee4d8cad5f295fc32

ARG OPENCLOUD_VERSION=7.5.0@sha256:6db1cfb06d430a663f16e9f33dcd4596d82a4875be0b4df233c26ce5f667ea74

FROM opencloudeu/opencloud-rolling:${OPENCLOUD_VERSION}

ARG UID=10001
ARG GID=10001

USER root

RUN addgroup -S -g $GID opencloud \
     && adduser -S -H --home /var/lib/opencloud --shell /sbin/nologin -u $UID -G opencloud opencloud \
     && chown -R $UID:$GID /var/lib/opencloud \
     && chown -R $UID:$GID /etc/opencloud \
     && install -d -o $UID -g $GID /etc/opencloud-configs /opt/web-extensions

USER opencloud

COPY --chmod=500 --chown=opencloud load-extensions.sh entrypoint.sh /var/lib/scripts/

# renovate: datasource=github-tags depName=opencloud-eu/web-extensions extractVersion="^unzip-v(?<version>\d+\.\d+\.\d+)$"
ARG UNZIP_VERSION=2.1.0
# renovate: datasource=github-tags depName=opencloud-eu/web-extensions extractVersion="^arcade-v(?<version>\d+\.\d+\.\d+)$"
ARG ARCADE_VERSION=3.0.0
# renovate: datasource=github-tags depName=opencloud-eu/web-extensions extractVersion="^maps-v(?<version>\d+\.\d+\.\d+)$"
ARG MAPS_VERSION=3.1.0
# renovate: datasource=github-tags depName=opencloud-eu/web-extensions extractVersion="^progress-bars-v(?<version>\d+\.\d+\.\d+)$"
ARG PROGRESS_BARS_VERSION=2.1.0
# renovate: datasource=github-tags depName=opencloud-eu/web-extensions extractVersion="^json-viewer-v(?<version>\d+\.\d+\.\d+)$"
ARG JSON_VIEWER_VERSION=2.1.0
# renovate: datasource=github-tags depName=opencloud-eu/web-extensions extractVersion="^external-sites-v(?<version>\d+\.\d+\.\d+)$"
ARG EXTERNAL_SITES_VERSION=2.1.0
# renovate: datasource=github-tags depName=opencloud-eu/web-extensions extractVersion="^draw-io-v(?<version>\d+\.\d+\.\d+)$"
ARG DRAWIO_VERSION=2.2.0

ENV OC_EXTENSION_UNZIP=https://github.com/opencloud-eu/web-extensions/releases/download/unzip-v${UNZIP_VERSION}/unzip-${UNZIP_VERSION}.zip \
    OC_EXTENSION_PROGRESS_BARS=https://github.com/opencloud-eu/web-extensions/releases/download/progress-bars-v${PROGRESS_BARS_VERSION}/progress-bars-${PROGRESS_BARS_VERSION}.zip \
    OC_EXTENSION_JSON_VIEWER=https://github.com/opencloud-eu/web-extensions/releases/download/json-viewer-v${JSON_VIEWER_VERSION}/json-viewer-${JSON_VIEWER_VERSION}.zip \
    OC_EXTENSION_ARCADE=https://github.com/opencloud-eu/web-extensions/releases/download/arcade-v${ARCADE_VERSION}/arcade-${ARCADE_VERSION}.zip \
    OC_EXTENSION_MAPS=https://github.com/opencloud-eu/web-extensions/releases/download/maps-v${MAPS_VERSION}/maps-${MAPS_VERSION}.zip \
    OC_EXTENSION_EXTERNAL_SITES=https://github.com/opencloud-eu/web-extensions/releases/download/external-sites-v${EXTERNAL_SITES_VERSION}/external-sites-${EXTERNAL_SITES_VERSION}.zip \
    OC_EXTENSION_DRAWIO=https://github.com/opencloud-eu/web-extensions/releases/download/draw-io-v${DRAWIO_VERSION}/draw-io-${DRAWIO_VERSION}.zip

# Bake extensions outside the data volume; the entrypoint syncs them into
# /var/lib/opencloud/web-extensions on every start (PVC mounts shadow images).
RUN /var/lib/scripts/load-extensions.sh /opt/web-extensions

VOLUME [ "/var/lib/opencloud", "/etc/opencloud-configs" ]
ENTRYPOINT [ "/var/lib/scripts/entrypoint.sh" ]
# 9200 serves TLS with a self-signed cert (opencloud init --insecure=false),
# so probe via curl; exec form keeps the command a single literal.
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD ["/usr/bin/curl", "--silent", "--fail", "--insecure", "--output", "/dev/null", "https://127.0.0.1:9200/health"]
