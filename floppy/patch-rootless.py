"""Make the upstream entrypoint and supervisord config start as a non-root user.

Fails the build when an anchor is missing or ambiguous, so upstream changes
surface at build time instead of as a crash-looping container.
"""

from pathlib import Path

ENTRYPOINT = Path("/entrypoint.sh")
SUPERVISORD = Path("/etc/supervisord.conf")

OWNERSHIP_START = "PUID=${PUID:-1000}\n"
OWNERSHIP_END = "# Probe the host once, here,"


def patch_entrypoint() -> None:
    text = ENTRYPOINT.read_text()
    if text.count(OWNERSHIP_START) != 1 or text.count(OWNERSHIP_END) != 1:
        raise SystemExit("entrypoint.sh: ownership block anchors not found exactly once")
    start = text.index(OWNERSHIP_START)
    end = text.index(OWNERSHIP_END)
    if end < start:
        raise SystemExit("entrypoint.sh: ownership block anchors out of order")
    block = text[start:end]
    if "usermod" not in block or "chown" not in block:
        raise SystemExit("entrypoint.sh: ownership block no longer holds usermod/chown")
    wrapped = 'if [ "$(id -u)" -eq 0 ]; then\n' + block + "fi\n\n"
    ENTRYPOINT.write_text(text[:start] + wrapped + text[end:])


def patch_supervisord() -> None:
    lines = SUPERVISORD.read_text().splitlines(keepends=True)
    kept = [line for line in lines if line.strip() != "user=root"]
    if len(lines) - len(kept) != 2:
        raise SystemExit("supervisord.conf: expected exactly two user=root lines")
    SUPERVISORD.write_text("".join(kept))


patch_entrypoint()
patch_supervisord()
