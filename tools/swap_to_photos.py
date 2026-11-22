#!/usr/bin/env python3
"""把 boards.html 的 SVG 示意圖換成實體照片（img/boards/*.webp）。"""
import re
import os

P = os.path.expanduser("~/learn-esp32-log/boards.html")
s = open(P, encoding="utf-8").read()

ALTS = {
    "esp32": "ESP32 DevKit V1（ESP32-WROOM-32）開發板實物",
    "s2": "ESP32-S2-DevKitM-1 開發板實物",
    "s3": "ESP32-S3-DevKitC-1 開發板實物",
    "c3": "ESP32-C3-DevKitM-1 開發板實物",
    "c6": "ESP32-C6-DevKitC-1 開發板實物",
    "h2": "ESP32-H2-DevKitM-1 開發板實物",
    "cam": "ESP32-CAM（含 OV2640 鏡頭）實物",
    "p4": "ESP32-P4-Function-EV-Board 實物",
}

count = 0
for key, alt in ALTS.items():
    # 在該卡片內，把 <div class="top"> 之後的 <svg ...>...</svg> 換成照片
    pat = re.compile(r'(<article class="card" id="' + key + r'".*?<div class="top">\s*)<svg.*?</svg>', re.S)
    def repl(m):
        return (m.group(1).replace('<div class="top">', '') +
                f'<div class="shot"><img src="img/boards/{key}.webp" alt="{alt}" loading="lazy"></div>\n    <div class="top">')
    s2, n = pat.subn(repl, s, count=1)
    if n:
        s = s2
        count += 1
    else:
        print("MISS", key)

# CSS：照片區
css_anchor = "/* ---------- 卡片 ---------- */"
css_add = """/* ---------- 板卡照片 ---------- */
.shot{
  background:linear-gradient(180deg,#f7f9fc 0%,#e7ecf3 100%);
  border-radius:12px; height:196px; margin-bottom:14px;
  display:flex; align-items:center; justify-content:center;
  padding:12px; overflow:hidden;
  box-shadow:inset 0 0 0 1px rgba(255,255,255,.6);
}
.shot img{
  max-width:100%; max-height:100%; width:auto; height:auto;
  object-fit:contain;
  filter:drop-shadow(0 8px 14px rgba(10,16,24,.22));
}
"""
if css_anchor in s and ".shot{" not in s:
    s = s.replace(css_anchor, css_add + css_anchor, 1)

# 頁尾：圖片來源與授權
old_foot = "本頁為中文整理版本，版面與文字為自行編寫，未使用原影片素材。"
new_foot = ("本頁為中文整理版本，版面與文字為自行編寫，未使用原影片素材。<br>\n"
            "圖片來源：ESP32-DevKitC／S2／S3／C3／C6／H2／P4 為 "
            '<a href="https://docs.espressif.com/projects/esp-dev-kits/" target="_blank" rel="noopener">Espressif 官方開發板文件</a>之產品圖；'
            'ESP32 與 ESP32-CAM 實物照來自 '
            '<a href="https://commons.wikimedia.org/wiki/File:ESP32.jpg" target="_blank" rel="noopener">Wikimedia Commons</a>'
            '（作者 Edwiyanto／Nowforever，CC BY-SA 4.0）。')
if old_foot in s:
    s = s.replace(old_foot, new_foot, 1)

open(P, "w", encoding="utf-8").write(s)
print("replaced", count, "cards")
