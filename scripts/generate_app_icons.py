#!/usr/bin/env python3
"""Generate native Windows (.ico), macOS (.icns), and PNG app icons from Startup Antigravity branding.

Tries `cairosvg` to rasterize `assets/logo.svg` first; falls back to an exact high-DPI
Pillow vector-style renderer matching `assets/logo.svg` (zero native Cairo DLLs needed on Windows).
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SVG_PATH = ROOT / "assets" / "logo.svg"


def _render_master_png(size: int = 1024):
    from PIL import Image, ImageDraw  # type: ignore

    # Try cairosvg first if available
    try:
        import cairosvg  # type: ignore

        png_bytes = cairosvg.svg2png(url=str(SVG_PATH), output_width=size, output_height=size)
        return Image.open(io.BytesIO(png_bytes)).convert("RGBA")
    except Exception:
        pass

    # Pure-Pillow high-DPI fallback matching assets/logo.svg (viewBox 0..256)
    scale = size / 256.0
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    def s(v: float) -> float:
        return v * scale

    # Rounded badge (#0F172A fill, #334155 border)
    draw.rounded_rectangle(
        [s(24), s(24), s(232), s(232)],
        radius=s(44),
        fill=(15, 23, 42, 255),
        outline=(51, 65, 85, 255),
        width=max(2, int(s(4))),
    )

    # Orbit ring (#334155)
    cx, cy, r = s(128), s(134), s(62)
    draw.ellipse(
        [cx - r, cy - r, cx + r, cy + r],
        outline=(51, 65, 85, 255),
        width=max(2, int(s(5))),
    )

    # Ascending geometric launch delta (#10B981)
    delta = [
        (s(128), s(54)),
        (s(178), s(176)),
        (s(128), s(148)),
        (s(78), s(176)),
    ]
    draw.polygon(delta, fill=(16, 185, 129, 255))

    # Inner ethical core diamond (#0F172A)
    diamond = [
        (s(128), s(100)),
        (s(144), s(126)),
        (s(128), s(140)),
        (s(112), s(126)),
    ]
    draw.polygon(diamond, fill=(15, 23, 42, 255))

    # Revenue velocity spark (#F59E0B)
    sx, sy, sr = s(182), s(74), s(8)
    draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(245, 158, 11, 255))

    return img


def generate_icons(out_dir: Path) -> dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    master = _render_master_png(1024)

    png_path = out_dir / "startup-antigravity.png"
    ico_path = out_dir / "startup-antigravity.ico"
    icns_path = out_dir / "startup-antigravity.icns"

    master.save(png_path, format="PNG")
    master.save(
        ico_path,
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    master.save(icns_path, format="ICNS")

    return {
        "png": str(png_path),
        "ico": str(ico_path),
        "icns": str(icns_path),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate .png, .ico, and .icns app icons.")
    parser.add_argument("--out-dir", default=str(ROOT / "dist" / "icons"))
    args = parser.parse_args(argv)
    paths = generate_icons(Path(args.out_dir))
    print(json.dumps(paths, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
