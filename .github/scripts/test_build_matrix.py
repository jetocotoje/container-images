#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import sys
import tempfile
import unittest


SCRIPT = pathlib.Path(__file__).with_name("build_matrix.py")
SPEC = importlib.util.spec_from_file_location("build_matrix", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
builder = importlib.util.module_from_spec(SPEC)
sys.modules["build_matrix"] = builder
SPEC.loader.exec_module(builder)


def service(platforms: str) -> dict[str, str]:
    return {
        "name": "librespeed",
        "dir": "librespeed",
        "context": "librespeed",
        "dockerfile": "librespeed/Dockerfile",
        "platforms": platforms,
    }


class PlatformRunnerTest(unittest.TestCase):
    def test_arm64_maps_to_native_arm_runner(self) -> None:
        self.assertEqual(builder.platform_runner("linux/arm64"), "ubuntu-24.04-arm")

    def test_amd64_and_unknown_platforms_use_default_runner(self) -> None:
        self.assertEqual(builder.platform_runner("linux/amd64"), builder.DEFAULT_RUNNER)
        self.assertEqual(builder.platform_runner("linux/riscv64"), builder.DEFAULT_RUNNER)


class ExpandMatrixEntriesTest(unittest.TestCase):
    def test_expands_each_service_into_one_entry_per_platform(self) -> None:
        entries = builder.expand_matrix_entries([service("linux/amd64,linux/arm64")])

        self.assertEqual(len(entries), 2)
        by_platform = {entry["platform"]: entry for entry in entries}
        self.assertEqual(
            set(by_platform),
            {"linux/amd64", "linux/arm64"},
        )
        for platform, entry in by_platform.items():
            self.assertEqual(entry["name"], "librespeed")
            self.assertEqual(entry["dir"], "librespeed")
            self.assertEqual(entry["context"], "librespeed")
            self.assertEqual(entry["dockerfile"], "librespeed/Dockerfile")
            self.assertEqual(entry["slug"], platform.replace("/", "-"))
        self.assertEqual(by_platform["linux/arm64"]["runner"], "ubuntu-24.04-arm")
        self.assertEqual(
            by_platform["linux/amd64"]["runner"], builder.DEFAULT_RUNNER
        )

    def test_skips_blank_platform_entries(self) -> None:
        self.assertEqual(builder.expand_matrix_entries([service("")]), [])
        self.assertEqual(
            builder.expand_matrix_entries([service("linux/amd64,")]),
            [
                {
                    "name": "librespeed",
                    "dir": "librespeed",
                    "context": "librespeed",
                    "dockerfile": "librespeed/Dockerfile",
                    "platform": "linux/amd64",
                    "slug": "linux-amd64",
                    "runner": builder.DEFAULT_RUNNER,
                }
            ],
        )


class WriteOutputTest(unittest.TestCase):
    def test_writes_both_matrices_and_has_work(self) -> None:
        with tempfile.NamedTemporaryFile("r", suffix=".out") as fh:
            os.environ["GITHUB_OUTPUT"] = fh.name
            try:
                builder.write_output(
                    {"include": [{"name": "librespeed", "platform": "linux/arm64"}]},
                    {"include": [{"name": "librespeed"}]},
                    True,
                )
                fh.seek(0)
                lines = fh.read().splitlines()
            finally:
                del os.environ["GITHUB_OUTPUT"]

        self.assertEqual(len(lines), 3)
        self.assertEqual(
            json.loads(lines[0].removeprefix("matrix=")),
            {"include": [{"name": "librespeed", "platform": "linux/arm64"}]},
        )
        self.assertEqual(
            json.loads(lines[1].removeprefix("merge_matrix=")),
            {"include": [{"name": "librespeed"}]},
        )
        self.assertEqual(lines[2], "has_work=true")


if __name__ == "__main__":
    unittest.main()
