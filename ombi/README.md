# Ombi

Ombi built from the upstream release tarballs with a fixed non-root user and no root-only init layer.

---

## Image

Tags (actual set depends on CI configuration):

- `latest` - latest successful build from the `main` branch
- `<OMBI_VERSION>` - based on Ombi version only

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
| `5000` | TCP      | `Web UI` |

### Storage

Paths inside the container that are intended for persistent or external data:

| Path in container | Contents / purpose                      | Notes                                                                |
|-------------------|-----------------------------------------|----------------------------------------------------------------------|
| `/config`         | Ombi databases, logs, and runtime state | Mount persistent storage here. Must be writable by the runtime user. |

### User / permissions

Runtime user and permissions expectations:

- Default user inside container: `ombi:ombi / 10001:10001`.
- The mounted `/config` path must already be writable by this user for fully rootless operation.
- Most of `/app/ombi` stays root-owned and read-only at runtime.
- The generated frontend file Ombi rewrites is redirected to `/config/runtime/index.html`, so the image can run with a read-only root filesystem.
- .NET diagnostics are disabled by default via `DOTNET_EnableDiagnostics=0` to reduce attach/debug surface inside the container.

### Read-only root filesystem

- Supported when `/config` is writable.
- Provide writable temporary storage such as `--tmpfs /tmp` when using `--read-only`.

### Startup arguments

- Default command: `--storage /config --host http://*:5000`
- Add Ombi startup arguments at runtime if needed, for example `--baseurl /ombi` when serving behind a reverse proxy path.
