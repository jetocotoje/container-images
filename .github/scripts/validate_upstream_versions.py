#!/usr/bin/env python3
"""Validate external version pins before expensive Docker builds."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Sequence


RENOVATE_ARG = re.compile(
    r"#\s*renovate:\s*(?P<meta>[^\n]+)\n"
    r"ARG\s+(?P<arg_name>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*\"?(?P<current_value>[^\"\s]+)\"?",
    re.MULTILINE,
)

SERVARR_ARCH = {
    "linux/amd64": "x64",
    "linux/arm64": "arm64",
}


@dataclass(frozen=True)
class RenovateArg:
    arg_name: str
    current_value: str
    datasource: str
    dep_name: str


def parse_metadata(meta: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for part in meta.split():
        if "=" not in part:
            continue
        key, raw_value = part.split("=", 1)
        values[key] = raw_value.strip('"')
    return values


def parse_renovate_args(dockerfile_text: str) -> list[RenovateArg]:
    args: list[RenovateArg] = []
    for match in RENOVATE_ARG.finditer(dockerfile_text):
        metadata = parse_metadata(match.group("meta"))
        datasource = metadata.get("datasource")
        dep_name = metadata.get("depName")
        if not datasource or not dep_name:
            continue
        args.append(
            RenovateArg(
                arg_name=match.group("arg_name"),
                current_value=match.group("current_value"),
                datasource=datasource,
                dep_name=dep_name,
            )
        )
    return args


def load_platforms(service_dir: pathlib.Path) -> list[str]:
    cfg_path = service_dir / "service.json"
    if not cfg_path.exists():
        return ["linux/amd64"]

    cfg = json.loads(cfg_path.read_text())
    platforms = cfg.get("platforms")
    if isinstance(platforms, list) and platforms:
        return [str(platform) for platform in platforms]
    return ["linux/amd64"]


def servarr_feed_url(dep_name: str, arch: str) -> str:
    return (
        f"https://{dep_name}.servarr.com/v1/update/nightly/changes"
        f"?os=linux&runtime=netcore&arch={arch}"
    )


def fetch_json(url: str, timeout: int = 30) -> object:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(f"failed to fetch {url}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"failed to parse JSON from {url}: {exc}") from exc


def version_exists(feed: object, version: str) -> tuple[bool, list[str]]:
    if not isinstance(feed, list):
        raise RuntimeError("expected Servarr feed to be a JSON array")

    versions: list[str] = []
    for item in feed:
        if isinstance(item, dict) and isinstance(item.get("version"), str):
            versions.append(item["version"])

    return version in versions, versions[:5]


def validate_servarr_arg(arg: RenovateArg, platforms: Sequence[str]) -> list[str]:
    errors: list[str] = []
    checked_arches: set[str] = set()

    for platform in platforms:
        arch = SERVARR_ARCH.get(platform)
        if arch is None:
            continue
        if arch in checked_arches:
            continue
        checked_arches.add(arch)

        url = servarr_feed_url(arg.dep_name, arch)
        feed = fetch_json(url)
        exists, latest = version_exists(feed, arg.current_value)
        if not exists:
            latest_text = ", ".join(latest) if latest else "none returned"
            errors.append(
                f"{arg.arg_name}={arg.current_value} missing from {arg.dep_name} nightly feed "
                f"for {platform} ({arch}); latest feed versions: {latest_text}"
            )

    return errors


def validate(dockerfile: pathlib.Path, service_dir: pathlib.Path) -> list[str]:
    renovate_args = parse_renovate_args(dockerfile.read_text())
    platforms = load_platforms(service_dir)

    errors: list[str] = []
    for arg in renovate_args:
        if arg.datasource == "custom.servarr-nightly":
            errors.extend(validate_servarr_arg(arg, platforms))

    return errors


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--service-dir", required=True, type=pathlib.Path)
    parser.add_argument("--dockerfile", required=True, type=pathlib.Path)
    args = parser.parse_args(argv)

    errors = validate(args.dockerfile, args.service_dir)
    if not errors:
        print("Upstream version pins valid.")
        return 0

    print("Upstream version pin validation failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    print("Update the pinned ARG or fix Renovate before running the Docker build.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
