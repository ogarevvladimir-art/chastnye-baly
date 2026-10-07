"""Д2 «в экран»: «Форматы» на проверочных окнах — покой и два наведения, верх блока у верха окна.

  python tools/d2_shots.py                 # → сверка/d2/<префикс>_<окно>_<состояние>.png + лист <префикс>_sheet.png
  python tools/d2_shots.py --prefix after

Окна — видимая область браузера: 1440×900, 1920×950 (экран 1920×1080), 1366×650 (1366×768), 1280×600 (1280×720), 1024×650 (1024×768).
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

from _serve import SVERKA, serve, url_for
from pilot_shots import STILL, eager

WINDOWS = [(1440, 900), (1920, 950), (1366, 650), (1280, 600), (1024, 650)]
STATES = [("rest", None), ("private", 0.25), ("corporate", 0.75)]


def shoot(browser, base, w, h, out, prefix):
    ctx = browser.new_context(viewport={"width": w, "height": h}, reduced_motion="reduce")
    page = ctx.new_page()
    page.goto(url_for(base, "site/index.html"), wait_until="networkidle")
    eager(page)
    page.add_style_tag(content=STILL)
    top = page.evaluate("document.querySelector('#formats').getBoundingClientRect().top + scrollY")
    page.evaluate("y => scrollTo({top: y, behavior: 'instant'})", top)
    page.wait_for_timeout(300)
    files = []
    for name, fx in STATES:
        page.mouse.move(w * fx if fx else w / 2, h * 0.7 if fx else 2)
        if not fx:
            page.evaluate("document.querySelector('#formats').dispatchEvent(new PointerEvent('pointerleave', {pointerType: 'mouse'}))")
        page.wait_for_timeout(250)
        f = out / f"{prefix}_{w}x{h}_{name}.png"
        page.screenshot(path=str(f))
        files.append(f)
    info = page.evaluate("""() => { const s = document.querySelector('#formats').getBoundingClientRect();
        return {h: Math.round(s.height)}; }""")
    ctx.close()
    return files, info


def sheet(rows, path, col_w=640):
    font = ImageFont.truetype("arial.ttf", 22)
    thumbs = []
    for label, files in rows:
        ims = [Image.open(f) for f in files]
        ims = [im.resize((col_w, round(im.height * col_w / im.width))) for im in ims]
        thumbs.append((label, ims))
    pad, head = 16, 34
    W = pad + len(STATES) * (col_w + pad)
    H = sum(head + max(im.height for im in ims) + pad for _, ims in thumbs) + pad
    out = Image.new("RGB", (W, H), (40, 40, 40))
    d = ImageDraw.Draw(out)
    y = pad
    for label, ims in thumbs:
        d.text((pad, y), label, fill=(220, 215, 205), font=font)
        y += head
        for i, im in enumerate(ims):
            out.paste(im, (pad + i * (col_w + pad), y))
        y += max(im.height for im in ims) + pad
    out.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", default="before")
    args = ap.parse_args()
    out = SVERKA / "d2"
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    with serve() as base, sync_playwright() as p:
        browser = p.chromium.launch()
        for w, h in WINDOWS:
            files, info = shoot(browser, base, w, h, out, args.prefix)
            rows.append((f"{w}×{h} — блок {info['h']} px", files))
            print(w, h, info)
        browser.close()
    sheet(rows, out / f"{args.prefix}_sheet.png")
    print(out / f"{args.prefix}_sheet.png")


if __name__ == "__main__":
    main()
