# Bazarr

Pinned upstream Bazarr with only its vendored certifi dependency updated. Application code, startup and the `--no-update True` setting are inherited from upstream.

## Dependency updates

`requirements.txt` pins certifi and its universal-wheel hash. Weekly rebuilds do not advance that pin; dependency updates must update the requirement and hash.

Every build checks that Bazarr's import context selects exactly one matching vendored certifi distribution and that Requests uses its bundle. G3/AAA must be absent; unaffected emSign roots may remain, following [Python's security guidance](https://discuss.python.org/t/information-for-python-users-regarding-emudhra-emsign-ca-certificate-security-incident/109576).

Native amd64 and arm64 CI requires HTTP health before publishing regular and weekly builds.

## Runtime interface

- HTTP: port `6767`, with `/` used for health checks.
- Persistence: `/config` holds configuration and application data.
- Media directories remain application-configured.
- Default user: upstream `nobody:nogroup`. Deployments may override the UID/GID when writable mounts have matching ownership.
- A read-only root filesystem requires writable configuration and media mounts.

This updates Bazarr's Requests-selected CA bundle, not Python's intrinsic denylist, pip's vendored CA bundle or OS packages. Configured subtitle-provider compatibility is not established by startup health checks.

Published tags are `latest` and the upstream Bazarr version. Both architectures are published as one index.
