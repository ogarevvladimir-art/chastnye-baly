"""Ц2: новый 08 «Этикет» на проверочных окнах страницы «Окна» — секция «Д3б · выбранное …» (328:3071).
На каждое окно — клон покоя 392:2940 («Ц2 · 08 · покой · W×H») и клон финала 392:2958 («Ц2 · 08 · финал · W×H»);
генератор пересчитывает их по правилам сайта (blocks.css, блок «08 Этикет (Ц2)», десктоп):

  u = (W − 128) / 1312, s = min(u, H / 900), половина = W / 2;
  покой: метка и интро на 104 (интро — 64 от шва, колонка min(416, половина − 128)), гигант 200s на 104 + 72s;
  «номер · для кого» на R = 104 + 328s («для кого» — +64u), правила на R + 40; окно фото — от T = R + 76 + 52s до низа
  (76 — высота «номер + правила» на сайте на всех пяти окнах, 2026-10-23); «Поле» половины — 0…T;
  фото привязаны к шву, верх окна = y 260 файла: «Кавалерам» — прямоугольник 720 × 960 (файл x 143…863) правым краем на шве,
  на 1024 он уже половины — масштаб g = max(u, половина / 720); «Дамам» — 1080 × 1440 от x −200u, y T − 260s − 480u;
  «Тон» — 960s от T − 260s; финал: высота 640s, строка 1 на 157s, строка 2 на 295s от X(400), капс 330 от оси на 447s.

  python c2_windows_gen.py ../_figma/c2_win_tree.json   # → ../_figma/c2_win_<N>.json (пачки ≤ 90 операций)

Дерево — get_nodes_info десяти клонов (полная глубина); координаты детей — от родителя (у детей группы «Фраза» — от кадра).
"""
import json
import re
import sys
from pathlib import Path

OUT = Path(__file__).parent.parent / "_figma"
WINS = [(1440, 900), (1920, 950), (1366, 650), (1280, 600), (1024, 650)]
WHO_H = 76

tree = json.load(open(sys.argv[1], encoding="utf-8"))
frames = {f["name"]: f for f in tree}


def kids(n):
    out = {}
    for c in n.get("children", []):
        out[c["name"]] = c
        if c["type"] == "GROUP":
            out.update(kids(c))
    return out


def ops_for(W, H):
    u = (W - 128) / 1312
    s = min(u, H / 900)
    half = W / 2
    R = 104 + 328 * s
    T = R + WHO_H + 52 * s
    col = min(416, half - 128)
    ops = []

    def mv(n, x, y):
        ops.append({"type": "move_nodes", "params": {"nodeIds": [n["id"]], "x": round(x, 1), "y": round(y, 1)}})

    def rs(n, w, h):
        ops.append({"type": "resize_nodes", "params": {"nodeIds": [n["id"]], "width": round(w, 1), "height": round(max(h, 1), 1)}})

    def fs(n, size):
        st = n.get("styles", {})
        if "mixed" in (st.get("fontFamily"), st.get("fontStyle")):
            ops.append({"type": "set_text_range", "params": {"nodeId": n["id"], "startOffset": 0,
                        "endOffset": len(n["characters"]), "fontSize": round(size, 1)}})
        else:
            ops.append({"type": "set_text", "params": {"nodeId": n["id"], "fontSize": round(size, 1)}})

    def tw(n, w):
        rs(n, w, n["bounds"]["height"])
        ops.append({"type": "set_text", "params": {"nodeId": n["id"], "textAutoResize": "HEIGHT"}})

    # ---------- покой ----------
    fr = frames[f"Ц2 · 08 · покой · {W}×{H}"]
    k = kids(fr)
    rs(fr, W, H)
    for name, x in (("Половина / Кавалерам", 0), ("Половина / Дамам", half)):
        hf = k[name]
        hk = kids(hf)
        mv(hf, x, 0)
        rs(hf, half, H)
        rs(hk["Поле"], half, T)
        mv(hk["Поле"], 0, 0)
        rs(hk["Тон"], half, 960 * s)
        mv(hk["Тон"], 0, T - 260 * s)
        if name.endswith("Кавалерам"):
            g = max(u, half / 720)
            rs(hk["Фото"], 720 * g, 960 * g)
            mv(hk["Фото"], half - 720 * g, T - 260 * s)
        else:
            rs(hk["Фото"], 1080 * u, 1440 * u)
            mv(hk["Фото"], -200 * u, T - 260 * s - 480 * u)
    mv(k["Метка"], 64, 104)
    fs(k["Гигант · Этикет"], 200 * s)
    mv(k["Гигант · Этикет"], 64, 104 + 72 * s)
    intro = k["Капс · фрагмент 1 · интро"]
    tw(intro, col)
    mv(intro, half + 64, 104)
    mv(k["Номер 01"], 64, R)
    mv(k["Для кого 01"], 64 + 64 * u, R)
    mv(k["Номер 02"], half + 64, R)
    mv(k["Для кого 02"], half + 64 + 64 * u, R)
    for name, x in (("Капс · фрагмент 2 · Кавалерам", 64), ("Капс · фрагмент 3 · Дамам", half + 64)):
        tw(k[name], col)
        mv(k[name], x, R + 40)

    # ---------- финал ----------
    fr = frames[f"Ц2 · 08 · финал · {W}×{H}"]
    k = kids(fr)
    rs(fr, W, round(640 * s))
    l1, l2, cont = k["Фраза · строка 1"], k["Фраза · строка 2"], k["Капс · финал"]
    fs(l1, 150 * s)
    fs(l2, 150 * s)
    mv(l1, 64, 157 * s)
    mv(l2, 64 + 336 * u, 295 * s)
    mv(cont, 64 + 656 * u, 447 * s)
    print(f"{W}×{H}: u {u:.3f}, s {s:.3f}, R {R:.1f}, T {T:.1f}, окно фото {H - T:.0f}, финал {round(640 * s)}")
    return ops


def shifted(ops, off):
    txt = json.dumps(ops, ensure_ascii=False)
    txt = re.sub(r'"\$(\d+)\.id"', lambda m: f'"${int(m.group(1)) + off}.id"', txt)
    return json.loads(txt)


n, batch = 0, []
for W, H in WINS:
    fo = ops_for(W, H)
    if batch and len(batch) + len(fo) > 90:
        n += 1
        json.dump(batch, open(OUT / f"c2_win_{n}.json", "w", encoding="utf-8"), ensure_ascii=False)
        print("пачка", n, len(batch))
        batch = []
    batch += shifted(fo, len(batch))
n += 1
json.dump(batch, open(OUT / f"c2_win_{n}.json", "w", encoding="utf-8"), ensure_ascii=False)
print("пачка", n, len(batch))
