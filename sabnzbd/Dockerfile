# syntax=docker/dockerfile:1@sha256:4edf897a3ffa55b89f906fc8cc78afdb3f1834cc9c7083565e611a8a7d5fe99e

ARG SABNZBD_VERSION=5.1.3@sha256:c89b0322721c3eba47221e5f916505e7e742684651f73c5215717340b6b5402f

FROM ghcr.io/home-operations/sabnzbd:${SABNZBD_VERSION}

USER root

COPY requirements.txt test-certifi.py /tmp/

RUN python -m pip install \
        --no-cache-dir \
        --no-deps \
        --disable-pip-version-check \
        --require-hashes \
        -r /tmp/requirements.txt \
    && python /tmp/test-certifi.py \
    && rm /tmp/requirements.txt /tmp/test-certifi.py

USER nobody:nogroup

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/', timeout=4).close()"]
