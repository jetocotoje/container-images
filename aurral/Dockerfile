# syntax=docker/dockerfile:1@sha256:4edf897a3ffa55b89f906fc8cc78afdb3f1834cc9c7083565e611a8a7d5fe99e

ARG AURRAL_VERSION=2.13.0@sha256:75dd06805e3daefd49eb4f91d19f4110f0ef6eb1d2b13e48ae36120d113b48f0

FROM ghcr.io/lklynet/aurral:${AURRAL_VERSION}

ARG BGUTIL_PLUGIN_VERSION=2.0.2

ADD --chmod=644 --checksum=sha256:a26b980bf6d8e8400d8f21445daa4d8381bf6183d20f0be309391f86b31e27ef \
    https://github.com/Brainicism/bgutil-ytdlp-pot-provider/releases/download/${BGUTIL_PLUGIN_VERSION}/bgutil-ytdlp-pot-provider.zip \
    /etc/yt-dlp/plugins/bgutil-ytdlp-pot-provider.zip

COPY test-plugin.py /tmp/test-plugin.py
RUN chmod 755 /etc/yt-dlp /etc/yt-dlp/plugins \
    && gosu 10001:10001 python3 -B /tmp/test-plugin.py "${BGUTIL_PLUGIN_VERSION}" \
    && rm /tmp/test-plugin.py

HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=3 \
    CMD ["node", "-e", "fetch('http://127.0.0.1:3001/api/health/live', {signal: AbortSignal.timeout(4000)}).then(r => { if (!r.ok) process.exit(1); }).catch(() => process.exit(1))"]
