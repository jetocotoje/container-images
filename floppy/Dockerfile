# syntax=docker/dockerfile:1@sha256:4edf897a3ffa55b89f906fc8cc78afdb3f1834cc9c7083565e611a8a7d5fe99e

ARG FLOPPY_VERSION=26.10.8@sha256:b90eb406e0b19725f9bef1bb6356f2492afc2991e8ba7dd6cd413b7514d60a4d

FROM ghcr.io/dannyvfilms/floppy:${FLOPPY_VERSION}

ARG UID=10001
ARG GID=10001

COPY patch-rootless.py /tmp/patch-rootless.py

RUN python /tmp/patch-rootless.py \
    && rm /tmp/patch-rootless.py \
    && groupmod -g "$GID" abc \
    && usermod -u "$UID" -g "$GID" abc \
    && touch /etc/nginx/nginx.ipv6.conf \
    && chown "$UID:$GID" /etc/nginx/nginx.conf /etc/nginx/nginx.ipv6.conf \
    && install -d -o "$UID" -g "$GID" /run/floppy /floppy/db /floppy/logs /floppy/backups \
    && chown "$UID:$GID" /floppy \
    && chown -R "$UID:$GID" /floppy/logs /floppy/staticfiles /var/lib/nginx /var/log/nginx

ENV PUID=$UID \
    PGID=$GID

USER $UID:$GID
