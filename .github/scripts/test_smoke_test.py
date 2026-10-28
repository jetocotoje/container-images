#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock


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


    def test_command_mode_does_not_wait_for_health(self) -> None:
        service_dir = self.service_dir({"smokeArgs": ["--version"]})
        with (
            mock.patch.object(smoke, "run_command", return_value=True) as run,
            mock.patch.object(smoke, "run_until_healthy") as wait,
        ):
            self.assertEqual(smoke.main([
                "--service-dir", str(service_dir), "--image", "example",
            ]), 0)
            run.assert_called_once_with("example", ["--version"])
            wait.assert_not_called()


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


    def test_allows_startup_beyond_default_deadline(self) -> None:
        states = [("running", "starting")] * 91 + [("running", "healthy")]
        self.assertEqual(self.wait(states, timeout=600), (True, 92))

    def test_extended_deadline_still_expires(self) -> None:
        states = [("running", "starting")] * 201
        self.assertEqual(self.wait(states, timeout=600), (False, 201))

    def test_extended_deadline_does_not_delay_failure(self) -> None:
        for state in [("running", "unhealthy"), ("exited", "starting")]:
            with self.subTest(state=state):
                self.assertEqual(self.wait([state], timeout=600), (False, 1))


class RunUntilHealthyTest(unittest.TestCase):
    def test_uses_image_start_period_as_readiness_allowance(self) -> None:
        cases = [
            ({}, 180),
            ({"StartPeriod": 0}, 180),
            ({"StartPeriod": 15_000_000_000}, 180),
            ({"StartPeriod": 30_000_000_000}, 180),
            ({"StartPeriod": 180_500_000_000}, 180.5),
            ({"StartPeriod": 600_000_000_000}, 600),
        ]
        for healthcheck, expected in cases:
            with self.subTest(healthcheck=healthcheck):
                with (
                    mock.patch.object(
                        smoke, "docker",
                        side_effect=[json.dumps(healthcheck), "container-id"],
                    ) as docker,
                    mock.patch.object(
                        smoke, "wait_healthy", return_value=True,
                    ) as wait,
                    mock.patch.object(smoke.subprocess, "run") as run,
                ):
                    self.assertTrue(smoke.run_until_healthy("example"))
                    self.assertEqual(docker.call_args_list, [
                        mock.call(
                            "image", "inspect", "--format",
                            "{{json .Config.Healthcheck}}", "example",
                        ),
                        mock.call("run", "--detach", "example"),
                    ])
                    wait.assert_called_once()
                    self.assertEqual(wait.call_args.kwargs["timeout"], expected)
                    run.assert_called_once_with(
                        ["docker", "rm", "--force", "--volumes", "container-id"],
                        capture_output=True,
                    )

    def test_missing_healthcheck_does_not_start_container(self) -> None:
        with (
            mock.patch.object(smoke, "docker", return_value="null") as docker,
            mock.patch.object(smoke, "wait_healthy") as wait,
            mock.patch.object(smoke.subprocess, "run") as run,
        ):
            self.assertFalse(smoke.run_until_healthy("example"))
            docker.assert_called_once_with(
                "image", "inspect", "--format",
                "{{json .Config.Healthcheck}}", "example",
            )
            wait.assert_not_called()
            run.assert_not_called()

    def test_failed_health_still_logs_and_cleans_up(self) -> None:
        with (
            mock.patch.object(
                smoke, "docker",
                side_effect=['{"StartPeriod": 600000000000}', "container-id"],
            ),
            mock.patch.object(smoke, "wait_healthy", return_value=False),
            mock.patch.object(smoke.subprocess, "run") as run,
        ):
            self.assertFalse(smoke.run_until_healthy("example"))
            self.assertEqual(run.call_args_list, [
                mock.call(["docker", "logs", "container-id"]),
                mock.call(
                    ["docker", "rm", "--force", "--volumes", "container-id"],
                    capture_output=True,
                ),
            ])


if __name__ == "__main__":
    unittest.main()
