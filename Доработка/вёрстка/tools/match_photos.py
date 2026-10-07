"""Поиск исходника в assets/ для каждого рендера фото из Figma (_figma/v1/shots/v1_img_<hash>_<c|p>_<id>.png).

1. Выбор исходника: каждый файл assets/ кадрируется как FILL (cover по центру) под пропорцию узла,
   сравнение — нормированная корреляция яркости на миниатюре 64 px. Топ-5 кандидатов.
2. Кроп: многомасштабный поиск рендера внутри кандидата (cv2.matchTemplate), лучший по корреляции.
   Результат — прямоугольник в пикселях исходника (работает и для FILL, и для CROP).

    python match_photos.py      # → _figma/v1/match.json, _figma/v1/match_sheet.jpg
"""
import json
import re
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps

Image.MAX_IMAGE_PIXELS = None
HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
ASSETS = PROJECT / "assets" / "photos"
V1 = HERE.parent / "_figma" / "v1"
SHOTS = V1 / "shots"
WORK = 900  # рабочая ширина исходника для поиска кропа


def gray(img):
    return np.asarray(img.convert("L"), dtype=np.float32)


def ncc(a, b):
    a = a - a.mean()
    b = b - b.mean()
    d = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / d) if d else 0.0


def cover(img, ratio):
    w, h = img.size
    if w / h > ratio:
        nw = round(h * ratio)
        return img.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    nh = round(w / ratio)
    return img.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))


def load_assets():
    out = {}
    for p in sorted(ASSETS.rglob("*")):
        if p.suffix.lower() not in (".jpg", ".jpeg", ".png", ".webp"):
            continue
        im = Image.open(p)
        im = ImageOps.exif_transpose(im)
        size = im.size
        im.draft("RGB", (WORK * 2, WORK * 2))
        im = im.convert("RGB")
        work = im.resize((WORK, round(WORK * im.height / im.width)), Image.LANCZOS)
        out[p.relative_to(PROJECT).as_posix()] = {"size": size, "work": work}
    return out


def find_crop(render, work):
    """Ищет рендер внутри work на разных масштабах. Возвращает (score, x, y, w) в координатах work."""
    rg = cv2.GaussianBlur(gray(render), (0, 0), 1.2)
    wg = cv2.GaussianBlur(gray(work), (0, 0), 1.2)
    H, W = wg.shape
    rh, rw = rg.shape
    best = (-1, 0, 0, 0)
    maxw = min(W, rw * H / rh)

    def try_w(tw):
        nonlocal best
        tw = int(round(tw))
        th = int(round(tw * rh / rw))
        if tw < 24 or th < 24 or tw > W or th > H:
            return
        t = cv2.resize(rg, (tw, th), interpolation=cv2.INTER_AREA)
        res = cv2.matchTemplate(wg, t, cv2.TM_CCOEFF_NORMED)
        _, mx, _, loc = cv2.minMaxLoc(res)
        if mx > best[0]:
            best = (mx, loc[0], loc[1], tw)

    for f in np.geomspace(0.15, 1.0, 40):
        try_w(maxw * f)
    for f in np.linspace(0.96, 1.04, 17):  # уточнение
        try_w(best[3] * f)
    return best


