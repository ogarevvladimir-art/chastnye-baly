"""Д3б «в экран»: 06, 07, 08 на проверочных окнах — блок целиком от верха окна (снимок всей высоты блока).

  python tools/d3b_shots.py [--prefix before]   # → сверка/d3b/<префикс>_<блок>_<окно>.png + лист <префикс>_sheet.png
"""
import argparse

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

from _serve import SVERKA, serve, url_for
from pilot_shots import STILL, eager

WINDOWS = [(1440, 900), (1920, 950), (1366, 650), (1280, 600), (1024, 650)]
BLOCKS = [("06", "#assistant"), ("07", "#lessons"), ("08", "#etiquette")]


def shoot(browser, base, w, h, out, prefix):
    ctx = browser.new_context(viewport={"width": w, "height": h}, reduced_motion="reduce")
    page = ctx.new_page()
    page.goto(url_for(base, "site/index.html"), wait_until="networkidle")
    eager(page)
    page.add_style_tag(content=STILL)
    res = []
    for name, sel in BLOCKS:
        top, bh = page.evaluate("s => { const r = document.querySelector(s).getBoundingClientRect(); return [r.top + scrollY, r.height]; }", sel)
        shots = []
        y = 0
        while y < bh - 1:
            page.evaluate("y => scrollTo({top: y, behavior: 'instant'})", top + y)
            page.wait_for_timeout(250)
            f = out / f"{prefix}_{name}_{w}x{h}_{len(shots)}.png"
            page.screenshot(path=str(f))
            shots.append(f)
            y += h
        res.append((name, round(bh), shots))
    ctx.close()
    return res


def sheet(rows, path, col_w=360):
    font = ImageFont.truetype("arial.ttf", 20)
    pad, head = 12, 30
    cols = []
    for label, files in rows:
        ims = [Image.open(f) for f in files]
        ims = [im.resize((col_w, round(im.height * col_w / im.width))) for im in ims]
        cols.append((label, ims))
    W = pad + len(cols) * (col_w + pad)
    H = head + pad + max(sum(im.height + 4 for im in ims) for _, ims in cols) + pad
    out = Image.new("RGB", (W, H), (40, 40, 40))
    d = ImageDraw.Draw(out)
    for i, (label, ims) in enumerate(cols):
        x = pad + i * (col_w + pad)
        d.text((x, pad), label, fill=(220, 215, 205), font=font)
        y = head + pad
        for im in ims:
            out.paste(im, (x, y))
            d.line([(x, y + im.height + 1), (x + col_w, y + im.height + 1)], fill=(230, 60, 60), width=2)
            y += im.height + 4
    out.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", default="before")
    args = ap.parse_args()
    out = SVERKA / "d3b"
    out.mkdir(parents=True, exist_ok=True)
    per_block = {b: [] for b, _ in BLOCKS}
    with serve() as base, sync_playwright() as p:
        browser = p.chromium.launch()
        for w, h in WINDOWS:
            for name, bh, shots in shoot(browser, base, w, h, out, args.prefix):
                per_block[name].append((f"{name} {w}×{h} блок {bh}", shots))
                print(name, w, h, bh, len(shots))
        browser.close()
    for name, rows in per_block.items():
        sheet(rows, out / f"{args.prefix}_{name}_sheet.png")


if __name__ == "__main__":
    main()
