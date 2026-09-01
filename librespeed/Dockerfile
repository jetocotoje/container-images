ARG LIBRESPEED_VERSION=6.2.1

FROM ghcr.io/librespeed/speedtest:${LIBRESPEED_VERSION}@sha256:705744f487048f209b4e389312ea82d4d5c36a76db3e5123b97d4b1649b724b5 AS source

FROM docker.io/library/php:8.5-apache-bookworm@sha256:68e1de9a82af09f1b0ae70611bd64a8702069ac1e036bdc5a12eb48e1a5cab2b

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

COPY --from=source /speedtest/ /opt/librespeed/
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
