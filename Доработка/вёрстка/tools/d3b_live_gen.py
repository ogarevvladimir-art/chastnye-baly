"""Д3б шаг 3: утверждённое (06 A, 07 один экран, 08 A1) — в действующий макет «Главная · v2 · фото с цветом» (191:626) и кадры состояний.
Координаты — утверждённые кадры 1440×900 (секции 328:2278 / 328:3071), id узлов сохраняются (перенос, а не замена).
Читает ../_figma/d3b_live_tree.json, пишет пачки ../_figma/d3b_live_<N>.json.

  06: 198:1168 (покой 01), 198:1206 (02), 198:1241 (03) — 900;
  07: 198:1288 — 900, панорама «Фото · Бал» уходит в 08;
  08: 207:1958 (Кавалерам), 207:2000 (Дамам) — 1800: экран 1 — шапка и интро, экран 2 (+900) — вкладки, фото, панель 656 × 448, финал.
"""
import json
from pathlib import Path

OUT = Path(__file__).parent.parent / "_figma"
tree = {f["id"]: f for f in json.load(open(OUT / "d3b_live_tree.json", encoding="utf-8"))}
batches = []


def kids(fid):
    return {c["name"]: c for c in tree[fid]["children"]}


def mv(ops, nid, x, y):
    ops.append({"type": "move_nodes", "params": {"nodeIds": [nid], "x": round(x, 1), "y": round(y, 1)}})


def rs(ops, nid, w, h):
    ops.append({"type": "resize_nodes", "params": {"nodeIds": [nid], "width": round(w, 1), "height": round(h, 1)}})


def header(ops, k, lead=None, intro_shift=False):
    mv(ops, k["Метка"]["id"], 64, 104)
    h2 = sorted([n for nm, n in k.items() if nm.startswith("Заголовок")], key=lambda n: n["bounds"]["y"])
    mv(ops, h2[0]["id"], h2[0]["bounds"]["x"], 160)
    mv(ops, h2[1]["id"], h2[1]["bounds"]["x"], 280)
    if lead:
        mv(ops, k["Лид"]["id"], *lead)


# ---------- 06: одним экраном ----------
for fid in ("198:1168", "198:1206", "198:1241"):
    ops = []
    k = kids(fid)
    rs(ops, fid, 1440, 900)
    header(ops, k, (960, 176))
    y = 440
    for nm, h in (("Строка 01", 112), ("Строка 02", 136), ("Строка 03", 136)):
        mv(ops, k[nm]["id"], 512, y)
        rs(ops, k[nm]["id"], 416, h)
        y += h
    for nm in ("Ответ 01", "Ответ 02", "Ответ 03"):
        mv(ops, k[nm]["id"], 960, 440 + (k[nm]["bounds"]["y"] - 640))
    mv(ops, k["Принцип"]["id"], 960, 770)
    mv(ops, k["Линия"]["id"], 960, 746)
    for nm in ("Кадр 01 Стесняетесь", "Кадр 02 Не умеете танцевать", "Кадр 03 Пришли без пары"):
        fr = k[nm]
        mv(ops, fr["id"], 0, 440)
        rs(ops, fr["id"], 448, 460)
        inner = fr["children"][0]
        mv(ops, inner["id"], inner["bounds"]["x"], inner["bounds"]["y"] - 50)
    pass  # имя кадра не меняем: на него могут опираться инструменты прошлых этапов
    batches.append(ops)

# ---------- 08: два экрана, A1 ----------
# источники вкладок и фото — утверждённые кадры A1: 328:2848 (Кавалерам), 328:2894 (Дамам)
TABS = {"207:1958": ["328:3049", "328:3050", "328:3051", "328:3052", "328:3053", "328:3054"],
        "207:2000": ["328:3055", "328:3056", "328:3057", "328:3058", "328:3059", "328:3060"]}
