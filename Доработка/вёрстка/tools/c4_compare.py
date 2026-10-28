"""Finale block (section.s-finale#contact): comparison with the Figma frames, the form and the fit to the window.

  python tools/c4_compare.py              # chromium and webkit (default): parts A, B, C, D
  python tools/c4_compare.py -b chromium  # one engine; then there is no "chromium vs webkit" line
  python tools/c4_compare.py -b webkit
  python tools/c4_compare.py --all        # print every row and check, not only the failures

Part A: three Figma frames (phone 390x844, tablet 834x1112, desktop 1440x900). Coordinates are section-relative:
x is the page-left edge (the section is full width), y is the top of the section. Compared: x, y, right (r),
bottom (b) and w where Figma gives them, and h of the section box. Text heights are reported, not compared
(Figma rounds line heights). Threshold 4 px.
Part B: desktop 1440x900 with the form open, viewport coordinates: panel, backdrop, fields, submit, consent,
close button, Escape. Threshold 4 px; the submit top and bottom 8 px; panel and backdrop colours are exact.
Part C: five desktop windows, section height = window height: every box inside the section, no overlaps (Ваш and
вечер may touch), --k12 and the gap team -> phrase reported. The form at each window: the panel inside the viewport,
no overflow of the panel (scrollHeight <= clientHeight + 1).
Part D: nine widths without horizontal scroll: at the section top, then at the section -200 px after 250 ms (as c3).

Output in сверка/c4/: report.txt (the printed report), report.json (every measured value, both engines),
site_<engine>_<frame>.png for each Figma frame and form_<engine>_1440.png. The points are hard-coded below, as in c3.
"""
import argparse
import json
import re
import sys

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

from _serve import SVERKA, serve, url_for
from pilot_shots import STILL, eager

OUT = SVERKA / "c4"
THRESH = 4                                  # px, position and size (as c3)
SEC = "section.s-finale#contact"
DLG = "dialog#form"
LINK = ".fin__link"                         # opens the form
HIDE = ".site-header,.skip{visibility:hidden!important}"   # screenshots only, as in c3
ENGINES = ["chromium", "webkit"]
FRAMES = {                                  # key: (width, window height, title for the report)
    "390": (390, 844, "телефон 390x844"),
    "834": (834, 1112, "планшет 834x1112"),
    "1440": (1440, 900, "десктоп 1440x900"),
}
WINDOWS = [(1440, 900), (1920, 950), (1366, 650), (1280, 600), (1024, 650)]
WIDTHS = [360, 390, 600, 834, 1023, 1024, 1280, 1440, 1920]
FIELD_ORDER = ["x", "y", "right", "bottom", "w", "h"]
KEY = {"x": "x", "y": "y", "right": "r", "bottom": "b", "w": "w", "h": "h"}   # Figma field -> measured key
HEAD_A = (f"{'точка':<9} {'Figma (x y r b w h)':<36} {'сайт':<34} "
          + " ".join(f"{'d' + KEY[f]:>7}" for f in FIELD_ORDER) + "  флаг")


def P(key, sel, h_cmp=False, **fig):
    """Figma point, expected px relative to the section. fig holds x, y, right, bottom, w, h where Figma gives them.
    h is only reported unless h_cmp is set (the section box); text heights are not compared."""
    return {"key": key, "sel": sel, "h_cmp": h_cmp, "fig": fig}


