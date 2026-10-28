# syntax=docker/dockerfile:1@sha256:4edf897a3ffa55b89f906fc8cc78afdb3f1834cc9c7083565e611a8a7d5fe99e

ARG FLOPPY_VERSION=26.10.22@sha256:c4959b1f2544f3cc6f8f305118ba4cd80360bf33f4e9562d66de7a4404b69b50

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
