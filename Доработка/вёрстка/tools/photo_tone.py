"""Тон «фото с цветом»: кривая RGB → RGB (многочлен 3-й степени) по паре «кроп исходника | рендер Figma».

Тот же приём, что в Доработка/фото-тон/ (W_terra, W05_ash, W06_slate, W10_ink): тон либо задан стопкой
заливок в Figma, либо уже запечён в загруженный файл. Здесь кривая подбирается на каждое фото отдельно
по рендеру узла и кропу из match.json; на сайт тон запекается в файлы (images.mjs берёт готовый JPEG-мастер).

    python photo_tone.py                 # подгонка по всем фото → _figma/v1/tone/<hash>.npy + отчёт
    python photo_tone.py --sheet         # + лист «исходник | Figma | наш тон»
"""
import json
import sys
from itertools import combinations_with_replacement as cwr
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps, ImageDraw

Image.MAX_IMAGE_PIXELS = None
HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
V1 = HERE.parent / "_figma" / "v1"
TONE = V1 / "tone"


def feats(x, deg=3):
    cols = [np.ones(len(x))]
    for d in range(1, deg + 1):
        for c in cwr(range(3), d):
            cols.append(np.prod(x[:, list(c)], axis=1))
    return np.stack(cols, 1)


def apply(im, W):
    a = np.asarray(im.convert("RGB"), np.float64) / 255
    flat = a.reshape(-1, 3)
    out = np.empty_like(flat)
    for i in range(0, len(flat), 400000):
        out[i:i + 400000] = feats(flat[i:i + 400000]) @ W
    return Image.fromarray((np.clip(out.reshape(a.shape), 0, 1) * 255 + 0.5).astype(np.uint8))


def source(rel):
    return ImageOps.exif_transpose(Image.open(PROJECT / rel)).convert("RGB")


def pair(m, size=None):
    """Кроп исходника по rect, приведённый к размеру рендера, и сам рендер."""
    r = Image.open(V1 / "shots" / f'v1_img_{m["hash"]}_{m["tone"]}_{m["node"].replace(":", "-")}.png').convert("RGB")
    if size:
        r = r.resize(size, Image.LANCZOS)
    x, y, w, h = m["rect"]
    src = source(m["src"])
    box = (max(0, x), max(0, y), min(src.width, x + w), min(src.height, y + h))
    s = src.resize(r.size, Image.LANCZOS, box=box)
    return s, r


def best_per_hash(matches):
    """Лучший рендер на фото; для тона предпочитаем тонированный (стопка «c»), если он надёжно найден."""
    best = {}
    for m in matches:
        key = (m["tone"] == "c" and m["score"] >= 0.9, m["score"])
        if m["hash"] not in best or key > best[m["hash"]][0]:
            best[m["hash"]] = (key, m)
    return {h: v[1] for h, v in best.items()}


def main():
    TONE.mkdir(exist_ok=True)
    matches = json.loads((V1 / "match.json").read_text(encoding="utf-8"))
    best = best_per_hash(matches)
    rng = np.random.default_rng(0)
    report = {}
    for h, m in best.items():
        w = min(480, m["render"][0])
        s, r = pair(m, (w, round(w * m["render"][1] / m["render"][0])))
        a = np.asarray(s, np.float64).reshape(-1, 3) / 255
        b = np.asarray(r, np.float64).reshape(-1, 3) / 255
        raw = np.abs(a - b).mean() * 255
        i = rng.choice(len(a), min(150000, len(a)), replace=False)
        W = np.linalg.lstsq(feats(a[i]), b[i], rcond=None)[0]
        err = np.abs(feats(a) @ W - b) * 255
        np.save(TONE / f"{h}.npy", W)
        report[h] = {"node": m["node"], "src": m["src"], "score": m["score"], "raw_diff": round(float(raw), 1),
                     "fit_mean": round(float(err.mean()), 2), "fit_p95": round(float(np.percentile(err, 95)), 1),
                     "toned": bool(raw > 6)}
        print(f'{h} {m["node"]:>9} {Path(m["src"]).name:38} tm {m["score"]:.3f}  сырой Δ {raw:5.1f}  '
              f'кривая Δ {err.mean():4.2f} (p95 {np.percentile(err, 95):4.1f})  {"тон" if raw > 6 else "без тона"}')
    (TONE / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    if "--sheet" in sys.argv:
        sheet(best)


def sheet(best):
    TH = 200
    tiles = []
    for h, m in best.items():
        W = np.load(TONE / f"{h}.npy")
        fw = round(TH * m["render"][0] / m["render"][1])
        s, r = pair(m, (fw, TH))
        t = Image.new("RGB", (fw * 3 + 16, TH + 20), (20, 20, 20))
        for k, im in enumerate((s, r, apply(s, W))):
            t.paste(im, (k * (fw + 8), 20))
        ImageDraw.Draw(t).text((4, 4), f"{h} {Path(m['src']).name}: исходник | Figma | кривая", fill=(230, 230, 230))
        tiles.append(t)
    Wd = 1800
    rows, row, x = [], [], 0
    for t in tiles:
        if x + t.width > Wd and row:
            rows.append(row)
            row, x = [], 0
        row.append(t)
        x += t.width + 12
    rows.append(row)
    out = Image.new("RGB", (Wd, sum(max(t.height for t in r) + 12 for r in rows)), (40, 40, 40))
    y = 0
    for r in rows:
        x = 0
        for t in r:
            out.paste(t, (x, y))
            x += t.width + 12
        y += max(t.height for t in r) + 12
    out.save(V1 / "tone_sheet.jpg", quality=85)


if __name__ == "__main__":
    main()
