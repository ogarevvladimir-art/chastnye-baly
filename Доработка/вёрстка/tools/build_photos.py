"""Мастера фото для сайта: кроп исходника по каталогу → тон «фото с цветом» запекается → PNG в tools/.cache/masters/.
Пишет манифест images.json для images.mjs (sharp: AVIF / WebP / JPEG по ширинам) и сводку photos_site.json для вёрстки.

Решения этапа 1 (2026-10-02): тон запекается в файлы; тон везде как на 1440 (и там, где кадры 390 / 834 стоят сырыми);
кропы без чужих логотипов — photo_overrides.json; апскейла нет.
Д4 (2026-10-05): замены снимков — photo_replace.json (новый исходник и точка фокуса; кадр, тон слота и правило ширин — из каталога).

    python build_photos.py            # мастера + images.json + photos_site.json
    node images.mjs                   # файлы в site/img/
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

from photo_tone import apply

Image.MAX_IMAGE_PIXELS = None
HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
V1 = HERE.parent / "_figma" / "v1"
MASTERS = HERE / ".cache" / "masters"
# плотности под раскладку: телефон до 3×, планшет до 2×, десктоп 1× / 1,5× (окно 1920 = 1,33 кадра 1440) / 2×
DENSITIES = {"m": [1, 2, 3], "t": [1, 2], "d": [1, 1.5, 2]}
MEDIA = {"m": "(max-width: 599px)", "t": "(min-width: 600px) and (max-width: 1023px)", "d": "(min-width: 1024px)"}


# Снимки, снятые с сайта (Ц3, решения 2026-10-27): блок («lessons» — панорама 07 убрана), снимок («evening/hall» — «Зал сверху»
# нового 02 нет) или раскладка блока («evening:t» — планшет нового 02 берёт десктопные кропы 5 : 6)
RETIRED = {"lessons", "evening/hall", "evening:t"}


def retired(meta, layout):
    b = meta["block"]
    return b in RETIRED or f'{b}/{meta["name"]}' in RETIRED or f"{b}:{layout}" in RETIRED


def replaced(c, rep):
    """Новый исходник для слота: cover кадра раскладки по точке фокуса (в области rect, если задана) → (src, rect)."""
    fw, fh = c["frame"]
    focus = rep["focus"].get(c["layout"], rep["focus"]["*"])
    with Image.open(PROJECT / rep["src"]) as im:
        W, H = ImageOps.exif_transpose(im).size if im.getexif().get(274, 1) in (5, 6, 7, 8) else im.size
    x0, y0, W, H = rep.get("rect", [0, 0, W, H])
    w, h = (H * fw / fh, H) if W / H > fw / fh else (W, W * fh / fw)
    return rep["src"], [round(x0 + (W - w) * focus[0]), round(y0 + (H - h) * focus[1]), round(w), round(h)]


def main():
    catalog = json.loads((V1 / "catalog.json").read_text(encoding="utf-8"))
    names = {k: v for k, v in json.loads((HERE / "photos.json").read_text(encoding="utf-8")).items() if k != "_"}
    MASTERS.mkdir(parents=True, exist_ok=True)
    manifest, site, flags = [], {}, []
    replace = {k: v for k, v in json.loads((HERE / "photo_replace.json").read_text(encoding="utf-8")).items() if k != "_"}
    by_src = {}
    for c in catalog:
        if retired(names[c["hash"]], c["layout"]):
            continue
        rep = replace.get(f'{names[c["hash"]]["block"]}/{names[c["hash"]]["name"]}')
        if rep:
            c = {**c, "override": "Д4: замена снимка (photo_replace.json)"}
            c["src"], c["rect"] = replaced(c, rep)
            c["gain"] = rep.get("gain")
        by_src.setdefault(c["src"], []).append(c)
    for src, items in by_src.items():
        im = ImageOps.exif_transpose(Image.open(PROJECT / src)).convert("RGB")
        for c in items:
            meta = names[c["hash"]]
            fw, fh = c["frame"]
            x, y, w, h = c["rect"]
            avail = w / fw  # пикселей исходника на CSS-пиксель
            widths = []
            for k in DENSITIES[c["layout"]]:
                if avail >= k * 0.98:
                    widths.append(round(fw * k))
                else:
                    top = int(w)  # самый крупный файл — во всю ширину кропа исходника
                    if not widths or top > widths[-1] * 1.15:
                        widths.append(top)
                    flags.append(f'{meta["block"]}/{meta["name"]}-{c["layout"]}: нужно {k}× ({round(fw * k)} px), '
                                 f'в исходнике {avail:.2f}× ({int(w)} px)')
                    break
            mw = max(widths)
            mh = round(mw * fh / fw)
            crop = im.resize((mw, mh), Image.LANCZOS, box=(x, y, x + w, y + h))
            crop = apply(crop, np.load(V1 / "tone" / f'{c["hash"]}.npy'))
            if c.get("gain"):
                crop = Image.fromarray(np.clip(np.asarray(crop, np.float32) * c["gain"] + 0.5, 0, 255).astype(np.uint8))
            master = MASTERS / f'{meta["block"]}-{meta["name"]}-{c["layout"]}.png'
            crop.save(master)
            manifest.append({"block": meta["block"], "name": meta["name"], "media": c["layout"],
                             "src": master.relative_to(PROJECT).as_posix(), "frame": [fw, fh], "widths": widths})
            site.setdefault(f'{meta["block"]}/{meta["name"]}', {"label": meta["label"], "src": src, "layouts": {}})
            site[f'{meta["block"]}/{meta["name"]}']["layouts"][c["layout"]] = {
                "media": MEDIA[c["layout"]], "frame": [fw, fh], "widths": widths,
                "rest_window": c["rest_window"], "rest_in_frame": c["rest_in_frame"],
                "figma_node": c["rest_node"], "override": c.get("override"),
            }
            print(f'{master.name:40} {mw}×{mh}  ширины {widths}')
    # Фото, добавленные в доработке без кадра каталога (01 «Подготовка», Д3а): nk-05, кроп 2 : 1 по центру,
    # тон Ink — среднее кривых трёх фото 03 «Музыка» (тот же Ink-блок; кривые Ink-фото почти совпадают)
    prep = ImageOps.exif_transpose(Image.open(PROJECT / "assets/photos/nk-05.jpg")).convert("RGB")
    pw, ph = prep.size
    prep = prep.crop((0, (ph - pw // 2) // 2, pw, (ph - pw // 2) // 2 + pw // 2)).resize((2880, 1440), Image.LANCZOS)
    music = [h for h, m in names.items() if m["block"] == "music"]
    toned = np.mean([np.asarray(apply(prep, np.load(V1 / "tone" / f"{h}.npy")), dtype=np.float32) for h in music], 0)
    Image.fromarray(np.clip(toned + 0.5, 0, 255).astype(np.uint8)).save(MASTERS / "prep-hall-d.png")
    manifest.append({"block": "prep", "name": "hall", "media": "d", "src": "Доработка/вёрстка/tools/.cache/masters/prep-hall-d.png",
                     "frame": [1440, 720], "widths": [1440, 2160, 2880]})
    manifest.extend(etiquette_ladies(catalog, names, replace))
    (HERE / "images.json").write_text(json.dumps({"images": manifest}, ensure_ascii=False, indent=1), encoding="utf-8")
    (HERE / "photos_site.json").write_text(json.dumps(site, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nмастеров {len(manifest)}; мало исходника — {len(flags)}:")
    print("\n".join("  " + f for f in flags))


def etiquette_ladies(catalog, names, replace):
    """Фото «Дамам» десктопа 08 (Ц2, 2026-10-23): увеличенный кусок «корпоративных» «Форматов» (×1,5 к файлу formats/corporate-d).
    Кадр 800 × 600 = половина «Дамам» x 0…800, y 300…900 кадра 392:2940 (запас 80 справа — половина шире 720u на узких окнах).
    В файле 971 × 959 это x 259…791,8, y 319,8…719,4: окно Figma 720 × 340 найдено в corporate-d-1942 поиском по шаблону
    (масштаб 1,332, совпадение 0,97). Кроп — из исходника, тон и gain — как у formats/corporate d.
    Телефон и планшет берут тот же увеличенный ряд гостей (окна Figma 392:3450 / 392:3501 найдены в том же файле: масштаб 2,352 и 1,868 к corporate-d-1942, совпадение 0,94 и 0,93), а не кропы «Форматов»."""
    c = next(c for c in catalog if names[c["hash"]]["block"] == "formats" and names[c["hash"]]["name"] == "corporate"
             and c["layout"] == "d")
    rep = replace.get("formats/corporate")
    src, (x, y, w, h) = replaced(c, rep) if rep else (c["src"], c["rect"])
    k = w / 971  # пикселей исходника на пиксель файла 971
    im = ImageOps.exif_transpose(Image.open(PROJECT / src)).convert("RGB")
    gain = (rep or {}).get("gain")
    entries = []
    # слоты: (слот, кадр w, кадр h, box в файле 971 × 959: x0, y0, x1, y1)
    for layout, fw, fh, bx0, by0, bx1, by1 in (
        ("d", 800, 600, 259, 319.8, 791.8, 719.4),
        ("t", 770, 520, 126, 429.5, 845.2, 915.2),
        ("m", 358, 448, 274.5, 383.5, 695.5, 910.3),
    ):
        box = (x + bx0 * k, y + by0 * k, x + bx1 * k, y + by1 * k)
        bw = int(box[2] - box[0])
        avail = (box[2] - box[0]) / fw
        widths = [round(fw * d) for d in DENSITIES[layout] if avail >= d * 0.98]
        if avail < DENSITIES[layout][-1] * 0.98 and bw > widths[-1] * 1.15:
            widths.append(bw)
        mw = max(widths)
        crop = im.resize((mw, round(mw * fh / fw)), Image.LANCZOS, box=box)
        crop = apply(crop, np.load(V1 / "tone" / f'{c["hash"]}.npy'))
        if gain:
            crop = Image.fromarray(np.clip(np.asarray(crop, np.float32) * gain + 0.5, 0, 255).astype(np.uint8))
        crop.save(MASTERS / f"etiquette-ladies-{layout}.png")
        print(f"etiquette-ladies-{layout}.png  {mw}  ширины {widths}  (исходника {avail:.2f}×)")
        entries.append({"block": "etiquette", "name": "ladies", "media": layout,
                        "src": f"Доработка/вёрстка/tools/.cache/masters/etiquette-ladies-{layout}.png",
                        "frame": [fw, fh], "widths": widths})
    return entries


if __name__ == "__main__":
    main()