# Figma points (top-left corner of each node, px): x from the page's left edge, y from the top of the section
ROWS = {
    "390": [
        P("section", SEC, h=828, h_cmp=True),
        P("label", ".fin__label", x=16, y=104),
        P("g1", ".fin__g1", x=16, y=140, h=38),
        P("g2", ".fin__g2", right=374, y=178, h=38),
        P("team", ".fin__team", x=158, y=264, w=216),
        P("phrase", ".fin__phrase", x=16, y=424, h=42),
        P("more", ".fin__more", x=158, y=482, w=216),
        P("link", ".fin__lt", right=374, y=610, bottom=644),
        P("contacts", ".fin__contacts", x=16, y=708),
    ],
    "834": [
        P("section", SEC, h=824, h_cmp=True),
        P("label", ".fin__label", x=32, y=96),
        P("g1", ".fin__g1", x=32, y=140, h=78),
        P("g2", ".fin__g2", right=802, y=218, h=78),
        P("team", ".fin__team", x=417, y=352, w=385),
        P("phrase", ".fin__phrase", x=32, y=486, h=77),
        P("more", ".fin__more", x=571, y=498, w=231, right=802),
        P("link", ".fin__lt", right=802, y=610, bottom=646),
        P("contacts", ".fin__contacts", x=32, y=710),
    ],
    "1440": [
        P("section", SEC, h=900, h_cmp=True),
        P("label", ".fin__label", x=64, y=104),
        P("g1", ".fin__g1", x=64, y=136, h=170),
        P("g2", ".fin__g2", right=1376, y=306, h=170),
        P("team", ".fin__team", x=720, y=520, w=416),
        P("phrase", ".fin__phrase", x=64, y=700, h=120),
        P("more", ".fin__more", x=888, y=712, w=256),
        P("link", ".fin__lt", right=1376, y=812, bottom=848),
        P("contacts", ".fin__contacts", x=64, y=852),
    ],
}

# Part C boxes (viewport coordinates) and their Figma names for the report
BOXES = {"label": ".fin__label", "g1": ".fin__g1", "g2": ".fin__g2", "team": ".fin__team",
         "phrase": ".fin__phrase", "more": ".fin__more", "lt": ".fin__lt", "contacts": ".fin__contacts"}
BOX_NAME = {"label": "метка", "g1": "Ваш", "g2": "вечер", "team": "команда", "phrase": "фраза",
            "more": "продолжение", "lt": "ссылка", "contacts": "контакты"}

# Form: selectors, and the expected boxes (viewport coordinates) as (field, expected, tolerance)
FORM_SEL = {"sec": SEC, "dialog": DLG, "panel": ".sheet__form", "field": ".field", "submit": ".sheet__submit",
            "consent": ".sheet__consent", "close": ".sheet__close"}
FORM_BOXES = {  # box: (name, [(field, expected, tolerance), ...]); fields x, y (top), w, h, r (right), b (bottom)
    "dlg": ("диалог #form (ширина = documentElement.clientWidth)",
            [("x", 0, 4), ("y", 0, 4), ("w", None, 4), ("h", 900, 4)]),
    "panel": ("панель .sheet__form", [("x", 720, 4), ("y", 136, 4), ("w", 656, 4), ("h", 700, 4)]),
    "field1": ("поле 1 (.field)", [("x", 760, 4), ("y", 295, 4), ("w", 576, 4), ("h", 72, 4)]),
    "field2": ("поле 2 (.field)", [("x", 760, 4), ("y", 395, 4), ("w", 576, 4), ("h", 72, 4)]),
    "field3": ("поле 3 (.field)", [("x", 760, 4), ("y", 495, 4), ("w", 576, 4), ("h", 158, 4)]),
    "submit": ("текст кнопки .sheet__submit (без padding 8 px сверху и снизу)",
               [("r", 1336, 4), ("y", 681, 4), ("b", 746, 4)]),
    "consent": ("блок .sheet__consent", [("x", 760, 4), ("y", 762, 4)]),
}

# Part A, one call per frame: x = page-left edge, y = top relative to the section (the reference element)
MEASURE_FRAME = """([rows, refSel]) => {
  const ref = document.querySelector(refSel);
  if (!ref) return null;
  const top = ref.getBoundingClientRect().top;
  const out = {};
  for (const r of rows) {
    const el = document.querySelector(r.sel);
    if (!el) { out[r.key] = null; continue; }
    const b = el.getBoundingClientRect();
    out[r.key] = { x: b.left + scrollX, r: b.right + scrollX, y: b.top - top, b: b.bottom - top, w: b.width, h: b.height };
  }
  return out;
}"""

