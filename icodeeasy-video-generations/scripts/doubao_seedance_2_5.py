#!/usr/bin/env python3
"""Create or run a Seedance 2.5 video generation task."""

from __future__ import annotations

from _video_common import StandardModelSpec, run_standard_model, validate_seedance25_inputs


MODEL_SPEC = StandardModelSpec(
    canonical_id="doubao-seedance-2.5",
    resolution_choices=("480p", "720p"),
    default_resolution="480p",
    ratio_choices=("16:9", "4:3", "1:1", "3:4", "9:16", "21:9", "adaptive"),
    default_ratio="9:16",
    duration_choices=tuple(range(4, 31)),
    default_duration=4,
    supports_audio=True,
    default_audio=True,
    supports_first_frame=True,
    supports_last_frame=True,
    max_reference_images=2,
    validate=validate_seedance25_inputs,
    reference_image_role="reference_image",
    max_reference_videos=10,
    frame_ratio="adaptive",
)


def main(argv: list[str] | None = None) -> int:
    return run_standard_model(MODEL_SPEC, argv)


if __name__ == "__main__":
    raise SystemExit(main())
