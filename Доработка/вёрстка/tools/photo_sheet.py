"""Контактный лист кропов фото: по строке на фото, кадры 390 | 834 | 1440 в тоне (кривая из photo_tone.py).

На кадре 1440 рамкой показано окно покоя, если файл шире (объединение окон состояний).
Флаги: плотность исходника ниже нужной (телефон 3×, планшет 2×, десктоп 2×) — красным.

    python photo_sheet.py                    # → сверка/фото/v1_kontakt_<n>.jpg
    python photo_sheet.py --raw 3734ed94 …   # + сырой кадр рядом (без тона) для указанных фото
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

from photo_tone import apply

Image.MAX_IMAGE_PIXELS = None
HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
V1 = HERE.parent / "_figma" / "v1"
OUT = HERE.parent / "сверка" / "фото"
NEED = {"m": 3, "t": 2, "d": 2}
TH = 260
FONT = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 15)
FONT_B = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 17)

_src_cache = {}


def source(rel):
    if rel not in _src_cache:
        _src_cache.clear()
        _src_cache[rel] = ImageOps.exif_transpose(Image.open(PROJECT / rel)).convert("RGB")
    return _src_cache[rel]


def tile(c, raw=False):
    x, y, w, h = c["rect"]
    fw, fh = c["frame"]
    tw = round(TH * fw / fh)
    im = source(c["src"]).resize((tw, TH), Image.LANCZOS, box=(x, y, x + w, y + h))
    if not raw:
        im = apply(im, np.load(V1 / "tone" / f'{c["hash"]}.npy'))
    d = ImageDraw.Draw(im)
    if c["layout"] == "d" and c["rest_in_frame"] and c["rest_in_frame"] != [0, 0, fw, fh]:
        k = TH / fh
        rx, ry, rw, rh = [v * k for v in c["rest_in_frame"]]
        d.rectangle([rx, ry, rx + rw - 1, ry + rh - 1], outline=(255, 210, 0), width=2)
    return im


def main():
    raw_for = set(sys.argv[sys.argv.index("--raw") + 1:]) if "--raw" in sys.argv else set()
    catalog = json.loads((V1 / "catalog.json").read_text(encoding="utf-8"))
    names = json.loads((HERE / "photos.json").read_text(encoding="utf-8"))
    by = {(c["hash"], c["layout"]): c for c in catalog}
    order = [h for h in names if h != "_"]
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for h in order:
        meta = names[h]
        items = []
        for lay, title in (("m", "390"), ("t", "834"), ("d", "1440")):
            c = by.get((h, lay))
            if not c:
                continue
            items.append((f"{title} · {c['frame'][0]}×{c['frame'][1]}", c, tile(c)))
            if h in raw_for and lay in "mt":
                items.append((f"{title} в Figma: без тона", c, tile(c, raw=True)))
        W = sum(t.width for *_, t in items) + 16 * (len(items) - 1)
        row = Image.new("RGB", (max(W, 900), TH + 76), (24, 24, 24))
        d = ImageDraw.Draw(row)
        src = Path(by[(h, items[0][1]["layout"])]["src"]).name
        d.text((0, 4), f'{meta["label"]}  —  {meta["block"]}/{meta["name"]}  ·  {src}', font=FONT_B, fill=(235, 230, 220))
        x = 0
        for cap, c, t in items:
            row.paste(t, (x, 30))
            dens = c["density"]
            weak = dens < NEED[c["layout"]]
            d.text((x, TH + 34), cap, font=FONT, fill=(170, 165, 155))
            d.text((x, TH + 52), f"исх {dens:.2f}×" + (f" < {NEED[c['layout']]}×" if weak else ""), font=FONT,
                   fill=(255, 110, 90) if weak else (170, 165, 155))
            x += t.width + 16
        rows.append(row)
    # листы по ~7 строк
    page, n = [], 1
    for i, r in enumerate(rows + [None]):
        if r is not None:
            page.append(r)
        if (len(page) == 7 or r is None) and page:
            W = max(p.width for p in page)
            sheet = Image.new("RGB", (W + 32, sum(p.height + 24 for p in page) + 16), (40, 40, 40))
            y = 16
            for p in page:
                sheet.paste(p, (16, y))
                y += p.height + 24
            path = OUT / f"v1_kontakt_{n}.jpg"
            sheet.save(path, quality=86)
            print(path.relative_to(HERE.parent))
            page, n = [], n + 1




def overrides_sheet():
    """Лист «как в Figma | без логотипа» для фото с поправкой кропа (photo_overrides.json)."""
    catalog = json.loads((V1 / "catalog.json").read_text(encoding="utf-8"))
    names = json.loads((HERE / "photos.json").read_text(encoding="utf-8"))
    rows = []
    for c in catalog:
        if not c.get("figma_rect"):
            continue
        a = tile(dict(c, rect=c["figma_rect"]))
        b = tile(c)
        row = Image.new("RGB", (max(a.width + b.width + 16, 700), TH + 76), (24, 24, 24))
        d = ImageDraw.Draw(row)
        lay = {"m": "390", "t": "834", "d": "1440"}[c["layout"]]
        d.text((0, 4), f'{names[c["hash"]]["label"]} · {lay}', font=FONT_B, fill=(235, 230, 220))
        row.paste(a, (0, 30))
        row.paste(b, (a.width + 16, 30))
        d.text((0, TH + 34), "как в Figma", font=FONT, fill=(170, 165, 155))
        d.text((a.width + 16, TH + 34), f"без логотипа · исх {c['density']:.2f}×", font=FONT, fill=(170, 165, 155))
        rows.append(row)
    W = max(r.width for r in rows)
    sheet = Image.new("RGB", (W + 32, sum(r.height + 24 for r in rows) + 16), (40, 40, 40))
    y = 16
    for r in rows:
        sheet.paste(r, (16, y))
        y += r.height + 24
    sheet.save(OUT / "v1_logotipy.jpg", quality=86)
    print((OUT / "v1_logotipy.jpg").relative_to(HERE.parent))


if __name__ == "__main__":
    overrides_sheet() if "--overrides" in sys.argv else main()
