# Prowlarr

Permanent wrapper over `ghcr.io/home-operations/prowlarr` that keeps the bundled .NET runtime on the latest .NET 8 patch
and runs `apk upgrade`. Upstream Prowlarr releases can lag several .NET patches behind, as with the Brotli decoder
CVE-2026-111497 fixed in 8.0.33.

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

The build compares the .NET version upstream bundles (`includedFrameworks` in `Prowlarr.runtimeconfig.json`) with
`DOTNET_VERSION`:

- Upstream bundles an older version of the same major: the runtime is overlaid as below.
- Upstream bundles `DOTNET_VERSION` or newer of the same major: `/app/bin` is left as shipped.
- Upstream bundles a different major, or `includedFrameworks` has no `Microsoft.NETCore.App`: the build fails.

The overlay:

- `dotnet-runtime` and `aspnetcore-runtime` `DOTNET_VERSION` (`linux-musl-x64` / `linux-musl-arm64`) are downloaded
  from `builds.dotnet.microsoft.com` and checked against the SHA-512 hashes read at build time from the release
  metadata (`release-metadata/<major>.<minor>/releases.json`, e.g.
  [8.0](https://builds.dotnet.microsoft.com/dotnet/release-metadata/8.0/releases.json)).
- Their `Microsoft.NETCore.App` and `Microsoft.AspNetCore.App` files and `libhostfxr.so` replace the ones in
  `/app/bin`. The runtime pack entries in `/app/bin/*.deps.json` and `Prowlarr.runtimeconfig.json` are rewritten to
  the new version, so SBOM scanners report it.

### Updates

- Renovate bumps `DOTNET_VERSION` to new patches within 8.0.x and automerges them.
- Moving to a new .NET major is done by hand. When upstream moves to one, the build fails: set `DOTNET_VERSION` to
  that major's latest patch and update the `allowedVersions` of the `dotnet-runtime` rule in `renovate.json`.
