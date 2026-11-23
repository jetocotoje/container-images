# syntax=docker/dockerfile:1@sha256:572cebbc2b15e6f84c077742952674889cb63cd5e9b80abdffcbe587b6f19183

ARG FLOPPY_VERSION=26.11.19@sha256:1eb6cfc2b79a53a892cd6bf39e67ab4e11731a25aaac1666b1cbac802c447fa3

FROM ghcr.io/dannyvfilms/floppy:${FLOPPY_VERSION}

ARG UID=10001
ARG GID=10001

COPY patch-rootless.py /tmp/patch-rootless.py

RUN apk upgrade --no-cache ca-certificates ca-certificates-bundle \
    && python /tmp/patch-rootless.py \
    && rm /tmp/patch-rootless.py \
    && groupmod -g "$GID" abc \
    && usermod -u "$UID" -g "$GID" abc \
    && touch /etc/nginx/nginx.ipv6.conf \
    && chown "$UID:$GID" /etc/nginx/nginx.conf /etc/nginx/nginx.ipv6.conf \
    && install -d -o "$UID" -g "$GID" /run/floppy /floppy/db /floppy/logs /floppy/backups \
    && chown "$UID:$GID" /floppy \
    && chown -R "$UID:$GID" /floppy/logs /floppy/staticfiles /var/lib/nginx /var/log/nginx

RUN ln -sf /dev/null /floppy/logs/floppy.log \
    && ln -sf /dev/null /floppy/logs/supervisord.log

ENV PUID=$UID \
    PGID=$GID \
    LOG_DIR=/floppy/logs

USER $UID:$GID

HEALTHCHECK --interval=30s --timeout=5s --start-period=600s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider "http://127.0.0.1:${FLOPPY_PORT:-8000}/health/"
