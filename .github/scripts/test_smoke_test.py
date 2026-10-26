#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys
import tempfile
import unittest


SCRIPT = pathlib.Path(__file__).with_name("smoke_test.py")
SPEC = importlib.util.spec_from_file_location("smoke_test", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
smoke = importlib.util.module_from_spec(SPEC)
sys.modules["smoke_test"] = smoke
SPEC.loader.exec_module(smoke)


class LoadSmokeArgsTest(unittest.TestCase):
    def service_dir(self, cfg: dict) -> pathlib.Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = pathlib.Path(tmp.name)
        (path / "service.json").write_text(json.dumps(cfg))
        return path

    def test_returns_none_without_smoke_args(self) -> None:
        self.assertIsNone(smoke.load_smoke_args(self.service_dir({})))

    def test_returns_smoke_args(self) -> None:
        cfg = {"smokeArgs": ["--version"]}
        self.assertEqual(smoke.load_smoke_args(self.service_dir(cfg)), ["--version"])

    def test_rejects_non_list_smoke_args(self) -> None:
        with self.assertRaises(ValueError):
            smoke.load_smoke_args(self.service_dir({"smokeArgs": "--version"}))


class WaitHealthyTest(unittest.TestCase):
    def wait(self, states: list[tuple[str, str]], timeout: float = 100) -> tuple[bool, int]:
        remaining = iter(states)
        now = [0.0]
        reads = [0]

        def read_state() -> tuple[str, str]:
            reads[0] += 1
            return next(remaining)

        def sleep(seconds: float) -> None:
            now[0] += seconds

        result = smoke.wait_healthy(read_state, timeout, lambda: now[0], sleep)
        return result, reads[0]

    def test_passes_once_healthy(self) -> None:
        result, reads = self.wait(
            [("running", "starting"), ("running", "starting"), ("running", "healthy")]
        )
        self.assertEqual((result, reads), (True, 3))

    def test_fails_when_unhealthy(self) -> None:
        result, reads = self.wait([("running", "starting"), ("running", "unhealthy")])
        self.assertEqual((result, reads), (False, 2))

    def test_fails_when_container_exits(self) -> None:
        result, reads = self.wait([("running", "starting"), ("exited", "starting")])
        self.assertEqual((result, reads), (False, 2))

    def test_fails_after_timeout(self) -> None:
        states = [("running", "starting")] * 10
        result, reads = self.wait(states, timeout=smoke.POLL_SECONDS * 2)
        self.assertEqual((result, reads), (False, 3))


if __name__ == "__main__":
    unittest.main()
