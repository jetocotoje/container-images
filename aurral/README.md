# Aurral

Pinned upstream Aurral with the bgutil yt-dlp plugin installed in `/etc/yt-dlp/plugins/`. Application code, startup and runtime settings are inherited from upstream.

The plugin archive is pinned by version and SHA-256 checksum. Update both together, keeping the plugin compatible with the deployed bgutil server. Each build verifies that the bundled yt-dlp discovers and registers the HTTP provider at the pinned plugin version as UID/GID 10001. Native amd64 and arm64 CI requires Aurral HTTP health before publishing.

## Runtime interface

- HTTP: port `3001`, with `/api/health/live` used for health checks.
- Persistence: `/config` holds Aurral data. Media paths remain application-configured.
- A read-only root filesystem needs writable data, media and `/tmp` mounts.
- The upstream entrypoint supports a deployment-supplied non-root UID/GID with matching writable mounts.
- Mount yt-dlp options at `/etc/yt-dlp.conf` to set the bgutil server URL. This image supplies no cookies or credentials.

Published tags are `latest` and the upstream Aurral version. Both architectures are published as one index. Renovate tracks the upstream Aurral image independently. Plugin and bgutil server updates share one reviewed PR without automerge; update the plugin checksum before accepting a plugin version bump.