# Part C, one call per window with the section at the top; viewport coordinates
MEASURE_WIN = """(a) => {
  const box = (el) => {
    if (!el) return null;
    const r = el.getBoundingClientRect();
    return { l: r.left, r: r.right, t: r.top, b: r.bottom, w: r.width, h: r.height };
  };
  const sec = document.querySelector(a.sec);
  const boxes = {};
  for (const [k, sel] of Object.entries(a.boxes)) boxes[k] = box(document.querySelector(sel));
  return {
    iw: innerHeight,
    cw: document.documentElement.clientWidth,
    sec: box(sec),
    k12: sec ? getComputedStyle(sec).getPropertyValue('--k12').trim() : null,
    boxes: boxes,
  };
}"""

# Form measurement, viewport coordinates: x, y = left and top; r, b = right and bottom
MEASURE_FORM = """(a) => {
  const q = (s) => document.querySelector(s);
  const box = (el) => {
    if (!el) return null;
    const r = el.getBoundingClientRect();
    return { x: r.left, y: r.top, w: r.width, h: r.height, r: r.right, b: r.bottom };
  };
  const dlg = q(a.dialog);
  const panel = q(a.panel);
  const scope = panel || dlg || document;
  const close = q(a.close);
  const cr = close ? close.getBoundingClientRect() : null;
  const bg = (el) => (el ? getComputedStyle(el).backgroundColor : null);
  return {
    sec: box(q(a.sec)),
    open: dlg ? dlg.open : null,
    dlg: box(dlg),
    dlgBg: bg(dlg),
    panel: box(panel),
    panelBg: bg(panel),
    panelScroll: panel ? [panel.scrollHeight, panel.clientHeight] : null,
    fields: [...scope.querySelectorAll(a.field)].slice(0, 3).map((el) => box(el)),
    submit: box(q(a.submit)),
    consent: box(q(a.consent)),
    close: cr ? { cx: cr.left + cr.width / 2, cy: cr.top + cr.height / 2 } : null,
  };
}"""

SW = "() => document.documentElement.scrollWidth - document.documentElement.clientWidth"
DLG_OPEN = "(s) => { const d = document.querySelector(s); return d ? d.open : null; }"


class Report:
    """Printed lines, kept for report.txt."""

    def __init__(self):
        self.lines = []

    def say(self, text=""):
        print(text)
        self.lines.append(text)


def near(part, key, name, value, expected, tol=THRESH):
    """Check: |value - expected| <= tol. A missing value (None) fails."""
    if value is None:
        name += " — нет элемента"
    ok = value is not None and abs(value - expected) <= tol
    return {"part": part, "key": key, "name": name, "value": value, "expected": expected, "tol": tol,
            "ok": ok, "px": True}


def at_most(part, key, name, value, limit):
    """Check: value <= limit, with 0.5 px of rounding allowed."""
    if value is None:
        name += " — нет элемента"
    ok = value is not None and value <= limit + 0.5
    return {"part": part, "key": key, "name": name, "value": value, "expected": f"<= {limit}", "tol": None,
            "ok": ok, "px": True}


def flag(part, key, name, ok, value=None, expected=None, px=False):
    """Yes / no check (colours, states, overlaps, preconditions). The value is shown, not compared."""
    return {"part": part, "key": key, "name": name, "value": value, "expected": expected, "tol": None,
            "ok": bool(ok), "px": px}


def info(part, key, name, value, expected=None, px=True):
    """Measured value, reported only: ok is None, so it is not counted as a check."""
    return {"part": part, "key": key, "name": name, "value": value, "expected": expected, "tol": None,
            "ok": None, "px": px}


