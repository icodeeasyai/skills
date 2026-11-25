"""Seedance 2.5 Flash request and dry-run contracts."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from _video_common import UserError, build_standard_parser, build_standard_payload
from doubao_seedance_2_5_flash import MODEL_SPEC


class Seedance25FlashTests(unittest.TestCase):
    def test_cli_dry_run_uses_public_flash_id_and_defaults(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "doubao_seedance_2_5_flash.py"),
             "--json", "run", "--dry-run", "--prompt", "A lake"],
            capture_output=True, text=True, check=True, timeout=5,
        )
        self.assertEqual(json.loads(result.stdout), {
            "model": "doubao-seedance-2-5-flash", "prompt": "A lake",
            "resolution": "480p", "ratio": "9:16", "duration": 4,
            "generate_audio": True,
        })

    def test_frame_mode_follows_first_image_ratio(self) -> None:
        args = build_standard_parser(MODEL_SPEC).parse_args([
            "create", "--prompt", "Move",
            "--first-frame", "https://cdn.example/first.png",
        ])
        self.assertEqual(build_standard_payload(MODEL_SPEC, args)["ratio"], "adaptive")

    def test_explicit_fixed_ratio_is_rejected_for_frame_only_generation(self) -> None:
        args = build_standard_parser(MODEL_SPEC).parse_args([
            "create", "--prompt", "Scene", "--ratio", "16:9",
            "--first-frame", "https://cdn.example/first.png",
        ])
        with self.assertRaisesRegex(UserError, "requires --ratio adaptive"):
            build_standard_payload(MODEL_SPEC, args)

    def test_accepts_five_videos_and_two_images_then_rejects_six_videos(self) -> None:
        options = ["create", "--prompt", "Follow @Video1", "--ratio", "16:9"]
        for index in range(5):
            options.extend(("--reference-video", f"https://cdn.example/{index}.mp4"))
        for index in range(2):
            options.extend(("--reference-image", f"https://cdn.example/{index}.png"))
        args = build_standard_parser(MODEL_SPEC).parse_args(options)
        payload = build_standard_payload(MODEL_SPEC, args)
        self.assertEqual(payload["ratio"], "16:9")
        self.assertEqual(len(payload["content"]), 7)
        args = build_standard_parser(MODEL_SPEC).parse_args(
            options + ["--reference-video", "https://cdn.example/six.mp4"]
        )
        with self.assertRaisesRegex(UserError, "at most 5 reference videos"):
            build_standard_payload(MODEL_SPEC, args)

    def test_rejects_ordinary_image_without_video_and_private_video_url(self) -> None:
        for options in (
            ["--reference-image", "https://cdn.example/reference.png"],
            ["--reference-video", "https://127.0.0.1/private.mp4"],
            ["--last-frame", "https://cdn.example/last.png"],
        ):
            with self.subTest(options=options), self.assertRaises(SystemExit):
                build_standard_parser(MODEL_SPEC).parse_args(
                    ["create", "--prompt", "Scene", *options]
                )


if __name__ == "__main__":
    unittest.main()
