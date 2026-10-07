"""Сверка набора: ширина слов в браузере (наши woff2 из site/fonts) против ширины автоширинных узлов Figma.

  python tools/type_check.py            # chromium + webkit, таблица в stdout и в _figma/type_check.md

Проверяет кернинг и трекинг (−3 % гигант, −5 % антиква, −7,5 % Stat). Допуск — 1 % ширины.
Браузер добавляет трекинг и после последней буквы, Figma — нет: колонка «Δ без хвоста» это учитывает.
"""
from pathlib import Path

from playwright.sync_api import sync_playwright

from _serve import VERSTKA, serve

U, O = "Unbounded", "Old Standard TT"
# (текст, гарнитура, начертание, вес, кегль, трекинг em, капс, ширина Figma, источник)
SAMPLES = [
    ("Балы", U, "normal", 700, 91, -0.03, True, 347, "229:863 M Giant XL"),
    ("Участники", U, "normal", 700, 45, -0.03, True, 359, "229:864 M Giant"),
    ("Балы", U, "normal", 700, 180, -0.03, True, 685, "229:931 T Giant XL"),
    ("Участники", U, "normal", 700, 92, -0.03, True, 733, "229:932 T Giant"),
    ("Разговор", U, "normal", 700, 112, -0.03, True, 732, "219:1913 D 01"),
    ("Концепция", U, "normal", 700, 112, -0.03, True, 906, "219:1918 D 01"),
    ("Репетиции", U, "normal", 700, 112, -0.03, True, 882, "219:1923 D 01"),
    ("Вечер", U, "normal", 700, 112, -0.03, True, 454, "219:1928 D 01"),
    ("Воспоминания", U, "normal", 700, 112, -0.03, True, 1260, "219:1933 D 01"),
    ("Профессионалы", U, "normal", 700, 107, -0.03, True, 1310, "213:858 D 05"),
    ("Омега", U, "normal", 700, 191, -0.03, True, 835, "218:907 D 10"),
    ("Кашемир", U, "normal", 700, 191, -0.03, True, 1306, "218:909 D 10"),
    ("Зрители", U, "normal", 700, 32, -0.02, True, 196, "198:891 D H3 (капс)"),
    ("Музыкальное", O, "normal", 400, 150, -0.05, False, 800, "223:2710 D H2"),
    ("сопровождение", O, "normal", 400, 150, -0.05, False, 913, "223:2711 D H2"),
    ("Танцмейстер", O, "normal", 400, 150, -0.05, False, 782, "198:878 D H2"),
    ("Танцевальные", O, "normal", 400, 150, -0.05, False, 859, "213:843 D H2"),
    ("Подготовка", O, "normal", 400, 150, -0.05, False, 694, "198:1290 D H2"),
    ("Танцевальный", O, "normal", 400, 150, -0.05, False, 871, "207:1960 D H2"),
    ("Избранные", O, "italic", 400, 150, -0.05, False, 688, "218:884 D H2 курсив"),
    ("этикет", O, "italic", 400, 150, -0.05, False, 498, "207:1961 D H2 курсив"),
    ("частные", O, "italic", 400, 64, -0.05, False, 236, "223:2177 D 64 курсив"),
    ("корпоративные", O, "italic", 400, 64, -0.05, False, 418, "223:2178 D 64 курсив"),
    ("Кавалерам", O, "normal", 400, 128, -0.05, False, 557, "207:1983 D 128"),
    ("Белый", O, "normal", 400, 230, -0.05, False, 615, "207:1931 D Display L"),
    ("18:00", O, "normal", 400, 224, -0.075, False, 516, "223:2476 D Stat"),
]
# Планшет, Giant 92, замер в Figma после стиля (ОБЩЕЕ адаптива, «Прецеденты этапа 5»)
T92 = {"Разговор": 601, "Концепция": 744, "Репетиции": 724, "Вечер": 373, "Воспоминания": 1035, "Зрители": 558,
       "Участники": 733, "Профессионалы": 1126, "Совместный": 856, "Формат": 533, "Номер от своих": 1028,
       "Стесняетесь": 835, "Не умеете": 648, "Танцевать": 688, "Пришли": 546, "Без пары": 586, "Омега": 402,
       "Бал": 249, "Кашемир": 629, "И шелк": 470, "Подготовка": 800, "Ассистент": 718, "Дресс-код": 689,
       "Связаться": 691}
SAMPLES += [(w, U, "normal", 700, 92, -0.03, True, fw, "T Giant 92") for w, fw in T92.items()]

JS = """samples => samples.map(([t, fam, st, wt, sz, ls, up]) => {
  const s = document.createElement('span');
  s.textContent = t;
  Object.assign(s.style, {fontFamily: `"${fam}"`, fontStyle: st, fontWeight: wt, fontSize: sz + 'px',
    letterSpacing: ls + 'em', textTransform: up ? 'uppercase' : 'none', whiteSpace: 'pre', position: 'absolute'});
  document.body.appendChild(s);
  const w = s.getBoundingClientRect().width; s.remove(); return w;
})"""


def main():
    rows = []
    with serve() as base, sync_playwright() as pw:
        css = f"""
        @font-face{{font-family:"Unbounded";src:url({base}/site/fonts/unbounded-regular.woff2);font-weight:400}}
        @font-face{{font-family:"Unbounded";src:url({base}/site/fonts/unbounded-bold.woff2);font-weight:700}}
        @font-face{{font-family:"Old Standard TT";src:url({base}/site/fonts/old-standard-regular.woff2)}}
        @font-face{{font-family:"Old Standard TT";src:url({base}/site/fonts/old-standard-italic.woff2);font-style:italic}}"""
        results = {}
        for bname in ("chromium", "webkit"):
            b = getattr(pw, bname).launch()
            p = b.new_page()
            p.goto(base + "/site/index.html")
            p.add_style_tag(content=css)
            p.evaluate("""async () => { for (const f of ['700 20px Unbounded','400 20px Unbounded','20px "Old Standard TT"','italic 20px "Old Standard TT"']) await document.fonts.load(f, 'АБВ'); }""")
            results[bname] = p.evaluate(JS, [list(s[:7]) for s in SAMPLES])
            b.close()
    worst = 0
    for i, s in enumerate(SAMPLES):
        t, fam, st, wt, sz, ls, up, fw, src = s
        wc, ww = results["chromium"][i], results["webkit"][i]
        tail = ls * sz                      # трекинг после последней буквы
        d = wc - tail - fw
        pct = 100 * d / fw
        worst = max(worst, abs(pct))
        rows.append((t, f"{fam.split()[0]} {'It ' if st == 'italic' else ''}{sz}", fw, round(wc, 1), round(ww, 1),
                     round(d, 1), round(pct, 2), src))
    lines = ["| слово | шрифт | Figma | chromium | webkit | Δ без хвоста | Δ % | узел |", "|---|---|---|---|---|---|---|---|"]
    lines += [f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]:+} | {r[6]:+} | {r[7]} |" for r in rows]
    flagged = [r for r in rows if abs(r[6]) > 1]
    summary = (f"Слов: {len(rows)}. Максимальное отклонение {worst:.2f} %. "
               f"За допуском 1 %: {', '.join(f'{r[0]} ({r[6]:+} %, {r[7]})' for r in flagged) or 'нет'}.")
    text = "# Сверка набора: браузер против Figma\n\n" + summary + "\n\n" + "\n".join(lines) + "\n"
    (VERSTKA / "_figma" / "type_check.md").write_text(text, "utf-8")
    print(text)


if __name__ == "__main__":
    main()
