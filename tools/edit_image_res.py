# tools/edit_image_res.py
# --------------------------------------
# Author: Jaelin Lee
# Description: Resize/pad an image to ensure at least 640x360 resolution.
# --------------------------------------
from pathlib import Path
from PIL import Image, ImageOps

INPUT_PATH = Path("app/img/drift_over_tick.png")
OUTPUT_PATH = Path("padded_output.png")
MIN_W, MIN_H = 640, 360  # baseline minimum size
EXTRA_W_PAD = 300  # add a bit more horizontal breathing room


def ensure_min_resolution(img: Image.Image, min_w: int, min_h: int) -> Image.Image:
    """Upscale proportionally and pad to hit minimum width/height, with extra width."""
    # Proportional upscale if below minimums
    w, h = img.size
    scale = max(min_w / w, min_h / h, 1.0)
    if scale > 1.0:
        new_size = (int(w * scale), int(h * scale))
        img = img.resize(new_size, Image.LANCZOS)

    # Pad to meet minimums
    w, h = img.size
    pad_left = max((min_w - w) // 2, 0)
    pad_right = max(min_w - w - pad_left, 0)
    pad_top = max((min_h - h) // 2, 0)
    pad_bottom = max(min_h - h - pad_top, 0)

    if pad_left or pad_right or pad_top or pad_bottom:
        img = ImageOps.expand(
            img, border=(pad_left, pad_top, pad_right, pad_bottom), fill="white"
        )

    # extra horizontal padding
    if EXTRA_W_PAD > 0:
        img = ImageOps.expand(
            img,
            border=(EXTRA_W_PAD // 2, 0, EXTRA_W_PAD - EXTRA_W_PAD // 2, 0),
            fill="white",
        )
    return img


def main():
    img = Image.open(INPUT_PATH)
    img = ensure_min_resolution(img, MIN_W, MIN_H)
    img.save(OUTPUT_PATH)
    print(f"Saved: {OUTPUT_PATH} ({img.size[0]}x{img.size[1]})")


if __name__ == "__main__":
    main()
