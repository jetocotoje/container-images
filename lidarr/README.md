# Lidarr

Lidarr pinned to the `nightly` update branch for plugin support, packaged as a hardened Debian Trixie image for read-only-rootfs deployments.

---

## Image

Tags (actual set depends on CI configuration):

- `latest` - latest successful build from the `main` branch
- `<LIDARR_VERSION>` - based on Lidarr version only

---

## Platforms

Published platforms:

- `linux/amd64`
- `linux/arm64`

---

## Runtime interface

### Network

Exposed ports inside the container:

| Port   | Protocol | Purpose  |
|--------|----------|----------|
| `8686` | TCP      | `Web UI` |

### Storage

Paths inside the container that are intended for persistent or external data:

| Path in container | Contents / purpose               | Notes                                                                |
|-------------------|----------------------------------|----------------------------------------------------------------------|
| `/config`         | Lidarr database and runtime data | Mount persistent storage here. Must be writable by the runtime user. |

### User / permissions

Runtime user and permissions expectations:

- Default user inside container: `10001:10001`.
- The mounted `/config` path must already be writable by this user for fully rootless operation.
- `HOME=/config`, `TMPDIR=/config/tmp`, and `.NET` diagnostics are disabled via `DOTNET_EnableDiagnostics=0`.
- Debian's `nodejs` runtime is included so Lidarr can perform local token generation when needed.
- The entrypoint creates `/config/tmp` on startup so the image works cleanly with `readOnlyRootFilesystem: true`.

### Startup arguments

- Default command: `--nobrowser --data=/config`
- Add Lidarr startup arguments at runtime if needed, for example `--port 8686`.

### Updates

- The image downloads official Lidarr release tarballs from the glibc `linux` nightly channel rather than the musl build.
- Downloads are verified against the SHA256 published by the Servarr release feed before extraction.
- The runtime image is a separate stage, so fetch tooling like `curl` and `jq` does not remain installed in production.
