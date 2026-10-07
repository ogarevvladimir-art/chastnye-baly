"""Д3в шаг 2: выбранное (09 A, 10 B, 11–подвал A) на проверочных окнах — секция «Д3в · выбранное … на проверочных окнах».
Система «в экран» (Д2): x и колонки × u, y и крупное × k (k ≤ s = min(u, H/900)), мелкий текст — px.

  python tools/d3v_windows_gen.py 0   # секция + клоны кадров вариантов → _figma/d3v_win0_<N>.json
  python tools/d3v_windows_gen.py 1   # дерево _figma/d3v_win_tree.json → ширины и кегли текстов, которые надо мерить → _figma/d3v_win1_<N>.json
  python tools/d3v_windows_gen.py 2   # дерево _figma/d3v_win_tree2.json (фактические высоты) → всё остальное → _figma/d3v_win2_<N>.json

Модели (то же считает код сайта):
  09 экран 1: шапка k = s (метка 104, строка 1 от X(304) на 104 + 56s, строка 2 от оси на 104 + 176s, 150s);
      «Мы поможем» — три колонки 336u / 320u / 336u (вторая правым краем к оси), ступени 40s / 98s, нижняя кромка на H − 48, метка на 32 выше;
      интро на 104 + 340s, но не ниже «метка − 32 − интро» и не выше низа строки 1 + 24.
  09 экран 2: лесенка 144k; «Кавалерам» 150k на 104, фото 400k × 629k правым краем на оси − 16u, «Дамам» на 104 + 144k от оси, фото дамы
      на 104 + 184k; правила — на высоте своих «+» (−9, снизу вверх не наезжают, зазор 8); «Белый» 230k на 24 ниже фото кавалера,
      продолжение — под фото дамы (+24), не выше «Белый» + 119k. k = min(s, (H − 168) / 878, (H − 168 − h_прод) / 813).
  10 экран 1: шапка k = s, лид от оси на 104 + 376s колонкой min(272, 272u).
  10 экран 2: счётчик 104, пункты 144 / 168 (px); суть 36s колонкой 656u от оси, низом самой длинной на H − 48, цифры — от верха сути;
      коллаж от 144: слоты × u по x, × k по y; название 191k (строки 162k) низом на низ фото B; k = min(s, (верх сути − 40 − 144) / 600).
  11 экран 1: «О нас» — метка 104, цитата 36s колонкой 960u от X(288), подпись через 36s; полоса «Связаться» низом на H:
      поля 96s, текст от X(288) шириной до ссылки − 24, ссылка к правому полю.
  11 экран 2: данные от X(288) (телефон и почта 64s, шаги 40s), панель от X(848) шириной 528u на 104: поля 40kp, зазоры 28kp, поле «о вечере» max(52, 120kp),
      «отправить» 72kp; kp = min(s, (H − 152 − 247) / 377); подвал 149 (поля 48) низом на H.

  python tools/d3v_windows_gen.py 3   # правка 2026-10-06: сжатые шапки 09 / 10 / 11 экран 1 (дерево _figma/d3v_win_tree3.json) → _figma/d3v_win3.json
      Не в экран: высота = низ содержимого + 96. 09 — интро под строкой 1 (+24), «Мы поможем» на 64 ниже интро и строки 2;
      10 — как было, без нижней пустоты; 11 — полоса «Связаться» на 96 ниже подписи «О нас».
"""
import json
import math
import sys
from pathlib import Path

OUT = Path(__file__).parent.parent / "_figma"
WINS = [(1440, 900), (1920, 950), (1366, 650), (1280, 600), (1024, 650)]
KINDS = [("09h", "332:4056", "09 · экран 1 — шапка и «Мы поможем»"),
         ("09f", "332:4122", "09 · экран 2 — фигуры и «Белый»"),
         ("10h", "332:4487", "10 · экран 1 — шапка"),
         ("10b", "332:4537", "10 · экран 2 — тело (Омега)"),
         ("11a", "332:4588", "11 · экран 1 — О нас + Связаться"),
         ("11c", "332:4610", "11 · экран 2 — Контакты + подвал")]