def label(r):
    """Expected value and tolerance of a check, printed after the measured value."""
    exp = r["expected"]
    if exp is None:
        return ""
    if isinstance(exp, str):
        return f" (ожидалось {exp})"
    if r["tol"] is None:
        return f" (ожидалось {exp:g})"
    return f" (ожидалось {exp:g}, допуск {r['tol']:g})"


def fmt(v):
    """Measured value for the printed report."""
    return f"{v:.1f}" if isinstance(v, float) else str(v)


def show(rep, recs, show_all):
    """Checks as printed lines: failures always, passing checks only with --all, info records never."""
    for r in recs:
        if r["ok"] is None or (r["ok"] and not show_all):
            continue
        value = "" if r["value"] is None else f": {fmt(r['value'])}"
        rep.say(f"  {'ok  ' if r['ok'] else 'FAIL'} {r['name']}{value}{label(r)}")


def part_total(rep, letter, recs, extra=""):
    """Totals of one part: the checks with a verdict and the failures among them."""
    checks = [r for r in recs if r["ok"] is not None]
    bad = sum(1 for r in checks if not r["ok"])
    rep.say(f"часть {letter}: FAIL {bad} из {len(checks)}" + (f", {extra}" if extra else ""))


def colour_is(value, rgb, alpha):
    """Computed colour rgb(...) or rgba(...) with exactly these channels and this alpha (within 0.01)."""
    m = re.fullmatch(r"rgba?\((.*)\)", value or "")
    if not m:
        return False
    try:
        nums = [float(p) for p in re.split(r"[,\s/]+", m.group(1).strip()) if p]
    except ValueError:
        return False
    if len(nums) not in (3, 4):
        return False
    return nums[:3] == [float(c) for c in rgb] and abs((nums[3] if len(nums) == 4 else 1.0) - alpha) <= 0.01


def box_recs(part, key, name, box, spec):
    """Checks of one box against (field, expected, tolerance) triples; a missing box fails every field."""
    return [near(part, f"{key}.{f}", f"{name}: {f}", None if box is None else box[f], exp, tol)
            for f, exp, tol in spec]


def open_page(browser, base, w, h):
    """Site page for comparison (as c3): no animations (STILL), lazy images loaded, fonts ready, +300 ms."""
    ctx = browser.new_context(viewport={"width": w, "height": h}, reduced_motion="reduce")
    page = ctx.new_page()
    page.goto(url_for(base, "site/index.html"), wait_until="networkidle")
    page.add_style_tag(content=STILL)
    eager(page)
    page.wait_for_timeout(300)
    return ctx, page


def scroll_section(page, dy=0, wait=300):
    """The section's offsetTop to the top of the window, plus dy. Instant scroll: smooth scrolling would start the
    entrance animations. False if the section is missing."""
    ok = page.evaluate("""([s, dy]) => {
      const el = document.querySelector(s);
      if (!el) return false;
      scrollTo({ left: 0, top: el.offsetTop + dy, behavior: 'instant' });
      return true;
    }""", [SEC, dy])
    page.wait_for_timeout(wait)
    return ok


def open_form(page):
    """Section to the top of the window, click the form link, wait 600 ms. Returns the error text, or None."""
    scroll_section(page)
    try:
        page.click(LINK, timeout=3000)
    except PlaywrightError as e:
        return (str(e).splitlines() or ["click failed"])[0]
    page.wait_for_timeout(600)
    return None


def shot_frame(page, key, path):
    """Frame screenshot as in c3: desktop = the window at the section top; phone and tablet = the whole section."""
    page.add_style_tag(content=HIDE)
    if key == "1440":
        scroll_section(page)
        page.screenshot(path=str(path))
    else:
        page.locator(SEC).screenshot(path=str(path), timeout=5000)


