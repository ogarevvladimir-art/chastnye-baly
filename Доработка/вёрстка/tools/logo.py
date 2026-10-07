"""Логотип Plyaskin Events: векторизация растрового PNG (potracer — Python-порт potrace) и производные.

Исходник — единственная версия знака: Прототип/assets/plyaskin-events-logo.png (1716 × 738, RGBA, один цвет).
Альфа увеличивается в 4 раза (бикубически), сглаживается (σ 3 px) и режется по 50 %: так потрейс не ловит ступеньки
сглаживания. Подбор — рендером Chromium против оригинала: 491 сегмент, средняя разница 0,27 / 255.
У potracer заливка — False, поэтому маска инвертирована.

    python logo.py          # → site/logo/*.svg, site/favicon.*, apple-touch-icon.png + сверка/логотип/
"""
import io
from pathlib import Path

import numpy as np
import potrace
from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
SRC = PROJECT / "Прототип" / "assets" / "plyaskin-events-logo.png"
SITE = PROJECT / "site"
CHECK = HERE.parent / "сверка" / "логотип"
UP = 4
COLORS = {"light": "#aba79a", "dark": "#060606"}  # над тёмным — Greige 100, над светлым — Ink


def fmt(v):
    s = f"{v:.1f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def pair(x, y):
    a, b = fmt(x), fmt(y)
    return a + ("" if b.startswith("-") else " ") + b


def trace():
    im = Image.open(SRC).convert("RGBA")
    a = im.getchannel("A").resize((im.width * UP, im.height * UP), Image.BICUBIC).filter(ImageFilter.GaussianBlur(3))
    bm = potrace.Bitmap(np.asarray(a) <= 127)
    path = bm.trace(turdsize=8 * UP, turnpolicy=potrace.POTRACE_TURNPOLICY_MINORITY,
                    alphamax=0.9, opticurve=True, opttolerance=0.8)
    # относительные команды: короче и сжимается лучше; точка отсчёта копится в округлённых значениях
    curves = []
    for curve in path:
        d = []
        pts = []
        cx, cy = round(curve.start_point.x / UP, 1), round(curve.start_point.y / UP, 1)
        pts.append((cx, cy))
        d.append(f"M{pair(cx, cy)}")
        for seg in curve.segments:
            if seg.is_corner:
                for q in (seg.c, seg.end_point):
                    x, y = round(q.x / UP, 1), round(q.y / UP, 1)
                    d.append(f"l{pair(x - cx, y - cy)}")
                    cx, cy = x, y
                    pts.append((x, y))
            else:
                c1 = (round(seg.c1.x / UP, 1), round(seg.c1.y / UP, 1))
                c2 = (round(seg.c2.x / UP, 1), round(seg.c2.y / UP, 1))
                e = (round(seg.end_point.x / UP, 1), round(seg.end_point.y / UP, 1))
                d.append("c" + " ".join(pair(px - cx, py - cy) for px, py in (c1, c2, e)))
                cx, cy = e
                pts += [c1, c2, e]
        d.append("z")
        xs, ys = [q[0] for q in pts], [q[1] for q in pts]
        curves.append(("".join(d), (min(xs), min(ys), max(xs), max(ys))))
    return im.size, curves


def bbox_of(size):
    a = np.asarray(Image.open(SRC).getchannel("A")) > 127
    ys, xs = np.where(a)
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def svg(viewbox, d, fill):
    x, y, w, h = viewbox
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x} {y} {w} {h}" role="img" aria-label="Plyaskin Events">'
            f'<path fill="{fill}" fill-rule="evenodd" d="{d}"/></svg>\n')


def render(svg_text, w, h, bg=None):
    """Рендер SVG в Chromium (Playwright) → PIL RGBA."""
    from playwright.sync_api import sync_playwright
    body = f'<html><body style="margin:0;background:{bg or "transparent"}">{svg_text}</body></html>'
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        page = b.new_page(viewport={"width": w, "height": h})
        page.set_content(body)
        png = page.screenshot(clip={"x": 0, "y": 0, "width": w, "height": h}, omit_background=bg is None)
        b.close()
    return Image.open(io.BytesIO(png)).convert("RGBA")


def sized(svg_text, w, h):
    return svg_text.replace("<svg ", f'<svg width="{w}" height="{h}" ', 1)


