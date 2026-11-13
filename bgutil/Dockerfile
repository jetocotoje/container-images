# syntax=docker/dockerfile:1@sha256:4edf897a3ffa55b89f906fc8cc78afdb3f1834cc9c7083565e611a8a7d5fe99e

ARG BGUTIL_VERSION=2.0.2@sha256:d7d34108b76e52c7d3b575fe9e797e4bf41c1b2a08f80c5292eff6f851ce8472

FROM brainicism/bgutil-ytdlp-pot-provider:${BGUTIL_VERSION} AS upstream

FROM node:26.13.1-bookworm-slim@sha256:5df79989ed685e09f0a98019db4cebfb22fb9df1a53c0161664a011f7ff6b0f1

WORKDIR /app
COPY --from=upstream /app/ /app/
COPY test-runtime.cjs /tmp/test-runtime.cjs

RUN node /tmp/test-runtime.cjs && rm /tmp/test-runtime.cjs

USER node

EXPOSE 4416

HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=3 \
    CMD ["node", "-e", "fetch('http://127.0.0.1:4416/ping', {signal: AbortSignal.timeout(4000)}).then(r => { if (!r.ok) process.exit(1); }).catch(() => process.exit(1))"]

ENTRYPOINT ["/usr/local/bin/node", "build/main.js"]
CMD ["--host", "0.0.0.0"]
