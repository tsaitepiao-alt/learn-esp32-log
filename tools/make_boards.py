#!/usr/bin/env python3
"""產生 8 款 ESP32 開發板的 SVG 示意圖（依實物比例與特徵繪製）。

輸出：/tmp/esp_boards/*.svg
每張圖包含：PCB 外形、排針、模組金屬罩與蛇形天線、USB 接頭、
按鍵、以及板上的型號絲印——這些就是實物最好辨認的特徵。
"""
import os

OUT = "/tmp/esp_boards"
os.makedirs(OUT, exist_ok=True)

SILVER = ('<linearGradient id="sh{i}" x1="0" y1="0" x2="0" y2="1">'
          '<stop offset="0" stop-color="#e8edf2"/><stop offset=".45" stop-color="#b9c4cf"/>'
          '<stop offset="1" stop-color="#8e9aa6"/></linearGradient>')
GOLD = "#d6a84a"


def pins(x, y, w, h, n, vertical=True, gap=0.0):
    """排針：沿邊緣畫 n 個金色焊點 + 針腳。"""
    out = []
    for i in range(n):
        if vertical:
            py = y + i * ((h - 6) / max(n - 1, 1))
            out.append(f'<rect x="{x}" y="{py:.1f}" width="5" height="4" rx="1" fill="{GOLD}" opacity=".9"/>')
            out.append(f'<rect x="{x - 2.5}" y="{py + 1:.1f}" width="2.5" height="2" fill="#f0d79a"/>')
        else:
            px = x + i * ((w - 6) / max(n - 1, 1))
            out.append(f'<rect x="{px:.1f}" y="{y}" width="4" height="5" rx="1" fill="{GOLD}" opacity=".9"/>')
            out.append(f'<rect x="{px + 1:.1f}" y="{y - 2.5}" width="2" height="2.5" fill="#f0d79a"/>')
    return "".join(out)