SEC = {"x": -4506, "y": 68300, "w": 6 * 2020 + 100, "h": 5 * 1250 + 300}
T = 104


def fname(W, H, label):
    return f"Д3в · {W}×{H} · {label}"


# ---------- проход 0: секция и клоны ----------
def pass0():
    b1 = [{"type": "create_section", "params": {"name": "Д3в · выбранное (09 A, 10 B, 11–подвал A) на проверочных окнах (2026-10-06)",
                                                "x": SEC["x"], "y": SEC["y"], "width": SEC["w"], "height": SEC["h"]}}]
    for r, (W, H) in enumerate(WINS):
        b1.append({"type": "create_text", "params": {"parentId": "$0.id", "name": f"Подпись ряда {W}×{H}", "text": f"{W} × {H}",
                   "x": 100, "y": 280 + r * 1250 - 110, "fontFamily": "Unbounded", "fontStyle": "Regular", "fontSize": 40,
                   "fillColor": "#c6c2b6", "textAutoResize": "WIDTH_AND_HEIGHT"}})
    (OUT / "d3v_win0_0.json").write_text(json.dumps(b1, ensure_ascii=False), encoding="utf-8")
    print("секция: d3v_win0_0.json — затем SEC_ID в d3v_win0_1/2 подставить из ответа")


