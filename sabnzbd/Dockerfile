# syntax=docker/dockerfile:1@sha256:572cebbc2b15e6f84c077742952674889cb63cd5e9b80abdffcbe587b6f19183

ARG SABNZBD_VERSION=5.1.3@sha256:07790a7829201d9ea302e8b862078beac4b1a07003fe8359e3f069b6bcd84a95

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