def point_recs(frame, r, m):
    """Records for one Figma point: a check per compared value; text heights are recorded for information only."""
    out = []
    for f in FIELD_ORDER:
        if f not in r["fig"]:
            continue
        val = None if m is None else m[KEY[f]]
        key, name = f"A/{frame}/{r['key']}.{f}", f"{r['key']}.{f}"
        if f == "h" and not r["h_cmp"]:
            out.append(info("A", key, name, val, expected=r["fig"][f]))
        else:
            out.append(near("A", key, name, val, r["fig"][f]))
    return out


def point_line(r, m, recs):
    """Table row for one Figma point: Figma values, site values, deltas of the given fields, flag."""
    if m is None:
        return f"{r['key']:<9} нет элемента: {r['sel']}"
    given = [f for f in FIELD_ORDER if f in r["fig"]]
    fig_s = " ".join(f"{KEY[f]}{r['fig'][f]:g}" for f in given)
    site_s = " ".join(f"{KEY[f]}{m[KEY[f]]:.1f}" for f in given)
    deltas = " ".join(f"{m[KEY[f]] - r['fig'][f]:+7.1f}" if f in given else " " * 7 for f in FIELD_ORDER)
    flag_s = ">4" if any(x["ok"] is False for x in recs) else ""
    return f"{r['key']:<9} {fig_s:<36} {site_s:<34} {deltas}  {flag_s}"


def part_a(browser, base, engine, rep, show_all):
    """Part A: Figma points of the three frames: table rows over the threshold, a summary and a screenshot per frame."""
    rep.say("\nчасть A — точки Figma (x, y — от левого края страницы и от верха секции; r, b — правый и нижний края):")
    recs, frames_bad = [], 0
    for key, (w, h, title) in FRAMES.items():
        ctx, page = open_page(browser, base, w, h)
        meas = page.evaluate(MEASURE_FRAME, [ROWS[key], SEC]) or {}
        frame_recs, rows = [], []
        for r in ROWS[key]:
            m = meas.get(r["key"])
            pr = point_recs(key, r, m)
            frame_recs += pr
            rows.append((r, m, pr))
        bad_points = sum(1 for _, _, pr in rows if any(x["ok"] is False for x in pr))
        worst = max(((abs(x["value"] - x["expected"]), x["name"]) for x in frame_recs
                     if x["ok"] is not None and x["value"] is not None), default=(0.0, "-"))
        head = f"{engine} · {w}x{h} · {title}"
        if bad_points == 0 and not show_all:
            rep.say(f"{head}: ok (≤{THRESH} px), наибольшее отклонение {worst[0]:.1f} px")
        else:
            rep.say(f"\n{head}")
            rep.say(HEAD_A)
            for r, m, pr in rows:
                if show_all or any(x["ok"] is False for x in pr):
                    rep.say(point_line(r, m, pr))
            rep.say(f"  кадр: наибольшее отклонение {worst[0]:.1f} px ({worst[1]}), точек > {THRESH} px: {bad_points}")
        frames_bad += 1 if bad_points else 0
        if meas.get("section") is not None:
            shot_frame(page, key, OUT / f"site_{engine}_{key}.png")
        else:
            rep.say(f"  снимок {key} не сделан: нет секции {SEC}")
        ctx.close()
        recs += frame_recs
    part_total(rep, "A", recs, extra=f"кадров > {THRESH} px: {frames_bad} из {len(FRAMES)}")
    return recs


