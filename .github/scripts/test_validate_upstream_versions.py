#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import pathlib
import sys
import tempfile
import unittest
from unittest import mock


SCRIPT = pathlib.Path(__file__).with_name("validate_upstream_versions.py")
SPEC = importlib.util.spec_from_file_location("validate_upstream_versions", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
sys.modules["validate_upstream_versions"] = validator
SPEC.loader.exec_module(validator)


class ValidateUpstreamVersionsTest(unittest.TestCase):
    def test_parses_renovate_arg_metadata(self) -> None:
        dockerfile = """# renovate: datasource=custom.servarr-nightly depName=lidarr versioning=loose
ARG LIDARR_VERSION=3.1.3.4970
"""

        args = validator.parse_renovate_args(dockerfile)

        self.assertEqual(len(args), 1)
        self.assertEqual(args[0].arg_name, "LIDARR_VERSION")
        self.assertEqual(args[0].current_value, "3.1.3.4970")
        self.assertEqual(args[0].datasource, "custom.servarr-nightly")
        self.assertEqual(args[0].dep_name, "lidarr")

    def test_validates_all_service_platform_arches(self) -> None:
        arg = validator.RenovateArg(
            arg_name="LIDARR_VERSION",
            current_value="3.1.3.4970",
            datasource="custom.servarr-nightly",
            dep_name="lidarr",
        )

        with mock.patch.object(
            validator,
            "fetch_json",
            return_value=[{"version": "3.1.3.4970"}],
        ) as fetch_json:
            errors = validator.validate_servarr_arg(arg, ["linux/amd64", "linux/arm64"])

        self.assertEqual(errors, [])
        self.assertEqual(fetch_json.call_count, 2)
        called_urls = [call.args[0] for call in fetch_json.call_args_list]
        self.assertTrue(any("arch=x64" in url for url in called_urls))
        self.assertTrue(any("arch=arm64" in url for url in called_urls))

    def test_reports_stale_version_with_latest_feed_values(self) -> None:
        arg = validator.RenovateArg(
            arg_name="LIDARR_VERSION",
            current_value="3.1.2.4928",
            datasource="custom.servarr-nightly",
            dep_name="lidarr",
        )

        with mock.patch.object(
            validator,
            "fetch_json",
            return_value=[{"version": "3.1.3.4970"}, {"version": "3.1.3.4968"}],
        ):
            errors = validator.validate_servarr_arg(arg, ["linux/amd64"])

        self.assertEqual(len(errors), 1)
        self.assertIn("LIDARR_VERSION=3.1.2.4928 missing", errors[0])
        self.assertIn("3.1.3.4970, 3.1.3.4968", errors[0])

    def test_validate_reads_service_platforms(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            service_dir = root / "lidarr"
            service_dir.mkdir()
            (service_dir / "service.json").write_text(
                '{"platforms":["linux/amd64","linux/arm64"]}'
            )
            dockerfile = service_dir / "Dockerfile"
            dockerfile.write_text(
                "# renovate: datasource=custom.servarr-nightly depName=lidarr versioning=loose\n"
                "ARG LIDARR_VERSION=3.1.3.4970\n"
            )

            with mock.patch.object(
                validator,
                "fetch_json",
                return_value=[{"version": "3.1.3.4970"}],
            ) as fetch_json:
                errors = validator.validate(dockerfile, service_dir)

        self.assertEqual(errors, [])
        self.assertEqual(fetch_json.call_count, 2)


if __name__ == "__main__":
    unittest.main()
