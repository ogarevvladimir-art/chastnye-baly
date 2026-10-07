"""Доступность (axe-core, WCAG 2.1 A / AA): страница в покое после всех входов, плюс открытое меню и лист формы.

  python tools/axe_check.py                  # 390, 834, 1440 — chromium
  python tools/axe_check.py -w 1440 -b webkit

axe-core — dev-зависимость tools/ (npm install). Печатает нарушения по правилам с примерами узлов.
"""
import argparse

from playwright.sync_api import sync_playwright

from _serve import TOOLS, serve, url_for, viewport_height

AXE = (TOOLS / "node_modules" / "axe-core" / "axe.min.js").read_text(encoding="utf-8")

RUN = """async () => {
  const r = await axe.run(document, { runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'] } });
  return r.violations.map(v => ({ id: v.id, impact: v.impact, n: v.nodes.length,
    nodes: v.nodes.slice(0, 40).map(n => n.target.join(' ') + (n.any[0] ? ' — ' + n.any[0].message.slice(0, 120) : '')) }));
}"""


def report(name, vs):
    total = sum(v["n"] for v in vs)
    print(f"{'ok ' if not vs else '!! '} {name}: нарушений {total}")
    for v in vs:
        print(f"     {v['id']} ({v['impact']}, {v['n']})")
        for n in v["nodes"]:
            print(f"       · {n}")
    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-w", "--widths", type=int, nargs="+", default=[390, 834, 1440])
    ap.add_argument("-b", "--browser", default="chromium", choices=["chromium", "webkit"])
    args = ap.parse_args()
    bad = 0
    with serve() as base, sync_playwright() as pw:
        b = getattr(pw, args.browser).launch()
        for w in args.widths:
            # reduced-motion: всё в покое (входы и смены не мешают замеру контраста)
            ctx = b.new_context(viewport={"width": w, "height": viewport_height(w)}, reduced_motion="reduce")
            p = ctx.new_page()
            p.goto(url_for(base, "site/index.html"), wait_until="networkidle")
            p.add_script_tag(content=AXE)
            bad += report(f"{w}: страница", p.evaluate(RUN))
            p.click(".site-header__menu")
            p.wait_for_timeout(400)
            bad += report(f"{w}: открытое меню", p.evaluate(RUN))
            p.keyboard.press("Escape")
            p.wait_for_timeout(400)
            p.evaluate("document.querySelector('.s-hero__link').click()")
            p.wait_for_timeout(300)
            bad += report(f"{w}: лист формы", p.evaluate(RUN))
            ctx.close()
        b.close()
    print(f"\nвсего нарушений: {bad}")


if __name__ == "__main__":
    main()
