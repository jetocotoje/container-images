# Prowlarr

Permanent wrapper over `ghcr.io/home-operations/prowlarr` that runs `apk upgrade`.

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