def main():
    assets = load_assets()
    print(f"исходников: {len(assets)}")
    small = {}
    results = []
    for shot in sorted(SHOTS.glob("v1_img_*.png")):
        m = re.match(r"v1_img_([0-9a-f]{8})_([cp])_(.+)\.png", shot.name)
        h8, tone, nid = m.group(1), m.group(2), m.group(3).replace("-", ":")
        render = Image.open(shot).convert("RGB")
        ratio = render.width / render.height
        rs = gray(render.resize((64, max(8, round(64 / ratio))), Image.LANCZOS))
        scores = []
        for name, a in assets.items():
            key = (name, round(ratio, 3))
            if key not in small:
                c = cover(a["work"], ratio)
                small[key] = gray(c.resize((64, max(8, round(64 / ratio))), Image.LANCZOS))
            scores.append((ncc(rs, small[key]), name))
        scores.sort(reverse=True)
        top = scores[:5]
        # кроп ищем у трёх лучших, берём лучший по matchTemplate
        best = None
        for s, name in top[:3]:
            r = find_crop(render.resize((min(240, render.width), round(min(240, render.width) / ratio))), assets[name]["work"])
            if best is None or r[0] > best[1][0]:
                best = (name, r)
        name, (sc, x, y, tw) = best
        sw, sh = assets[name]["size"]
        k = sw / WORK
        rect = [round(x * k), round(y * k), round(tw * k), round(tw / ratio * k)]
        results.append({
            "hash": h8, "tone": tone, "node": nid, "render": [render.width, render.height],
            "src": name, "src_size": [sw, sh], "rect": rect, "score": round(sc, 3),
            "fill_top": [[round(s, 3), n] for s, n in top],
        })
        print(f"{h8} {tone} {nid:>9}  {render.width}x{render.height}  → {name}  {sw}x{sh}  "
              f"кроп {rect}  tm {sc:.3f}  fill {top[0][0]:.3f}/{top[1][0]:.3f}")
    # второй проход: у одного hash один исходник — тот, что найден с лучшей корреляцией
    # (кандидаты первого шага отбирались по пропорции окна, у кропов CROP / узких окон это промахивается)
    fixed = json.loads((V1 / "match_fixed.json").read_text(encoding="utf-8")) if (V1 / "match_fixed.json").exists() else {}
    src_of = {}
    for r in results:
        if r["hash"] not in src_of or r["score"] > src_of[r["hash"]][0]:
            src_of[r["hash"]] = (r["score"], r["src"])
    for h, name in fixed.items():  # исходник, найденный полным поиском (match_fixed.json: hash → путь)
        src_of[h] = (1, name)
    for r in results:
        name = src_of[r["hash"]][1]
        if name == r["src"] and r["score"] >= 0.9:
            continue
        render = Image.open(SHOTS / f'v1_img_{r["hash"]}_{r["tone"]}_{r["node"].replace(":", "-")}.png').convert("RGB")
        ratio = render.width / render.height
        sc, x, y, tw = find_crop(render.resize((min(240, render.width), round(min(240, render.width) / ratio))), assets[name]["work"])
        sw, sh = assets[name]["size"]
        k = sw / WORK
        r.update(src=name, src_size=[sw, sh], score=round(sc, 3),
                 rect=[round(x * k), round(y * k), round(tw * k), round(tw / ratio * k)], second_pass=True)
        print(f'  2-й проход {r["hash"]} {r["node"]} → {name} кроп {r["rect"]} tm {sc:.3f}')
    (V1 / "match.json").write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    sheet(results)


def sheet(results):
    """Контактный лист: рендер Figma | кроп исходника, по 2 пары в ряд."""
    TH = 220
    tiles = []
    for r in results:
        a = Image.open(PROJECT / r["src"])
        a = ImageOps.exif_transpose(a).convert("RGB")
        x, y, w, h = r["rect"]
        crop = a.crop((x, y, x + w, y + h))
        f = Image.open(SHOTS / f'v1_img_{r["hash"]}_{r["tone"]}_{r["node"].replace(":", "-")}.png').convert("RGB")
        fw = round(TH * f.width / f.height)
        f = f.resize((fw, TH))
        crop = crop.resize((fw, TH))
        t = Image.new("RGB", (fw * 2 + 8, TH + 22), (20, 20, 20))
        t.paste(f, (0, 22))
        t.paste(crop, (fw + 8, 22))
        from PIL import ImageDraw
        ImageDraw.Draw(t).text((4, 4), f'{r["hash"]} {r["node"]} → {Path(r["src"]).name} {r["score"]}', fill=(230, 230, 230))
        tiles.append(t)
    W = 1800
    rows, row, x = [], [], 0
    for t in tiles:
        if x + t.width > W and row:
            rows.append(row)
            row, x = [], 0
        row.append(t)
        x += t.width + 12
    rows.append(row)
    H = sum(max(t.height for t in r) + 12 for r in rows)
    out = Image.new("RGB", (W, H), (40, 40, 40))
    y = 0
    for r in rows:
        x = 0
        for t in r:
            out.paste(t, (x, y))
            x += t.width + 12
        y += max(t.height for t in r) + 12
    out.save(V1 / "match_sheet.jpg", quality=85)


if __name__ == "__main__":
    main()
