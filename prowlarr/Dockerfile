# syntax=docker/dockerfile:1@sha256:572cebbc2b15e6f84c077742952674889cb63cd5e9b80abdffcbe587b6f19183

ARG PROWLARR_VERSION=3.1.0.5799@sha256:15b68a6e69f893a3ede6fed405594d3f5d9e9d13648246a0fefbafe4fd7f595b

FROM ghcr.io/home-operations/prowlarr:${PROWLARR_VERSION}

USER root

RUN apk upgrade --no-cache

USER nobody:nogroup

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD ["curl", "--fail", "--silent", "--output", "/dev/null", "http://127.0.0.1:9696/ping"]
