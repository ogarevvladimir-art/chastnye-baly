"""Д3б шаг 1б: 08 «экран 2» с фото (панорама из 07) и заметным переключателем — варианты A1 (вкладки) и B1 (крупные слова).
Дерево клонов — ../_figma/d3b_08_clones.json (4 кадра: A1 Кавалерам, A1 Дамам, B1 Кавалерам, B1 Дамам).
Пишет пачки в ../_figma/d3b_ops3_<N>.json (по кадру)."""
import json
from pathlib import Path

OUT = Path(__file__).parent.parent / "_figma"
frames = json.load(open(OUT / "d3b_08_clones.json", encoding="utf-8"))

PANEL, INK, GREIGE, LIGHT, TERRA = "#c6c2b6", "#060606", "#aba79a", "#c6c2b6", "#c96a42"


def build(fr, variant, role):
    ops = []
    fid = fr["id"]
    kids = fr["children"]
    by = {c["name"]: c for c in kids}
    dam = role == "Д"

    def mv(nid, x, y):
        ops.append({"type": "move_nodes", "params": {"nodeIds": [nid], "x": x, "y": y}})

    def rs(nid, w, h):
        ops.append({"type": "resize_nodes", "params": {"nodeIds": [nid], "width": w, "height": h}})

    def text(name, s, x, y, size, color, family="Unbounded", style="Regular", upper=False, ls=2, lh=None, opacity=None):
        p = {"parentId": fid, "name": name, "text": s, "x": x, "y": y, "fontFamily": family, "fontStyle": style,
             "fontSize": size, "fillColor": color, "letterSpacingUnit": "PERCENT", "letterSpacingValue": ls,
             "textAutoResize": "WIDTH_AND_HEIGHT"}
        if upper:
            p["textCase"] = "UPPER"
        if lh:
            p.update(lineHeightUnit="PERCENT", lineHeightValue=lh)
        ops.append({"type": "create_text", "params": p})
        if opacity is not None:
            ops.append({"type": "set_opacity", "nodeIds": [f"${len(ops) - 1}.id"], "params": {"opacity": opacity}})

    def rect(name, x, y, w, h, fill=None, stroke=None):
        ops.append({"type": "create_rectangle", "params": {"parentId": fid, "name": name, "x": x, "y": y, "width": w, "height": h,
                                                            "fillColor": fill or "#060606"}})
        i = len(ops) - 1
        if not fill:
            ops.append({"type": "set_opacity", "nodeIds": [f"${i}.id"], "params": {"opacity": 1}})
            ops.append({"type": "set_fills", "nodeIds": [f"${i}.id"], "params": {"paints": []}})
        if stroke:
            ops.append({"type": "set_strokes", "nodeIds": [f"${i}.id"], "params": {"color": stroke, "strokeWeight": 1}})

    # прежний переключатель капсом 12 — убрать
    ops.append({"type": "delete_nodes", "params": {"nodeIds": [c["id"] for c in kids if c["name"].startswith(("Нав", "Зона / Нав"))]}})

    # фото — под всеми слоями
    ph = by["Фото · Бал"]
    inner = ph["children"][0]["id"]
    ops.append({"type": "reorder_nodes", "nodeIds": [ph["id"]], "params": {"order": "sendToBack"}})

    if variant == "A1":
        P0, PH = 152, 448                       # панель под вкладками 48
        ph_box = (0, 104, 656, 496)              # фото слева, вровень с вкладками и панелью
        inner_xy = (0, -230)
        F1 = 640
    else:
        P0, PH = 104, 480
        ph_box = (0, 312, 656, 272)              # фото под крупным переключателем, низом по панели
        inner_xy = (0, -330)
        F1 = 624
    mv(ph["id"], ph_box[0], ph_box[1])
    rs(ph["id"], ph_box[2], ph_box[3])
    rs(inner, 1100, 733)
    mv(inner, *inner_xy)

    # панель и правила
    for nm in ("Панель", "Зона / Панель"):
        mv(by[nm]["id"], 720, P0)
        rs(by[nm]["id"], 656, PH)
    mv(by["Счётчик"]["id"], 752, P0 + 32)
    ops.append({"type": "set_text", "params": {"nodeId": by["Счётчик"]["id"], "text": "02 / 02" if dam else "01 / 02"}})
    line0 = P0 + 88
    on, off = [], []
    for c in kids:
        nm = c["name"]
        if nm.startswith("Строка "):
            mv(c["id"], 752, line0 + (int(nm[-1]) - 1) * 56)
        elif nm.startswith("Правило"):
            mine = nm.split("·")[1].strip()[0] == role
            mv(c["id"], 752, line0 + (int(nm[-1]) - 1) * 56 + (12 if mine else 28))
            (on if mine else off).append(c["id"])
        elif nm.startswith("Номер"):
            mv(c["id"], c["bounds"]["x"], line0 + (int(nm[-1]) - 1) * 56 + 12)
        elif nm.startswith("Роль"):
            mine = (nm == "Роль · Дамам") == dam
            mv(c["id"], c["bounds"]["x"], P0 + PH - 32 - 102 + (0 if mine else 16))
            (on if mine else off).append(c["id"])
        elif nm == "+":
            top = c["bounds"]["y"] < 300
            mv(c["id"], c["bounds"]["x"], (104 if top else P0 + PH) + (c["bounds"]["y"] - (104 if top else 584)))
    ops.append({"type": "set_opacity", "nodeIds": on, "params": {"opacity": 1}})
    ops.append({"type": "set_opacity", "nodeIds": off, "params": {"opacity": 0}})

    # финал
    mv(by["Финал · строка 1"]["id"], 64, F1)
    mv(by["Финал · строка 2 (к правому краю панели)"]["id"], 637, F1 + 120)
    mv(by["Финал · продолжение капсом"]["id"], 64, F1 + 204)

    # переключатель
    if variant == "A1":
        # вкладки-закладки над панелью: активная — цвета панели и сливается с ней, неактивная — контур
        for i, (word, num, is_on) in enumerate((("Кавалерам", "01", not dam), ("Дамам", "02", dam))):
            x = 720 + i * 328
            if is_on:
                rect(f"Вкладка · {word} · активна", x, 104, 328, 48, fill=PANEL)
            else:
                rect(f"Вкладка · {word}", x + 0.5, 104.5, 327, 47.5, stroke="#aba79a66")
            col = INK if is_on else LIGHT
            text(f"Вкладка · {word} · текст", word, x + 24, 118, 16, col, upper=True)
            text(f"Вкладка · {word} · номер", num, x + 328 - 24 - 24, 120, 12, col, ls=62)
    else:
        # крупные слова антиквой слева: активное — Greige Light и линия Terracotta, неактивное — 40 %
        for word, num, y, w, is_on in (("Кавалерам", "01", 104, 313, not dam), ("Дамам", "02", 200, 194, dam)):
            text(f"Переключатель · {word}", word, 64, y, 72, LIGHT if is_on else GREIGE, family="Old Standard TT",
                 ls=-5, lh=80, opacity=None if is_on else 0.4)
            text(f"Переключатель · {word} · номер", num, 400, y + 8, 11, LIGHT if is_on else GREIGE, ls=40,
                 opacity=None if is_on else 0.4)
            if is_on:
                rect(f"Переключатель · {word} · линия", 64, y + 70, w, 2, fill=TERRA)
    return ops


SPEC = [("A1", "К"), ("A1", "Д"), ("B1", "К"), ("B1", "Д")]
for n, (fr, (v, r)) in enumerate(zip(frames, SPEC), 1):
    ops = build(fr, v, r)
    json.dump(ops, open(OUT / f"d3b_ops3_{n}.json", "w", encoding="utf-8"), ensure_ascii=False)
    print(n, fr["name"], len(ops))
