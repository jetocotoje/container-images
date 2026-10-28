# SABnzbd

Pinned upstream SABnzbd with only its certifi dependency updated. Application code, startup and runtime settings are inherited from upstream.

## Dependency updates

`requirements.txt` pins certifi and its wheel hash. Weekly rebuilds do not advance that pin; dependency updates must update the requirement and hash. Every build checks the selected certifi distribution against that exact pin and verifies that the compromised G3/AAA trust paths are absent. Unaffected emSign roots may remain, following [Python's security guidance](https://discuss.python.org/t/information-for-python-users-regarding-emudhra-emsign-ca-certificate-security-incident/109576).

Native amd64 and arm64 CI requires HTTP health before publishing regular and weekly builds.

## Runtime interface

- HTTP: port `8080`, with `/` used for health checks.
- Persistence: `/config` holds configuration and queue data. Download/media paths remain application-configured.
- Writable temporary storage: `/tmp`.
- Default user: upstream `nobody:nogroup`. Deployments may override the UID/GID when writable mounts have matching ownership.
- A read-only root filesystem requires writable `/config` and `/tmp` mounts.

This updates SABnzbd's certifi-backed trust, not Python's intrinsic denylist, pip's vendored CA bundle or OS packages.

Published tags are `latest` and the upstream SABnzbd version. Both architectures are published as one index.
