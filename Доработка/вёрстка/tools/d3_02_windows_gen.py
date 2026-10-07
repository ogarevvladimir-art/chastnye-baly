"""02 «Вечер» A на проверочных окнах. python gen_02w.py <W> <H> <open 1..5> <section> <x> <y> [--plan]

Модель (1440×900 = 1:1):
  u = (min(W,1920) − 128) / 1312, s = min(u, H/900), k = min(s, (H − 206 − descMax) / 623)
  шапка: метка 104; H2 120k, l1 top 104+15+17k, l2 = l1 + 96k, x0+336u
  список: верх = H − 64 − (360k + 14k + 23 + descMax); строка 72k (16k + имя 38,4k + 17,6k); раскрытая + 14k + мета 15 + 8 + описание
  колонка справа x0+896u, ширина 416u; текст в ней — min(416, 416u) px; лид сверху 104; итог прижат к H − 64; фото — остаток
"""
import json, sys
from fontTools.ttLib import TTFont

FONTS = "C:/Users/ogare/Desktop/Мои документы/Plyaskin group/Частные балы сайт/site/fonts/"
_f = TTFont(FONTS + "unbounded-regular.woff2")
_cm, _hm, _upm = _f.getBestCmap(), _f["hmtx"], _f["head"].unitsPerEm


def tw(s, size, ls):
    s = s.upper()
    return sum(_hm[_cm.get(ord(c), _cm[32])][0] for c in s) / _upm * size + ls * size * len(s)


def lines(text, width, size=12, ls=0.02):
    n, cur = 1, ""
    for w in text.split(" "):
        t = (cur + " " + w).strip()
        if tw(t, size, ls) > width and cur:
            n, cur = n + 1, w
        else:
            cur = t
    return n


LEAD = "Сценарий каждого бала пишется заново — под конкретных гостей, локацию и настроение. Чтобы дать общее представление, вот как может выглядеть структура вечера:"
NOTE = ("а не готовая программа. Мы адаптируем сценарий под ваш формат: от камерного вечера на тридцать человек до масштабного бала на двести. "
        "Длительность, количество пауз и интенсивность танцевальной части подстраиваются под ваших гостей.")
STEPS = [
    ("18:00", "60 мин", "тихо", "Сбор гостей и приветствие", 3,
     "Гости приходят, знакомятся, общаются за фуршетом. В зале играет оркестр.", "223:2467"),
    ("19:00", "20 мин", "вступление", "Торжественное открытие", 6,
     "Первыми выходят хозяева бала. Выступают оперные артисты и балетная труппа — первые минуты задают тон всему вечеру. Затем — вальс-открытие, после которого на паркет приглашают всех гостей.", "223:2468"),
    ("19:20", "150 мин", "пик", "Танцевальная программа", 12,
     "Вальсы, кадрили, свинг, фокстрот, латина. Танцмейстер ведёт зал: чередует ритмы, вовлекает гостей, следит за темпом. Между танцами — паузы для общения и фуршетов.", "223:2469"),
    ("21:50", "30 мин", "внимание в зал", "Шоу-номера", 9,
     "Выступления профессиональных танцоров, совместные номера, хореография от гостей — в эти моменты всё внимание на паркете.", "223:2470"),
    ("22:20", "40 мин", "общий выход", "Финальный танец и завершение", 9,
     "Общий финальный вальс: все гости выходят на паркет. После этого вечер завершается.", "223:2471"),
]
SLATE, LIGHT, G80, G50, G35, DIV, TERRA = "#222222", "#c6c2b6", "#aba79acc", "#aba79a80", "#aba79a59", "#aba79a33", "#c96a42"

W, H, OPEN = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
SEC, FX, FY = sys.argv[4], float(sys.argv[5]), float(sys.argv[6])
X0 = 64
u = (min(W, 1920) - 128) / 1312
s = min(u, H / 900)
dw = min(560, 720 * u)                       # ширина описания
MEAS = {560: [36, 72, 54, 54, 36], 491.7: [36, 72, 72, 54, 36]}   # высоты в Figma
desc_h = MEAS[560 if dw >= 560 else 491.7]
dmax = max(desc_h)
k = min(s, (H - 206 - dmax) / 622)
cw = min(416, 416 * u)                       # ширина текста правой колонки
xc = X0 + 896 * u
LEAD_H = {416: 72, 392.5: 90, 365.3: 90, 284.1: 108}
NOTE_H = {416: 108, 392.5: 126, 365.3: 126, 284.1: 180}
lead_h = LEAD_H[round(cw, 1)]
note_h = NOTE_H[round(cw, 1)]

r = lambda v: round(v, 1)
plan = dict(W=W, H=H, u=r(u), s=r(s), k=round(k, 4), dw=r(dw), desc_h=desc_h, cw=r(cw), lead_h=lead_h, note_h=note_h)

