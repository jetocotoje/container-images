#!/usr/bin/env python3
"""
Smoke-test a locally loaded service image before it is published.

A service whose ``service.json`` sets ``smokeArgs`` passes when the image run
with those arguments exits 0. Any other service passes once its container
reports ``healthy``; an image without a HEALTHCHECK fails.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
import time
from typing import Callable

HEALTH_TIMEOUT_SECONDS = 180
POLL_SECONDS = 3


def log(msg: str) -> None:
    print(msg, flush=True)


def load_smoke_args(service_dir: pathlib.Path) -> list[str] | None:
    cfg = json.loads((service_dir / "service.json").read_text())
    args = cfg.get("smokeArgs")
    if args is None:
        return None
    if not isinstance(args, list) or not all(isinstance(a, str) for a in args):
        raise ValueError(f"{service_dir}/service.json: smokeArgs must be a list of strings")
    return args


def docker(*args: str) -> str:
    proc = subprocess.run(["docker", *args], text=True, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(f"docker {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout.strip()


def run_command(image: str, args: list[str]) -> bool:
    log(f"Running {image} {' '.join(args)}")
    return subprocess.run(["docker", "run", "--rm", image, *args]).returncode == 0


def wait_healthy(
    read_state: Callable[[], tuple[str, str]],
    timeout: float = HEALTH_TIMEOUT_SECONDS,
    clock: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
) -> bool:
    deadline = clock() + timeout
    while True:
        status, health = read_state()
        log(f"container {status}, health {health or '-'}")
        if health == "healthy":
            return True
        if status != "running" or health == "unhealthy" or clock() >= deadline:
            return False
        sleep(POLL_SECONDS)


def run_until_healthy(image: str) -> bool:
    if docker("image", "inspect", "--format", "{{json .Config.Healthcheck}}", image) == "null":
        log(f"{image} has no HEALTHCHECK and its service.json sets no smokeArgs")
        return False

    container = docker("run", "--detach", image)

    def read_state() -> tuple[str, str]:
        state = docker(
            "inspect",
            "--format",
            "{{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}",
            container,
        )
        status, _, health = state.partition(" ")
        return status, health

    healthy = False
    try:
        healthy = wait_healthy(read_state)
    finally:
        if not healthy:
            subprocess.run(["docker", "logs", container])
        subprocess.run(["docker", "rm", "--force", "--volumes", container], capture_output=True)
    return healthy


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--service-dir", required=True, type=pathlib.Path)
    parser.add_argument("--image", required=True)
    opts = parser.parse_args(argv)

    args = load_smoke_args(opts.service_dir)
    ok = run_until_healthy(opts.image) if args is None else run_command(opts.image, args)
    log(f"Smoke test {'passed' if ok else 'FAILED'} for {opts.image}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
