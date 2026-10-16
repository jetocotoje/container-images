# ssync

[ssync](https://github.com/fosskar/ssync) built from source, with [age](https://github.com/FiloSottile/age) (which ssync shells out to) built from source, on `debian:trixie-slim`.

---

## Image

Tags (actual set depends on CI configuration):

- `latest` - latest successful build from the `main` branch
- `v<SSYNC_VERSION>` - based on the upstream ssync release tag

---

## Platforms

Published platforms:

- `linux/amd64`

---

## Runtime interface

The entrypoint is `catatonit -- ssync`; the default command is `daemon`. Pass `--config <path> daemon` to use a config outside the default lookup (`$HOME/.config/ssync/config.toml`, then `/etc/ssync/config.toml`).

### Storage

| Path in container | Contents / purpose                                         | Notes                                                    |
|-------------------|------------------------------------------------------------|----------------------------------------------------------|
| `/var/lib/ssync`  | `$HOME`; put `data_dir` and agent session dirs below it    | Persistent volume.                                       |
| `/tmp`            | Short-lived copies of the age identity during decryption   | Required with a read-only rootfs; use a memory `emptyDir`. |

ssync refuses an age identity or cluster file whose mode grants any group or world access.

### User / permissions

- Default user inside container: `ssync:ssync / 10001:10001`.
- No root init or writable image filesystem is required at runtime.
