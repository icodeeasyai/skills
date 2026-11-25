"""Seedance 2.0 command contracts."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from _video_common import build_standard_parser, build_standard_payload  # noqa: E402
from doubao_seedance_2_0 import MODEL_SPEC  # noqa: E402


SCRIPT = SCRIPTS / "doubao_seedance_2_0.py"


class Seedance20Tests(unittest.TestCase):
    def test_frames_default_to_adaptive_and_preserve_an_explicit_ratio(self) -> None:
        parser = build_standard_parser(MODEL_SPEC)
        options = ["create", "--prompt", "Scene", "--first-frame", "https://cdn.example/first.png"]
        implicit = build_standard_payload(MODEL_SPEC, parser.parse_args(options))
        explicit = build_standard_payload(MODEL_SPEC, parser.parse_args(options + ["--ratio", "16:9"]))
        self.assertEqual(implicit["ratio"], "adaptive")
        self.assertEqual(explicit["ratio"], "16:9")

    def test_supports_4k_adaptive_ratio_and_audio_by_default(self) -> None:
        args = build_standard_parser(MODEL_SPEC).parse_args(
            ("create", "--prompt", "A bustling night market", "--resolution", "4K", "--ratio", "adaptive", "--duration", "15")
        )

        payload = build_standard_payload(MODEL_SPEC, args)

        self.assertEqual(
            payload,
            {
                "model": "doubao-seedance-2.0",
                "prompt": "A bustling night market",
                "resolution": "4K",
                "ratio": "adaptive",
                "duration": 15,
                "generate_audio": True,
            },
        )

    def test_rejects_duration_outside_four_to_fifteen_seconds(self) -> None:
        with self.assertRaises(SystemExit):
            build_standard_parser(MODEL_SPEC).parse_args(
                ("create", "--prompt", "x", "--duration", "16")
            )

    def test_dry_run_uses_the_model_without_paid_confirmation(self) -> None:
        environment = os.environ.copy()
        environment.pop("ICODEEASY_API_KEY", None)
        environment.pop("OPENAI_API_KEY", None)
        environment.pop("ANTHROPIC_AUTH_TOKEN", None)
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--json", "create", "--dry-run", "--prompt", "No network"],
            text=True,
            capture_output=True,
            env=environment,
            timeout=5,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["model"], "doubao-seedance-2.0")


if __name__ == "__main__":
    unittest.main()
