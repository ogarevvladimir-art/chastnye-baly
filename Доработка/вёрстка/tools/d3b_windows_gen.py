"""Д3б шаг 2: выбранное (06 A, 07 один экран, 08 экран 1 + экран 2 A1) на проверочных окнах — секция 328:3071.
Система «в экран» (Д2): x и колонки × u, y и крупное × k (k ≤ s = min(u, H/900)), мелкий текст — px.

  python d3b_windows_gen.py 1   # проход 1: ширины текстов и кегли → ../_figma/d3b_win1_<N>.json
  python d3b_windows_gen.py 2   # проход 2: по фактическим высотам (дерево ../_figma/d3b_win_tree2.json) → ../_figma/d3b_win2_<N>.json

Модели (то же считает код сайта):
  06: k = min(s, (H − 152) / 720); шапка 104 / 104+56k / 104+176k, H2 150k; лид справа от первой строки H2;
      тело с T = 104 + 336k: фото 448u × (H − T) от края, строки 112k / 136k / 136k (название 32k), ответ на T,
      «Принцип» 36k низом на H − 48, линия на 24 выше.
  07: шапка как 06; лесенка низом на H − 40k, ступени 304u шагом 336u, отступы 144 / 104 / 64 / 24 × k, «Суть» 36k, зазоры 20k;
      k — наибольшее ≤ s, при котором верх ступени 04 ≥ низ H2 + 24.
  08 экран 1: шапка (k = s), интро — 104 + 320k / 392k / 482k, колонки min(320, 320u) / min(400, 400u), интро 2 — правым краем к оси.
  08 экран 2: вкладки 48 (px) на 104, панель от 152: счётчик 32k, правила с 88k шагом p = max(56k, текст + 20), роль 128k низом на 32k;
      финал 150k: строка 1 на 40k ниже панели, строка 2 — правым краем к W − 64; низ — H − 20k; фото слева до низа панели.
      k — наибольшее ≤ s, при котором всё помещается.
"""
import json
import sys
from pathlib import Path

OUT = Path(__file__).parent.parent / "_figma"
WINS = [(1920, 950), (1366, 650), (1280, 600), (1024, 650)]
KINDS = ["06", "06v", "07", "08h", "08p"]
PASS = int(sys.argv[1])
tree = json.load(open(OUT / ("d3b_win_tree.json" if PASS == 1 else "d3b_win_tree2.json"), encoding="utf-8"))
W1440_H2 = {"Танцевальный": 871, "Подготовка": 694}
report = []
NODES = {}


def index(n):
    NODES[n["id"]] = n
    for c in n.get("children", []):
        index(c)


for f in tree:
    index(f)


def kids(n):
    return {c["name"]: c for c in n.get("children", [])}


