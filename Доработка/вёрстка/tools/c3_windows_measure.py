"""Ц3: новый 07 «Уроки» на проверочных окнах страницы «Окна» — позиции с сайта (а не формулой: высоты капса зависят от переносов).
На каждом из пяти окон меряет #lessons: метка, фраза (верх блока строки, кегль), гигант (верх блока, кегль), метки и капс фрагментов
(x, y, ширина). Координаты — от левого края окна и верха секции; кегли — computed font-size.

  python c3_windows_measure.py      # сервер tools/serve.py запущен → ../_figma/c3_win_points.json
"""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).parent.parent / "_figma" / "c3_win_points.json"
WINS = [(1440, 900), (1920, 950), (1366, 650), (1280, 600), (1024, 650)]
JS = """() => {
  const s = document.querySelector('#lessons'), r0 = s.getBoundingClientRect();
  const b = (el) => { const r = el.getBoundingClientRect(); return { x: +r.x.toFixed(1), y: +(r.y - r0.y).toFixed(1), w: +r.width.toFixed(1), h: +r.height.toFixed(1) }; };
  const fs = (el) => parseFloat(getComputedStyle(el).fontSize);
  const ph = s.querySelector('.less__phrase'), g = s.querySelector('.less__giant');
  return { section_h: r0.height, k7: s.style.getPropertyValue('--k7'),
    label: b(s.querySelector('.less__label')),
    phrase: { ...b(ph), fontSize: fs(ph) }, giant: { ...b(g), fontSize: fs(g) },
    steps: [...s.querySelectorAll('.less__step')].map((st) => ({ label: b(st.querySelector('.less__stage')), text: b(st.querySelector('.less__text')) })) };
}"""

res = {}
with sync_playwright() as p:
    br = p.chromium.launch()
    for w, h in WINS:
        pg = br.new_page(viewport={"width": w, "height": h})
        pg.goto("http://127.0.0.1:8080/site/")
        pg.evaluate("document.fonts.ready")
        pg.evaluate("window.scrollTo(0, document.querySelector('#lessons').offsetTop)")
        pg.wait_for_timeout(500)
        res[f"{w}x{h}"] = pg.evaluate(JS)
        pg.close()
    br.close()
OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
for k, v in res.items():
    print(k, "k7", v["k7"], "phrase", v["phrase"]["y"], v["phrase"]["fontSize"], "giant", v["giant"]["x"], v["giant"]["y"], v["giant"]["fontSize"],
          "steps", [(st["label"]["x"], st["label"]["y"], st["text"]["w"], st["text"]["h"]) for st in v["steps"]])
