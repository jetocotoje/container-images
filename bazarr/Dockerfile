# syntax=docker/dockerfile:1@sha256:4edf897a3ffa55b89f906fc8cc78afdb3f1834cc9c7083565e611a8a7d5fe99e

ARG BAZARR_VERSION=1.6.2@sha256:b8434a7339ebd9c2bfe4464c28db79944e0f52f47da85345fc7e0563c19f83ac

FROM ghcr.io/home-operations/bazarr:${BAZARR_VERSION}

USER root

COPY requirements.txt test-certifi.py /tmp/

RUN PYTHONPATH=/app/bin/libs python -m pip --disable-pip-version-check uninstall --yes certifi \
    && python -m pip install \
        --no-cache-dir \
        --no-deps \
        --disable-pip-version-check \
        --require-hashes \
        --upgrade \
        --target /app/bin/libs \
        -r /tmp/requirements.txt \
    && python /tmp/test-certifi.py \
    && rm /tmp/requirements.txt /tmp/test-certifi.py

USER nobody:nogroup

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:6767/', timeout=4).close()"]