def pass0_clones(sec):
    batches = [[], []]
    for r, (W, H) in enumerate(WINS):
        b = batches[r // 3]
        for i, (kind, src, label) in enumerate(KINDS):
            n = len(b)
            b.append({"type": "clone_node", "params": {"nodeId": src, "parentId": sec, "x": 100 + i * 2020, "y": 280 + r * 1250}})
            b.append({"type": "rename_node", "params": {"nodeId": f"${n}.id", "name": fname(W, H, label)}})
            b.append({"type": "resize_nodes", "params": {"nodeIds": [f"${n}.id"], "width": W, "height": H}})
    for j, b in enumerate(batches):
        (OUT / f"d3v_win0_{j + 1}.json").write_text(json.dumps(b, ensure_ascii=False), encoding="utf-8")
        print(f"d3v_win0_{j + 1}.json", len(b))


# ---------- проходы 1 и 2 ----------
class Fr:
    def __init__(self, node, W, H, ops):
        self.n, self.W, self.H, self.ops = node, W, H, ops
        self.u = (W - 128) / 1312
        self.s = min(self.u, H / 900)

    def X(self, x):
        return 64 + (x - 64) * self.u

    def c(self, *path, node=None):
        n = node or self.n
        for nm in path:
            n = next(ch for ch in n["children"] if ch["name"] == nm)
        return n

    def all(self, prefix):
        return [ch for ch in self.n["children"] if ch["name"].startswith(prefix)]

    def h(self, n):
        return n["bounds"]["height"]

    def op(self, t, **p):
        self.ops.append({"type": t, "params": p})

    def mv(self, n, x, y):
        self.op("move_nodes", nodeIds=[n["id"]], x=round(x, 1), y=round(y, 1))

    def rs(self, n, w, h):
        self.op("resize_nodes", nodeIds=[n["id"]], width=round(max(w, 0.01), 2), height=round(max(h, 0.01), 1))

    def fs(self, n, size):
        st = n.get("styles", {})
        if "mixed" in (st.get("fontFamily"), st.get("fontStyle"), st.get("fontSize")):
            self.op("set_text_range", nodeId=n["id"], startOffset=0, endOffset=len(n["characters"]), fontSize=round(size, 1))
        else:
            self.op("set_text", nodeId=n["id"], fontSize=round(size, 1))

    def tw(self, n, w):
        """Текст с переносом: ширина задана, высота по тексту."""
        self.rs(n, w, self.h(n))
        self.op("set_text", nodeId=n["id"], textAutoResize="HEIGHT")

    def free(self, n):
        self.op("set_auto_layout", nodeId=n["id"], layoutMode="NONE")


def k09f(f, h_c):
    return min(f.s, (f.H - 168) / 878, (f.H - 168 - h_c) / 813)


K_RULES = ["К · Бабочка", "К · Рубашка", "К · Смокинг", "К · Туфли"]
D_RULES = ["Д · Причёска", "Д · Украшения", "Д · Платье", "Д · Обувь"]
SVC = {"Сервис 1": 336, "Сервис 2": 320, "Сервис 3": 336}
TEXT10 = ("Суть · Омега", "Суть · Кашемир")


def p1(kind, f):
    u, s = f.u, f.s
    f.rs(f.c("Header"), f.W, 72)
    if kind == "09h":
        f.tw(f.c("Интро"), min(320, 320 * u))
        for n, w in SVC.items():
            f.tw(f.c(n), min(w, w * u))
        f.fs(f.c("Заголовок — строка 1"), 150 * s)
        f.fs(f.c("Заголовок — строка 2 (на оси)"), 150 * s)
    elif kind == "09f":
        for n in K_RULES:
            f.tw(f.c(n), min(224, 224 * u))
        for n in D_RULES:
            f.tw(f.c(n), min(240, 240 * u))
        f.tw(f.c("Белый · продолжение"), min(400, 400 * u))
    elif kind == "10h":
        f.tw(f.c("Подзаголовок"), min(272, 272 * u))
    elif kind == "10b":
        for n in TEXT10:
            f.fs(f.c(n), 36 * s)
            f.tw(f.c(n), 656 * u)
        f.tw(f.c("Пункт · Кашемир"), min(352, 352 * u))
    elif kind == "11a":
        g = f.c("Цитата и подпись")
        f.free(g)
        f.fs(f.c("Цитата и подпись", "Цитата"), 36 * s)
        f.tw(f.c("Цитата и подпись", "Цитата"), min(960 * u, f.W - 64 - f.X(288)))
        f.tw(f.c("Цитата и подпись", "Подпись"), min(416, 416 * u))
        band = f.c("CTABand — 12 Связаться")
        f.free(band)
        txt = f.c("Текст CTA", node=band)
        f.free(txt)
        tw = f.W - 64 - 243 - 24 - f.X(288)
        f.tw(f.c("Заголовок CTA", node=txt), tw)
        f.tw(f.c("Подводка", node=txt), min(416, 416 * u))
    elif kind == "11c":
        data = f.c("Контактные данные")
        f.free(data)
        f.tw(f.c("Вступление", node=data), min(416, 416 * u))
        for grp, num in (("Телефон", "Номер телефона"), ("Электронная почта", "Адрес Email")):
            g = f.c(grp, node=data)
            f.free(g)
            f.fs(f.c(num, node=g), 64 * s)


def kp11(f, h_c=34):
    """Шаг панели: высота при kp = 213 + согласие + 377·kp (согласие — 2 строки, на узкой панели 3)."""
    return min(f.s, (f.H - 152 - 213 - h_c) / 377)


def p2(kind, f):
    u, s, X, H, W = f.u, f.s, f.X, f.H, f.W
    A = X(720)
    if kind == "09h":
        l1, l2 = f.c("Заголовок — строка 1"), f.c("Заголовок — строка 2 (на оси)")
        f.mv(f.c("Номер секции"), 64, T)
        f.mv(l1, X(304), T + 56 * s)
        f.mv(l2, A, T + 176 * s)
        sv = {n: f.c(n) for n in SVC}
        o3 = max(98 * s, 40 * s + f.h(sv["Сервис 2"]) + 4)      # третья колонка не выше низа второй: они сходятся на оси
        offs = {"Сервис 1": 0, "Сервис 2": 40 * s, "Сервис 3": o3}
        top = H - 48 - max(offs[n] + f.h(sv[n]) for n in SVC)
        f.mv(f.c("Мы поможем · метка"), 64, top - 32)
        f.mv(sv["Сервис 1"], 64, top)
        f.mv(sv["Сервис 2"], A - sv["Сервис 2"]["bounds"]["width"], top + offs["Сервис 2"])
        f.mv(sv["Сервис 3"], A, top + offs["Сервис 3"])
        intro = f.c("Интро")
        y = max(T + 56 * s + f.h(l1) + 24, min(T + 340 * s, top - 32 - 32 - f.h(intro)))
        f.mv(intro, 64, y)
        return f"интро {y:.0f}, «Мы поможем» {top - 32:.0f}"
    if kind == "09f":
        cont = f.c("Белый · продолжение")
        k = k09f(f, f.h(cont))
        d = 144
        kx, ky = A - 16 * u - 400 * k, T + 65 * k
        dx, dy = A, T + (d + 40) * k
        f.fs(f.c("Роль · Кавалерам"), 150 * k); f.mv(f.c("Роль · Кавалерам"), 64, T)
        f.fs(f.c("Роль · Дамам"), 150 * k); f.mv(f.c("Роль · Дамам"), A, T + d * k)
        f.mv(f.c("Фото · Кавалер"), kx, ky); f.rs(f.c("Фото · Кавалер"), 400 * k, 629 * k)
        f.mv(f.c("Фото · Дама"), dx, dy); f.rs(f.c("Фото · Дама"), 400 * k, 629 * k)
        f.mv(f.c("Номер · Кавалерам"), A + 16 * u, T + 85 * k)
        f.mv(f.c("Номер · Дамам"), dx + 400 * k + 16 * u, T + (d + 84) * k)
        # «+»: в кадре варианта 1440 (k0 = 0,834, фото кавалера 370,5 / 158,2, дамы 720 / 257,4) → пересчёт от фото
        k0 = (900 - 168) / 878
        sub = f.all("+ · подложка")
        plus = [ch for ch in f.n["children"] if ch["name"] == "+"]
        my = []
        for i in range(8):
            grp = sub[2 * i:2 * i + 2] + plus[2 * i:2 * i + 2]
            ox, oy, nx, ny = (704 - 400 * k0, 104 + 65 * k0, kx, ky) if i < 4 else (720, 104 + 184 * k0, dx, dy)
            a = grp[0]["bounds"]
            cx, cy = a["x"] + 9, a["y"]
            ncx, ncy = nx + (cx - ox) * k / k0, ny + (cy - oy) * k / k0
            for ln in grp:
                b = ln["bounds"]
                f.mv(ln, b["x"] + ncx - cx, b["y"] + ncy - cy)
            my.append(ncy)
        for names, ys, side in ((K_RULES, my[:4], "k"), (D_RULES, my[4:], "d")):
            bottom = -1e9
            for n, y in zip(names, ys):
                r = f.c(n)
                w = r["bounds"]["width"]
                x = kx - 16 * u - w if side == "k" else dx + 400 * k + 16 * u
                t = max(y - 9, bottom + 8)
                f.mv(r, x, t)
                bottom = t + f.h(r)
        wt = ky + 629 * k + 24
        f.fs(f.c("Белый · слово"), 230 * k)
        f.mv(f.c("Белый · слово"), 64, wt)
        cy = max(wt + 119 * k, dy + 629 * k + 24)
        f.mv(cont, A, cy)
        return f"k {k:.3f}, низ «Белого» {wt + 184 * k:.0f}, низ продолжения {cy + f.h(cont):.0f} (предел {H - 40})"
    if kind == "10h":
        f.mv(f.c("Метка"), 64, T)
        f.fs(f.c("Заголовок · 1"), 150 * s); f.mv(f.c("Заголовок · 1"), 64, T + 56 * s)
        f.fs(f.c("Заголовок · 2"), 150 * s); f.mv(f.c("Заголовок · 2"), A, T + 176 * s)
        f.mv(f.c("Подзаголовок"), A, T + 376 * s)
        return ""
    if kind == "10b":
        f.mv(f.c("Счётчик"), 64, T)
        f.mv(f.c("Пункт · Омега"), 64, T + 40)
        f.mv(f.c("Пункт · Кашемир"), 64, T + 64)
        ht = max(f.h(f.c(n)) for n in TEXT10)
        tt = H - 48 - ht
        for c in f.n["children"]:
            nm = c["name"]
            if nm.startswith(("Цифра", "Подпись ·")):
                f.mv(c, 64, tt + c["bounds"]["y"] - 606)          # в кадре варианта цифры — от 606
        f.mv(f.c("Суть · Омега"), A, tt)
        f.mv(f.c("Суть · Кашемир"), A, tt + 16)                    # скрытый слой вечера 2 — на 16 ниже (вплывает)
        top = 144
        k = min(s, (tt - 40 - top) / 600)
        SL = {"B": (384, 480, 0, 600), "A": (64, 288, 160, 360), "C": (896, 288, 80, 360), "D": (1216, 160, 280, 200)}
        list_bottom = T + 64 + f.h(f.c("Пункт · Кашемир"))
        for c in f.all("Слот"):
            x0, w0, off, h0 = SL[c["name"].split()[1]]
            w, hh = w0 * u, h0 * k
            if x0 == 64:                                       # слот A под пунктами: не выше низа пунктов + 16
                off = max(off, (list_bottom + 16 - top) / k)
            ph = c["children"][0]
            if c["bounds"]["width"] < 1:                           # закрытый слот вечера 2: нулевая ширина по центру
                f.mv(c, X(x0) + w / 2, top + off * k); f.rs(c, 0.01, hh)
                f.mv(ph, -w / 2, 0); f.rs(ph, w, hh)
            else:
                f.mv(c, X(x0), top + off * k); f.rs(c, w, hh)
                f.mv(ph, 0, 0); f.rs(ph, w, hh)
        g = f.c("Название")
        f.mv(g, 64, top + 276 * k); f.rs(g, W - 128, 324 * k)
        for i, ch in enumerate(g["children"]):
            f.fs(ch, 191 * k)
            if ch["styles"].get("textAlignHorizontal") == "RIGHT":
                f.rs(ch, W - 128, ch["bounds"]["height"])
            f.mv(ch, 0, [0, 162, 340, 502][i] * k)
        return f"k {k:.3f}, верх сути {tt:.0f} (самая длинная {ht:.0f})"
    if kind == "11a":
        f.mv(f.c("Номер секции"), 64, T)
        g = f.c("Цитата и подпись")
        q, cap = f.c("Цитата", node=g), f.c("Подпись", node=g)
        f.mv(q, 0, 0); f.mv(cap, 0, f.h(q) + 36 * s)
        f.rs(g, q["bounds"]["width"], f.h(q) + 36 * s + f.h(cap))
        f.mv(g, X(288), T)
        band = f.c("CTABand — 12 Связаться")
        txt = f.c("Текст CTA", node=band)
        ti, le = f.c("Заголовок CTA", node=txt), f.c("Подводка", node=txt)
        f.mv(ti, 0, 0); f.mv(le, 0, f.h(ti) + 20)
        th = f.h(ti) + 20 + f.h(le)
        f.rs(txt, ti["bounds"]["width"], th)
        bh = 96 * s * 2 + th
        f.rs(band, W, bh)
        f.mv(band, 0, H - bh)
        f.mv(f.c("Номер секции", node=band), 64, 96 * s)
        f.mv(txt, X(288), 96 * s)
        f.mv(f.c("Link / Text", node=band), W - 64 - 243, 96 * s)
        return f"полоса {bh:.0f}, низ «О нас» {T + f.h(q) + 36 * s + f.h(cap):.0f} (полоса с {H - bh:.0f})"
    if kind == "11c":
        data = f.c("Контактные данные")
        intro = f.c("Вступление", node=data)
        f.mv(intro, 224 * u, 0)
        y = f.h(intro)
        for grp, num, gap in (("Телефон", "Номер телефона", 27), ("Электронная почта", "Адрес Email", 23)):
            g = f.c(grp, node=data)
            nn = f.c(num, node=g)
            y += 40 * s
            f.mv(f.c(grp, node=data), 224 * u, y)
            f.mv(nn, 0, gap)
            gh = gap + 58 * s
            f.rs(g, 528 * u, gh)
            y += gh
        f.rs(data, 752 * u, y)
        f.mv(data, 64, T)
        kp = kp11(f)
        if 528 * f.u - 80 * kp < 380:                          # согласие на узкой панели — в 3 строки
            kp = kp11(f, 51)
        p = f.c("Грейдж-панель формы")
        f.free(p)
        pw = 528 * u
        iw = pw - 80 * kp
        y = 40 * kp
        title = f.c("Заголовок формы", node=p)
        f.mv(title, 40 * kp, y); y += f.h(title)
        for fld in ("Поле · Как вас зовут", "Поле · Телефон", "Поле · Несколько слов о вечере"):
            fr = f.c(fld, node=p)
            f.free(fr)
            area = f.c("Область ввода", node=fr)
            line = f.c("Линия поля", node=fr)
            val = f.c("Значение", node=area)
            ah = max(52, 120 * kp) if fld.endswith("вечере") else 34
            f.free(area)
            f.rs(area, iw, ah); f.mv(area, 0, 27)
            f.tw(val, iw); f.mv(val, 0, 6)
            f.rs(line, iw, 1); f.mv(line, 0, 27 + ah + 10)
            fh = 27 + ah + 11
            f.rs(fr, iw, fh)
            y += 28 * kp
            f.mv(fr, 40 * kp, y); y += fh
        sub = f.c("Отправка", node=p)
        f.free(sub)
        btn, cons = f.c("Кнопка", node=sub), f.c("Согласие", node=sub)
        f.fs(btn, 72 * kp); f.tw(btn, iw); f.mv(btn, 0, 0)
        f.tw(cons, min(416, iw)); f.mv(cons, 0, 65 * kp + 16)
        sh = 65 * kp + 16 + (51 if iw < 380 else f.h(cons))
        f.rs(sub, iw, sh)
        y += 28 * kp
        f.mv(sub, 40 * kp, y); y += sh + 40 * kp
        f.rs(p, pw, y)
        f.mv(p, X(848), T)
        foot = f.c("Footer")
        f.rs(foot, W, 149)
        f.rs(f.c("Разделитель", node=foot), W, 1)
        f.rs(f.c("Содержимое футера", node=foot), W, 148)
        f.mv(foot, 0, H - 149)
        f.ops.append({"type": "reorder_nodes", "nodeIds": [p["id"]], "params": {"order": "bringToFront"}})   # панель над подвалом
        return f"kp {kp:.3f}, панель {T}…{T + y:.0f} (предел {H - 48})"
    return ""


PAD = 96          # сжатые шапки (правка 2026-10-06): высота по содержимому, под ним 96


def p3(kind, f):
    """Сжатые шапки 09 / 10 / 11 экран 1: не в экран, высота = низ содержимого + 96; кегль и шаги — как у соседей (s)."""
    u, s, X, W = f.u, f.s, f.X, f.W
    A = X(720)
    ops = f.ops
    i0 = len(ops)
    if kind == "09h":
        l1, l2 = f.c("Заголовок — строка 1"), f.c("Заголовок — строка 2 (на оси)")
        f.mv(f.c("Номер секции"), 64, T)
        f.mv(l1, X(304), T + 56 * s)
        f.mv(l2, A, T + 176 * s)
        intro = f.c("Интро")
        yi = T + 56 * s + f.h(l1) + 24                          # интро в левой колонке сразу под строкой 1
        f.mv(intro, 64, yi)
        lab = max(yi + f.h(intro), T + 176 * s + f.h(l2)) + 64   # «Мы поможем» на 64 ниже интро и строки 2
        top = lab + 32
        sv = {n: f.c(n) for n in SVC}
        o3 = max(98 * s, 40 * s + f.h(sv["Сервис 2"]) + 4)
        offs = {"Сервис 1": 0, "Сервис 2": 40 * s, "Сервис 3": o3}
        f.mv(f.c("Мы поможем · метка"), 64, lab)
        f.mv(sv["Сервис 1"], 64, top)
        f.mv(sv["Сервис 2"], A - sv["Сервис 2"]["bounds"]["width"], top + offs["Сервис 2"])
        f.mv(sv["Сервис 3"], A, top + offs["Сервис 3"])
        hh = top + max(offs[n] + f.h(sv[n]) for n in SVC) + PAD
    elif kind == "10h":
        f.mv(f.c("Метка"), 64, T)
        f.mv(f.c("Заголовок · 1"), 64, T + 56 * s)
        f.mv(f.c("Заголовок · 2"), A, T + 176 * s)
        lead = f.c("Подзаголовок")
        f.mv(lead, A, T + 376 * s)
        hh = T + 376 * s + f.h(lead) + PAD
    elif kind == "11a":
        g = f.c("Цитата и подпись")
        q, cap = f.c("Цитата", node=g), f.c("Подпись", node=g)
        gh = f.h(q) + 36 * s + f.h(cap)
        f.mv(f.c("Номер секции"), 64, T)
        f.mv(g, X(288), T)
        band = f.c("CTABand — 12 Связаться")
        txt = f.c("Текст CTA", node=band)
        th = sum(f.h(c) for c in txt["children"]) + 20
        bh = 96 * s * 2 + th
        bt = T + gh + PAD                                         # полоса на 96 ниже подписи
        f.mv(band, 0, bt)
        hh = bt + bh
    else:
        return ""
    ops.insert(i0, {"type": "resize_nodes", "params": {"nodeIds": [f.n["id"]], "width": W, "height": round(hh, 1)}})
    return f"высота {hh:.0f} (окно {f.H})"


def pass3():
    """Сжатые шапки по дереву d3v_win_tree3.json (текущее состояние кадров) → _figma/d3v_win3.json."""
    tree = json.load(open(OUT / "d3v_win_tree3.json", encoding="utf-8"))
    byname = {fr["name"]: fr for fr in tree}
    ops = []
    for W, H in WINS:
        for kind, _, label in KINDS:
            if kind in ("09h", "10h", "11a"):
                rep = p3(kind, Fr(byname[fname(W, H, label)], W, H, ops))
                print(f"{W}×{H} {kind}: {rep}")
    (OUT / "d3v_win3.json").write_text(json.dumps(ops, ensure_ascii=True), encoding="utf-8")
    print("d3v_win3.json", len(ops))


def passN(n):
    tree = json.load(open(OUT / ("d3v_win_tree.json" if n == 1 else "d3v_win_tree2.json"), encoding="utf-8"))
    byname = {fr["name"]: fr for fr in tree}
    for r, (W, H) in enumerate(WINS):
        ops = []
        for kind, _, label in KINDS:
            fr = byname[fname(W, H, label)]
            f = Fr(fr, W, H, ops)
            if n == 1:
                p1(kind, f)
            else:
                rep = p2(kind, f)
                if rep:
                    print(f"{W}×{H} {kind}: {rep}")
        (OUT / f"d3v_win{n}_{r}.json").write_text(json.dumps(ops, ensure_ascii=True), encoding="utf-8")
        print(f"d3v_win{n}_{r}.json", len(ops))


if __name__ == "__main__":
    a = sys.argv[1]
    if a == "0":
        pass0()
    elif a == "0c":
        pass0_clones(sys.argv[2])
    elif a == "3":
        pass3()
    else:
        passN(int(a))
