#!/usr/bin/env python3
"""Create a transparent PNG from matching black- and white-background renders."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def clamp_byte(value: float) -> int:
    return max(0, min(255, int(round(value))))


def alpha_from_pair(black: Image.Image, white: Image.Image, threshold: int) -> Image.Image:
    black_rgba = black.convert("RGBA")
    white_rgba = white.convert("RGBA")
    if black_rgba.size != white_rgba.size:
        raise ValueError(f"image sizes differ: black={black_rgba.size}, white={white_rgba.size}")

    out = Image.new("RGBA", black_rgba.size, (0, 0, 0, 0))
    bp = black_rgba.load()
    wp = white_rgba.load()
    op = out.load()

    for y in range(black_rgba.height):
        for x in range(black_rgba.width):
            br, bg, bb, ba = bp[x, y]
            wr, wg, wb, wa = wp[x, y]

            # In a black/white matte pair:
            # black = alpha * color
            # white = alpha * color + (1 - alpha) * white
            bg_leak = ((wr - br) + (wg - bg) + (wb - bb)) / 3.0
            alpha = clamp_byte(255.0 - bg_leak)
            alpha = min(alpha, ba, wa)

            if alpha <= threshold:
                op[x, y] = (0, 0, 0, 0)
                continue

            scale = 255.0 / alpha
            op[x, y] = (
                clamp_byte(br * scale),
                clamp_byte(bg * scale),
                clamp_byte(bb * scale),
                alpha,
            )

    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--black", required=True, help="Render on a flat #000000 background.")
    parser.add_argument("--white", required=True, help="Render on a flat #ffffff background.")
    parser.add_argument("--output", required=True, help="Transparent PNG output path.")
    parser.add_argument("--mask-out", help="Optional alpha mask preview path.")
    parser.add_argument("--threshold", type=int, default=2, help="Alpha values at or below this become fully transparent.")
    args = parser.parse_args()

    black_path = Path(args.black).expanduser().resolve()
    white_path = Path(args.white).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()

    with Image.open(black_path) as black, Image.open(white_path) as white:
        result = alpha_from_pair(black, white, args.threshold)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.save(output_path)

    if args.mask_out:
        mask_path = Path(args.mask_out).expanduser().resolve()
        mask_path.parent.mkdir(parents=True, exist_ok=True)
        result.getchannel("A").save(mask_path)

    print(f"wrote {output_path}")


if __name__ == "__main__":
    main()
