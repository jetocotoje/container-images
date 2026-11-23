# syntax=docker/dockerfile:1@sha256:572cebbc2b15e6f84c077742952674889cb63cd5e9b80abdffcbe587b6f19183

ARG BAZARR_VERSION=1.6.2@sha256:6c40dfa683f767d28d1dc502837ed0a5a57682a84231f03e704e2b3f61b25a46

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
