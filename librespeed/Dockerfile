# syntax=docker/dockerfile:1@sha256:ecfaec9ed6d810b56388c508f4121597bfbba70d41a6dfeee4d8cad5f295fc32

# Release tag and the commit it points to; Renovate updates both together.
ARG LIBRESPEED_VERSION=v6.2.1
ARG LIBRESPEED_COMMIT=ca1e033d8d8c63214563ea344663e70dd39f0d7a

FROM --platform=$BUILDPLATFORM docker.io/library/php:8.5-apache-bookworm@sha256:68e1de9a82af09f1b0ae70611bd64a8702069ac1e036bdc5a12eb48e1a5cab2b AS fetch

ARG LIBRESPEED_VERSION
ARG LIBRESPEED_COMMIT

WORKDIR /src

RUN curl --fail --show-error --silent --location --retry 5 --retry-delay 2 --retry-all-errors \
        "https://github.com/librespeed/speedtest/archive/${LIBRESPEED_COMMIT}.tar.gz" \
        -o /tmp/librespeed.tar.gz \
    && tar --extract --gzip --file /tmp/librespeed.tar.gz --strip-components=1 \
    && rm /tmp/librespeed.tar.gz \
    && rm -rf .eslintrc.json .github .gitignore .logo .prettierignore .prettierrc.json \
        DESIGN_SWITCH.md DEVELOPMENT.md Dockerfile Dockerfile.alpine LICENSE README.md \
        doc.md doc_docker.md docker examples package.json package-lock.json tests \
        results/*.sql

FROM docker.io/library/php:8.5-apache-bookworm@sha256:68e1de9a82af09f1b0ae70611bd64a8702069ac1e036bdc5a12eb48e1a5cab2b

ARG UID=10001
ARG GID=10001

# libc6-dev is the real package behind the virtual libc-dev in the base image's PHPIZE_DEPS.
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends libfreetype6-dev libjpeg62-turbo-dev libpng-dev libpq-dev \
    && docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install gd mysqli pdo_mysql pgsql pdo_pgsql \
    && apt-mark manual libfreetype6 libjpeg62-turbo libpng16-16 libpq5 \
    && apt-get purge --yes --auto-remove \
        libfreetype6-dev libjpeg62-turbo-dev libpng-dev libpq-dev \
        autoconf dpkg-dev file g++ gcc libc6-dev make pkg-config re2c \
    && rm -rf /var/lib/apt/lists/* /usr/src/php.tar.xz /usr/src/php.tar.xz.asc /usr/src/php \
    && groupadd --gid "$GID" librespeed \
    && useradd --uid "$UID" --gid "$GID" --home-dir /tmp --shell /usr/sbin/nologin librespeed \
    && mkdir -p /opt/librespeed /database \
    && chown librespeed:librespeed /database

COPY --from=fetch /src/ /opt/librespeed/
COPY --chmod=755 docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

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
