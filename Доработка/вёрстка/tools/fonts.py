"""Сабсет шрифтов сайта → site/fonts/*.woff2.

Запуск: python tools/fonts.py  (из Доработка/вёрстка)
Нужны fonttools и brotli (pip install fonttools brotli).

Исходники — папка «Шрифты/» проекта:
  Unbounded/Unbounded[wght].ttf   — Google Fonts, OFL, variable wght 200–900 → два статичных начертания 400 и 700
                                    (этап 2: WebKit под Windows не применяет оси вариативного шрифта, а других весов на сайте нет)
  OldStandardTT-Regular.ttf, OldStandardTT-Italic.ttf — Google Fonts, OFL
Набор знаков: латиница, кириллица (рус. + укр. Ґ), типографские знаки, стрелки.
"""
from io import BytesIO
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = Path(__file__).resolve().parents[3]          # «Частные балы сайт/»
SRC = ROOT / "Шрифты"
OUT = ROOT / "site" / "fonts"

UNICODES = (
    list(range(0x20, 0x7F))                          # ASCII
    + list(range(0xA0, 0x100))                       # Latin-1: nbsp, «», ·, ©, ° …
    + [0x131, 0x152, 0x153, 0x2C6, 0x2DA, 0x2DC]
    + list(range(0x400, 0x460))                      # кириллица, Ё ё
    + [0x490, 0x491]
    + list(range(0x2010, 0x2016))                    # дефисы и тире
    + list(range(0x2018, 0x201F))                    # кавычки ‘ ’ ‚ “ ” „
    + [0x2022, 0x2026, 0x2030, 0x2039, 0x203A, 0x20AC, 0x20BD, 0x2116, 0x2122, 0x2212]
    + list(range(0x2190, 0x2194))                    # ← ↑ → ↓
)

FONTS = [
    # (исходник, выход, wght — число (статичный срез) или None)
    (SRC / "Unbounded" / "Unbounded[wght].ttf", "unbounded-regular.woff2", 400),
    (SRC / "Unbounded" / "Unbounded[wght].ttf", "unbounded-bold.woff2", 700),
    (SRC / "OldStandardTT-Regular.ttf", "old-standard-regular.woff2", None),
    (SRC / "OldStandardTT-Italic.ttf", "old-standard-italic.woff2", None),
]


def build(src, name, wght):
    font = TTFont(src)
    if wght:
        font = instancer.instantiateVariableFont(font, {"wght": wght}, updateFontNames=False)
        buf = BytesIO()                     # перезагрузка: иначе subset падает на ленивом gvar
        font.save(buf)
        buf.seek(0)
        font = TTFont(buf)
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["*"]          # kern, liga, case, ss — всё, что есть в шрифте
    opts.name_IDs = ["*"]
    opts.name_languages = ["*"]
    opts.notdef_outline = True
    opts.glyph_names = False
    opts.hinting = False                   # экранный хинтинг не нужен, экономит вес
    opts.drop_tables += ["DSIG"]
    s = subset.Subsetter(opts)
    s.populate(unicodes=UNICODES)
    s.subset(font)
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / name
    font.flavor = "woff2"
    font.save(out)
    missing = [hex(u) for u in UNICODES if u not in font.getBestCmap()]
    print(f"{name:28} {out.stat().st_size / 1024:6.1f} КБ  нет в шрифте: {len(missing)} знаков")


if __name__ == "__main__":
    for src, name, wght in FONTS:
        build(src, name, wght)
