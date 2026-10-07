"""Каталог фото для сайта: фото × раскладка (m 390 / t 834 / d 1440) → окно на экране и кроп в пикселях исходника.

Вход: _figma/v1/images.json (figma_images.py), match.json (match_photos.py).
- Узел раскладки — тот, у которого видимое окно больше всего (покой или кадр состояния той же ширины).
- FILL: cover по центру узла → окно внутри узла → прямоугольник исходника.
- CROP (кроп вручную в Figma): прямоугольник берётся из найденного рендера (рендер = окно узла).
- Проверка: где есть рендер узла, геометрия FILL сравнивается с найденным прямоугольником.

    python photo_catalog.py       # → _figma/v1/catalog.json + таблица
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
V1 = HERE.parent / "_figma" / "v1"
LOGO = "244cbb7b"

# корни состояний → раскладка (у кадров состояний ширина корня не всегда равна ширине макета)
# Фото, которые в Figma загружены уже обрезанными (Доработка/фото-тон/): область исходника, которую видит Figma.
# 10 — tone10.py jobs2 / obj (640×800), 05 — tone05_zanaves2.py (fill 2400×1500, фокус по вертикали),
# 02 «05» IMG_4988 — по рендеру: высота 569 с y 30, по ширине исходник целиком.
PRECROP = {
    "57f56af0": [340, 0, 640, 800], "953b6aad": [510, 0, 640, 800], "5d6e8392": [280, 0, 640, 800],
    "6d40c111": [240, 0, 640, 800], "2a2892c5": [136, 0, 640, 800], "c65adc72": [280, 0, 640, 800],
    "6805c40d": [280, 0, 640, 800], "e019e4b4": [280, 0, 640, 800],
    "563f43eb": [0, 866, 1706, 1066], "81dba541": [0, 11, 1280, 800],
    "041cc7a1": [0, 30, 945, 569],
}

_ov = json.loads((Path(__file__).resolve().parent / "photo_overrides.json").read_text(encoding="utf-8"))
OVERRIDES = {k: v for k, v in _ov.items() if k != "_"}

LAYOUT_BY_ROOT = {"191:626": "d", "258:4034": "m", "258:4531": "t",
                  "242:2122": "m", "242:2154": "m", "252:1368": "m",
                  "256:3092": "t", "256:3126": "t", "256:3860": "t"}


def layout(root_id):
    return LAYOUT_BY_ROOT.get(root_id, "d")


def fill_rect(box, win, src, pre=None):
    """Окно win (абс. координаты) узла box при FILL → прямоугольник в исходнике src (w, h).
    pre — область исходника, загруженная в Figma (если файл в Figma уже обрезан)."""
    px, py, sw, sh = pre or [0, 0, src[0], src[1]]
    bx, by, bw, bh = box
    s = max(bw / sw, bh / sh)  # cover
    ox = (sw * s - bw) / 2
    oy = (sh * s - bh) / 2
    x0 = (win[0] - bx + ox) / s
    y0 = (win[1] - by + oy) / s
    return [round(px + x0), round(py + y0), round(win[2] / s), round(win[3] / s)]


def render_rect(m, n):
    """Прямоугольник исходника для окна узла n по найденному рендеру m (рендер = окно или весь узел)."""
    win, box = n["window"], n["box"]
    r = m["rect"]
    rw, rh = m["render"]
    if abs(rw / rh - win[2] / max(win[3], 1)) < 0.02:
        return r
    k = r[2] / box[2]
    return [round(r[0] + (win[0] - box[0]) * k), round(r[1] + (win[1] - box[1]) * k),
            round(win[2] * k), round(win[3] * k)]


def main():
    nodes = json.loads((V1 / "images.json").read_text(encoding="utf-8"))
    matches = json.loads((V1 / "match.json").read_text(encoding="utf-8"))
    src_of = {m["hash"]: (m["src"], m["src_size"]) for m in matches}
    by_node = {m["node"]: m for m in matches}

    node_by_id = {n["id"]: n for n in nodes}
    main_roots = ("191:626", "258:4034", "258:4531")

    def window(n, lay):
        # карусель 03 на телефоне и планшете: окно урезано прокруткой ленты — рамка = карточка целиком
        if lay in "mt" and "03 Музыка" in n["path"]:
            return n["box"]
        return n["window"]

    def same_geometry(o, n, win):
        return (o["box"][2:] == n["box"][2:] and o["window"][2:] == win[2:]
                and [o["window"][i] - o["box"][i] for i in (0, 1)] == [win[i] - n["box"][i] for i in (0, 1)])

    def src_rect(n, h, lay, size):
        """Прямоугольник исходника для окна узла: FILL — геометрия, CROP — найденный рендер той же геометрии."""
        win = window(n, lay)
        if n["scaleMode"] == "FILL":
            return fill_rect(n["box"], win, size, PRECROP.get(h)), "FILL" + (" от кропа фото-тон" if h in PRECROP else "")
        for m in matches:
            o = node_by_id.get(m["node"])
            if m["hash"] == h and o and m["score"] >= 0.9 and same_geometry(o, n, win):
                return render_rect(m, o), f'{n["scaleMode"]} по рендеру {m["node"]}'
        return None, f'{n["scaleMode"]} — нужен рендер узла'

    # сверка геометрии: все узлы фото, у которых есть надёжный рендер
    checks = {}
    for m in matches:
        n = node_by_id.get(m["node"])
        if not n or m["score"] < 0.9 or n["scaleMode"] != "FILL" or n["window"][2] < 60:
            continue
        g = fill_rect(n["box"], n["window"], m["src_size"], PRECROP.get(m["hash"]))
        mr = render_rect(m, n)
        checks.setdefault(m["hash"], []).append((round(max(abs(a - b) for a, b in zip(g, mr)) / max(g[2], 1), 3), m["node"]))

    groups = {}
    for n in nodes:
        h = n["hash"][:8]
        if h != LOGO:
            groups.setdefault((h, layout(n["root"].split()[0])), []).append(n)

    catalog = []
    for (h, lay), group in sorted(groups.items()):
        src, size = src_of[h]
        rest = max((n for n in group if n["root"].split()[0] in main_roots),
                   key=lambda n: window(n, lay)[2] * window(n, lay)[3], default=None)
        parts = []  # (узел, окно, прямоугольник исходника, способ)
        for n in group:
            win = window(n, lay)
            if win[2] < 1 or win[3] < 1:
                continue
            r, how = src_rect(n, h, lay, size)
            if r:
                parts.append((n, win, r, how))
        if not parts:
            continue
        x0 = min(r[0] for _, _, r, _ in parts)
        y0 = min(r[1] for _, _, r, _ in parts)
        x1 = max(r[0] + r[2] for _, _, r, _ in parts)
        y1 = max(r[1] + r[3] for _, _, r, _ in parts)
        # пикселей исходника на CSS-пиксель; max — по незумленному окну (наведение scale ≤ 8 % делает CSS)
        dens = max(r[2] / w[2] for _, w, r, _ in parts)
        over = max(-x0, -y0, x1 - size[0], y1 - size[1])
        if over > 3:
            print(f"!! {h} {lay}: кроп выходит за исходник на {over} px")
        x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, size[0]), min(y1, size[1])
        union = [x0, y0, x1 - x0, y1 - y0]
        frame = [round(union[2] / dens), round(union[3] / dens)]
        rest_part = next((p for p in parts if p[0] is rest), None)
        rest_in = None
        if rest_part:
            r = rest_part[2]
            rest_in = [round((r[0] - x0) / dens), round((r[1] - y0) / dens), round(r[2] / dens), round(r[3] / dens)]
        override = OVERRIDES.get(h, {}).get(lay)
        figma_rect = None
        if override:
            figma_rect, union = union, override["rect"]
            dens = union[2] / frame[0]
        catalog.append({
            "hash": h, "layout": lay, "figma_rect": figma_rect, "override": override and override["why"], "src": src, "src_size": size, "precrop": PRECROP.get(h),
            "rect": union, "frame": frame, "density": round(dens, 2),
            "rest_node": rest["id"] if rest else None, "rest_path": rest["path"] if rest else None,
            "rest_window": [round(v) for v in window(rest, lay)] if rest else None, "rest_in_frame": rest_in,
            "states": [{"node": n["id"], "root": n["root"].split()[0], "window": [round(v) for v in w], "rect": r, "how": how}
                       for n, w, r, how in parts],
            "how": sorted({how for *_, how in parts}),
        })
    worst = {h: max(c) for h, c in checks.items()}
    for c in catalog:
        c["check"] = worst.get(c["hash"])
    (V1 / "catalog.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=1), encoding="utf-8")
    for c in catalog:
        same = c["rest_in_frame"] and c["rest_in_frame"][2:] == c["frame"] and c["rest_in_frame"][:2] == [0, 0]
        print(f'{c["hash"]} {c["layout"]} кадр {c["frame"][0]:>4}×{c["frame"][1]:<4} {Path(c["src"]).name[:28]:28} '
              f'кроп {c["rect"]}  исх/px {c["density"]:5.2f}  '
              f'{"" if same else "покой " + str(c["rest_in_frame"])}  {"; ".join(c["how"])}'
              f'  {"" if c["check"] is None else "Δ %.1f%%" % (c["check"][0] * 100)}')


if __name__ == "__main__":
    main()
