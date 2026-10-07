# Контуры букв горизонтального гиганта для раскадровки входа (этап 4, блок 10).
# python _контуры_букв_гор.py <слово.svg> <префикс вывода> <число букв> <x глифа в полосе> <y глифа в полосе> [старт, с] [всего, с] [ширина полосы]
# слово.svg — SVG-экспорт неповёрнутого текста Giant 45 (габарит глифов). На выходе <префикс>_0/_25/_100.svg
# для import_svg в полосу «ширина × 38» (overflow: clip). Формула пилота: scaleX 3 → 1 от левого края буквы,
# сдвиг вправо i × 49, буква 0,8 с, шаг 0,05, expo-out, призрак 20 %. «всего» — длительность всей раскадровки
# (для 25 %), чтобы строки одного слова считались по общему времени.
# Этап 5 (планшет): [сдвиг буквы, px] [высота полосы] — сдвиг держим в em слова (49 / 91 ≈ 0,54em: 180 → 97, 92 → 50).
import re, sys

SRC, OUT, N_EXPECT = sys.argv[1], sys.argv[2], int(sys.argv[3])
GX, GY = float(sys.argv[4]), float(sys.argv[5])
START = float(sys.argv[6]) if len(sys.argv) > 6 else 0.15
TOTAL = float(sys.argv[7]) if len(sys.argv) > 7 and sys.argv[7] != '-' else None
STRIP_W = float(sys.argv[8]) if len(sys.argv) > 8 else 358
SHIFT = float(sys.argv[9]) if len(sys.argv) > 9 else 49
STRIP_H = float(sys.argv[10]) if len(sys.argv) > 10 else 38

svg = open(SRC, encoding='utf-8').read()
m = re.search(r'<path d="([^"]+)"([^>]*)/>', svg)
d, attrs = m.group(1), m.group(2)
fr = re.search(r'fill-rule="([^"]+)"', attrs)
fill_rule = f' fill-rule="{fr.group(1)}"' if fr else ''
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
    # same letter only when the sub-path lies inside the previous one (counters); at −3 % tracking
    # neighbours overlap (Г / А), so plain overlap is not enough
    if groups and a < groups[-1]['x1'] - 1 and b <= groups[-1]['x1'] + 1:
        groups[-1]['s'].append(s); groups[-1]['x1'] = max(groups[-1]['x1'], b)
    else:
        groups.append({'x0': a, 'x1': b, 's': [s]})
print('groups', len(groups), [(round(g['x0'], 1), round(g['x1'], 1), len(g['s'])) for g in groups])
# [склейка] — номера групп через «+», которые принадлежат одной букве (Ы = Ь + I): «3+4»
for spec in (sys.argv[11].split(',') if len(sys.argv) > 11 else []):
    a, b = (int(v) for v in spec.split('+'))
    groups[a]['s'] += groups[b]['s']; groups[a]['x1'] = max(groups[a]['x1'], groups[b]['x1'])
    groups[b] = None
groups = [g for g in groups if g]
assert len(groups) == N_EXPECT, len(groups)


def expo_out(t):
    if t <= 0: return 0.0
    if t >= 1: return 1.0
    return 1 - 2 ** (-10 * t)


n = len(groups)
total = TOTAL or (START + 0.05 * (n - 1) + 0.8)
for label, frac in (('0', 0.0), ('25', 0.25), ('100', 1.0)):
    t = total * frac
    paths = []
    for i, g in enumerate(groups):
        p = expo_out((t - (START + 0.05 * i)) / 0.8) if frac < 1 else 1.0
        s = 3 - 2 * p
        dshift = i * SHIFT * (1 - p)
        op = max(p, 0.2)
        x0 = g['x0']
        # X = GX + x0 + s*(x - x0) + dshift ; Y = GY + y
        e = GX + x0 - s * x0 + dshift
        paths.append(
            f'<path d="{"".join(g["s"])}"{fill_rule} fill="#C6C2B6" fill-opacity="{op:.2f}" '
            f'transform="matrix({s:.4f} 0 0 1 {e:.3f} {GY:.3f})"/>')
        print(label, i, 'p=%.3f op=%.2f' % (p, op))
    out = (f'<svg width="{STRIP_W:g}" height="{STRIP_H:g}" viewBox="0 0 {STRIP_W:g} {STRIP_H:g}" fill="none" '
           f'xmlns="http://www.w3.org/2000/svg">' + ''.join(paths) + '</svg>')
    open(f'{OUT}_{label}.svg', 'w', encoding='utf-8').write(out)
    print(label, 'len', len(out))
