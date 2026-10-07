"""Д3в шаг 1: варианты A / B для 09, 10, 11–подвал на 1440×900 (s = u = 1).

  python tools/d3v_variants_gen.py clones            # → _figma/d3v_ops1.json: секция, клоны действующих кадров, шапка сайта, подписи рядов
  python tools/d3v_variants_gen.py layout            # читает _figma/d3v_clones.json (get_nodes_info клонов) → _figma/d3v_ops2_<ряд>.json

Раскладка (подробно — ЖУРНАЛ, Д3в шаг 1):
  09 A — два экрана: шапка + «Мы поможем» / фигуры лесенкой + «Белый» (k по высоте); 09 B — три экрана в прежнем порядке.
  10 A — шапка + история вечера (пункты, цифры, суть) / коллаж + название; 10 B — шапка / тело одним экраном (название на фото).
  11 A — два экрана: «О нас» + «Связаться» / «Контакты» + подвал; 11 B — три экрана, по блоку на экран.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE.parent / "_figma"
HEADER = "307:2542"                       # экземпляр шапки сайта (логотип + «Меню»)
SEC = {"x": -4506, "y": 63700, "w": 8000, "h": 4100}
COLS = [100, 1640, 3180, 4720, 6260]
ROWS = {"09": 280, "10": 1580, "11": 2880}
H = 900

# ряд → [(вариант, экран, подпись, базовый кадр, доп. клоны [(id, y)])]
FRAMES = {
    "09": [("A", 1, "шапка и «Мы поможем»", "207:1882", []),
           ("A", 2, "фигуры и «Белый»", "207:1882", []),
           ("B", 1, "шапка", "207:1882", []),
           ("B", 2, "фигуры", "207:1882", []),
           ("B", 3, "«Белый» и «Мы поможем»", "207:1882", [])],
    "10": [("A", 1, "шапка и история вечера", "218:882", []),
           ("A", 2, "коллаж и название", "218:882", []),
           ("B", 1, "шапка", "218:882", []),
           ("B", 2, "тело одним экраном", "218:882", [])],
    "11": [("A", 1, "11 О нас + 12 Связаться", "191:890", [("191:895", 620)]),
           ("A", 2, "Контакты + подвал", "191:901", [("191:930", 752)]),
           ("B", 1, "11 О нас", "191:890", []),
           ("B", 2, "12 Связаться", "191:895", []),
           ("B", 3, "Контакты + подвал", "191:901", [("191:930", 752)])],
}
AUTO = {"191:890", "191:895", "191:901"}  # кадры с автолейаутом: снять, иначе высоту не задать
ROW_TITLE = {"09": "09 Дресс-код · A — два экрана / B — три экрана",
             "10": "10 Вечера · A — шапка + история / коллаж · B — шапка / тело одним экраном",
             "11": "11 О нас · 12 Связаться · Контакты · подвал · A — два экрана / B — три экрана"}


def name(row, v, scr, label):
    return f"Д3в · {v} · {row} · экран {scr} — {label} · 1440×900"


def clones():
    ops = [{"type": "create_section", "params": {"name": "Д3в · 09 / 10 / 11–подвал в экран · варианты A / B (2026-10-06)",
                                                 "x": SEC["x"], "y": SEC["y"], "width": SEC["w"], "height": SEC["h"]}}]
    for row, fr in FRAMES.items():
        ops.append({"type": "create_text", "params": {"parentId": "$0.id", "name": f"Подпись ряда {row}", "text": ROW_TITLE[row],
                    "x": 100, "y": ROWS[row] - 110, "fontFamily": "Unbounded", "fontStyle": "Regular", "fontSize": 40,
                    "fillColor": "#c6c2b6", "textAutoResize": "WIDTH_AND_HEIGHT"}})
        for i, (v, scr, label, base, extra) in enumerate(fr):
            n = len(ops)
            ops.append({"type": "clone_node", "params": {"nodeId": base, "parentId": "$0.id", "x": COLS[i], "y": ROWS[row]}})
            if base in AUTO:
                ops.append({"type": "set_auto_layout", "params": {"nodeId": f"${n}.id", "layoutMode": "NONE"}})
            ops.append({"type": "resize_nodes", "params": {"nodeIds": [f"${n}.id"], "width": 1440, "height": H}})
            ops.append({"type": "rename_node", "params": {"nodeId": f"${n}.id", "name": name(row, v, scr, label)}})
            for eid, y in extra:
                ops.append({"type": "clone_node", "params": {"nodeId": eid, "parentId": f"${n}.id", "x": 0, "y": y}})
            ops.append({"type": "clone_node", "params": {"nodeId": HEADER, "parentId": f"${n}.id", "x": 0, "y": 0}})
    (OUT / "d3v_ops1.json").write_text(json.dumps(ops, ensure_ascii=False), encoding="utf-8")
    print(len(ops), "операций")


# ---------- проход 2: раскладка ----------
T = 104                                    # верхняя линия содержимого
ops = {}


class F:
    """Кадр-клон: узлы первого уровня по имени (первый с таким именем)."""
    def __init__(self, row, fr):
        self.row, self.fr, self.id = row, fr, fr["id"]
        self.all = fr["children"]
        self.k = {}
        for c in self.all:
            self.k.setdefault(c["name"], c)

    def __getitem__(self, n):
        return self.k[n]

    def op(self, t, **p):
        ops.setdefault(self.row, []).append({"type": t, "params": p})

    def mv(self, node, x, y):
        self.op("move_nodes", nodeIds=[node["id"]], x=round(x, 1), y=round(y, 1))

    def rs(self, node, w, h):
        self.op("resize_nodes", nodeIds=[node["id"]], width=round(w, 2), height=round(h, 1))

    def fs(self, node, size):
        self.op("set_text", nodeId=node["id"], fontSize=round(size, 1))

    def rm(self, nodes):
        ids = [n["id"] for n in nodes]
        if ids:
            self.op("delete_nodes", nodeIds=ids)

    def keep(self, prefixes):
        """Удалить всё, кроме шапки сайта и узлов с именами на prefixes."""
        self.rm([c for c in self.all if c["name"] != "Header" and not c["name"].startswith(tuple(prefixes))])


def frames_by_name():
    return {f["name"]: f for f in json.load(open(OUT / "d3v_clones.json", encoding="utf-8"))}


def nm(row, v, scr):
    return next(name(row, vv, sc, label) for vv, sc, label, *_ in FRAMES[row] if vv == v and sc == scr)


# ----- 09 -----
HEAD09 = ("Номер секции", "Заголовок", "Интро")
HELP09 = ("Мы поможем", "Сервис")
K_RULES = ["К · Бабочка", "К · Рубашка", "К · Смокинг", "К · Туфли"]
D_RULES = ["Д · Причёска", "Д · Украшения", "Д · Платье", "Д · Обувь"]


def head09(f):
    f.mv(f["Номер секции"], 64, T)
    f.mv(f["Заголовок — строка 1"], 304, T + 56)
    f.mv(f["Заголовок — строка 2 (на оси)"], 720, T + 176)
    f.mv(f["Интро"], 64, T + 340)


def help09(f, bottom=H - 48):
    top = bottom - 184                     # метка → низ «Сервис 3»: 184, как в макете
    for n, dy in (("Мы поможем · метка", 0), ("Сервис 1", 32), ("Сервис 2", 72), ("Сервис 3", 130)):
        f.mv(f[n], f[n]["bounds"]["x"], top + dy)


def marks09(f):
    """8 «+» по 4 линии (2 подложки + 2 штриха), порядок макета: К бабочка, рубашка, смокинг, туфли; Д причёска, украшения, платье, обувь."""
    sub = [c for c in f.all if c["name"] == "+ · подложка"]
    plus = [c for c in f.all if c["name"] == "+"]
    return [sub[2 * i:2 * i + 2] + plus[2 * i:2 * i + 2] for i in range(8)]


def figures09(f, k, d, top=T):
    """Фигуры лесенкой: «Кавалерам» на top, фото 400k × 629k (правый край 704), «Дамам» на top + d·k, правила на высоте «+»."""
    kx, ky = 704 - 400 * k, top + 65 * k
    dx, dy = 720, top + (d + 40) * k
    f.fs(f["Роль · Кавалерам"], 150 * k); f.mv(f["Роль · Кавалерам"], 64, top)
    f.fs(f["Роль · Дамам"], 150 * k); f.mv(f["Роль · Дамам"], 720, top + d * k)
    f.mv(f["Фото · Кавалер"], kx, ky); f.rs(f["Фото · Кавалер"], 400 * k, 629 * k)
    f.mv(f["Фото · Дама"], dx, dy); f.rs(f["Фото · Дама"], 400 * k, 629 * k)
    f.mv(f["Номер · Кавалерам"], 736, top + 85 * k)
    f.mv(f["Номер · Дамам"], dx + 400 * k + 16, top + (d + 84) * k)
    my = []
    for i, grp in enumerate(marks09(f)):
        ox, oy, nx, ny = (304, 680, kx, ky) if i < 4 else (720, 840, dx, dy)
        a = grp[0]["bounds"]                              # подложка-горизонталь: центр «+» ≈ (x + 9, y)
        cx, cy = a["x"] + 9, a["y"]
        ncx, ncy = nx + (cx - ox) * k, ny + (cy - oy) * k
        for ln in grp:
            b = ln["bounds"]
            f.mv(ln, b["x"] + ncx - cx, b["y"] + ncy - cy)
        my.append(ncy)
    for names, ys, x in ((K_RULES, my[:4], kx - 16 - 224), (D_RULES, my[4:], dx + 400 * k + 16)):
        bottom = -1e9
        for n, y in zip(names, ys):
            r = f[n]
            t = max(y - 9, bottom + 8)                    # как --nudge на сайте: нижнее сдвигается
            f.mv(r, x, t)
            bottom = t + r["bounds"]["height"]
    return ky + 629 * k, dy + 629 * k


def white09(f, k, top, cont_min):
    f.fs(f["Белый · слово"], 230 * k)
    f.mv(f["Белый · слово"], 64, top)
    f.mv(f["Белый · продолжение"], 720, max(top + 119 * k, cont_min))


def lay09(fb):
    f = F("09", fb[nm("09", "A", 1)])                     # A1 — шапка + «Мы поможем»
    f.keep(HEAD09 + HELP09); head09(f); help09(f)
    f = F("09", fb[nm("09", "A", 2)])                     # A2 — лесенка 144 + «Белый» под фото кавалера, низ «Белого» на H − 40
    f.keep(("Роль", "Фото", "Номер ·", "К ·", "Д ·", "+", "Белый"))
    d, k = 144, (H - 40 - 24 - T) / 878
    kb, db = figures09(f, k, d)
    white09(f, k, kb + 24, db + 24)
    print(f"09 A2: k = {k:.3f}, лесенка {d}")
    f = F("09", fb[nm("09", "B", 1)]); f.keep(HEAD09); head09(f)
    f = F("09", fb[nm("09", "B", 2)]); f.keep(("Роль", "Фото", "Номер ·", "К ·", "Д ·", "+"))
    k = (H - 40 - T) / (185 + 669)
    figures09(f, k, 185)
    print(f"09 B2: k = {k:.3f}")
    f = F("09", fb[nm("09", "B", 3)]); f.keep(("Белый",) + HELP09)
    white09(f, 1, T + 56, 0); help09(f)


# ----- 10 -----
HEAD10 = ("Метка", "Заголовок", "Подзаголовок")
STORY10 = ("Счётчик", "Пункт", "Цифра", "Подпись ·", "Суть")
SLOTS = {"B": (0, 600), "A": (160, 360), "C": (80, 360), "D": (280, 200)}   # сдвиг от верха B, высота
TEXT_MAX = 246                            # «Суть · Кашемир» — самая длинная (6 строк)


def head10(f):
    f.mv(f["Метка"], 64, T)
    f.mv(f["Заголовок · 1"], 64, T + 56)
    f.mv(f["Заголовок · 2"], 720, T + 176)
    f.mv(f["Подзаголовок"], 720, T + 376)


def story10(f, list_top, text_top):
    f.mv(f["Счётчик"], 64, list_top)
    f.mv(f["Пункт · Омега"], 64, list_top + 40)
    f.mv(f["Пункт · Кашемир"], 64, list_top + 64)
    dy = text_top - 1536
    for c in f.all:
        if c["name"].startswith(("Цифра", "Подпись ·", "Суть")):
            f.mv(c, c["bounds"]["x"], c["bounds"]["y"] + dy)


def collage10(f, top, k, name_top):
    for c in f.all:
        if c["name"].startswith("Слот"):
            off, h = SLOTS[c["name"].split()[1]]
            f.mv(c, c["bounds"]["x"], top + off * k)
            f.rs(c, c["bounds"]["width"], h * k)
            ph = c["children"][0]
            f.rs(ph, ph["bounds"]["width"], h * k)
    g = f["Название"]
    f.mv(g, 64, name_top); f.rs(g, 1312, 324 * k)
    for i, ch in enumerate(g["children"]):
        f.fs(ch, 191 * k)
        f.mv(ch, 0, [0, 162, 340, 502][i] * k)


def lay10(fb):
    text_top = H - 48 - TEXT_MAX                         # самая длинная суть низом на H − 48
    f = F("10", fb[nm("10", "A", 1)]); f.keep(HEAD10 + STORY10); head10(f); story10(f, T + 376, text_top)
    f = F("10", fb[nm("10", "A", 2)]); f.keep(("Слот", "Название"))
    k = (H - 40 - T) / 834
    collage10(f, T, k, T + 510 * k)
    print(f"10 A2: k = {k:.3f}")
    f = F("10", fb[nm("10", "B", 1)]); f.keep(HEAD10); head10(f)
    f = F("10", fb[nm("10", "B", 2)]); f.keep(STORY10 + ("Слот", "Название"))
    top = T + 40
    k = (text_top - 40 - top) / 600
    story10(f, T, text_top)
    collage10(f, top, k, top + 600 * k - 324 * k)
    print(f"10 B2: k = {k:.3f}")


# ----- 11 -----
def lay11(fb):
    for v, scr in (("A", 1), ("B", 1)):
        f = F("11", fb[nm("11", v, scr)])
        f.mv(f["Номер секции"], 64, T); f.mv(f["Цитата и подпись"], 288, T)
    f = F("11", fb[nm("11", "B", 2)])
    f.mv(f["Номер секции"], 64, T); f.mv(f["Текст CTA"], 288, T); f.mv(f["Link / Text"], 1133, T)
    for v, scr in (("A", 2), ("B", 3)):
        f = F("11", fb[nm("11", v, scr)])
        f.mv(f["Контактные данные"], 64, T); f.mv(f["Грейдж-панель формы"], 848, T)
        foot = f["Footer"]
        f.op("set_auto_layout", nodeId=foot["children"][1]["id"], paddingTop=48, paddingBottom=48)
        f.mv(foot, 0, H - 149)


def layout():
    fb = frames_by_name()
    lay09(fb); lay10(fb); lay11(fb)
    for row, o in ops.items():
        (OUT / f"d3v_ops2_{row}.json").write_text(json.dumps(o, ensure_ascii=False), encoding="utf-8")
        print(row, len(o), "операций")


if __name__ == "__main__":
    {"clones": clones, "layout": layout}[sys.argv[1]]()
