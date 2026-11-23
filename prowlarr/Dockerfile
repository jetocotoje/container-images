# syntax=docker/dockerfile:1@sha256:572cebbc2b15e6f84c077742952674889cb63cd5e9b80abdffcbe587b6f19183

ARG PROWLARR_VERSION=3.0.2.5780@sha256:58fa5dbed20738ce0a72077315e818eeb731cb4b4a5173c4a837d343a9573750

FROM ghcr.io/home-operations/prowlarr:${PROWLARR_VERSION}

USER root

RUN apk upgrade --no-cache

USER nobody:nogroup

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD ["curl", "--fail", "--silent", "--output", "/dev/null", "http://127.0.0.1:9696/ping"]
