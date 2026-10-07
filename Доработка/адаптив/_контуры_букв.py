# Контуры букв гиганта для раскадровки входа (этап 3, блок 05).
# python _контуры_букв.py <слово.svg> <префикс вывода> <число букв> [merge_last|-] [высота полосы]
# слово.svg — SVG-экспорт неповёрнутого текста Giant 45; на выходе <префикс>_0/_25/_100.svg
# для import_svg в полосу 76 × высота (слово повёрнуто на 90°, начало — низ полосы; 05 — 600, 06 — 448).
import re, sys, math

SRC = sys.argv[1]
OUT = sys.argv[2]          # prefix for output svgs
N_EXPECT = int(sys.argv[3])
STRIP_H = int(sys.argv[5]) if len(sys.argv) > 5 else 600   # word origin at (0, STRIP_H)
DU, DV = 3.15, 1.125       # svg -> text-node offsets (ЖУРНАЛ, этап 2)

svg = open(SRC, encoding='utf-8').read()
m = re.search(r'<path d="([^"]+)"([^>]*)/>', svg)
d, attrs = m.group(1), m.group(2)
fill_rule = ''
fr = re.search(r'fill-rule="([^"]+)"', attrs)
if fr:
    fill_rule = f' fill-rule="{fr.group(1)}"'
subs = [s for s in re.split(r'(?=M)', d) if s.strip()]


def xrange_of(s):
    xs = []
    toks = re.findall(r'[MLHVCZQ]|-?\d+\.?\d*(?:e-?\d+)?', s)
    cmd = None; buf = []
    for t in toks:
        if t.isalpha():
            cmd = t; buf = []; continue
        buf.append(float(t))
        if cmd in ('M', 'L') and len(buf) == 2:
            xs.append(buf[0]); buf = []
        elif cmd == 'H' and len(buf) == 1:
            xs.append(buf[0]); buf = []
        elif cmd == 'V' and len(buf) == 1:
            buf = []
        elif cmd == 'C' and len(buf) == 6:
            xs += buf[0::2]; buf = []
        elif cmd == 'Q' and len(buf) == 4:
            xs += buf[0::2]; buf = []
    return min(xs), max(xs)


items = sorted(((*xrange_of(s), s) for s in subs), key=lambda t: t[0])
groups = []
for a, b, s in items:
    # same letter when the x-ranges overlap by more than 1 px (counters, split strokes)
    if groups and a < groups[-1]['x1'] - 1:
        groups[-1]['s'].append(s); groups[-1]['x1'] = max(groups[-1]['x1'], b)
    else:
        groups.append({'x0': a, 'x1': b, 's': [s]})
# two-part letter at the end (Ы)
if len(groups) == N_EXPECT + 1 and sys.argv[4:5] == ['merge_last']:
    h = groups.pop(); groups[-1]['s'] += h['s']; groups[-1]['x1'] = h['x1']
print('groups', len(groups), [(round(g['x0'], 1), round(g['x1'], 1), len(g['s'])) for g in groups])
assert len(groups) == N_EXPECT, len(groups)


def expo_out(t):
    if t <= 0: return 0.0
    if t >= 1: return 1.0
    return 1 - 2 ** (-10 * t)


n = len(groups)
total = 0.15 + 0.05 * (n - 1) + 0.8
for label, frac in (('0', 0.0), ('25', 0.25), ('100', 1.0)):
    t = total * frac
    paths = []
    for i, g in enumerate(groups):
        p = expo_out((t - (0.15 + 0.05 * i)) / 0.8) if frac < 1 else 1.0
        s = 3 - 2 * p
        dshift = i * 49 * (1 - p)
        op = max(p, 0.2)
        x0 = g['x0']
        # X = y + DV ; Y = STRIP_H - DU - (x0 + s*(x - x0) + dshift)
        a, b, c, dd = 0, -s, 1, 0
        e = DV
        f = STRIP_H - DU - x0 + s * x0 - dshift
        paths.append(
            f'<path d="{"".join(g["s"])}"{fill_rule} fill="#C6C2B6" fill-opacity="{op:.2f}" '
            f'transform="matrix({a} {b:.4f} {c} {dd} {e:.3f} {f:.3f})"/>')
        print(label, i, 'p=%.3f op=%.2f' % (p, op))
    out = f'<svg width="76" height="{STRIP_H}" viewBox="0 0 76 {STRIP_H}" fill="none" xmlns="http://www.w3.org/2000/svg">' + ''.join(paths) + '</svg>'
    open(f'{OUT}_{label}.svg', 'w', encoding='utf-8').write(out)
    print(label, 'len', len(out))