PHOTO = {"207:1958": "328:2892", "207:2000": "328:2938"}
O = 900
for fid, role in (("207:1958", "К"), ("207:2000", "Д")):
    ops = []
    k = kids(fid)
    lst = tree[fid]["children"]
    rs(ops, fid, 1440, 1800)
    header(ops, k)
    for n in lst:
        if n["name"].startswith("Интро"):
            mv(ops, n["id"], n["bounds"]["x"], n["bounds"]["y"] - 16)
    # экран 2
    P0, PH = O + 152, 448
    for nm in ("Панель", "Зона / Панель"):
        mv(ops, k[nm]["id"], 720, P0)
        rs(ops, k[nm]["id"], 656, PH)
    mv(ops, k["Счётчик"]["id"], 752, P0 + 32)
    ops.append({"type": "set_text", "params": {"nodeId": k["Счётчик"]["id"], "text": "01 / 02" if role == "К" else "02 / 02"}})
    line0 = P0 + 88
    for n in lst:
        nm = n["name"]
        if nm.startswith("Строка "):
            mv(ops, n["id"], 752, line0 + (int(nm[-1]) - 1) * 56)
        elif nm.startswith("Правило"):
            mine = nm.split("·")[1].strip()[0] == role
            mv(ops, n["id"], 752, line0 + (int(nm[-1]) - 1) * 56 + (12 if mine else 28))
        elif nm.startswith("Номер"):
            mv(ops, n["id"], n["bounds"]["x"], line0 + (int(nm[-1]) - 1) * 56 + 12)
        elif nm.startswith("Роль"):
            mine = (nm == "Роль · Дамам") == (role == "Д")
            mv(ops, n["id"], n["bounds"]["x"], P0 + PH - 134 + (0 if mine else 16))
        elif nm == "+":
            top = n["bounds"]["y"] < 1000
            base_old, base_new = (752, O + 104) if top else (1392, P0 + PH)
            mv(ops, n["id"], n["bounds"]["x"], base_new + (n["bounds"]["y"] - base_old))
    # прежний переключатель капсом 12 — удалить; зоны прототипа — на вкладки
    ops.append({"type": "delete_nodes", "params": {"nodeIds": [n["id"] for n in lst if n["name"].startswith("Нав")]}})
    for nm, x in (("Зона / Нав · Кавалерам", 720), ("Зона / Нав · Дамам", 1048)):
        mv(ops, k[nm]["id"], x, O + 104)
        rs(ops, k[nm]["id"], 328, 48)
        ops.append({"type": "rename_node", "params": {"nodeId": k[nm]["id"], "name": nm.replace("Нав", "Вкладка")}})
    # вкладки и фото — клоны из утверждённых кадров (на 1440 сдвиг только по y: +900)
    SRC = {"328:3049": (720, 104), "328:3050": (744, 118), "328:3051": (1000, 120), "328:3052": (1048.5, 104.5),
           "328:3053": (1072, 118), "328:3054": (1328, 120), "328:3055": (720.5, 104.5), "328:3056": (744, 118),
           "328:3057": (1000, 120), "328:3058": (1048, 104), "328:3059": (1072, 118), "328:3060": (1328, 120)}
    for sid in TABS[fid]:
        x, y = SRC[sid]
        ops.append({"type": "clone_node", "params": {"nodeId": sid, "parentId": fid, "x": x, "y": O + y}})
    ops.append({"type": "clone_node", "params": {"nodeId": PHOTO[fid], "parentId": fid, "x": 0, "y": O + 104}})
    ops.append({"type": "reorder_nodes", "nodeIds": [f"${len(ops) - 1}.id"], "params": {"order": "sendToBack"}})
    # финал: строка 1 и 2 от поля, продолжение капсом справа
    F1 = P0 + PH + 40
    mv(ops, k["Финал · строка 1"]["id"], 64, F1)
    l2 = k["Финал · строка 2 (к правому краю панели)"]["id"]
    mv(ops, l2, 64, F1 + 120)
    ops.append({"type": "rename_node", "params": {"nodeId": l2, "name": "Финал · строка 2 (от поля)"}})
    cont = k["Финал · продолжение капсом"]["id"]
    ops.append({"type": "set_text", "params": {"nodeId": cont, "textAlignHorizontal": "RIGHT"}})
    mv(ops, cont, 976, F1 + 204)
    ops.append({"type": "rename_node", "params": {"nodeId": cont, "name": "Финал · продолжение капсом (к правому полю)"}})
    pass  # имя кадра не меняем: на него могут опираться инструменты прошлых этапов
    batches.append(ops)

# ---------- 07: один экран, панорама уходит в 08 (после клонов) ----------
ops = []
fid = "198:1288"
k = kids(fid)
rs(ops, fid, 1440, 900)
header(ops, k, (960, 176))
mv(ops, k["Ступени"]["id"], 64, 450)
ops.append({"type": "delete_nodes", "params": {"nodeIds": [k["Фото · Бал"]["id"]]}})
ops.append({"type": "rename_node", "params": {"nodeId": fid, "name": tree[fid]["name"].replace("C+D", "C в экран")}})
batches.append(ops)

for i, b in enumerate(batches, 1):
    json.dump(b, open(OUT / f"d3b_live_{i}.json", "w", encoding="utf-8"), ensure_ascii=False)
    print(i, len(b))
