"""Д3б шаг 1: варианты A / B для 06, 07, 08 на 1440×900 (s = u = 1) — раскладка клонов секции 328:2278.
Читает дерево клонов (../_figma/d3b_clones.json), пишет пачки операций figma-mcp-express в ../_figma/d3b_ops2_<блок>.json.
В пачке 07 ссылка "$LAST.id" заменяется номером операции create_rectangle."""
import json
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE.parent / "_figma"
frames = {f["id"]: f for f in json.load(open(OUT / "d3b_clones.json", encoding="utf-8"))}
ops = {"06": [], "07": [], "08": []}


def kids(fid):
    return {c["name"]: c for c in frames[fid]["children"]}


def kid_list(fid):
    return frames[fid]["children"]


def mv(b, nid, x, y):
    ops[b].append({"type": "move_nodes", "params": {"nodeIds": [nid], "x": round(x, 1), "y": round(y, 1)}})


def rs(b, nid, w, h):
    ops[b].append({"type": "resize_nodes", "params": {"nodeIds": [nid], "width": round(w, 1), "height": round(h, 1)}})


def rm(b, ids):
    if ids:
        ops[b].append({"type": "delete_nodes", "params": {"nodeIds": ids}})


def shift(b, node, dy, dx=0):
    bb = node["bounds"]
    mv(b, node["id"], bb["x"] + dx, bb["y"] + dy)


def header(b, k, lead_xy):
    """Шапка раздела «в экран» (Д3а): метка 104, H2 104 + 56 / 104 + 176, кегль 150 (s = 1)."""
    mv(b, k["Метка"]["id"], 64, 104)
    h2 = [n for nm, n in k.items() if nm.startswith("Заголовок")]
    h2.sort(key=lambda n: n["bounds"]["y"])
    mv(b, h2[0]["id"], h2[0]["bounds"]["x"], 160)
    mv(b, h2[1]["id"], h2[1]["bounds"]["x"], 280)
    if lead_xy:
        mv(b, k["Лид"]["id"], *lead_xy)


def h2_ids(k):
    return [n["id"] for nm, n in k.items() if nm.startswith("Заголовок") or nm in ("Метка", "Лид")]


def pick(nodes, prefixes):
    return [n for n in nodes if n["name"].startswith(prefixes)]


# ---------- 06 Ассистент ----------
BODY06 = ("Строка", "Ответ", "Линия", "Принцип", "Кадр")


def body06(fid, top, photo_h, pad=0):
    """Тело 06 с верхом top: фото 448 × photo_h от края, строки 112 / 136 / 136, ответ справа, «Принцип» — к низу фото."""
    b = "06"
    k = kids(fid)
    y = top
    for nm, h in (("Строка 01", 112), ("Строка 02", 136), ("Строка 03", 136)):
        mv(b, k[nm]["id"], 512, y)
        rs(b, k[nm]["id"], 416, h)
        y += h
    for nm in ("Ответ 01", "Ответ 02", "Ответ 03"):
        off = k[nm]["bounds"]["y"] - 640            # активный — 0, скрытые — +16 (вплывают)
        mv(b, k[nm]["id"], 960, top + off)
    bottom = top + photo_h - pad                    # низ «Принципа»
    mv(b, k["Принцип"]["id"], 960, bottom - 82)
    mv(b, k["Линия"]["id"], 960, bottom - 82 - 24)
    for nm in ("Кадр 01 Стесняетесь", "Кадр 02 Не умеете танцевать", "Кадр 03 Пришли без пары"):
        fr = k[nm]
        mv(b, fr["id"], 0, top)
        rs(b, fr["id"], 448, photo_h)
        inner = fr["children"][0]
        ib = inner["bounds"]
        mv(b, inner["id"], ib["x"], ib["y"] - (560 - photo_h) / 2)


for fid in ("328:2279", "328:2322"):                  # A — одним экраном
    header("06", kids(fid), (960, 176))
    body06(fid, 440, 460, 48)                         # 440 … 900: фото до низа, низ «Принципа» на 852

fid = "328:2365"                                      # B · экран 1 — шапка
k = kids(fid)
header("06", k, (720, 480))
rm("06", [n["id"] for n in pick(kid_list(fid), BODY06)])

