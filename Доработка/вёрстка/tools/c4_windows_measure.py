"""Ц4: measure the finale «11–12» (section.s-finale, #contact) on the five check windows of the live site.

For each window: scroll the section to the top of the window, wait for fonts and reveal transitions,
then read the named elements (label, giants, team, phrase, more, link text box with its underline,
contacts) and every .fin__* element inside the section (to check the mapping to Figma names).
x = from the window left, y = from the section top, w / h = border box, fontSize = computed style.

Output: ../_figma/c4_win_points.json  (site server must run: python tools/serve.py)

    python c4_windows_measure.py
"""
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent.parent / "_figma" / "c4_win_points.json"
SITE_URL = "http://127.0.0.1:8080/site/"
WINDOWS = [(1440, 900), (1920, 950), (1366, 650), (1280, 600), (1024, 650)]
NAMED = {
    "label": ".fin__label",
    "g1": ".fin__g1",
    "g2": ".fin__g2",
    "team": ".fin__team",
    "phrase": ".fin__phrase",
    "more": ".fin__more",
    "lt": ".fin__lt",
    "contacts": ".fin__contacts",
}
MEASURE_JS = r"""(named) => {
  const s = document.querySelector('section.s-finale');
  if (!s) return { error: 'section.s-finale not found' };
  const r0 = s.getBoundingClientRect();
  const box = (el) => {
    const r = el.getBoundingClientRect(), cs = getComputedStyle(el);
    return { x: +r.left.toFixed(2), y: +(r.top - r0.top).toFixed(2), w: +r.width.toFixed(2), h: +r.height.toFixed(2),
             fontSize: parseFloat(cs.fontSize), opacity: cs.opacity, transform: cs.transform,
             text: (el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 60) };
  };
  const out = {
    section_h: +r0.height.toFixed(2), section_w: +r0.width.toFixed(2), vp_top: +r0.top.toFixed(2),
    k12: s.style.getPropertyValue('--k12'),
    contact_is_section: document.querySelector('#contact') === s,
    els: {}, all_fin: [],
  };
  for (const [key, sel] of Object.entries(named)) {
    const el = s.querySelector(sel);
    out.els[key] = el ? box(el) : null;
  }
  for (const el of s.querySelectorAll('[class*="fin__"]')) {
    out.all_fin.push({ cls: el.getAttribute('class'), ...box(el) });
  }
  return out;
}"""


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    res = {}
    with sync_playwright() as p:
        br = p.chromium.launch()
        for w, h in WINDOWS:
            pg = br.new_page(viewport={"width": w, "height": h})
            pg.goto(SITE_URL)
            pg.evaluate("document.fonts.ready.then(() => true)")
            # bring section.s-finale (#contact) to the top of the window
            pg.evaluate("""() => {
              const s = document.querySelector('section.s-finale');
              window.scrollTo({ top: s.getBoundingClientRect().top + window.scrollY, behavior: 'instant' });
            }""")
            pg.wait_for_timeout(1500)  # let reveal transitions finish after the scroll
            pg.evaluate("document.fonts.ready.then(() => true)")
            res[f"{w}x{h}"] = pg.evaluate(MEASURE_JS, NAMED)
            pg.close()
        br.close()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")

    for key, v in res.items():
        if "error" in v:
            print(key, "ERROR", v["error"])
            continue
        missing = [k for k, e in v["els"].items() if e is None]
        print(f"{key}: section_h={v['section_h']} section_w={v['section_w']} vp_top={v['vp_top']} "
              f"k12={v['k12']!r} contact_is_section={v['contact_is_section']} missing={missing}")
        for k, e in v["els"].items():
            if e:
                print(f"  {k:9s} x={e['x']:8.2f} y={e['y']:8.2f} w={e['w']:8.2f} h={e['h']:7.2f} "
                      f"fs={e['fontSize']:6.2f} op={e['opacity']} tf={e['transform']} | {e['text'][:30]}")
        print("  all_fin:", "; ".join(f"{f['cls']}@{f['y']}/{f['h']}" for f in v["all_fin"]))


if __name__ == "__main__":
    main()
