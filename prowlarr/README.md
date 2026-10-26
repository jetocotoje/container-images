# Prowlarr

Temporary wrapper over `ghcr.io/home-operations/prowlarr` that replaces the bundled .NET runtime with Microsoft's
.NET 8.0.33 build, which fixes the Brotli decoder CVE-2026-111497, and runs `apk upgrade`.

Delete this image once an upstream Prowlarr release bundles .NET 8.0.33 or newer. The build fails once the upstream
image's bundled runtime is no older than `DOTNET_VERSION`.

---

## Image

Tags (actual set depends on CI configuration):

- `latest` - latest successful build from the `main` branch
- `<PROWLARR_VERSION>` - based on the upstream Prowlarr version only

---

## Platforms

Published platforms:

- `linux/amd64`
- `linux/arm64`

---

## Runtime interface

Unchanged from `ghcr.io/home-operations/prowlarr`.

### Network

| Port   | Protocol | Purpose  |
|--------|----------|----------|
| `9696` | TCP      | `Web UI` |

### Storage

| Path in container | Contents / purpose                 | Notes                                    |
|-------------------|------------------------------------|------------------------------------------|
| `/config`         | Prowlarr database and runtime data | Must be writable by the runtime user.    |

### User / permissions

- Default user inside container: `nobody:nogroup`.

### Runtime overlay

- `dotnet-runtime` and `aspnetcore-runtime` 8.0.33 (`linux-musl-x64` / `linux-musl-arm64`) are downloaded from
  `builds.dotnet.microsoft.com` and checked against the SHA-512 hashes pinned in the Dockerfile, taken from the
  [8.0 release metadata](https://builds.dotnet.microsoft.com/dotnet/release-metadata/8.0/releases.json).
- Their `Microsoft.NETCore.App` and `Microsoft.AspNetCore.App` files and `libhostfxr.so` replace the ones in
  `/app/bin`. The runtime pack entries in `/app/bin/*.deps.json` and `Prowlarr.runtimeconfig.json` are rewritten to
  the new version, so SBOM scanners report it.
- To move to a newer .NET 8 patch, update `DOTNET_VERSION` and the four hashes by hand.