fid = "328:2408"                                      # B · экран 2 — тело по центру экрана под шапкой
rm("06", h2_ids(kids(fid)))
body06(fid, 104 + (796 - 560) // 2, 560)

# ---------- 07 Уроки ----------
STEPS_H = 410

fid = "328:2451"                                      # A — одним экраном, ступени на панораме
k = kids(fid)
header("07", k, (960, 176))
mv("07", k["Ступени"]["id"], 64, 900 - 40 - STEPS_H)
ph = k["Фото · Бал"]
mv("07", ph["id"], 0, 360)
rs("07", ph["id"], 1440, 540)
mv("07", ph["children"][0]["id"], 0, -210)
ASH = {"r": 0.2431, "g": 0.2431, "b": 0.2431}
ops["07"] += [
    {"type": "create_rectangle", "params": {"parentId": fid, "name": "Тон · под ступенями", "x": 0, "y": 360, "width": 1440, "height": 540}},
    {"type": "set_fills", "nodeIds": ["$LAST.id"], "params": {"paints": [{"type": "GRADIENT_LINEAR",
        "gradientTransform": [[0, 1, 0], [-1, 0, 1]],
        "gradientStops": [{"position": 0, "color": {**ASH, "a": 0}}, {"position": 0.2, "color": {**ASH, "a": 0.75}},
                          {"position": 0.4, "color": {**ASH, "a": 0.9}}, {"position": 1, "color": {**ASH, "a": 0.96}}]}]}},
    {"type": "reorder_nodes", "nodeIds": ["$LAST.id"], "params": {"order": "sendToBack"}},
    {"type": "reorder_nodes", "nodeIds": [ph["id"]], "params": {"order": "sendToBack"}},
]
last = len(ops["07"]) - 4
for o in ops["07"][last + 1:]:
    o["nodeIds"] = [f"${last}.id" if x == "$LAST.id" else x for x in o["nodeIds"]]

fid = "328:2492"                                      # B · экран 1 — шапка и ступени
k = kids(fid)
header("07", k, (960, 176))
mv("07", k["Ступени"]["id"], 64, 900 - 40 - STEPS_H)
rm("07", [k["Фото · Бал"]["id"]])

fid = "328:2533"                                      # B · экран 2 — панорама во весь экран
k = kids(fid)
rm("07", h2_ids(k) + [k["Ступени"]["id"]])
ph = k["Фото · Бал"]
mv("07", ph["id"], 0, 0)
rs("07", ph["id"], 1440, 900)
mv("07", ph["children"][0]["id"], 0, -30)

# ---------- 08 Этикет ----------
INTRO = ("Интро",)
PANEL = ("Панель", "Счётчик", "Строка", "Правило", "Номер", "Роль", "+", "Зона / Панель")
NAV = ("Нав", "Зона / Нав")
FINAL = ("Финал",)


def screen1_08(fid):
    k = kids(fid)
    lst = kid_list(fid)
    header("08", k, None)
    for n in pick(lst, INTRO):
        shift("08", n, -16)                           # H2 поднялся на 16 (176 → 160): интро за ним
    rm("08", [n["id"] for n in pick(lst, PANEL + NAV + FINAL)])


screen1_08("328:2574")
screen1_08("328:2682")

# A · экран 2 — переключатель, панель 656 × 480, финал под панелью; продолжение капсом — слева от второй строки финала
fid = "328:2628"
k = kids(fid)
lst = kid_list(fid)
rm("08", h2_ids(k) + [n["id"] for n in pick(lst, INTRO)])
P0, PH = 104, 480
dyp = P0 - 752
for n in pick(lst, NAV):
    shift("08", n, dyp)
for nm in ("Панель", "Зона / Панель"):
    mv("08", k[nm]["id"], 720, P0)
    rs("08", k[nm]["id"], 656, PH)
mv("08", k["Счётчик"]["id"], 752, P0 + 32)
LINE0, STEP = P0 + 88, 56
for n in lst:
    nm = n["name"]
    if nm.startswith("Строка "):
        mv("08", n["id"], 752, LINE0 + (int(nm[-1]) - 1) * STEP)
    elif nm.startswith("Правило"):
        mv("08", n["id"], 752, LINE0 + (int(nm[-1]) - 1) * STEP + (12 if "К" in nm.split("·")[1] else 28))
    elif nm.startswith("Номер"):
        mv("08", n["id"], n["bounds"]["x"], LINE0 + (int(nm[-1]) - 1) * STEP + 12)
    elif nm == "Роль · Кавалерам":
        mv("08", n["id"], n["bounds"]["x"], P0 + PH - 32 - 102)
    elif nm == "Роль · Дамам":
        mv("08", n["id"], n["bounds"]["x"], P0 + PH - 32 - 102 + 16)
    elif nm == "+":
        shift("08", n, dyp if n["bounds"]["y"] < 1000 else (P0 + PH) - 1392)
F1 = P0 + PH + 40
mv("08", k["Финал · строка 1"]["id"], 64, F1)
mv("08", k["Финал · строка 2 (к правому краю панели)"]["id"], 637, F1 + 120)
mv("08", k["Финал · продолжение капсом"]["id"], 64, F1 + 120 + 84)

# B · экран 2 — переключатель и панель 640 по центру экрана под шапкой
fid = "328:2736"
k = kids(fid)
lst = kid_list(fid)
rm("08", h2_ids(k) + [n["id"] for n in pick(lst, INTRO + FINAL)])
dy = 104 + (796 - 640) // 2 - 752
for n in pick(lst, PANEL + NAV):
    shift("08", n, dy)

# B · экран 3 — финал по центру экрана
fid = "328:2790"
k = kids(fid)
lst = kid_list(fid)
rm("08", h2_ids(k) + [n["id"] for n in pick(lst, INTRO + PANEL + NAV)])
dy = 104 + (796 - 324) // 2 - 1512
for n in pick(lst, FINAL):
    shift("08", n, dy)

for b, o in ops.items():
    json.dump(o, open(OUT / f"d3b_ops2_{b}.json", "w", encoding="utf-8"), ensure_ascii=False)
    print(b, len(o))