def part_b(browser, base, engine, rep, show_all):
    """Part B: desktop 1440x900 with the form open (viewport coordinates), a screenshot, then Escape."""
    rep.say("\nчасть B — форма открыта, окно 1440x900 (вьюпорт; x, y — левый и верхний край; r, b — правый и нижний;"
            " w, h — размеры):")
    ctx, page = open_page(browser, base, 1440, 900)
    err = open_form(page)
    m = page.evaluate(MEASURE_FORM, FORM_SEL)
    sec, close, cons = m["sec"], m["close"], m["consent"]
    recs = [flag("B", "B/click", "клик по .fin__link открывает форму", err is None, value=err),
            near("B", "B/sec.y", "секция: верх в окне", None if sec is None else sec["y"], 0, tol=1),
            flag("B", "B/open", "диалог #form открыт", m["open"] is True, value=m["open"]),
            flag("B", "B/dlg.bg", "фон диалога #form", colour_is(m["dlgBg"], (6, 6, 6), 0.6),
                 value=m["dlgBg"], expected="rgba(6, 6, 6, 0.6)"),
            flag("B", "B/panel.bg", "фон панели .sheet__form", colour_is(m["panelBg"], (198, 194, 182), 1.0),
                 value=m["panelBg"], expected="rgb(198, 194, 182)")]
    sub = m["submit"]                                   # the text box: the button minus its 8 px padding top and bottom
    sub_text = None if sub is None else {**sub, "y": sub["y"] + 8, "b": sub["b"] - 8}
    boxes = {"dlg": m["dlg"], "panel": m["panel"], "submit": sub_text, "consent": m["consent"],
             "field1": m["fields"][0] if len(m["fields"]) > 0 else None,
             "field2": m["fields"][1] if len(m["fields"]) > 1 else None,
             "field3": m["fields"][2] if len(m["fields"]) > 2 else None}
    cw = page.evaluate("() => document.documentElement.clientWidth")   # dialog open: the scroll lock's gutter included
    for key, (name, spec) in FORM_BOXES.items():
        if key == "dlg":                                # the expected width is clientWidth, not a fixed 1440
            spec = [(f, cw if f == "w" else e, t) for f, e, t in spec]
        recs += box_recs("B", f"B/{key}", name, boxes[key], spec)
    recs.append(near("B", "B/close.cx", "крестик .sheet__close: центр x",
                     None if close is None else close["cx"], 1324))
    recs.append(near("B", "B/close.cy", "крестик .sheet__close: центр y",
                     None if close is None else close["cy"], 188))
    recs.append(at_most("B", "B/consent.w", "блок .sheet__consent: w", None if cons is None else cons["w"], 416))
    page.screenshot(path=str(OUT / f"form_{engine}_1440.png"))
    page.keyboard.press("Escape")
    page.wait_for_timeout(600)
    still_open = page.evaluate(DLG_OPEN, DLG)
    recs.append(flag("B", "B/esc", "Escape закрывает диалог: open = false через 600 мс", still_open is False,
                     value=still_open))
    ctx.close()
    show(rep, recs, show_all)
    part_total(rep, "B", recs)
    return recs