def mark_svg(curves, size=32, pad=0.16, bg="#060606", fg="#aba79a", rx=0):
    """Знак «P» из первой строки логотипа на квадрате: favicon, apple-touch."""
    p = [c for c in curves if c[1][2] < 265 and c[1][3] < 340]
    x0 = min(c[1][0] for c in p); y0 = min(c[1][1] for c in p)
    x1 = max(c[1][2] for c in p); y1 = max(c[1][3] for c in p)
    side = max(x1 - x0, y1 - y0) / (1 - 2 * pad)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    vb = f"{fmt(cx - side / 2)} {fmt(cy - side / 2)} {fmt(side)} {fmt(side)}"
    rect = f'<rect x="{fmt(cx - side / 2)}" y="{fmt(cy - side / 2)}" width="{fmt(side)}" height="{fmt(side)}" rx="{fmt(side * rx)}" fill="{bg}"/>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">{rect}'
            f'<path fill="{fg}" fill-rule="evenodd" d="{"".join(c[0] for c in p)}"/></svg>\n')


def main():
    size, curves = trace()
    d = "".join(c[0] for c in curves)
    x0, y0, x1, y1 = (int(v) for v in bbox_of(size))
    vb = (x0, y0, x1 - x0, y1 - y0)
    (SITE / "logo").mkdir(parents=True, exist_ok=True)
    for name, color in COLORS.items():
        (SITE / "logo" / f"logo-{name}.svg").write_text(svg(vb, d, color), encoding="utf-8")
    # для вставки в шапку inline: цвет от currentColor (смена «над светлым» — CSS-переходом)
    (SITE / "logo" / "logo.svg").write_text(svg(vb, d, "currentColor"), encoding="utf-8")
    print("viewBox", vb, "| контуров", len(curves), "|",
          {f.name: f.stat().st_size for f in (SITE / "logo").glob("*.svg")})

    # favicon: SVG (знак P), ICO 16 + 32 + 48, apple-touch 180 (без прозрачности, углы скругляет iOS)
    fav = mark_svg(curves)
    (SITE / "favicon.svg").write_text(fav, encoding="utf-8")
    icons = [render(sized(fav, s, s), s, s) for s in (16, 32, 48)]
    icons[-1].save(SITE / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)], append_images=icons[:-1])
    touch = mark_svg(curves, pad=0.22)
    render(sized(touch, 180, 180), 180, 180).convert("RGB").save(SITE / "apple-touch-icon.png", optimize=True)
    print("favicon.svg", (SITE / "favicon.svg").stat().st_size, "| favicon.ico", (SITE / "favicon.ico").stat().st_size,
          "| apple-touch-icon.png", (SITE / "apple-touch-icon.png").stat().st_size)

    sheet(vb, d, fav, touch)


def sheet(vb, d, fav, touch):
    """Сверка: оригинал PNG и SVG при 2× шапки (94 × 36) и подвала (135 × 52), крупно, оба цвета, значки."""
    CHECK.mkdir(parents=True, exist_ok=True)
    orig = Image.open(SRC).convert("RGBA")
    a = np.asarray(orig.getchannel("A"))
    ys, xs = np.where(a > 127)
    orig = orig.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))

    def png_tint(w, h, color):
        im = orig.resize((w, h), Image.LANCZOS)
        c = Image.new("RGBA", im.size, color)
        c.putalpha(im.getchannel("A"))
        return c

    rows = []
    for (w, title) in ((188, "шапка 94 × 36 при 2×"), (270, "подвал 135 × 52 при 2×"), (900, "крупно")):
        h = round(w * vb[3] / vb[2])
        for name, color, bg in (("light", COLORS["light"], "#060606"), ("dark", COLORS["dark"], "#c6c2b6")):
            sv = render(sized(svg(vb, d, color), w, h), w, h)
            row = Image.new("RGB", (w * 2 + 60, h + 40), bg)
            row.paste(png_tint(w, h, color), (20, 30), png_tint(w, h, color))
            row.paste(sv, (w + 40, 30), sv)
            from PIL import ImageDraw, ImageFont
            f = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 13)
            ImageDraw.Draw(row).text((20, 8), f"{title} · {name}: PNG (оригинал) | SVG", font=f,
                                     fill=(200, 196, 186) if name == "light" else (40, 40, 40))
            rows.append(row)
    icons = [render(sized(fav, s, s), s, s) for s in (16, 32, 64)] + [render(sized(touch, 180, 180), 180, 180)]
    row = Image.new("RGB", (600, 220), (90, 90, 90))
    x = 20
    for ic in icons:
        row.paste(ic, (x, 20), ic)
        x += ic.width + 30
    rows.append(row)
    W = max(r.width for r in rows)
    out = Image.new("RGB", (W + 40, sum(r.height + 16 for r in rows) + 24), (50, 50, 50))
    y = 20
    for r in rows:
        out.paste(r, (20, y))
        y += r.height + 16
    out.save(CHECK / "v1_logo_sravnenie.png")
    print((CHECK / "v1_logo_sravnenie.png").relative_to(HERE.parent))


if __name__ == "__main__":
    main()
