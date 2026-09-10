# OpenCloud

OpenCloud built with 10001:10001 user and some extensions.

Included extensions:

- Unzip
- Arcade
- Maps
- Progress Bars
- JSON Viewer
- External Sites
- Draw.IO

---

## Image

Tags (actual set depends on CI configuration):

- `latest` – latest successful build from the `main` branch
- `<OPENCLOUD_VERSION>` – Based on OpenCloud version only

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
| `9200` | TCP      | `Web UI` |
| `9233` | TCP      | `NATS`   |

### Storage

Paths inside the container that are intended for persistent or external data:

| Path in container        | Contents / purpose   | Notes                                                                                |
|--------------------------|----------------------|--------------------------------------------------------------------------------------|
| `/var/lib/opencloud`     | All stored data      | Extensions under `web-extensions/` are re-synced from the image on every start       |
| `/etc/opencloud-configs` | Custom configuration | Any yaml configuration files are copied from here to /etc/opencloud for k8s purposes |

### User / permissions

Runtime user and permissions expectations:

- Default user inside container: `opencloud:opencloud / 10001:10001`.
- Files under the configured config and cache paths should be writable by this user.