def module(cx, cy, w, h, label, idx, antenna=True):
    """模組：金屬罩 + 上方蛇形天線 + 型號字。"""
    x, y = cx - w / 2, cy - h / 2
    parts = []
    if antenna:
        ay = y - 12
        zz = " ".join(f"{x + 6 + i * 3},{ay + (4 if i % 2 else 0)}" for i in range(int((w - 12) / 3) + 1))
        parts.append(f'<polyline points="{zz}" fill="none" stroke="#c8a24a" stroke-width="1.6"/>')
        parts.append(f'<rect x="{x + 4}" y="{ay - 2}" width="{w - 8}" height="2" fill="#2a3138" opacity=".6"/>')
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2" fill="url(#sh{idx})" stroke="#7f8b97" stroke-width=".8"/>')
    # 罩上的散熱壓紋
    for i in range(3):
        yy = y + h * (0.25 + i * 0.22)
        parts.append(f'<line x1="{x + 3}" y1="{yy:.1f}" x2="{x + w - 3}" y2="{yy:.1f}" stroke="#9aa7b4" stroke-width=".6" opacity=".7"/>')
    fs = max(4.2, min(6.2, w / 7.2))
    parts.append(f'<text x="{cx}" y="{cy + fs / 3:.1f}" font-size="{fs:.1f}" fill="#3d4753" '
                 f'text-anchor="middle" font-family="ui-monospace,Menlo,monospace" font-weight="700">{label}</text>')
    return "".join(parts)


def usb(cx, y, kind="micro"):
    """USB 接頭（位於板子下緣）。"""
    if kind == "c":
        return (f'<rect x="{cx - 13}" y="{y - 9}" width="26" height="9" rx="4.5" fill="#cfd6dd" stroke="#8b96a1" stroke-width=".8"/>'
                f'<rect x="{cx - 9}" y="{y - 6}" width="18" height="3" rx="1.5" fill="#7d8894"/>')
    # micro-USB：梯形
    return (f'<path d="M{cx - 11},{y} L{cx - 8},{y - 9} L{cx + 8},{y - 9} L{cx + 11},{y} Z" fill="#cfd6dd" stroke="#8b96a1" stroke-width=".8"/>'
            f'<rect x="{cx - 7}" y="{y - 6.5}" width="14" height="2.6" rx="1.3" fill="#7d8894"/>')


def board(name, w, h, pcb, label, pins_n=15, module_w=40, module_h=48, usb_kind="micro",
          usb_count=1, buttons=True, cam=False, sd=False, header4=False, rj45=False,
          fpc=False, edge_label=True, module_label=None):
    idx = abs(hash(name)) % 999
    pad = 26
    vb_w, vb_h = w + pad * 2, h + pad * 2 + 14
    x0, y0 = pad, pad + 10

    s = [f'<svg viewBox="0 0 {vb_w} {vb_h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{label} 示意圖">']
    s.append(f'<defs>{SILVER.format(i=idx)}'
             f'<radialGradient id="gl{idx}" cx="50%" cy="0%" r="80%">'
             f'<stop offset="0" stop-color="#ffffff" stop-opacity=".10"/>'
             f'<stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient></defs>')
    # 陰影
    s.append(f'<rect x="{x0 + 2}" y="{y0 + 3}" width="{w}" height="{h}" rx="5" fill="#000" opacity=".45"/>')
    # PCB
    s.append(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="5" fill="{pcb}" stroke="#2c3540" stroke-width="1"/>')
    s.append(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="5" fill="url(#gl{idx})"/>')

    # 排針（左右兩側）
    if pins_n:
        s.append(pins(x0 + 2, y0 + 8, w, h - 12, pins_n))
        s.append(pins(x0 + w - 7, y0 + 8, w, h - 12, pins_n))

    # 模組
    mx = x0 + w / 2
    my = y0 + h * (0.30 if not cam else 0.42)
    s.append(module(mx, my, module_w, module_h, module_label or label, idx))

    # USB
    uy = y0 + h
    if usb_count == 2:
        s.append(usb(mx - 12, uy, usb_kind))
        s.append(usb(mx + 12, uy, usb_kind))
    elif usb_count == 1:
        s.append(usb(mx, uy, usb_kind))

    # 按鍵
    if buttons:
        for i, bx in enumerate((x0 + 12, x0 + 23)):
            s.append(f'<rect x="{bx}" y="{y0 + h - 20}" width="7" height="7" rx="1.6" fill="#232b34" stroke="#3b4753" stroke-width=".7"/>')

    # 相機（ESP32-CAM）
    if cam:
        cxx, cyy = x0 + w / 2, y0 + h * 0.34
        s.append(f'<rect x="{cxx - 26}" y="{cyy - 22}" width="52" height="44" rx="3" fill="#1a2430" stroke="#2f3d4c" stroke-width="1"/>')
        s.append(f'<circle cx="{cxx}" cy="{cyy}" r="15" fill="#0b0f14" stroke="#39485a" stroke-width="2"/>')
        s.append(f'<circle cx="{cxx}" cy="{cyy}" r="8.5" fill="#101b28"/>')
        s.append(f'<circle cx="{cxx - 3}" cy="{cyy - 3}" r="3" fill="#4a6a8f" opacity=".85"/>')
        s.append(f'<circle cx="{cxx}" cy="{cyy}" r="15" fill="none" stroke="#5b6f85" stroke-width=".8" opacity=".6"/>')

    # SD 卡槽
    if sd:
        s.append(f'<rect x="{x0 + w / 2 - 17}" y="{y0 + h - 26}" width="34" height="12" rx="2" fill="#9aa6b2" stroke="#6f7c89" stroke-width=".8"/>')
        s.append(f'<rect x="{x0 + w / 2 - 14}" y="{y0 + h - 23}" width="28" height="4" rx="1" fill="#5c6874"/>')

    # 2×4 排針（CAM 底部）
    if header4:
        for r in range(2):
            for c in range(4):
                s.append(f'<rect x="{x0 + 8 + c * 9}" y="{y0 + h - 12 + r * 6}" width="5" height="4" rx="1" fill="{GOLD}"/>')

    # RJ45（P4）
    if rj45:
        s.append(f'<rect x="{x0 + w - 46}" y="{y0 + h - 34}" width="36" height="28" rx="2" fill="#2b333d" stroke="#46535f" stroke-width="1"/>')
        s.append(f'<rect x="{x0 + w - 41}" y="{y0 + h - 29}" width="26" height="16" rx="1.5" fill="#151b22"/>')

    # FPC 排線座（P4）
    if fpc:
        s.append(f'<rect x="{x0 + 10}" y="{y0 + h - 12}" width="46" height="7" rx="1.5" fill="#c9a44f" opacity=".85"/>')
        s.append(f'<rect x="{x0 + 10}" y="{y0 + h - 30}" width="46" height="7" rx="1.5" fill="#c9a44f" opacity=".85"/>')

    # 板上型號絲印
    if edge_label:
        s.append(f'<text x="{x0 + w / 2}" y="{y0 + h - 6}" font-size="5.4" fill="#8f9db0" text-anchor="middle" '
                 f'font-family="ui-monospace,Menlo,monospace" letter-spacing=".4">{name.upper()}</text>')

    s.append('</svg>')
    return "".join(s)


BOARDS = {
    "esp32": dict(w=150, h=78, pcb="#101519", label="ESP32-WROOM-32", pins_n=15,
                  module_w=44, module_h=50, usb_count=1, module_label="ESP32-WROOM-32"),
    "s2": dict(w=136, h=66, pcb="#12161b", label="ESP32-S2-MINI-1", pins_n=15,
               module_w=32, module_h=34, usb_count=1, module_label="S2-MINI-1"),
    "s3": dict(w=158, h=80, pcb="#0f1418", label="ESP32-S3-WROOM-1", pins_n=22,
               module_w=44, module_h=50, usb_count=2, module_label="S3-WROOM-1"),
    "c3": dict(w=124, h=62, pcb="#12161b", label="ESP32-C3-MINI-1", pins_n=15,
               module_w=26, module_h=28, usb_count=1, module_label="C3-MINI-1"),
    "c6": dict(w=138, h=68, pcb="#0f1418", label="ESP32-C6-WROOM-1", pins_n=15,
               module_w=34, module_h=38, usb_kind="c", usb_count=1, module_label="C6-WROOM-1"),
    "h2": dict(w=118, h=60, pcb="#12161b", label="ESP32-H2-MINI-1", pins_n=15,
               module_w=24, module_h=26, usb_kind="c", usb_count=1, module_label="H2-MINI-1"),
    "cam": dict(w=96, h=128, pcb="#16324d", label="ESP32-CAM", pins_n=0,
                module_w=34, module_h=38, usb_count=0, buttons=False, cam=True, sd=True,
                header4=True, module_label="ESP32-S"),
    "p4": dict(w=196, h=112, pcb="#0f1418", label="ESP32-P4", pins_n=20,
               module_w=46, module_h=46, usb_kind="c", usb_count=1, rj45=True, fpc=True,
               module_label="ESP32-P4"),
}

for k, v in BOARDS.items():
    svg = board(k, **v)
    open(os.path.join(OUT, f"{k}.svg"), "w", encoding="utf-8").write(svg)
    print(k, len(svg))
