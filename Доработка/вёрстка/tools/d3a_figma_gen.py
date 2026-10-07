"""Генератор раскладки Д3а (01 B, 03 A, 04 B) на проверочных окнах по системе «в экран» (Д2).
x × u, y и крупное × s = min(u, H/900), мелкое — px. Пишет пачки операций figma-mcp-express в ops_NN.json."""
import json, math, sys
from pathlib import Path

HERE = Path(__file__).parent
TREE = Path(r"C:/Users/ogare/Desktop/Мои документы/VS CODE/.figma-mcp-cache/get_nodes_info-9d890c20.json")
WINS = [(1920, 950), (1366, 650), (1280, 600), (1024, 650)]
KINDS = ["01h", "01r", "01v", "03", "04h", "04r", "04v"]
ONLY = sys.argv[1:] or KINDS                 # python d3a_figma_gen.py 03 — только эти виды
# Самое длинное описание 03 («Духовой оркестр») по факту Figma при ширине min(416, колонка): строк × 18
DESC_H = {1920: 108, 1366: 108, 1280: 108, 1024: 144}
# «Свинг · фокстрот · латина» (305) шире колонки 1024 (284): переносится на вторую строку Label (15,4), как на сайте
DANCES_W = 305

frames = json.load(open(TREE, encoding="utf-8"))
ops = []
report = []


def kids(n):
    return {c["name"]: c for c in n.get("children", [])}


def mv(nid, x, y):
    ops.append({"type": "move_nodes", "params": {"nodeIds": [nid], "x": round(x, 1), "y": round(y, 1)}})


def rs(nid, w, h):
    ops.append({"type": "resize_nodes", "params": {"nodeIds": [nid], "width": round(w, 1), "height": round(h, 1)}})


def fs(nid, size):
    ops.append({"type": "set_text", "params": {"nodeId": nid, "fontSize": round(size, 1)}})


def autoh(nid):
    ops.append({"type": "set_text", "params": {"nodeId": nid, "textAutoResize": "HEIGHT"}})


WORD_W = {"Разговор": 732, "Концепция": 906, "Репетиции": 882, "Вечер": 454, "Воспоминания": 1260}