def frame_ops(fr, W, H, kind):
    ops = []
    u = (W - 128) / 1312
    s = min(u, H / 900)
    X = lambda x: 64 + (x - 64) * u
    k_ = kids(fr)

    def mv(nid, x, y):
        ops.append({"type": "move_nodes", "params": {"nodeIds": [nid], "x": round(x, 1), "y": round(y, 1)}})

    def rs(nid, w, h):
        ops.append({"type": "resize_nodes", "params": {"nodeIds": [nid], "width": round(w, 1), "height": round(max(h, 1), 1)}})

    def fs(nid, size):
        node = NODES[nid]
        st = node.get("styles", {})
        if "mixed" in (st.get("fontFamily"), st.get("fontStyle")):
            # смешанные начертания (курсив + прямой) — кегль только диапазоном
            ops.append({"type": "set_text_range", "params": {"nodeId": nid, "startOffset": 0,
                        "endOffset": len(node["characters"]), "fontSize": round(size, 1)}})
        else:
            ops.append({"type": "set_text", "params": {"nodeId": nid, "fontSize": round(size, 1)}})

    def tw(node, w):
        """Ширина текста с переносом: ширина фиксирована, высота по тексту."""
        rs(node["id"], w, node["bounds"]["height"])
        ops.append({"type": "set_text", "params": {"nodeId": node["id"], "textAutoResize": "HEIGHT"}})

    def h(node):
        return node["bounds"]["height"]

    def header(kk, lead_after=None):
        mv(k_["Метка"]["id"], 64, 104)
        h2 = sorted([n for nm, n in k_.items() if nm.startswith("Заголовок")], key=lambda n: n["bounds"]["y"])
        fs(h2[0]["id"], 150 * kk)
        fs(h2[1]["id"], 150 * kk)
        mv(h2[0]["id"], 64, 104 + 56 * kk)
        mv(h2[1]["id"], X(720), 104 + 176 * kk)
        if lead_after:
            lw = min(416, 416 * W / 1440)
            x = max(min(X(960), W - 64 - lw), 64 + lead_after * kk + 25)
            w = min(lw, W - 64 - x)
            if PASS == 1:
                tw(k_["Лид"], w)
            mv(k_["Лид"]["id"], x, 104 + 72 * kk)

    if PASS == 1:
        rs(k_["Header"]["id"], W, 72)

    # ---------- 06 ----------
    if kind in ("06", "06v"):
        kk = min(s, (H - 152) / 720)
        header(kk, W1440_H2["Танцевальный"])
        aw = min(416, 416 * u)
        T = 104 + 336 * kk
        y = T
        for nm, hh in (("Строка 01", 112), ("Строка 02", 136), ("Строка 03", 136)):
            row = k_[nm]
            rk = kids(row)
            mv(row["id"], X(512), y)
            rs(row["id"], 416 * u, hh * kk)
            rs(rk["Линия"]["id"], 416 * u, rk["Линия"]["bounds"]["height"])
            mv(rk["Номер"]["id"], 0, 24 * kk)
            if PASS == 1:
                fs(rk["Название"]["id"], 32 * kk)
                tw(rk["Название"], 416 * u)
            mv(rk["Название"]["id"], 0, 56 * kk)
            y += hh * kk
        for nm in ("Ответ 01", "Ответ 02", "Ответ 03"):
            fr2 = k_[nm]
            fk = kids(fr2)
            active = fr2["bounds"]["y"] <= min(k_[a]["bounds"]["y"] for a in ("Ответ 01", "Ответ 02", "Ответ 03")) + 0.5
            mv(fr2["id"], X(960), T + (0 if active else 16))
            if PASS == 1:
                for c in fr2["children"]:
                    if c["name"] != "Метка":
                        tw(c, aw)
            else:
                # ответ → метка на 32 ниже → пояснение на 16 ниже метки; без метки — пояснение на 16 ниже ответа
                yy = h(fk["Ответ"])
                if "Метка" in fk:
                    mv(fk["Метка"]["id"], 0, yy + 32)
                    yy += 32 + 15
                if "Пояснение" in fk:
                    mv(fk["Пояснение"]["id"], 0, yy + 16)
                    yy += 16 + h(fk["Пояснение"])
                rs(fr2["id"], aw, yy)
        pr = k_["Принцип"]
        if PASS == 1:
            fs(pr["id"], 36 * kk)
            tw(pr, aw)
        else:
            a2 = kids(k_["Ответ 02"])
            ans_bottom = T + h(a2["Ответ"]) + 32 + 15 + 16 + h(a2["Пояснение"])   # ответ 02 раскрыт (на T)
            line_y = H - 48 - h(pr) - 24
            pw = 448 * u
            if ans_bottom + 16 <= line_y:
                mv(pr["id"], X(960), H - 48 - h(pr))
                mv(k_["Линия"]["id"], X(960), line_y)
                rs(k_["Линия"]["id"], aw, 1)
                where = "справа"
            else:
                # правая колонка не вмещает самый длинный ответ и «Принцип»: «Принцип» — на низ фото под тень Slate
                sh = min(240 * kk + 120, H - T)
                ops.append({"type": "create_rectangle", "params": {"parentId": fr["id"], "name": "Тон · под «Принципом»",
                            "x": 0, "y": round(H - sh, 1), "width": round(pw, 1), "height": round(sh, 1)}})
                ri = len(ops) - 1
                SL = {"r": 0.1333, "g": 0.1333, "b": 0.1333}
                ops.append({"type": "set_fills", "nodeIds": [f"${ri}.id"], "params": {"paints": [{"type": "GRADIENT_LINEAR",
                            "gradientTransform": [[0, 1, 0], [-1, 0, 1]],
                            "gradientStops": [{"position": 0, "color": {**SL, "a": 0}}, {"position": 0.45, "color": {**SL, "a": 0.75}},
                                              {"position": 1, "color": {**SL, "a": 0.92}}]}]}})
                ops.append({"type": "reorder_nodes", "nodeIds": [f"${ri}.id"], "params": {"order": "bringToFront"}})
                box = 140
                rs(pr["id"], pw - 64, box)
                ops.append({"type": "set_text", "params": {"nodeId": pr["id"], "textAutoResize": "NONE", "textAlignVertical": "BOTTOM"}})
                mv(pr["id"], 32, H - 32 - box)
                ops.append({"type": "reorder_nodes", "nodeIds": [pr["id"]], "params": {"order": "bringToFront"}})
                ops.append({"type": "set_opacity", "nodeIds": [k_["Линия"]["id"]], "params": {"opacity": 0}})
                where = "на фото"
            report.append(f"{W}×{H} {kind}: k {kk:.3f}, H2 {150 * kk:.0f}, тело с {T:.0f}, низ ответа 02 {ans_bottom:.0f}, линия «Принципа» {line_y:.0f} → {where}")
        pw = 448 * u
        for nm in ("Кадр 01 Стесняетесь", "Кадр 02 Не умеете танцевать", "Кадр 03 Пришли без пары") if PASS == 1 else ():
            ph = k_[nm]
            mv(ph["id"], 0, T)
            rs(ph["id"], pw, H - T)
            inner = ph["children"][0]
            # снимок — по ширине кадра, центр по вертикали (cover: 448 × 560 → не меньше кадра)
            g = max(pw / 448, (H - T) / 460)
            iw, ih = inner["bounds"]["width"], inner["bounds"]["height"]
            nw, nh = iw * g, ih * g
            rs(inner["id"], nw, nh)
            mv(inner["id"], (pw - nw) / 2, (H - T - nh) / 2)

    # ---------- 07 ----------
    if kind == "07":
        steps = k_["Ступени"]
        sk = steps["children"]
        OFFS = [144, 104, 64, 24]
        cw = 304 * u
        if PASS == 1:
            kk = s
            for st in sk:
                tk = kids(kids(st)["Текст ступени"])
                for nm in ("Этап", "Абзац"):
                    tw(tk[nm], cw)
            header(kk, W1440_H2["Подготовка"])
        else:
            body = [h(kids(kids(st)["Текст ступени"])["Абзац"]) for st in sk]
            # высота ступени i: отступ·k + 20k + 15 + 20k + 82k + 20k + абзац;  низ — H − 40k
            def fit(kk):
                tops = [H - 40 * kk - (OFFS[i] * kk + 142 * kk + 15 + body[i]) for i in range(4)]
                top = min(tops)                         # верх лесенки (ступень 01 — самая высокая)
                return top, top + 24 * kk >= 104 + 296 * kk + 24 - 0.01
            kk = s
            while not fit(kk)[1]:
                kk -= 0.001
            top, _ = fit(kk)
            header(kk, W1440_H2["Подготовка"])
            mv(steps["id"], 64, top)
            rs(steps["id"], 1312 * u, H - 40 * kk - top)
            # «Ступени» — горизонтальный автолейаут: зазор колонок 32u
            ops.append({"type": "set_auto_layout", "params": {"nodeId": steps["id"], "itemSpacing": round(32 * u, 1)}})
            for i, st in enumerate(sk):
                stk = kids(st)
                tx = stk["Текст ступени"]
                tk = kids(tx)
                ops.append({"type": "set_auto_layout", "params": {"nodeId": st["id"], "paddingTop": round(OFFS[i] * kk, 1)}})
                ops.append({"type": "set_auto_layout", "params": {"nodeId": tx["id"], "paddingTop": round(20 * kk, 1), "itemSpacing": round(20 * kk, 1)}})
                fs(tk["Суть"]["id"], 36 * kk)
                rs(st["id"], cw, st["bounds"]["height"])
                rs(stk["Разделитель"]["id"], cw, 1)
                rs(tx["id"], cw, tx["bounds"]["height"])
                mv(st["id"], 336 * u * i, 0)
            report.append(f"{W}×{H} 07: k {kk:.3f} (s {s:.3f}), H2 {150 * kk:.0f}, лесенка с {top:.0f}, абзацы {body}")

    # ---------- 08 экран 1 ----------
    if kind == "08h":
        kk = s
        header(kk)
        w12, w3 = min(320, 320 * u), min(400, 400 * u)
        i1, i2, i3 = k_["Интро 1"], k_["Интро 2"], k_["Интро 3"]
        if PASS == 1:
            tw(i1, w12)
            tw(i2, w12)
            tw(i3, w3)
        mv(i1["id"], 64, 104 + 320 * kk)
        mv(i2["id"], X(720) - w12, 104 + 392 * kk)
        mv(i3["id"], X(720), 104 + 482 * kk)
        if PASS == 2:
            report.append(f"{W}×{H} 08 экран 1: H2 {150 * kk:.0f}, низ интро 3 {104 + 482 * kk + h(i3):.0f} (H − 48 = {H - 48})")

    # ---------- 08 экран 2 (A1) ----------
    if kind == "08p":
        # панель не уже 608: правила (до 496 px) идут в одну строку; фото слева уступает место
        pw = max(656 * u, 608)
        px = W - 64 - pw
        rules = [c for c in fr["children"] if c["name"].startswith("Правило")]
        for r in rules:
            tw(r, pw - 104)
        if PASS == 2:
            th = 18
            def total(kk):
                p = max(56 * kk, th + 20)
                PH = 88 * kk + 4 * p + 2 * kk + 102 * kk + 32 * kk
                return PH, p, 152 + PH + 40 * kk + 240 * kk + 20 * kk
            kk = s
            while total(kk)[2] > H:
                kk -= 0.001
            PH, p, _ = total(kk)
            P0 = 152
            for nm in ("Панель", "Зона / Панель"):
                mv(k_[nm]["id"], px, P0)
                rs(k_[nm]["id"], pw, PH)
            mv(k_["Счётчик"]["id"], px + 32, P0 + 32 * kk)
            line0 = P0 + 88 * kk
            for c in fr["children"]:
                nm = c["name"]
                if nm.startswith("Строка "):
                    i = int(nm[-1]) - 1
                    mv(c["id"], px + 32, line0 + i * p)
                    rs(c["id"], pw - 64, 1)
                elif nm.startswith("Правило"):
                    i = int(nm[-1]) - 1
                    mine = "К" in nm.split("·")[1]
                    mv(c["id"], px + 32, line0 + i * p + 12 + (0 if mine else 16))
                elif nm.startswith("Номер"):
                    i = int(nm[-1]) - 1
                    mv(c["id"], px + pw - 32 - c["bounds"]["width"], line0 + i * p + 12)
                elif nm.startswith("Роль"):
                    fs(c["id"], 128 * kk)
                    wr = (557 if "Кавалерам" in nm else 344) * kk
                    mine = "Кавалерам" in nm
                    mv(c["id"], px + pw - 32 - wr, P0 + PH - 32 * kk - 102 * kk + (0 if mine else 16))
            pb = P0 + PH
            corners = [c for c in fr["children"] if c["name"] == "+"]
            for c in corners:
                bx, by_ = c["bounds"]["x"], c["bounds"]["y"]
                left = bx < 1000
                top = by_ < 300
                base_x = (px - 32) if left else (px + pw + 16)
                base_y = 104 if top else pb
                mv(c["id"], base_x + (bx - (688 if left else 1392)), base_y + (by_ - (104 if top else 600)))
            # вкладки
            tab = pw / 2
            for c in fr["children"]:
                nm = c["name"]
                if nm.startswith("Вкладка"):
                    second = "Дамам" in nm
                    x0 = px + (tab if second else 0)
                    if nm.endswith("активна") or nm in ("Вкладка · Кавалерам", "Вкладка · Дамам"):
                        inset = 0 if nm.endswith("активна") else 0.5
                        mv(c["id"], x0 + inset, 104 + inset)
                        rs(c["id"], tab - 2 * inset, 48 - inset)
                    elif nm.endswith("текст"):
                        mv(c["id"], x0 + 24, 118)
                    elif nm.endswith("номер"):
                        mv(c["id"], x0 + tab - 24 - c["bounds"]["width"], 120)
            # фото слева до низа панели
            ph = k_["Фото · Бал"]
            fw, fh = px - 64, pb - 104
            mv(ph["id"], 0, 104)
            rs(ph["id"], fw, fh)
            g = max(fw / 656, fh / 496)
            inner = ph["children"][0]
            rs(inner["id"], 1100 * g, 733 * g)
            mv(inner["id"], 0, -230 * g + (fh - 496 * g) / 2)
            # финал
            f1 = k_["Финал · строка 1"]
            f2 = k_["Финал · строка 2 (к правому краю панели)"]
            fs(f1["id"], 150 * kk)
            fs(f2["id"], 150 * kk)
            F1 = pb + 40 * kk
            mv(f1["id"], 64, F1)
            # правка пользователя: «не нужно —» — от поля, продолжение капсом — справа, правым краем к полю
            mv(f2["id"], 64, F1 + 120 * kk)
            cont = k_["Финал · продолжение капсом"]["id"]
            ops.append({"type": "set_text", "params": {"nodeId": cont, "textAlignHorizontal": "RIGHT"}})
            mv(cont, W - 64 - 400, F1 + 120 * kk + 120 * kk - 36)
            report.append(f"{W}×{H} 08 экран 2: k {kk:.3f} (s {s:.3f}), панель {PH:.0f}, шаг правил {p:.0f}, финал {150 * kk:.0f}, фото {fw:.0f}×{fh:.0f}")
    return ops


import re

def shifted(ops, off):
    """Ссылки "$N.id" внутри кадра → номера в общей пачке."""
    txt = json.dumps(ops, ensure_ascii=False)
    txt = re.sub(r'"\$(\d+)\.id"', lambda m: f'"${int(m.group(1)) + off}.id"', txt)
    return json.loads(txt)


n = 0
batch = []
for wi, (W, H) in enumerate(WINS):
    for ki, kind in enumerate(KINDS):
        fo = frame_ops(tree[wi * 5 + ki], W, H, kind)
        if batch and len(batch) + len(fo) > 95:
            n += 1
            json.dump(batch, open(OUT / f"d3b_win{PASS}_{n}.json", "w", encoding="utf-8"), ensure_ascii=False)
            print(n, len(batch))
            batch = []
        batch += shifted(fo, len(batch))
n += 1
json.dump(batch, open(OUT / f"d3b_win{PASS}_{n}.json", "w", encoding="utf-8"), ensure_ascii=False)
print(n, len(batch))
print("\n".join(report))
