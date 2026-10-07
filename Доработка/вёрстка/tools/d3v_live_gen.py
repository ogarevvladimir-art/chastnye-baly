"""Д3в шаг 3: утверждённое (09 A, 10 B, 11–подвал A, шапки сжаты) — в действующий макет «Главная · v2 · фото с цветом» (191:626).
Координаты — кадры окна 1440×900 из секции «Д3в · выбранное … на проверочных окнах»; id узлов сохраняются (перенос, а не замена).
Читает ../_figma/d3v_live_tree.json (действующие кадры) и ../_figma/d3v_live_win.json (кадры окна), пишет ../_figma/d3v_live_<N>.json.

  09 207:1882 ← экран 1 (334:1850, сжат до 744) + экран 2 (334:1864, со сдвигом 744) → 1644;
  10 218:882 «Омега» ← экран 1 (334:1918, 648) + экран 2 (334:1928, сдвиг 648) → 1548;
     219:1006 «Кашемир» — то же, но открыты слоты Кашемира, фото Омеги ×1,06 от центра, тексты и цифры на 16 выше,
     строки названия на 340k выше (как в прежнем кадре состояния);
  11–подвал — автолейауты остаются, меняются отступы: «11 О нас» сверху 104 (→ 431), «Контакты» 104 / 23 (→ 751),
     «Содержимое футера» 48 / 48 (подвал → 149). «12 Связаться» не меняется.
"""
import json
from collections import defaultdict
from pathlib import Path

OUT = Path(__file__).parent.parent / "_figma"
LIVE = {f["id"]: f for f in json.load(open(OUT / "d3v_live_tree.json", encoding="utf-8"))}
WIN = {f["id"]: f for f in json.load(open(OUT / "d3v_live_win.json", encoding="utf-8"))}
report = []


def r1(v):
    return round(v, 2)


def occ_index(children):
    """(имя, номер вхождения) → узел: «+» и «+ · подложка» повторяются, порядок в клонах тот же."""
    seen, out = defaultdict(int), {}
    for c in children:
        out[(c["name"], seen[c["name"]])] = c
        seen[c["name"]] += 1
    return out


def sync(ops, live, win, dy=0.0, top=False):
    """Узел live → геометрия и кегль win (рекурсивно по детям с тем же именем)."""
    lb, wb = live["bounds"], win["bounds"]
    ls, ws = live.get("styles", {}), win.get("styles", {})
    lfs, wfs = ls.get("fontSize"), ws.get("fontSize")
    fs_changed = live["type"] == "TEXT" and isinstance(wfs, (int, float)) and lfs != wfs
    if fs_changed:
        if "mixed" in (ls.get("fontFamily"), ls.get("fontStyle")):
            ops.append({"type": "set_text_range", "params": {"nodeId": live["id"], "startOffset": 0,
                                                             "endOffset": len(live["characters"]), "fontSize": r1(wfs)}})
        else:
            ops.append({"type": "set_text", "params": {"nodeId": live["id"], "fontSize": r1(wfs)}})
    size_diff = abs(lb["width"] - wb["width"]) > 0.05 or abs(lb["height"] - wb["height"]) > 0.05
    if live["type"] == "TEXT":
        if size_diff and not fs_changed:                       # колонка текста: ширина задана, высота по тексту
            ops.append({"type": "resize_nodes", "params": {"nodeIds": [live["id"]], "width": r1(wb["width"]), "height": r1(wb["height"])}})
            ops.append({"type": "set_text", "params": {"nodeId": live["id"], "textAutoResize": "HEIGHT"}})
        elif fs_changed and abs(lb["width"] - wb["width"]) > 0.05 and lb["width"] == 1312:
            pass                                                # строки названия 10 правым краем — ширина поля
    elif size_diff:
        ops.append({"type": "resize_nodes", "params": {"nodeIds": [live["id"]], "width": max(0.01, r1(wb["width"])), "height": r1(wb["height"])}})
    x, y = wb["x"], wb["y"] + dy
    if not top and (abs(lb["x"] - x) > 0.05 or abs(lb["y"] - y) > 0.05):
        ops.append({"type": "move_nodes", "params": {"nodeIds": [live["id"]], "x": r1(x), "y": r1(y)}})
    if live.get("children") and win.get("children") and live["type"] != "INSTANCE":
        wi = occ_index(win["children"])
        for key, lc in occ_index(live["children"]).items():
            if key in wi:
                sync(ops, lc, wi[key])
            else:
                report.append(f"  нет пары: {live['name']} / {key[0]}")