def fit_recs(m, w, h):
    """Part C checks for one window, section at the top: section height and top, every box inside the section, no
    overlaps (Ваш and вечер may touch). --k12, the team-phrase gap and the box edges are reported."""
    k = f"{w}x{h}"
    sec, bx = m["sec"], m["boxes"]
    if sec is None:
        return [flag("C", f"C/{k}/sec", f"{k}: секция {SEC} есть", False)]
    recs = [near("C", f"C/{k}/sec.h", f"{k}: высота секции = высота окна", sec["h"], m["iw"], tol=1),
            near("C", f"C/{k}/sec.t", f"{k}: верх секции в окне", sec["t"], 0, tol=1)]
    for n, sel in BOXES.items():
        if bx.get(n) is None:
            recs.append(flag("C", f"C/{k}/{n}", f"{k}: {BOX_NAME[n]} ({sel}) есть", False))
    outside = [BOX_NAME[n] for n in BOXES if bx.get(n) is not None and (
        bx[n]["l"] < sec["l"] - 0.5 or bx[n]["r"] > sec["r"] + 0.5
        or bx[n]["t"] < sec["t"] - 0.5 or bx[n]["b"] > sec["b"] + 0.5)]
    recs.append(flag("C", f"C/{k}/inside", f"{k}: все блоки внутри секции", not outside,
                     value=", ".join(outside) or "нет"))
    pairs = []
    names = list(BOXES)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if {a, b} == {"g1", "g2"} or bx.get(a) is None or bx.get(b) is None:
                continue                        # Ваш and вечер may touch vertically
            p, q = bx[a], bx[b]
            if min(p["r"], q["r"]) - max(p["l"], q["l"]) > 0.5 and min(p["b"], q["b"]) - max(p["t"], q["t"]) > 0.5:
                pairs.append(f"{BOX_NAME[a]} × {BOX_NAME[b]}")
    recs.append(flag("C", f"C/{k}/overlap", f"{k}: блоки не перекрываются", not pairs,
                     value=", ".join(pairs) or "нет"))
    gap = None
    if bx.get("phrase") is not None and bx.get("team") is not None:
        gap = bx["phrase"]["t"] - bx["team"]["b"]           # vertical gap: top of the phrase minus bottom of the team
    recs.append(info("C", f"C/{k}/gap", f"{k}: зазор team → фраза", gap))
    recs.append(info("C", f"C/{k}/k12", f"{k}: --k12", m["k12"], px=False))
    for n in BOXES:
        if bx.get(n) is not None:
            for e in ("l", "r", "t", "b"):
                recs.append(info("C", f"C/{k}/{n}.{e}", f"{k}: {BOX_NAME[n]} {e}", bx[n][e]))
    for e in ("t", "b", "h"):
        recs.append(info("C", f"C/{k}/sec.{e}", f"{k}: секция {e}", sec[e]))
    return recs


def form_win_recs(fm, w, h, iw, cw):
    """Part C form at one window: the dialog opened, the panel inside the viewport, the panel does not overflow."""
    k = f"{w}x{h}"
    opened = fm["open"] is True
    recs = [flag("C", f"C/{k}/open", f"{k}: диалог #form открыт", opened, value=fm["open"])]
    p = fm["panel"]
    if p is None:
        recs.append(flag("C", f"C/{k}/panel", f"{k}: панель .sheet__form есть", False))
    else:
        margin = min(p["x"], p["y"], cw - p["r"], iw - p["b"])       # distance to the nearest viewport edge
        recs.append(flag("C", f"C/{k}/panel.in", f"{k}: панель целиком во вьюпорте, запас до края, px",
                         opened and margin >= -0.5, value=round(margin, 1), expected=">= 0", px=True))
    sc = fm["panelScroll"]
    if sc is None:
        recs.append(flag("C", f"C/{k}/panel.scroll", f"{k}: переполнение панели", False))
    else:
        over = sc[0] - sc[1]
        recs.append(flag("C", f"C/{k}/panel.scroll", f"{k}: переполнение панели, scrollHeight - clientHeight",
                         opened and over <= 1, value=over, expected="<= 1", px=True))
    return recs


def part_c(browser, base, engine, rep, show_all):
    """Part C: five desktop windows with the section at the top, then the form at each window."""
    rep.say("\nчасть C — подгонка под окно: секция у верха окна, затем форма в том же окне:")
    recs, gaps = [], []
    for w, h in WINDOWS:
        ctx, page = open_page(browser, base, w, h)
        scroll_section(page)
        m = page.evaluate(MEASURE_WIN, {"sec": SEC, "boxes": BOXES})
        wr = fit_recs(m, w, h)
        err = open_form(page)
        fm = page.evaluate(MEASURE_FORM, FORM_SEL)
        wr.append(flag("C", f"C/{w}x{h}/click", f"{w}x{h}: клик по .fin__link открывает форму", err is None,
                       value=err))
        wr += form_win_recs(fm, w, h, m["iw"], m["cw"])
        ctx.close()
        gap = next((r["value"] for r in wr if r["key"].endswith("/gap")), None)
        if gap is not None:
            gaps.append((gap, f"{w}x{h}"))
        gap_s = "нет" if gap is None else f"{gap:.1f} px"
        rep.say(f"окно {w}x{h}: innerHeight {m['iw']}, clientWidth {m['cw']}, "
                f"--k12 {m['k12'] or 'не задан'}, зазор team → фраза {gap_s}")
        show(rep, wr, show_all)
        recs += wr
    if gaps:
        smallest, where = min(gaps)
        rep.say(f"наименьший зазор team → фраза: {smallest:.1f} px (окно {where})")
    part_total(rep, "C", recs)
    return recs