ops = []
F = "$0.id"


def op(t, **p):
    ops.append({"type": t, "params": p})
    return len(ops) - 1


def ref(i):
    return f"${i}.id"


def clone(node, x, y, name):
    i = op("clone_node", nodeId=node, parentId=F, x=r(x), y=r(y))
    op("rename_node", nodeId=ref(i), name=name)
    return i


def text(t, x, y, name, size=11, color=G80, ls=40, lh=140, family="Unbounded", case="UPPER", w=None):
    p = dict(parentId=F, text=t, x=r(x), y=r(y), fontFamily=family, fontSize=round(size, 2), fillColor=color,
             letterSpacingUnit="PERCENT", letterSpacingValue=ls, lineHeightUnit="PERCENT", lineHeightValue=lh, name=name)
    if case:
        p["textCase"] = case
    i = op("create_text", **p)
    if w:
        op("resize_nodes", nodeIds=[ref(i)], width=r(w), height=20)
        op("set_text", nodeId=ref(i), textAutoResize="HEIGHT")
    return i


op("create_frame", parentId=SEC, name=f"Д3 · 02 · A · {'покой (01)' if OPEN == 1 else f'наведение 0{OPEN}'} · {W}×{H}",
   x=FX, y=FY, width=W, height=H, fillColor=SLATE, clipsContent=True)

# Шапка
clone("223:2473", X0, 104, "Номер секции")
l1 = 104 + 15 + 17 * k
i = clone("223:2596", X0, l1, "Заголовок · 1")
op("set_text", nodeId=ref(i), fontSize=round(120 * k, 2))
i = clone("223:2597", X0 + 336 * u, l1 + 96 * k, "Заголовок · 2")
op("set_text", nodeId=ref(i), fontSize=round(120 * k, 2))

# Правая колонка: лид, фото, итог
i = clone("223:2475", xc, 104, "Лид")
op("resize_nodes", nodeIds=[ref(i)], width=r(cw), height=20)
op("set_text", nodeId=ref(i), textAutoResize="HEIGHT")
note_top = H - 64 - note_h
big_top = note_top - 16 * k - 38.4 * k
ph_top = 104 + lead_h + 32 * k
ph_bot = big_top - 40 * k
i = clone(STEPS[OPEN - 1][6], xc, ph_top, f"Фото 0{OPEN}")
op("resize_nodes", nodeIds=[ref(i)], width=r(416 * u), height=r(ph_bot - ph_top))
op("set_opacity", nodeIds=[ref(i)], opacity=1)
text("Это ориентир,", xc, big_top, "Итог · крупно", size=48 * k, color=LIGHT, ls=-5, lh=80, family="Old Standard TT", case=None)
i = text(NOTE, xc, note_top, "Итог · капсом", size=12, ls=2, lh=150, w=cw)
op("set_text_range", nodeId=ref(i), startOffset=0, endOffset=24, color=LIGHT)
plan.update(photo=[r(xc), r(ph_top), r(416 * u), r(ph_bot - ph_top)], note_top=r(note_top), big_top=r(big_top))

# Список этапов
top = H - 64 - (373 * k + 23 + dmax)
plan["list_top"] = r(top)
plan["title_bottom"] = r(l1 + 192 * k)
xn = X0 + 112 * u
for n, (t, dur, inten, name, w, desc, _) in enumerate(STEPS, 1):
    on = n == OPEN
    op("create_rectangle", parentId=F, x=X0, y=r(top), width=r(832 * u), height=w if on else 1,
       fillColor=TERRA if on else DIV, name=f"Строка 0{n} · линия")
    text(t, X0, top + 16 * k + (38.4 * k - 15) / 2, f"Строка 0{n} · время", color=LIGHT if on else G50)
    text(name, xn, top + 16 * k, f"Строка 0{n} · название", size=48 * k, color=LIGHT if on else G50, ls=-5, lh=80,
         family="Old Standard TT", case=None)
    if on:
        my = top + 16 * k + 38.4 * k + 13 * k
        text(dur, xn, my, f"Строка 0{n} · длительность", color=G80)
        text(inten, xn + tw(dur, 11, 0.4) + 24, my, f"Строка 0{n} · интенсивность", color=TERRA)
        text(desc, xn, my + 23, f"Строка 0{n} · описание", size=12, ls=2, lh=150, w=dw)
        top += 72 * k + 13 * k + 23 + desc_h[n - 1]
    else:
        top += 72 * k
plan["list_bottom"] = r(top)

i = op("clone_node", nodeId="307:2470", parentId=F, x=0, y=0)
op("resize_nodes", nodeIds=[ref(i)], width=W, height=72)

if "--plan" in sys.argv:
    print(json.dumps(plan, ensure_ascii=False))
else:
    print(json.dumps(ops, ensure_ascii=False, separators=(",", ":")))
