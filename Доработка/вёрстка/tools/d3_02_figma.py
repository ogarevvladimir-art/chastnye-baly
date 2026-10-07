"""Д3 · 02 «Вечер» A (список этапов) → действующие кадры 1440×900: блок 223:2466 в 191:626 и состояния 223:2492…2570.

python d3_02_figma.py <номер кадра 1..5>  >  ops.json     (1 — покой в 191:626, 2…5 — наведение на строку N)

Перенос, а не пересборка: метка, заголовок, лид, примечание и пять фото сохраняют id; часы, партитура, «Зал сверху»,
итог лесенкой и зона прототипа удаляются. Геометрия — модель 1440×900 (k = 1), как в утверждённом 318:2378 / 318:2413.
Фото — целиком 5 : 6 в «Окне фото» и сдвинуты к точке фокуса (01 0 %, 02 50 %, 03 50 %, 04 0 %, 05 90 %).
"""
import json, sys
from fontTools.ttLib import TTFont

FONTS = "C:/Users/ogare/Desktop/Мои документы/Plyaskin group/Частные балы сайт/site/fonts/"
_f = TTFont(FONTS + "unbounded-regular.woff2")
_cm, _hm, _upm = _f.getBestCmap(), _f["hmtx"], _f["head"].unitsPerEm


def tw(s, size, ls):
    s = s.upper()
    return sum(_hm[_cm.get(ord(c), _cm[32])][0] for c in s) / _upm * size + ls * size * len(s)


# id кадра → id детей: шаг id между кадрами постоянный, порядок детей одинаков
FRAMES = {1: "223:2466", 2: "223:2492", 3: "223:2518", 4: "223:2544", 5: "223:2570"}
KIDS = {  # смещения от id кадра
    "photos": [1, 2, 3, 4, 5], "hall": 6, "label": 7, "lead": 9,
    "drop": [10, 11, 12, 13, 14, 15, 16, 22, 25],  # время, длит., интенс., название, описание, счётчик, партитура, тон, зона
    "note": 24,
}
TITLES = {1: ("223:2596", "223:2597", ["223:2611", "223:2612", "223:2613"]),
          2: ("223:2599", "223:2600", ["223:2614", "223:2615", "223:2616"]),
          3: ("223:2602", "223:2603", ["223:2617", "223:2618", "223:2619"]),
          4: ("223:2605", "223:2606", ["223:2620", "223:2621", "223:2622"]),
          5: ("223:2608", "223:2609", ["223:2623", "223:2624", "223:2625"])}

NOTE = ("а не готовая программа. Мы адаптируем сценарий под ваш формат: от камерного вечера на тридцать человек до масштабного бала на двести. "
        "Длительность, количество пауз и интенсивность танцевальной части подстраиваются под ваших гостей.")
STEPS = [
    ("18:00", "60 мин", "тихо", "Сбор гостей и приветствие", 3,
     "Гости приходят, знакомятся, общаются за фуршетом. В зале играет оркестр."),
    ("19:00", "20 мин", "вступление", "Торжественное открытие", 6,
     "Первыми выходят хозяева бала. Выступают оперные артисты и балетная труппа — первые минуты задают тон всему вечеру. Затем — вальс-открытие, после которого на паркет приглашают всех гостей."),
    ("19:20", "150 мин", "пик", "Танцевальная программа", 12,
     "Вальсы, кадрили, свинг, фокстрот, латина. Танцмейстер ведёт зал: чередует ритмы, вовлекает гостей, следит за темпом. Между танцами — паузы для общения и фуршетов."),
    ("21:50", "30 мин", "внимание в зал", "Шоу-номера", 9,
     "Выступления профессиональных танцоров, совместные номера, хореография от гостей — в эти моменты всё внимание на паркете."),
    ("22:20", "40 мин", "общий выход", "Финальный танец и завершение", 9,
     "Общий финальный вальс: все гости выходят на паркет. После этого вечер завершается."),
]
FOCUS = [0, 0.5, 0.5, 0, 0.9]
LIGHT, G80, G50, DIV, TERRA = "#c6c2b6", "#aba79acc", "#aba79a80", "#aba79a33", "#c96a42"

OPEN = int(sys.argv[1])
FID = FRAMES[OPEN]
base = int(FID.split(":")[1])
kid = lambda d: f"223:{base + d}"

# Модель на 1440×900: u = s = k = 1
X0, XN, XC, CW, DW = 64, 176, 960, 416, 560
DESC_H = [36, 72, 54, 54, 36]            # высоты описаний в Figma на ширине 560
LEAD_H, NOTE_H = 72, 108
note_top = 900 - 64 - NOTE_H             # 728
big_top = note_top - 16 - 38.4           # 673,6
ph_top = 104 + LEAD_H + 32               # 208
ph_h = big_top - 40 - ph_top             # 425,6
PH_FULL = CW * 6 / 5                     # 499,2

