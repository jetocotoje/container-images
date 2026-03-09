# renovate: datasource=github-releases depName=opencloud-eu/opencloud
ARG OPENCLOUD_VERSION=5.2.0
ARG TARGETARCH

FROM --platform=linux/${TARGETARCH} opencloudeu/opencloud-rolling:${OPENCLOUD_VERSION}

ARG UID=10001
ARG GID=10001
ARG EXTENSIONS_DIR=/var/lib/opencloud/web-extensions

USER root

RUN addgroup -S -g $GID opencloud \
     && adduser -S -H --home /var/lib/opencloud --shell /bin/bash -u $UID -G opencloud opencloud \
     && chown -R $UID:$GID /var/lib/opencloud \
     && chown -R $UID:$GID /etc/opencloud \
     && mkdir /etc/opencloud-configs \
     && chown -R $UID:$GID /etc/opencloud-configs

USER opencloud

COPY --chmod=500 --chown=opencloud load-extensions.sh entrypoint.sh /var/lib/scripts/

# renovate: datasource=github-tags depName=opencloud-eu/web-extensions extractVersion="^unzip-v(?<version>\d+\.\d+\.\d+)$"
ARG UNZIP_VERSION=1.0.4
# renovate: datasource=github-tags depName=opencloud-eu/web-extensions extractVersion="^arcade-v(?<version>\d+\.\d+\.\d+)$"
ARG ARCADE_VERSION=1.0.0
# renovate: datasource=github-tags depName=opencloud-eu/web-extensions extractVersion="^maps-v(?<version>\d+\.\d+\.\d+)$"
ARG MAPS_VERSION=1.0.2
# renovate: datasource=github-tags depName=opencloud-eu/web-extensions extractVersion="^progress-bars-v(?<version>\d+\.\d+\.\d+)$"
ARG PROGRESS_BARS_VERSION=1.1.0
# renovate: datasource=github-tags depName=opencloud-eu/web-extensions extractVersion="^json-viewer-v(?<version>\d+\.\d+\.\d+)$"
ARG JSON_VIEWER_VERSION=1.0.2
# renovate: datasource=github-tags depName=opencloud-eu/web-extensions extractVersion="^external-sites-v(?<version>\d+\.\d+\.\d+)$"
ARG EXTERNAL_SITES_VERSION=1.3.0
# renovate: datasource=github-tags depName=opencloud-eu/web-extensions extractVersion="^draw-io-v(?<version>\d+\.\d+\.\d+)$"
ARG DRAWIO_VERSION=1.0.1

ENV OC_EXTENSION_UNZIP=https://github.com/opencloud-eu/web-extensions/releases/download/unzip-v${UNZIP_VERSION}/unzip-${UNZIP_VERSION}.zip \
    OC_EXTENSION_PROGRESS_BARS=https://github.com/opencloud-eu/web-extensions/releases/download/progress-bars-v${PROGRESS_BARS_VERSION}/progress-bars-${PROGRESS_BARS_VERSION}.zip \
    OC_EXTENSION_JSON_VIEWER=https://github.com/opencloud-eu/web-extensions/releases/download/json-viewer-v${JSON_VIEWER_VERSION}/json-viewer-${JSON_VIEWER_VERSION}.zip \
    OC_EXTENSION_ARCADE=https://github.com/opencloud-eu/web-extensions/releases/download/arcade-v${ARCADE_VERSION}/arcade-${ARCADE_VERSION}.zip \
    OC_EXTENSION_MAPS=https://github.com/opencloud-eu/web-extensions/releases/download/maps-v${MAPS_VERSION}/maps-${MAPS_VERSION}.zip \
    OC_EXTENSION_EXTERNAL_SITES=https://github.com/opencloud-eu/web-extensions/releases/download/external-sites-v${EXTERNAL_SITES_VERSION}/external-sites-${EXTERNAL_SITES_VERSION}.zip \
    OC_EXTENSION_DRAWIO=https://github.com/opencloud-eu/web-extensions/releases/download/draw-io-v${DRAWIO_VERSION}/draw-io-${DRAWIO_VERSION}.zip

RUN /var/lib/scripts/load-extensions.sh "$EXTENSIONS_DIR"

VOLUME [ "/var/lib/opencloud", "/etc/opencloud-configs" ]
ENTRYPOINT [ "/bin/sh" ]
CMD [ "/var/lib/scripts/entrypoint.sh" ]
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD bash -c ' \
    exec 3<>/dev/tcp/127.0.0.1/9200 || exit 1 \
    printf "GET /health HTTP/1.0\r\nHost: localhost\r\n\r\n" >&3 \
    IFS= read -r status <&3 || exit 1 \
    echo "$status" | grep -q " 200 " || exit 1 \
  '

VOLUME ["/config", "/cache"]
