#!/usr/bin/env python3
"""
Render optional image tags from service.json templates.

This replaces the previous inline bash/awk snippet with a clearer Python script
that is easier to test and reason about.  It keeps the original behaviour but
adds better validation and logging.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import sys
from typing import Dict, List


ARG_LINE = re.compile(r"^\s*ARG\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+?)\s*(?:#.*)?$")
# Version args may pin the base image digest (e.g. 12.0@sha256:...); tags use
# the bare version.
DIGEST_SUFFIX = re.compile(r"@sha256:[0-9a-f]{64}$")


def parse_args(dockerfile: pathlib.Path, names: List[str]) -> Dict[str, str]:
    values: Dict[str, str] = {}
    if not dockerfile.exists():
        print(f"{dockerfile} does not exist; no ARG values to read.")
        return values

    wanted = set(names)
    if not wanted:
        return values

    with dockerfile.open(encoding="utf-8") as fh:
        for line in fh:
            match = ARG_LINE.match(line)
            if not match:
                continue
            arg_name, raw_value = match.groups()
            if arg_name not in wanted:
                continue
            cleaned = DIGEST_SUFFIX.sub("", raw_value.strip().strip("'").strip('"'))
            if cleaned:
                values[arg_name] = cleaned
                print(f"Found {arg_name}={cleaned}")

    return values


def render_tags(
    image: str, templates: List[str], args: List[str], values: Dict[str, str]
) -> List[str]:
    rendered: List[str] = []
    for template in templates:
        tag_value = template
        for arg in args:
            placeholder = f"{{{arg}}}"
            if placeholder in tag_value and arg in values:
                tag_value = tag_value.replace(placeholder, values[arg])

        if re.search(r"{[^{}]+}", tag_value):
            print(f"Skipping template '{template}' -> '{tag_value}' (missing values)")
            continue

        rendered.append(f"{image}:{tag_value}")
    return rendered


def write_output(tags: List[str]) -> None:
    output_path = os.environ["GITHUB_OUTPUT"]
    with open(output_path, "a", encoding="utf-8") as fh:
        if not tags:
            fh.write("extra_tags=\n")
            return

        fh.write("extra_tags<<EOF\n")
        fh.write("\n".join(tags))
        fh.write("\nEOF\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Render template-based docker tags.")
    parser.add_argument(
        "--service-dir", required=True, help="Directory containing service.json"
    )
    parser.add_argument("--dockerfile", required=True, help="Path to Dockerfile")
    parser.add_argument(
        "--image", required=True, help="Base image name (registry/repo)"
    )
    args = parser.parse_args()

    cfg_path = pathlib.Path(args.service_dir) / "service.json"
    if not cfg_path.exists():
        print(f"No service.json found at {cfg_path}; no extra tags.")
        write_output([])
        return 0

    cfg = json.loads(cfg_path.read_text())
    version_args = cfg.get("versionArgs", []) or []
    templates = cfg.get("tagTemplates", []) or []

    print(f"versionArgs: {version_args}")
    print(f"tagTemplates: {templates}")

    if not templates:
        print("No tagTemplates configured; skipping extra tag generation.")
        write_output([])
        return 0

    dockerfile = pathlib.Path(args.dockerfile)
    values = parse_args(dockerfile, version_args)
    extra_tags = render_tags(args.image, templates, version_args, values)

    if not extra_tags:
        print("No valid extra tags rendered.")
        write_output([])
        return 0

    print("Extra image references:")
    for tag in extra_tags:
        print(f"  {tag}")

    write_output(extra_tags)

    return 0


if __name__ == "__main__":
    sys.exit(main())
