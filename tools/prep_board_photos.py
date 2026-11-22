#!/usr/bin/env python3
"""把 8 張開發板照片統一成「淺色底商品圖」：鋪白底、裁邊、縮圖、輸出 WebP。

所有圖都放在同一個淺色底上，避免深色卡片上出現突兀的白框或灰框。
輸出：~/learn-esp32-log/img/boards/<key>.webp（最長邊 640）
"""
import os
from PIL import Image

SRC = "/tmp/boards_img"
DST = os.path.expanduser("~/learn-esp32-log/img/boards")
os.makedirs(DST, exist_ok=True)

FILES = {
    "esp32": "esp32.jpg",
    "s2": "s2.png",
    "s3": "s3.png",
    "c3": "c3.png",
    "c6": "c6.png",
    "h2": "h2.png",
    "p4": "p4.png",
    "cam": "cam.jpg",
}
TILE = (246, 248, 251)   # 淺色底，與卡片內的光板一致


def flatten(im):
    im = im.convert("RGBA")
    bg = Image.new("RGBA", im.size, TILE + (255,))
    return Image.alpha_composite(bg, im).convert("RGB")


def trim(im, pad=8):
    """裁掉四周與底色相同的邊（留 8px 呼吸空間）。"""
    from PIL import ImageChops
    bg = Image.new("RGB", im.size, TILE)
    diff = ImageChops.difference(im, bg).convert("L").point(lambda v: 255 if v > 10 else 0)
    box = diff.getbbox()
    if not box:
        return im
    l, t, r, b = box
    return im.crop((max(0, l - pad), max(0, t - pad), min(im.width, r + pad), min(im.height, b + pad)))


total = 0
for key, fn in FILES.items():
    im = Image.open(os.path.join(SRC, fn))
    im = flatten(im)
    im = trim(im)
    w, h = im.size
    scale = 640 / max(w, h)
    if scale < 1:
        im = im.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)
    out = os.path.join(DST, f"{key}.webp")
    im.save(out, "WEBP", quality=88, method=6)
    kb = os.path.getsize(out) // 1024
    total += kb
    print(f"{key}: {im.size} {kb}KB")
print("total", total, "KB")
