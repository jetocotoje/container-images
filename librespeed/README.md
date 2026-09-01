# LibreSpeed

LibreSpeed built from upstream source on `php:8.4-apache`, packaged for rootless Kubernetes deployments.

---

## Image

Tags (actual set depends on CI configuration):

- `latest` - latest successful build from the `main` branch
- `v<LIBRESPEED_VERSION>` - based on the upstream LibreSpeed release

The upstream source is copied from LibreSpeed's SHA256-pinned multi-platform image.

---

## Platforms

Published platforms:

- `linux/amd64`
- `linux/arm64`

---

## Runtime interface

### Network

Exposed ports inside the container:

| Port   | Protocol | Purpose       |
|--------|----------|---------------|
| `8080` | TCP      | LibreSpeed UI |

`WEBPORT` defaults to `8080`. Keep it `>= 1024`; Apache runs as a non-root user and cannot bind privileged ports.

### Storage

Paths intended for writable runtime data:

| Path in container | Contents / purpose                                  | Notes                                                       |
|-------------------|-----------------------------------------------------|-------------------------------------------------------------|
| `/tmp`            | Generated webroot and copied Apache configuration   | Required. Use `emptyDir` or tmpfs with read-only rootfs.    |
| `/database`       | SQLite telemetry database at `/database/db.sql`     | Required only when `TELEMETRY=true` with SQLite telemetry.  |

The image does not write to `/etc/apache2`, `/var/www/html`, `/var/run`, or `/var/lock` at startup. The entrypoint builds a disposable webroot and Apache configuration under `/tmp/librespeed`.

### User / permissions

Runtime user and permissions expectations:

- Default user inside container: `librespeed:librespeed / 10001:10001`.
- `/tmp` must be writable by this user.
- `/database` must be writable by this user when using SQLite telemetry.
- No root init, chown, or writable image filesystem is required at runtime.

### Modes

Supported `MODE` values match the upstream image:

- `standalone` - frontend and local backend under `/backend`.
- `frontend` - frontend only; use `/servers.json` or `SERVER_LIST_URL` for backend list.
- `backend` - backend files served from webroot.
- `dual` - frontend plus backend.

Common environment variables:

- `TITLE`
- `TAGLINE`
- `USE_NEW_DESIGN=true`
- `SERVER_LIST_URL`
- `GDPR_EMAIL` (`EMAIL` remains a deprecated fallback)
- `IPINFO_APIKEY`
- `TELEMETRY=true`
- `PASSWORD` (required when `TELEMETRY=true`)
- `DB_TYPE=sqlite|mysql|postgresql`
- `DB_USERNAME`, `DB_PASSWORD`, `DB_HOSTNAME`, `DB_NAME`, `DB_PORT`
- `ENABLE_ID_OBFUSCATION=true`
- `OBFUSCATION_SALT=0x...`
- `REDACT_IP_ADDRESSES=true`

### Kubernetes

Minimal pod security settings:

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 10001
  runAsGroup: 10001
  fsGroup: 10001
  seccompProfile:
    type: RuntimeDefault
containers:
  - name: librespeed
    image: ghcr.io/<owner>/<repo>/librespeed:latest
    ports:
      - name: http
        containerPort: 8080
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop: ["ALL"]
    volumeMounts:
      - name: tmp
        mountPath: /tmp
volumes:
  - name: tmp
    emptyDir: {}
```

Add writable telemetry storage only when using SQLite telemetry:

```yaml
volumeMounts:
  - name: tmp
    mountPath: /tmp
  - name: database
    mountPath: /database
volumes:
  - name: tmp
    emptyDir: {}
  - name: database
    persistentVolumeClaim:
      claimName: librespeed-database
```