for wi, (W, H) in enumerate(WINS):
    u = (W - 128) / 1312
    s = min(u, H / 900)
    X = lambda x: 64 + (x - 64) * u
    f = W / 1440
    for ki, kind in enumerate(KINDS):
        if kind not in ONLY:
            continue
        fr = frames[wi * 7 + ki]
        fid = fr["id"]
        k = kids(fr)
        rs(fid, W, H)
        ops.append({"type": "rename_node", "params": {"nodeId": fid, "name": fr["name"].replace("1440×900", f"{W}×{H}")}})
        rs(k["Header"]["id"], W, 72)
        if kind == "01h":
            mv(k["Номер секции"]["id"], 64, 104)
            for nm, x, y in (("Заголовок · 1", 64, 104 + 56 * s), ("Заголовок · 2 на оси", X(720), 104 + 176 * s)):
                fs(k[nm]["id"], 150 * s)
                mv(k[nm]["id"], x, y)
            mv(k["Лид · от оси"]["id"], X(720), 104 + 376 * s)
        elif kind in ("01r", "01v"):
            hov = kind == "01v"
            step = min(128 * s, math.floor((H - 104 - 24 - 130 - 1) / 5))
            kk = step / 128
            report.append(f"{W}×{H} 01: шаг {step:.0f}, слово {112 * kk:.0f}")
            steps = k["Шаги"]
            mv(steps["id"], 0, 104)
            rs(steps["id"], W, 5 * step + 1 + (130 if hov else 0))
            rows = [c for c in steps["children"] if c["name"].startswith("Шаг")]
            for i, row in enumerate(rows):
                rk = kids(row)
                h = step + (130 if hov and i == 0 else 0)
                y = i * step + (130 if hov and i > 0 else 0)
                rs(row["id"], W, h)
                mv(row["id"], 0, y)
                word = rk["Слово"]
                fs(word["id"], 112 * kk)
                mv(word["id"], 64, 17 * kk)
                rs(rk["Разделитель"]["id"], 1312 * u, 1)
                mv(rk["Номер"]["id"], 64 + WORD_W[word["characters"]] * kk + 16, 17 * kk + 6)
                mv(rk["Описание"]["id"], X(736), step)
            line = [c for c in steps["children"] if c["name"] == "Линия низ"][0]
            mv(line["id"], 0, 5 * step + (130 if hov else 0))
            rs(line["id"], W, 1)
            rs(kids(line)["Разделитель"]["id"], 1312 * u, 1)
        elif kind == "03":
            col_w = 416 * u
            # описание — колонкой min(416, колонка) (мелкий текст в px, как на сайте); высота — по факту Figma
            desc_w = min(416, col_w)
            desc_h = DESC_H[W]
            title_h = 64 * s
            dances_y = 56 + title_h + 20
            desc_y = dances_y + 36
            wrap = 15.4 if DANCES_W > col_w else 0      # только у «Формата 02»
            col_h = desc_y + wrap + desc_h
            col_top = H - 40 * s - col_h
            # H2 ужимается сверх s, если колонки не помещаются под вторую строку (низкие окна)
            kh = min(s, (col_top - 24 - 104) / 296)
            report.append(f"{W}×{H} 03: колонки с {col_top:.0f}, H2 {150 * kh:.0f} (по s {150 * s:.0f})")
            mv(k["Метка"]["id"], 64, 104)
            for nm, x, y in (("Заголовок · 1", 64, 104 + 56 * kh), ("Заголовок · 2 лесенкой", X(400), 104 + 176 * kh)):
                fs(k[nm]["id"], 150 * kh)
                mv(k[nm]["id"], x, y)
            lw = min(416, 416 * W / 1440)
            lead = k["Лид"]["id"]
            rs(lead, lw, 54)
            autoh(lead)
            mv(lead, min(X(960), W - 64 - lw), 104 + 72 * kh)
            ph_y = 104 + 256 * kh                     # 360 на 1440: на 200 ниже верха H2
            ph_h = H - ph_y
            for nm in ("Фото 01 Симфонический", "Фото 02 Духовой", "Фото 03 Группа"):
                ph = k[nm]
                rs(ph["id"], W, ph_h)
                mv(ph["id"], 0, ph_y)
                inner = ph["children"][0]
                b = inner["bounds"]
                g = max(f, ph_h / 540)
                rs(inner["id"], b["width"] * g, b["height"] * g)
                mv(inner["id"], (W - 1440 * g) / 2 + b["x"] * g, b["y"] * g)
            tone = k["Тон · под колонками"]["id"]
            ty = col_top - 136 * s
            rs(tone, W, H - ty)
            mv(tone, 0, ty)
            for nm, x in (("Формат 01", 64), ("Формат 02", 512), ("Формат 03", 960)):
                col = k[nm]
                ck = kids(col)
                rs(col["id"], col_w, col_h)
                mv(col["id"], X(x), col_top)
                rs(ck["Линия"]["id"], col_w, ck["Линия"]["bounds"]["height"])
                fs(ck["Название"]["id"], 32 * s)
                mv(ck["Название"]["id"], 0, 56)
                mv(ck["Танцы"]["id"], 0, dances_y)
                w2 = nm == "Формат 02" and wrap
                if w2:
                    rs(ck["Танцы"]["id"], col_w, 30.8)
                    autoh(ck["Танцы"]["id"])
                rs(ck["Описание"]["id"], desc_w, desc_h)
                autoh(ck["Описание"]["id"])
                mv(ck["Описание"]["id"], 0, desc_y + (wrap if w2 else 0))
        elif kind == "04h":
            mv(k["Метка"]["id"], 64, 104)
            fs(k["Заголовок"]["id"], 150 * s)
            mv(k["Заголовок"]["id"], 64, 104 + 56 * s)
            mv(k["Лид"]["id"], X(720), 104 + 256 * s)
        else:
            hov = kind == "04v"
            q = k["Цитата"]["id"]
            q_h = 173 * s
            q_y = H - 64 * s - q_h
            ops.append({"type": "set_text_range", "params": {"nodeId": q, "startOffset": 0, "endOffset": len(k["Цитата"]["characters"]), "fontSize": round(64 * s, 1)}})
            rs(q, 864 * u, q_h)
            autoh(q)
            mv(q, 64, q_y)
            tw = min(416, 416 * W / 1440)
            t = k["Абзац · темп"]["id"]
            rs(t, tw, 90)
            autoh(t)
            mv(t, min(X(960), W - 64 - tw), q_y + 12 * s)
            hs = q_y - 48 * s
            report.append(f"{W}×{H} 04: сцена {hs:.0f}, цитата с {q_y:.0f}")
            scene = k["Сцена"]
            mv(scene["id"], 0, 0)
            rs(scene["id"], W, hs)
            panels = scene["children"]
            geo = [(0, 400 * f), (408 * f, 1032 * f)] if hov else [(0, 716 * f), (724 * f, 716 * f)]
            g = max(f, hs / 614)
            for p, (px, pw) in zip(panels, geo):
                pk = kids(p)
                rs(p["id"], pw, hs)
                mv(p["id"], px, 0)
                inner = [c for c in p["children"] if c["name"].startswith("Снимок")][0]
                b = inner["bounds"]
                rs(inner["id"], b["width"] * g, b["height"] * g)
                mv(inner["id"], b["x"] * g, b["y"] * g)
                rs(pk["Тон"]["id"], pw, 400 * s)
                mv(pk["Тон"]["id"], 0, hs - 400 * s)
                rs(pk["Затемнение"]["id"], pw, hs)
                mv(pk["Абзац"]["id"], max(40, min(576 * f, pw - 40 - 416)), hs - 48 - 108)
                fs(pk["Слово"]["id"], 32 * s)
                mv(pk["Слово"]["id"], 40, hs - 48 - 32 * s)
                mv(pk["Номер"]["id"], 40, hs - 48 - 32 * s - 32)

print("\n".join(report))
CH = 70
for i in range(0, len(ops), CH):
    (HERE / f"ops_{i // CH:02d}.json").write_text(json.dumps(ops[i:i + CH], ensure_ascii=False), encoding="utf-8")
print(len(ops), "операций,", math.ceil(len(ops) / CH), "пачек")
