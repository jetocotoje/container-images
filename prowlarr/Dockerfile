# syntax=docker/dockerfile:1@sha256:4edf897a3ffa55b89f906fc8cc78afdb3f1834cc9c7083565e611a8a7d5fe99e

ARG PROWLARR_VERSION=3.0.2.5780@sha256:58fa5dbed20738ce0a72077315e818eeb731cb4b4a5173c4a837d343a9573750

FROM ghcr.io/home-operations/prowlarr:${PROWLARR_VERSION}

USER root

RUN apk upgrade --no-cache

USER nobody:nogroup

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD ["curl", "--fail", "--silent", "--output", "/dev/null", "http://127.0.0.1:9696/ping"]