def transfer(fid, screens):
    """Действующий кадр fid ← экраны [(id кадра окна, сдвиг)]: дети ищутся по имени во всех экранах по порядку."""
    ops = []
    fr = LIVE[fid]
    pool = {}
    for wid, dy in screens:
        for key, n in occ_index([c for c in WIN[wid]["children"] if c["name"] != "Header"]).items():
            pool.setdefault(key, (n, dy))
    total = sum(WIN[w]["bounds"]["height"] for w, _ in screens)
    ops.append({"type": "resize_nodes", "params": {"nodeIds": [fid], "width": 1440, "height": r1(total)}})
    for key, lc in occ_index(fr["children"]).items():
        if key in pool:
            n, dy = pool[key]
            sync(ops, lc, n, dy)
        else:
            report.append(f"{fr['name'][:40]}: нет пары для «{key[0]}» — узел не тронут")
    report.append(f"{fid}: высота {total:.0f}, операций {len(ops)}")
    return ops


def kashmir(ops, fid):
    """Состояние 2 «Кашемир»: поверх раскладки «Омеги» — открыть слоты Кашемира, фото Омеги ×1,06, тексты −16, строки названия."""
    fr = LIVE[fid]
    k = {c["name"]: c for c in fr["children"]}
    win = {c["name"]: c for c in WIN["334:1928"]["children"]}
    dy = 648
    out = []
    for nm, c in k.items():
        if nm.startswith("Слот") and "Кашемир" in nm:
            om = win[nm.replace("Кашемир", "Омега")]["bounds"]
            out.append({"type": "move_nodes", "params": {"nodeIds": [c["id"]], "x": r1(om["x"]), "y": r1(om["y"] + dy)}})
            out.append({"type": "resize_nodes", "params": {"nodeIds": [c["id"]], "width": r1(om["width"]), "height": r1(om["height"])}})
            ph = c["children"][0]
            out.append({"type": "move_nodes", "params": {"nodeIds": [ph["id"]], "x": 0, "y": 0}})
            out.append({"type": "resize_nodes", "params": {"nodeIds": [ph["id"]], "width": r1(om["width"]), "height": r1(om["height"])}})
        elif nm.startswith("Слот") and "Омега" in nm:
            om = win[nm]["bounds"]
            ph = c["children"][0]
            w, h = om["width"] * 1.06, om["height"] * 1.06
            out.append({"type": "move_nodes", "params": {"nodeIds": [ph["id"]], "x": r1(-(w - om["width"]) / 2), "y": r1(-(h - om["height"]) / 2)}})
            out.append({"type": "resize_nodes", "params": {"nodeIds": [ph["id"]], "width": r1(w), "height": r1(h)}})
        elif nm.startswith(("Суть", "Цифра", "Подпись ·")):
            b = win[nm]["bounds"]
            out.append({"type": "move_nodes", "params": {"nodeIds": [c["id"]], "x": r1(b["x"]), "y": r1(b["y"] + dy - 16)}})
    g = win["Название"]
    kk = g["bounds"]["height"] / 324
    for ch, off in zip(k["Название"]["children"], (-340, -178, 0, 162)):
        out.append({"type": "move_nodes", "params": {"nodeIds": [ch["id"]], "x": 0, "y": r1(off * kk)}})
    # слоты и тексты после общего переноса: убрать из ops перенос тех же узлов, чтобы не путать порядок
    ops.extend(out)


batches = []
batches.append(transfer("207:1882", [("334:1850", 0), ("334:1864", 744)]))
batches.append(transfer("218:882", [("334:1918", 0), ("334:1928", 648)]))
b = transfer("219:1006", [("334:1918", 0), ("334:1928", 648)])
kashmir(b, "219:1006")
batches.append(b)
batches.append([
    {"type": "set_auto_layout", "params": {"nodeId": "191:890", "paddingTop": 104, "paddingBottom": 96}},
    {"type": "set_auto_layout", "params": {"nodeId": "191:901", "paddingTop": 104, "paddingBottom": 23}},
    {"type": "set_auto_layout", "params": {"nodeId": "191:932", "paddingTop": 48, "paddingBottom": 48}},
])

for i, b in enumerate(batches, 1):
    (OUT / f"d3v_live_{i}.json").write_text(json.dumps(b, ensure_ascii=False), encoding="utf-8")
    print(f"d3v_live_{i}.json", len(b))
print("\n".join(report))
