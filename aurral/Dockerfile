# syntax=docker/dockerfile:1@sha256:572cebbc2b15e6f84c077742952674889cb63cd5e9b80abdffcbe587b6f19183

ARG AURRAL_VERSION=3.0.1@sha256:dfca50e61cfdea54506c9836431a3c6b526873e0650f4a348a4a032a1324b7dc

FROM ghcr.io/lklynet/aurral:${AURRAL_VERSION}

# renovate: datasource=github-releases depName=Brainicism/bgutil-ytdlp-pot-provider
ARG BGUTIL_PLUGIN_VERSION=2.0.2

ADD --chmod=644 --checksum=sha256:a26b980bf6d8e8400d8f21445daa4d8381bf6183d20f0be309391f86b31e27ef \
    https://github.com/Brainicism/bgutil-ytdlp-pot-provider/releases/download/${BGUTIL_PLUGIN_VERSION}/bgutil-ytdlp-pot-provider.zip \
    /etc/yt-dlp/plugins/bgutil-ytdlp-pot-provider.zip

COPY test-plugin.py /tmp/test-plugin.py
RUN chmod 755 /etc/yt-dlp /etc/yt-dlp/plugins \
    && env -u LD_PRELOAD setpriv --reuid 10001 --regid 10001 --clear-groups python3 -B /tmp/test-plugin.py "${BGUTIL_PLUGIN_VERSION}" \
    && rm /tmp/test-plugin.py

HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=3 \
    CMD ["node", "-e", "fetch('http://127.0.0.1:3001/api/health/live', {signal: AbortSignal.timeout(4000)}).then(r => { if (!r.ok) process.exit(1); }).catch(() => process.exit(1))"]
