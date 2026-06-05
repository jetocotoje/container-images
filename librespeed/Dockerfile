# renovate: datasource=github-tags depName=librespeed/speedtest
ARG LIBRESPEED_VERSION=v6.1.0
ARG LIBRESPEED_SHA256=2032765ade84a36d0c0a896617002fd0afa90aaccb56255af05dd4b97f7555fb

FROM docker.io/library/debian:trixie-slim@sha256:b6e2a152f22a40ff69d92cb397223c906017e1391a73c952b588e51af8883bf8 AS source

ARG LIBRESPEED_VERSION
ARG LIBRESPEED_SHA256

RUN apt-get update \
    && apt-get install --yes --no-install-recommends ca-certificates curl tar \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src

RUN curl --fail --location --show-error \
      "https://github.com/librespeed/speedtest/archive/refs/tags/${LIBRESPEED_VERSION}.tar.gz" \
      --output /tmp/librespeed.tar.gz \
    && echo "${LIBRESPEED_SHA256}  /tmp/librespeed.tar.gz" | sha256sum --check \
    && tar --extract --gzip --strip-components=1 --file /tmp/librespeed.tar.gz \
    && rm /tmp/librespeed.tar.gz

FROM docker.io/library/php:8.5-apache-bookworm@sha256:d992958f00ee1af14d47870ae8e0328a9f721b2a577236d09b640ac3e694993c

ARG UID=10001
ARG GID=10001

RUN apt-get update \
    && apt-get install --yes --no-install-recommends libfreetype6-dev libjpeg62-turbo-dev libpng-dev libpq-dev \
    && docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install gd mysqli pdo_mysql pgsql pdo_pgsql \
    && apt-mark manual libfreetype6 libjpeg62-turbo libpng16-16 libpq5 \
    && apt-get purge --yes --auto-remove libfreetype6-dev libjpeg62-turbo-dev libpng-dev libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid "$GID" librespeed \
    && useradd --uid "$UID" --gid "$GID" --home-dir /tmp --shell /usr/sbin/nologin librespeed \
    && mkdir -p /opt/librespeed /database \
    && chown librespeed:librespeed /database

COPY --from=source /src/ /opt/librespeed/
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

RUN chmod 755 /usr/local/bin/docker-entrypoint.sh

ENV HOME=/tmp \
    MODE=standalone \
    WEBPORT=8080 \
    TITLE=LibreSpeed \
    TAGLINE="No Flash, No Java, No Websockets, No Bullsh*t" \
    TELEMETRY=false \
    ENABLE_ID_OBFUSCATION=false \
    REDACT_IP_ADDRESSES=false \
    USE_NEW_DESIGN=false

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD ["/bin/bash", "-c", "case \"${MODE:-standalone}\" in backend) path=/empty.php ;; frontend) path=/ ;; *) path=/backend/empty.php ;; esac; exec 3<>/dev/tcp/127.0.0.1/${WEBPORT:-8080} || exit 1; printf 'GET %s HTTP/1.0\\r\\nHost: localhost\\r\\n\\r\\n' \"$path\" >&3; IFS= read -r status <&3 || exit 1; [[ \"$status\" == *' 200 '* ]] || exit 1"]

STOPSIGNAL SIGWINCH

USER librespeed:librespeed

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
