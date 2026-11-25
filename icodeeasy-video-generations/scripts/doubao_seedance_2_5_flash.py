#!/usr/bin/env python3
"""Create or run a Seedance 2.5 Flash video generation task."""

from __future__ import annotations

from dataclasses import replace

from _video_common import run_standard_model, validate_seedance25_flash_inputs
from doubao_seedance_2_5 import MODEL_SPEC as SEEDANCE_25_SPEC


MODEL_SPEC = replace(
    SEEDANCE_25_SPEC,
    canonical_id="doubao-seedance-2-5-flash",
    max_reference_videos=5,
    validate=validate_seedance25_flash_inputs,
)


def main(argv: list[str] | None = None) -> int:
    return run_standard_model(MODEL_SPEC, argv)


if __name__ == "__main__":
    raise SystemExit(main())
