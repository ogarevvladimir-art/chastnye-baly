"""Д4: заливки Figma для заменённых снимков — кадр под пропорции каждого узла, тон слота запечён (как на сайте).

Стопку тона в узлах (снимок + серый + Greige + цвет поверхности + снимок) плагин не отдаёт с режимами наложения —
поэтому, как с фото 01 в Д3а, в узел ставится одна заливка: уже тонированный снимок (кривая слота + gain из photo_replace.json).
Узлы — состояния каталога (_figma/v1/catalog.json); размеры узлов — из выгрузки плагина (--nodes, get_nodes_info depth 0).

    python d4_figma.py --nodes <get_nodes_info.json>   # → .cache/figma_d4/<слот>-<w>x<h>.jpg + .cache/figma_d4/plan.json
"""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

from photo_tone import apply

Image.MAX_IMAGE_PIXELS = None
HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
V1 = HERE.parent / "_figma" / "v1"
OUT = HERE / ".cache" / "figma_d4"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nodes", required=True)
    args = ap.parse_args()
    nodes = {n["id"]: n for n in json.loads(Path(args.nodes).read_text(encoding="utf-8"))}
    catalog = json.loads((V1 / "catalog.json").read_text(encoding="utf-8"))
    names = {k: v for k, v in json.loads((HERE / "photos.json").read_text(encoding="utf-8")).items() if k != "_"}
    replace = {k: v for k, v in json.loads((HERE / "photo_replace.json").read_text(encoding="utf-8")).items() if k != "_"}
    OUT.mkdir(parents=True, exist_ok=True)
    plan, srcs = {}, {}
    for c in catalog:
        key = f'{names[c["hash"]]["block"]}/{names[c["hash"]]["name"]}'
        rep = replace.get(key)
        if not rep:
            continue
        if rep["src"] not in srcs:
            srcs[rep["src"]] = ImageOps.exif_transpose(Image.open(PROJECT / rep["src"])).convert("RGB")
        im = srcs[rep["src"]]
        x0, y0, W, H = rep.get("rect", [0, 0, *im.size])
        fx, fy = rep["focus"].get(c["layout"], rep["focus"]["*"])
        tone = np.load(V1 / "tone" / f'{c["hash"]}.npy')
        for s in c["states"]:
            b = nodes[s["node"]]["bounds"]
            nw, nh = round(b["width"]), round(b["height"])
            name = f'{key.replace("/", "-")}-{nw}x{nh}.jpg'
            if name not in plan:
                a = nw / nh
                w, h = (H * a, H) if W / H > a else (W, W / a)
                x, y = x0 + (W - w) * fx, y0 + (H - h) * fy
                ow = min(round(2 * nw), round(w), 2880)
                crop = im.resize((ow, round(ow / a)), Image.LANCZOS, box=(x, y, x + w, y + h))
                crop = apply(crop, tone)
                if rep.get("gain"):
                    crop = Image.fromarray(np.clip(np.asarray(crop, np.float32) * rep["gain"] + 0.5, 0, 255).astype(np.uint8))
                crop.save(OUT / name, quality=88)
                plan[name] = {"path": str(OUT / name), "nodes": []}
                print(f"{name:52} {crop.width}×{crop.height}")
            plan[name]["nodes"].append(s["node"])
    (OUT / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(plan), "файлов,", sum(len(p["nodes"]) for p in plan.values()), "узлов")


if __name__ == "__main__":
    main()
