"""Ц3: новый 02 «Вечер» на проверочных окнах страницы «Окна» — позиции с сайта (высоты капса зависят от переносов).
На каждом из пяти окон меряет шапку (метка, фраза, гигант, капс; от верха шапки) и экран этапа 1 закреплённой сцены
(время, окно фото, слово, капс этапа, «ориентир»; от верха сцены). x — от левого края окна; кегли — computed font-size;
рамки — блоков строк (как текстовые узлы Figma: высота = строки × lh).

  python c3_02_windows_measure.py      # сервер tools/serve.py запущен → ../_figma/c3_02_win_points.json
"""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).parent.parent / "_figma" / "c3_02_win_points.json"
WINS = [(1440, 900), (1920, 950), (1366, 650), (1280, 600), (1024, 650)]
JS = """() => {
  const s = document.querySelector('#evening'), H = s.querySelector('.eve__head').getBoundingClientRect();
  const S = s.querySelector('.eve__stage').getBoundingClientRect(), a = s.querySelector('.eve__step[data-i="1"]');
  const r = (b, R) => ({ x: +b.x.toFixed(1), y: +(b.y - R.y).toFixed(1), w: +b.width.toFixed(1), h: +b.height.toFixed(1) });
  const b = (el, R) => r(el.getBoundingClientRect(), R);
  const fs = (el) => parseFloat(getComputedStyle(el).fontSize);
  const q = (c) => s.querySelector(c), ph = q('.eve__phrase'), gi = q('.eve__giant'), wd = a.querySelector('.eve__wi');
  return { head_h: +H.height.toFixed(1), stage_h: +S.height.toFixed(1), pinned: s.hasAttribute('data-pin'),
    head: { label: b(q('.eve__label'), H), phrase: { ...b(ph, H), fontSize: fs(ph) }, giant: { ...b(gi, H), fontSize: fs(gi) }, lead: b(q('.eve__lead'), H) },
    step: { time: b(a.querySelector('.eve__time'), S), photo: b(a.querySelector('.eve__photo'), S),
            word: { ...b(wd, S), fontSize: fs(wd) }, text: b(a.querySelector('.eve__text'), S), note: b(q('.eve__note'), S) } };
}"""

res = {}
with sync_playwright() as p:
    br = p.chromium.launch()
    for w, h in WINS:
        pg = br.new_page(viewport={"width": w, "height": h})
        pg.goto("http://127.0.0.1:8080/site/")
        pg.evaluate("document.fonts.ready")
        pg.evaluate("window.scrollTo(0, document.querySelector('.eve__track').getBoundingClientRect().top + scrollY)")
        pg.wait_for_timeout(1200)
        res[f"{w}x{h}"] = pg.evaluate(JS)
        pg.close()
    br.close()
OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
for k, v in res.items():
    hd, st = v["head"], v["step"]
    print(k, "head", v["head_h"], "phrase", hd["phrase"]["y"], hd["phrase"]["fontSize"], "giant", hd["giant"]["x"], hd["giant"]["y"], hd["giant"]["fontSize"],
          "lead", hd["lead"]["x"], hd["lead"]["y"], hd["lead"]["w"], "| stage", v["stage_h"], v["pinned"], "photo", list(st["photo"].values()),
          "word", st["word"]["y"], st["word"]["h"], st["word"]["fontSize"], "text", st["text"]["x"], st["text"]["w"], st["text"]["h"], "note", st["note"]["y"], st["note"]["w"], st["note"]["h"])