ops = []


def op(t, **p):
    ops.append({"type": t, "params": p})
    return len(ops) - 1


ref = lambda i: f"${i}.id"
r = lambda v: round(v, 2)


def text(t, x, y, name, size=11, color=G80, ls=40, lh=140, family="Unbounded", case="UPPER", w=None):
    p = dict(parentId=FID, text=t, x=r(x), y=r(y), fontFamily=family, fontSize=size, fillColor=color,
             letterSpacingUnit="PERCENT", letterSpacingValue=ls, lineHeightUnit="PERCENT", lineHeightValue=lh, name=name)
    if case:
        p["textCase"] = case
    i = op("create_text", **p)
    if w:
        op("resize_nodes", nodeIds=[ref(i)], width=w, height=20)
        op("set_text", nodeId=ref(i), textAutoResize="HEIGHT")
    return i


label = ["покой · 01 «Сбор гостей» раскрыт"] + [f"наведение 0{n} «{STEPS[n - 1][3]}»" for n in range(2, 6)]
op("rename_node", nodeId=FID, name=f"Section / 02 Вечер · A список этапов · {OPEN} {label[OPEN - 1]}")
op("resize_nodes", nodeIds=[FID], width=1440, height=900)

# Удаляется старая сцена и итог
t1, t2, finals = TITLES[OPEN]
op("delete_nodes", nodeIds=[kid(d) for d in KIDS["drop"]] + [kid(KIDS["hall"])] + finals)

# Шапка: метка 104, H2 120 (l1 136, l2 232 от 400), лид справа сверху
op("move_nodes", nodeIds=[kid(KIDS["label"])], x=X0, y=104)
op("set_text", nodeId=t1, fontSize=120)
op("move_nodes", nodeIds=[t1], x=X0, y=136)
op("set_text", nodeId=t2, fontSize=120)
op("move_nodes", nodeIds=[t2], x=400, y=232)
op("rename_node", nodeId=t2, name="Заголовок · 2")
op("move_nodes", nodeIds=[kid(KIDS["lead"])], x=XC, y=104)
op("rename_node", nodeId=kid(KIDS["lead"]), name="Лид")

# Фото: окно-маска, внутри пять снимков целиком, сдвиг к фокусу
m = op("create_frame", parentId=FID, name="Окно фото", x=XC, y=ph_top, width=CW, height=r(ph_h), clipsContent=True)
op("set_fills", nodeId=ref(m), paints=[])
photos = [kid(d) for d in KIDS["photos"]]
op("reparent_nodes", nodeIds=photos, parentId=ref(m), preserveAbsolutePosition=False)
op("resize_nodes", nodeIds=photos, width=CW, height=r(PH_FULL))
for n, pid in enumerate(photos):
    op("move_nodes", nodeIds=[pid], x=0, y=r(-(PH_FULL - ph_h) * FOCUS[n]))
    op("set_opacity", nodeIds=[pid], opacity=1 if n == OPEN - 1 else 0)

# Итог: крупно + продолжение капсом, прижат к низу
text("Это ориентир,", XC, big_top, "Итог · крупно", size=48, color=LIGHT, ls=-5, lh=80, family="Old Standard TT", case=None)
note = kid(KIDS["note"])
op("set_text", nodeId=note, text=NOTE)
op("move_nodes", nodeIds=[note], x=XC, y=note_top)
op("set_text_range", nodeId=note, startOffset=0, endOffset=24, color=LIGHT)
op("rename_node", nodeId=note, name="Итог · капсом")

# Список этапов: нижний край самой длинной раскрытой строки (02) — на H − 64
top = 900 - 64 - (373 + 23 + max(DESC_H))
for n, (t, dur, inten, name, w, desc) in enumerate(STEPS, 1):
    on = n == OPEN
    op("create_rectangle", parentId=FID, x=X0, y=r(top), width=832, height=w if on else 1,
       fillColor=TERRA if on else DIV, name=f"Строка 0{n} · линия")
    text(t, X0, top + 16 + (38.4 - 15) / 2, f"Строка 0{n} · время", color=LIGHT if on else G50)
    text(name, XN, top + 16, f"Строка 0{n} · название", size=48, color=LIGHT if on else G50, ls=-5, lh=80,
         family="Old Standard TT", case=None)
    if on:
        my = top + 16 + 38.4 + 13
        text(dur, XN, my, f"Строка 0{n} · длительность", color=G80)
        text(inten, XN + tw(dur, 11, 0.4) + 24, my, f"Строка 0{n} · интенсивность", color=TERRA)
        text(desc, XN, my + 23, f"Строка 0{n} · описание", size=12, ls=2, lh=150, w=DW)
        top += 72 + 13 + 23 + DESC_H[n - 1]
    else:
        top += 72

print(json.dumps(ops, ensure_ascii=False, separators=(",", ":")))