def part_d(browser, base, engine, rep, show_all):
    """Part D: no horizontal scroll at nine widths (height 900): at the section top, then -200 px after 250 ms."""
    rep.say("\nчасть D — горизонтальный скролл (scrollWidth - clientWidth, высота 900):"
            " у секции, затем секция -200 px через 250 мс:")
    recs = []
    for w in WIDTHS:
        ctx, page = open_page(browser, base, w, 900)
        scroll_section(page)
        a = page.evaluate(SW)
        scroll_section(page, dy=-200, wait=250)
        b = page.evaluate(SW)
        ctx.close()
        recs.append(flag("D", f"D/{w}/a", f"{w}: у секции", a <= 0, value=a, expected="<= 0", px=True))
        recs.append(flag("D", f"D/{w}/b", f"{w}: секция -200 px через 250 мс", b <= 0, value=b, expected="<= 0",
                         px=True))
    show(rep, recs, show_all)
    part_total(rep, "D", recs)
    return recs


def run_engine(browser, base, engine, rep, show_all):
    """The four parts for one engine; every record is tagged with the engine."""
    recs = []
    for part in (part_a, part_b, part_c, part_d):
        recs += part(browser, base, engine, rep, show_all)
    for r in recs:
        r["engine"] = engine
    return recs


def max_diff(records):
    """Largest |chromium - webkit| over the px values both engines measured: (difference, key)."""
    by_key = {}
    for r in records:
        if r["px"] and isinstance(r["value"], (int, float)):
            by_key.setdefault(r["key"], {})[r["engine"]] = r["value"]
    best = (0.0, None)
    for key, vals in by_key.items():
        if "chromium" in vals and "webkit" in vals and abs(vals["chromium"] - vals["webkit"]) > best[0]:
            best = (abs(vals["chromium"] - vals["webkit"]), key)
    return best


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-b", "--browser", default="both", choices=["chromium", "webkit", "both"])
    ap.add_argument("--all", action="store_true", help="print every row and check, not only the failures")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    engines = ENGINES if args.browser == "both" else [args.browser]
    OUT.mkdir(parents=True, exist_ok=True)
    rep, records = Report(), []
    with serve() as base, sync_playwright() as p:
        for engine in engines:
            rep.say(f"\n=== {engine} ===")
            browser = getattr(p, engine).launch()
            records += run_engine(browser, base, engine, rep, args.all)
            browser.close()
    checks = [r for r in records if r["ok"] is not None]
    fails = [r for r in checks if not r["ok"]]
    rep.say(f"\nитого, движки: {', '.join(engines)}: FAIL {len(fails)} из {len(checks)} проверок")
    diff, where = max_diff(records) if len(engines) == 2 else (None, None)
    if diff is None:
        rep.say("chromium vs webkit max diff: не считается, запущен один движок")
    else:
        rep.say(f"наибольшее расхождение движков: {where or 'нет общих точек'} ({diff:.1f} px)")
        rep.say(f"chromium vs webkit max diff {diff:.1f} px")
    summary = {"threshold_px": THRESH, "engines": engines, "checks": len(checks), "fails": len(fails),
               "chromium_vs_webkit_max_diff_px": diff, "max_diff_at": where, "records": records}
    (OUT / "report.txt").write_text("\n".join(rep.lines) + "\n", encoding="utf-8")
    (OUT / "report.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
