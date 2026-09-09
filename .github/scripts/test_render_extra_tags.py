#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import pathlib
import sys
import tempfile
import unittest


SCRIPT = pathlib.Path(__file__).with_name("render_extra_tags.py")
SPEC = importlib.util.spec_from_file_location("render_extra_tags", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
renderer = importlib.util.module_from_spec(SPEC)
sys.modules["render_extra_tags"] = renderer
SPEC.loader.exec_module(renderer)


class ParseArgsTest(unittest.TestCase):
    def test_strips_pinned_digest_from_arg_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dockerfile = pathlib.Path(tmp) / "Dockerfile"
            dockerfile.write_text(
                "ARG JELLYFIN_VERSION=10.11.11@sha256:"
                + "a" * 64
                + "\nARG OTHER=keep\n"
            )

            values = renderer.parse_args(dockerfile, ["JELLYFIN_VERSION", "OTHER"])

        self.assertEqual(values, {"JELLYFIN_VERSION": "10.11.11", "OTHER": "keep"})

    def test_returns_empty_for_missing_dockerfile(self) -> None:
        values = renderer.parse_args(pathlib.Path("/nonexistent/Dockerfile"), ["X"])

        self.assertEqual(values, {})


class RenderTagsTest(unittest.TestCase):
    def test_renders_fully_substituted_templates(self) -> None:
        tags = renderer.render_tags(
            "ghcr.io/acme/app",
            ["{VERSION}", "{VERSION}-extra"],
            ["VERSION"],
            {"VERSION": "1.2.3"},
        )

        self.assertEqual(
            tags, ["ghcr.io/acme/app:1.2.3", "ghcr.io/acme/app:1.2.3-extra"]
        )

    def test_skips_templates_with_missing_values(self) -> None:
        tags = renderer.render_tags("ghcr.io/acme/app", ["{VERSION}"], ["VERSION"], {})

        self.assertEqual(tags, [])


if __name__ == "__main__":
    unittest.main()
