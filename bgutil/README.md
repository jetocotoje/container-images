# bgutil

Pinned upstream bgutil application and dependencies on a separately pinned Node base. Builds check the native Brotli version, Node's default CA roots and the canvas native module. Native amd64 and arm64 CI requires HTTP health before publishing.

## Runtime interface

- HTTP: port `4416`, with `/ping` used for health checks.
- Default user: `node` (UID/GID 1000).
- Writable temporary storage: `/tmp`; no persistent data is required.
- Keep the unauthenticated API private. The matching yt-dlp plugin connects using `--extractor-args "youtubepot-bgutilhttp:base_url=http://bgutil:4416"`.

Published tags are `latest` and the upstream bgutil version. Both architectures are published as one index. Renovate groups upstream bgutil and Aurral's bgutil plugin updates in one reviewed PR without automerge. On each upstream update, compare its user, working directory, environment, entrypoint and arguments with this Dockerfile. Node base updates retain the repository's automatic policy; weekly rebuilds retain their pins.
