"""Каталог фото макета: все IMAGE-заливки из выгрузок get_node / get_nodes_info (_figma/v1/tree_*.json).

Для каждого узла с картинкой — корень (страница / состояние), секция, абсолютная рамка узла,
видимое окно (пересечение с рамками предков, у которых clipsContent или просто рамка фрейма),
стопка заливок (фото с цветом или простое фото), hash.

    python figma_images.py            # → _figma/v1/images.json + сводка в консоль
    python figma_images.py -v         # + строка на каждый узел с фото
"""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
V1 = HERE.parent / "_figma" / "v1"
TREES = ["tree_1440.json", "tree_390_834.json", "tree_states.json"]


def load(name):
    data = json.loads((V1 / name).read_text(encoding="utf-8"))
    return data if isinstance(data, list) else [data]


def inter(a, b):
    x0, y0 = max(a[0], b[0]), max(a[1], b[1])
    x1, y1 = min(a[0] + a[2], b[0] + b[2]), min(a[1] + a[3], b[1] + b[3])
    return [x0, y0, max(0, x1 - x0), max(0, y1 - y0)]


def walk(node, ox, oy, clip, path, out, root):
    b = node.get("bounds") or {}
    x, y = ox + b.get("x", 0), oy + b.get("y", 0)
    w, h = b.get("width", 0), b.get("height", 0)
    box = [x, y, w, h]
    fills = (node.get("styles") or {}).get("fills") or []
    imgs = [f for f in fills if isinstance(f, dict) and f.get("type") == "IMAGE"]
    if imgs:
        win = inter(box, clip) if clip else box
        out.append({
            "root": root,
            "section": path[1] if len(path) > 1 else path[0],
            "path": " / ".join(path[1:] + [node.get("name", "")]),
            "id": node["id"],
            "type": node.get("type"),
            "box": [round(v, 1) for v in box],
            "window": [round(v, 1) for v in win],
            "hash": imgs[0]["imageHash"],
            "scaleMode": imgs[0].get("scaleMode"),
            "stack": ["IMG" if isinstance(f, dict) and f.get("type") == "IMAGE" else
                      (f if isinstance(f, str) else f.get("type")) for f in fills],
            "opacity": node.get("opacity", 1),
            "visible": node.get("visible", True),
        })
    # фреймы режут детей (в макете у секций и рамок фото clipsContent включён — проверяется рендером)
    child_clip = clip
    if node.get("type") in ("FRAME", "INSTANCE", "COMPONENT") and path:
        child_clip = inter(box, clip) if clip else box
    for ch in node.get("children") or []:
        walk(ch, x, y, child_clip, path + [node.get("name", "")], out, root)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-v", "--verbose", action="store_true", help="print one line per node with a photo")
    args = ap.parse_args()
    out = []
    for t in TREES:
        for r in load(t):
            root = f'{r["id"]} {r.get("name", "")}'
            # корень — в своих координатах (0, 0)
            r = dict(r, bounds=dict(r["bounds"], x=0, y=0))
            walk(r, 0, 0, None, [], out, root)
    dst = V1 / "images.json"
    dst.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    hashes = {}
    for o in out:
        hashes.setdefault(o["hash"], []).append(o)
    print(f"узлов с фото: {len(out)}, разных картинок: {len(hashes)}")
    if not args.verbose:
        print(f"{len(out)} nodes written to {dst}")
        return
    for o in out:
        st = "цвет" if len(o["stack"]) > 1 else "фото"
        print(f'{o["root"][:28]:28} | {o["section"][:30]:30} | {o["id"]:>12} | {o["hash"][:8]} | {st} | '
              f'окно {o["window"][2]:.0f}×{o["window"][3]:.0f} @ {o["window"][0]:.0f},{o["window"][1]:.0f} | '
              f'узел {o["box"][2]:.0f}×{o["box"][3]:.0f} | {o["path"][-60:]}')


if __name__ == "__main__":
    main()
