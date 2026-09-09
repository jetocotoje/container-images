#!/usr/bin/env python3
"""
Discover buildable services and emit GitHub Actions matrix payloads.

The previous inline bash script grew unwieldy and was error-prone when the
repository state changed (e.g., missing base commit or filenames containing
spaces).  This Python version keeps the same behaviour but in a clearer form,
adds better logging, and handles edge-cases like zero SHAs.

Two matrices are emitted: ``matrix`` expands each selected service into one
entry per target platform (each pinned to a runner that executes that platform
natively), and ``merge_matrix`` has one entry per service for the job that
stitches the per-platform digests into a multi-platform manifest.
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
from typing import Dict, Iterable, List, Sequence, Set

ZERO_SHA = "0" * 40
# README-only updates should not trigger builds.
IGNORED_TOP_LEVEL_ENTRIES = {"README", "README.md"}
# Platforms need a runner that executes them natively; anything unlisted
# fails fast on the default runner instead of silently falling back to QEMU.
PLATFORM_RUNNERS = {
    "linux/arm64": "ubuntu-24.04-arm",
}
DEFAULT_RUNNER = "ubuntu-latest"


def log(msg: str) -> None:
    print(msg, flush=True)


def run_git(
    args: Sequence[str], check: bool = True
) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        ["git", *args],
        text=True,
        capture_output=True,
        check=False,
    )
    if check and proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc


def load_dirs_from_stdout(stdout: str) -> List[str]:
    dirs: Set[str] = set()
    for line in stdout.splitlines():
        if not line:
            continue
        parts = line.split("/", 1)
        top = parts[0]
        if top in IGNORED_TOP_LEVEL_ENTRIES:
            continue
        dirs.add(top)
    return sorted(dirs)


def tracked_top_level_dirs() -> List[str]:
    proc = run_git(["ls-files"])
    return load_dirs_from_stdout(proc.stdout)


def changed_top_level_dirs(base: str | None) -> List[str]:
    if not base or base == ZERO_SHA:
        log("No usable base SHA; treating all tracked dirs as changed.")
        return tracked_top_level_dirs()

    log(f"Fetching base commit {base} for diff comparison.")
    run_git(["fetch", "origin", base, "--depth=1"], check=False)

    diff = run_git(["diff", "--name-only", f"{base}...HEAD"], check=False)
    if diff.returncode != 0:
        log(
            f"git diff failed ({diff.stderr.strip() or diff.returncode}); "
            "falling back to building all services."
        )
        return tracked_top_level_dirs()

    return load_dirs_from_stdout(diff.stdout)


def load_services() -> List[Dict[str, str]]:
    services: List[Dict[str, str]] = []
    for cfg_path in sorted(pathlib.Path(".").glob("*/service.json")):
        dir_path = cfg_path.parent
        name = dir_path.name
        cfg = json.loads(cfg_path.read_text())

        context = cfg.get("context", str(dir_path))
        dockerfile = cfg.get("dockerfile")
        dockerfile_path = (
            str(dir_path / dockerfile) if dockerfile else str(dir_path / "Dockerfile")
        )

        platforms = cfg.get("platforms")
        platforms_value = (
            ",".join(platforms)
            if isinstance(platforms, list) and platforms
            else "linux/amd64"
        )

        services.append(
            {
                "name": name,
                "dir": str(dir_path),
                "context": context,
                "dockerfile": dockerfile_path,
                "platforms": platforms_value,
            }
        )

    return services

def platform_runner(platform: str) -> str:
    return PLATFORM_RUNNERS.get(platform, DEFAULT_RUNNER)


def expand_matrix_entries(
    services: Sequence[Dict[str, str]],
) -> List[Dict[str, str]]:
    entries: List[Dict[str, str]] = []
    for svc in services:
        for platform in (p.strip() for p in svc["platforms"].split(",")):
            if not platform:
                continue
            entries.append(
                {
                    "name": svc["name"],
                    "dir": svc["dir"],
                    "context": svc["context"],
                    "dockerfile": svc["dockerfile"],
                    "platform": platform,
                    "slug": platform.replace("/", "-"),
                    "runner": platform_runner(platform),
                }
            )
    return entries


def select_services(
    services: Sequence[Dict[str, str]],
    changed_dirs: Iterable[str],
) -> List[Dict[str, str]]:
    changed = set(changed_dirs)
    log(f"Changed top-level dirs: {', '.join(changed) if changed else '(none)'}")

    if not services:
        return []

    if not changed:
        log("No changed dirs detected; building all services.")
        return list(services)

    selected = [
        svc
        for svc in services
        if svc["name"] in changed or svc["dir"].split("/", 1)[0] in changed
    ]

    if selected:
        log(
            f"Selected {len(selected)} services based on changes: "
            f"{', '.join(svc['name'] for svc in selected)}"
        )
        return selected

    log("No service-specific changes detected; defaulting to all services.")
    return list(services)


def write_output(
    matrix: Dict[str, List[Dict[str, str]]],
    merge_matrix: Dict[str, List[Dict[str, str]]],
    has_work: bool,
) -> None:
    output_path = os.environ["GITHUB_OUTPUT"]
    with open(output_path, "a", encoding="utf-8") as fh:
        fh.write(f"matrix={json.dumps(matrix)}\n")
        fh.write(f"merge_matrix={json.dumps(merge_matrix)}\n")
        fh.write(f"has_work={'true' if has_work else 'false'}\n")


def dump(label: str, data: object) -> None:
    log(f"{label}:")
    print(json.dumps(data, indent=2))


def main() -> int:
    event_name = os.environ.get("EVENT_NAME", "")
    base = (
        os.environ.get("PR_BASE_SHA")
        if event_name == "pull_request"
        else os.environ.get("BEFORE_SHA")
    )

    log("### Discovering services (*/service.json)")
    services = load_services()
    dump("All services", services)

    if not services:
        log("No services detected; emitting empty matrix.")
        write_output({"include": []}, {"include": []}, False)
        return 0

    log("### Determining changed directories")
    changed_dirs = changed_top_level_dirs(base)

    selected = select_services(services, changed_dirs)
    has_work = bool(selected)

    build_matrix = {"include": expand_matrix_entries(selected)}
    merge_matrix = {"include": selected}
    dump("Final build matrix payload", build_matrix)
    dump("Final merge matrix payload", merge_matrix)
    write_output(build_matrix, merge_matrix, has_work)
    return 0


if __name__ == "__main__":
    sys.exit(main())
