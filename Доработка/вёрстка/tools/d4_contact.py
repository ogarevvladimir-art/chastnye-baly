"""Д4, шаг 1: контактный лист замен фото (П-05, П-06).

Строка = слот: «сейчас» и кандидаты из assets/. Каждый снимок — в кадре десктопа 1440 и телефона 390 (cover по точке фокуса),
под ним запас разрешения: min по окнам 390 @3×, 834 @2×, 1440 @2× (≥ 1,0 — чётко). Окна — замер сайта (scratch boxes.json → BOXES).

    python tools/d4_contact.py      # → сверка/d4/contact_<n>.png
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from _serve import PROJECT, SVERKA

A = PROJECT / "assets/photos"
ORIG = PROJECT.parent / "Правки по сайту бал/2024"
OUT = SVERKA / "d4"

# окна фото на сайте (CSS px) после Д2–Д3: 390, 834, 1440
BOXES = {
    "hero": [(390, 780), (834, 1130), (1440, 900)],
    "corporate": [(358, 448), (770, 520), (971, 959)],
    "evening": [(358, 448), (385, 481), (416, 499)],      # 02: на десктопе снимок целиком 5 : 6 в ширину колонки
    "music": [(310, 388), (360, 450), (1440, 540)],
    "dancemaster": [(304, 448), (770, 560), (1032, 615)],
    "show": [(355, 600), (834, 560), (1440, 900)],
    "lessons": [(390, 488), (834, 556), (1440, 480)],
}
DPR = (3, 2, 2)

# (файл, фокус x, фокус y, область исходника или None, пометка)
C = lambda f, fx=.5, fy=.5, rect=None, note="": (f, fx, fy, rect, note)
SLOTS = [
    ("Hero · обложка", "hero", [C("bg-1.jpg", note="сейчас"), C("@buzin_photo-1178.jpg", fy=.95, note="зал, колонны"),
                                C("farkovets1289.jpg", fy=.8, note="РЕК · танцующий зал, свет"), C("0533.jpg", fy=.55, note="конфетти — он же рек. для 02 «22:20»")]),
    ("Форматы · корпоративные", "corporate", [C("KOR_0924_1.jpg", note="сейчас"), C("KOR_0906_1.jpg", note="РЕК · полонез в розовом зале"),
                                             C("KOR_1385_1.jpg", note="ведущий, синий зал"), C("KOR_0895_1.jpg", fx=.4, note="ведущий и гости")]),
    ("02 · 18:00 Сбор гостей", "evening", [C("1W1A2194.jpg", fy=0, note="сейчас, 1280 px"),
                                          C(ORIG / "1W1A2194.jpg", fx=.62, fy=0, note="РЕК · тот же кадр, оригинал 4000")]),
    ("02 · 19:00 Торжественное открытие", "evening", [C("BI4A0526.jpg", note="сейчас"), C("13.09.25 Бал. Гимназия №2 (102).jpg", fx=.55, note="РЕК · вальс-открытие"),
                                                     C("venue-03.jpg", fy=.6, note="балерина"), C("ball-02.jpg", note="балетная труппа")]),
    ("02 · 19:20 Танцевальная программа", "evening", [C("nk-08.jpg", note="сейчас"), C("422A2400.jpg", fx=.4, note="РЕК · зал танцует, оркестр"),
                                                      C("13.09.25 Бал. Гимназия №2 (101).jpg", fx=.42, note="гимназия, общий танец"), C("nk-02.jpg", note="зал сверху, колонны пар"), C("NesterovaMaria_0747_resized.jpg", note="НОВОЕ · пары в полумраке")]),
    ("02 · 21:50 Шоу-номера", "evening", [C("BI4A1223.jpg", fx=.45, note="сейчас"), C("NesterovaMaria_0106_resized.jpg", fy=.55, note="РЕК · танго в красном"),
                                         C("nk-01.jpg", fx=.42, note="пары в белом"), C("NesterovaMaria_0049_resized.jpg", fx=.42, note="пара у оркестра"), C("NesterovaMaria_0353_resized.jpg", fx=.4, note="НОВОЕ · та же пара, крупнее")]),
    ("02 · 22:20 Финальный танец", "evening", [C("IMG_4988.jpg", fy=0, note="сейчас, 945 px"), C("0533.jpg", fy=.6, note="РЕК · конфетти над залом"),
                                              C("@buzin_photo-1178.jpg", fy=1, note="весь зал танцует"), C("farkovets1289.jpg", fy=.75, note="зал, свет")]),
    ("03 · Духовой / джаз-бэнд", "music", [C("NesterovaMaria_0093_resized.jpg", note="сейчас (обрывок «…ВАЦИЙ» вверху)"),
                                          C("nk-03.jpg", fx=.55, fy=.45, rect=(0, 0, 2950, 2667), note="РЕК · валторна; «#…PARTY» справа срезан"),
                                          C("NesterovaMaria_0094_resized.jpg", note="струнные — не духовые"), C("NesterovaMaria_0543_resized.jpg", rect=(330, 0, 2560, 1707), fx=.3, note="НОВОЕ · духовые; «…ВАЦИЙ» слева срезан")]),
    ("03 · Музыкальная группа", "music", [C("153A4668.jpg", note="сейчас — логотип «Бал дебютантов»"),
                                         C("NesterovaMaria_0057_resized.jpg", fy=.45, note="РЕК · солисты с оркестром"),
                                         C("NesterovaMaria_1131.jpg", fy=.35, note="дуэт; за ним обрывок надписи «Бал…»"), C("NesterovaMaria_0351_resized.jpg", fy=.6, note="НОВОЕ · солистка с оркестром")]),
    ("04 · Зрители", "dancemaster", [C("Xz6-zmZA4SoVS51daBA0t.webp", note="сейчас — логотип ВМПАВТО"),
                                    C("KOR_0895_1.jpg", fx=.4, note="РЕК · гости вдоль зала, ведущий"), C("KOR_0906_1.jpg", note="гости в линии")]),
    ("04 · Участники", "dancemaster", [C("NesterovaMaria_0126_resized.jpg", note="сейчас — «Бал инноваций» над головой"),
                                      C("13.09.25 Бал. Гимназия №2 (101).jpg", note="РЕК · все танцуют"),
                                      C("422A2400.jpg", note="танцмейстер ведёт зал"), C("nk-02.jpg", note="колонны пар сверху"), C("NesterovaMaria_0747_resized.jpg", note="НОВОЕ · гости танцуют")]),
    ("05 · Профессионалы", "show", [C("ball-07.jpg", note="сейчас"), C("nk-01.jpg", fx=.4, note="РЕК · пары в белом, 4000 px"),
                                   C("NesterovaMaria_0049_resized.jpg", fx=.45, note="пара у оркестра"), C("NesterovaMaria_0353_resized.jpg", fx=.4, note="НОВОЕ · та же пара, крупнее")]),
    ("05 · Совместный", "show", [C("BI4A1223.jpg", note="сейчас — тот же снимок в 02"), C("KOR_0445_1.jpg", note="РЕК · гости в паре с танцорами"),
                                C("13.09.25 Бал. Гимназия №2 (102).jpg", fy=.6, note="пара в зале"), C("NesterovaMaria_0298_resized.jpg", fy=1, note="НОВОЕ · гости в паре, дым")]),
    ("05 · Номер от своих", "show", [C("NesterovaMaria_0041_resized.jpg", note="сейчас"), C("KOR_0440_1.jpg", note="выход в дыму, фиолетовый"), C("NesterovaMaria_0297_resized.jpg", fy=1, note="РЕК · НОВОЕ · номер сотрудников в дыму"), C("NesterovaMaria_0306_resized.jpg", fy=1, note="НОВОЕ · то же, поклон")]),
    ("07 · Уроки, панорама", "lessons", [C("DSC03350_resized.jpg", note="сейчас"), C("nk-02.jpg", fy=.6, note="РЕК · зал сверху, 4000 px"),
                                         C("13.09.25 Бал. Гимназия №2 (101).jpg", fy=.6, note="зал гимназии")]),
]

FONT = ImageFont.truetype("arial.ttf", 18)
BOLD = ImageFont.truetype("arialbd.ttf", 22)
H = 300          # высота кадра десктопа на листе
PH = 220         # высота кадра телефона


def load(f, rect):
    p = Path(f) if isinstance(f, Path) else A / f
    im = ImageOps.exif_transpose(Image.open(p)).convert("RGB")
    if rect:
        im = im.crop(rect)
    return im


def crop(im, aspect, fx, fy):
    W, Hh = im.size
    if W / Hh > aspect:
        w, h = round(Hh * aspect), Hh
    else:
        w, h = W, round(W / aspect)
    x, y = round((W - w) * fx), round((Hh - h) * fy)
    return im.crop((x, y, x + w, y + h))


def margin(im, kind):
    W, Hh = im.size
    ks = []
    for (bw, bh), d in zip(BOXES[kind], DPR):
        a = bw / bh
        cw, ch = (Hh * a, Hh) if W / Hh > a else (W, W / a)
        ks.append(cw / (bw * d))
    return ks


def tile(entry, kind):
    f, fx, fy, rect, note = entry
    im = load(f, rect)
    (mw, mh), _, (dw, dh) = BOXES[kind]
    d = crop(im, dw / dh, fx, fy); d.thumbnail((round(H * dw / dh), H), Image.LANCZOS)
    m = crop(im, mw / mh, fx, fy); m.thumbnail((round(PH * mw / mh), PH), Image.LANCZOS)
    ks = margin(im, kind)
    w = d.width + 8 + m.width
    t = Image.new("RGB", (max(w, 330), H + 62), "white")
    t.paste(d, (0, 0)); t.paste(m, (d.width + 8, H - m.height))
    dr = ImageDraw.Draw(t)
    name = Path(f).name if isinstance(f, Path) else f
    worst = min(ks)
    col = (0, 120, 0) if worst >= 1 else (170, 110, 0) if worst >= .8 else (190, 0, 0)
    dr.text((0, H + 4), f"{name[:34]}  {im.width}×{im.height}", fill="black", font=FONT)
    dr.text((0, H + 26), "запас 390/834/1440: " + " / ".join(f"{k:.1f}" for k in ks) + f"   {note}", fill=col, font=FONT)
    return t


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for title, kind, cands in SLOTS:
        tiles = [tile(c, kind) for c in cands]
        w = 360 + sum(t.width + 24 for t in tiles)
        r = Image.new("RGB", (w, H + 80), "white")
        dr = ImageDraw.Draw(r)
        dr.text((8, 8), title, fill="black", font=BOLD)
        (mw, mh), _, (dw, dh) = BOXES[kind]
        dr.text((8, 44), f"десктоп 1440: {dw}×{dh}", fill=(90, 90, 90), font=FONT)
        dr.text((8, 68), f"телефон 390: {mw}×{mh}", fill=(90, 90, 90), font=FONT)
        x = 360
        for i, t in enumerate(tiles):
            r.paste(t, (x, 8))
            if i == 0:
                dr.rectangle((x - 4, 4, x + t.width + 2, H + 74), outline=(150, 150, 150), width=2)
            x += t.width + 24
        rows.append(r)
        print(title, "ok")
    per = 5
    for n in range(0, len(rows), per):
        chunk = rows[n:n + per]
        sheet = Image.new("RGB", (max(r.width for r in chunk), sum(r.height + 16 for r in chunk)), "white")
        y = 0
        for r in chunk:
            sheet.paste(r, (0, y)); y += r.height
            ImageDraw.Draw(sheet).line((0, y + 6, sheet.width, y + 6), fill=(200, 200, 200), width=2); y += 16
        sheet.save(OUT / f"contact_{n // per + 1}.png")


if __name__ == "__main__":
    main()
