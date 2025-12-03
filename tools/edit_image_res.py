# tools/edit_image_res.py
# --------------------------------------
# Author: Jaelin Lee
# Description: Quick utility to resize images (used for project assets).
# --------------------------------------

from PIL import Image, ImageOps

input_path = "tools/input.png"
output_path = "padded_output.png"

img = Image.open(input_path)
w, h = img.size

min_h = 600
if h < min_h:
    padding = (0, (min_h - h) // 2)  # horizontal=0, vertical=half top/bottom
    img = ImageOps.expand(img, border=(0, padding[1], 0, padding[1]), fill="white")

img.save(output_path)
print("Saved:", output_path)
