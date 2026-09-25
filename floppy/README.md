# Floppy

Upstream Floppy image patched to run as a non-root user with no capabilities.

The upstream entrypoint starts as root to remap user `abc` to `PUID`/`PGID` and chown its paths. This image fixes `abc` to
`10001:10001` at build time, skips that ownership step when not running as root, and drops the `user=root` lines from the
supervisord config. `patch-rootless.py` fails the build when the upstream anchors it patches change.

---

## Image

Tags (actual set depends on CI configuration):

- `latest` – latest successful build from the `main` branch
- `<FLOPPY_VERSION>` – based on the upstream Floppy version only

---

## Platforms

Published platforms:

- `linux/amd64`
- `linux/arm64`

---

## Runtime interface

### Network

Exposed ports inside the container:

| Port   | Protocol | Purpose                     |
|--------|----------|-----------------------------|
| `8000` | TCP      | `Web UI (nginx → gunicorn)` |

### Storage

Paths inside the container that are intended for persistent or external data:

| Path in container | Contents / purpose                | Notes                                |
|-------------------|-----------------------------------|--------------------------------------|
| `/floppy/backups` | Scheduled CSV exports             | Must be writable by `10001:10001`.   |
| `/floppy/db`      | SQLite database without `DB_HOST` | Unused with PostgreSQL.              |
| `/tmp`            | Gunicorn socket, boot sizing      | Must be writable.                    |

### User / permissions

Runtime user and permissions expectations:

- Default user inside container: `abc:abc / 10001:10001`.
- Runs with all capabilities dropped and `allowPrivilegeEscalation: false`.
- `PUID`/`PGID` are fixed at build time; setting them at runtime has no effect.
- Root filesystem must stay writable: startup renders nginx config and collects static files into the image paths.
