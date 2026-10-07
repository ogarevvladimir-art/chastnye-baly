"""Собирает ТЕКСТ.md из выгрузок scan_text_nodes (папка ../_figma) и сверяет 390 / 834 с десктопом.

Запуск: python tools/figma_text.py  (из Доработка/вёрстка)
Выгрузки делаются через figma-mcp-express batch(scan_text_nodes) — см. ЖУРНАЛ, этап 0.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "_figma"


def load(name):
    return [r["data"]["textNodes"] for r in json.loads((FIG / name).read_text("utf-8"))["results"]]


rest_d = load("text_1440_rest.json")          # 16 секций 191:626
rest_mt = load("text_390_834_rest.json")      # 12 кадров 258:4034, затем 12 кадров 258:4531
st1 = load("text_states.json")
st2 = load("text_states2.json")
rest_m, rest_t = rest_mt[:12], rest_mt[12:]

# Курсив и ссылки в смешанных узлах десктопа — по рендеру (_figma/v0_mixed_sheet.png)
# и по отдельным узлам H2 Italic на 390.
MIXED = {
    "223:2154": "*Ваша* история.",
    "223:2155": "*Ваш* вечер.",
    "219:1909": "*Как* мы готовим",
    "219:2109": "*ваш* вечер",
    "223:2596": "*Как* проходит",
    "223:2612": "*а* не готовая",
    "198:893": "*Выйти танцевать* оказывается проще, чем весь вечер быть зрителем.",
    "198:1297": "*Страх*\nисчезает",
    "198:1309": "*Не лекция* —\nпоказываем",
    "198:1303": "*Нет чужих* —\nтолько свои",
    "198:1315": "*Подготовка* —\nчасть события",
    "225:862": "*к* балу",
    "207:1884": "*Не* ограничение,",
    "207:1885": "*а* стиль",
    "191:929": "Нажимая «отправить», вы соглашаетесь с [политикой конфиденциальности].",
    "258:4500": "Нажимая «отправить», вы соглашаетесь с [политикой конфиденциальности].",
}

# Блоки: (заголовок, якорь, десктоп-покой, десктоп-состояния, 390, 834)
BLOCKS = [
    ("Шапка и меню", "—",
     [], [("219:1067 меню открыто", st1[6])],
     [("229:1138 меню", st1[7])], [("254:2334 меню", st1[8])]),
    ("Hero → Форматы", "#formats",
     [rest_d[0], rest_d[1]], [("223:2222 Hero C·2", st2[11]), ("223:2185 наведение «Частные»", st2[0]),
                              ("223:2203 наведение «Корпоративные»", st2[1])],
     [("258:4035", rest_m[0])], [("258:4532", rest_t[0])]),
    ("01 Подготовка", "#prep", [rest_d[2]], [("219:1939 наведение", st2[10])],
     [("258:4069", rest_m[1])], [("258:4568", rest_t[1])]),
    ("02 Вечер", "#evening", [rest_d[3]], [(f"{i} шаг", s) for i, s in
                                           zip(["223:2492", "223:2518", "223:2544", "223:2570"], st1[0:4])],
     [("258:4101", rest_m[2])], [("258:4600", rest_t[2])]),
    ("03 Музыка", "#music", [rest_d[4]], [("223:2654", st2[8]), ("223:2682", st2[9])],
     [("258:4163", rest_m[3])], [("258:4662", rest_t[3])]),
    ("04 Танцмейстер", "#dancemaster", [rest_d[5]], [("198:897", st2[2]), ("198:918", st2[3])],
     [("258:4193", rest_m[4])], [("258:4692", rest_t[4])]),
    ("05 Шоу", "#show", [rest_d[6]], [("213:872", st2[4]), ("213:899", st2[5])],
     [("258:4216", rest_m[5]), ("242:2122", st1[11]), ("242:2154", st1[12])],
     [("258:4715", rest_t[5]), ("256:3092", st1[15]), ("256:3126", st1[16])]),
    ("06 Ассистент", "#assistant", [rest_d[7]], [("198:1206", st1[4]), ("198:1241", st1[5])],
     [("258:4250", rest_m[6])], [("258:4750", rest_t[6])]),
    ("07 Уроки", "#lessons", [rest_d[8]], [], [("258:4281", rest_m[7])], [("258:4781", rest_t[7])]),
    ("08 Этикет", "#etiquette", [rest_d[9]], [("207:2000 Дамам", st2[6])],
     [("258:4316", rest_m[8]), ("247:1052 Дамам", st1[13])], [("258:4816", rest_t[8]), ("256:3489 Дамам", st1[17])]),
    ("09 Дресс-код", "#dresscode", [rest_d[10]], [], [("258:4370", rest_m[9])], [("258:4870", rest_t[9])]),
    ("10 Вечера", "#evenings", [rest_d[11]], [("219:1006 Кашемир", st2[7])],
     [("258:4433", rest_m[10]), ("252:1368 Кашемир", st1[14])], [("258:4933", rest_t[10]), ("256:3860 Кашемир", st1[18])]),
    ("11 О нас · 12 Связаться · Контакты · подвал", "#about, #contact",
     [rest_d[12], rest_d[13], rest_d[14], rest_d[15]], [],
     [("258:4478", rest_m[11])], [("258:4982", rest_t[11])]),
    ("Форма (лист)", "—", [], [], [("253:2035 лист", st1[9])], [("256:3842 лист", st1[10])]),
]


# Различия раскладки, а не текста: слова есть только на десктопе по замыслу адаптива.
EXPECTED = {
    "Шапка и меню": ("меню 390 / 834 — гиганты без номеров «01 — …» (решение адаптива, этап 1)",
                     {f"{i:02d}" for i in range(1, 13)}),
    "Hero → Форматы": ("ссылки навигации и телефон живут в десктопной шапке `Header · v2`; на 390 / 834 их нет в шапке — они в меню",
                       {"000-00-00", "495", "7", "вечера", "как", "нас", "о", "происходит", "связаться"}),
    "11 О нас · 12 Связаться · Контакты · подвал": (
        "на десктопе поля формы показаны заполненными примерами («Анна», «+7 916 …», «Юбилей родителей…»); на 390 / 834 поля пустые",
        {"916", "анна", "весной", "около", "родителей", "шестидесяти", "юбилей"}),
}


def text_of(n):
    if n["id"] in MIXED:
        return MIXED[n["id"]]
    if n["characters"].startswith("Нажимая «отправить»"):
        return MIXED["191:929"]
    fn = n["fontName"]
    t = n["characters"]
    if isinstance(fn, dict) and fn.get("style") == "Italic":
        return f"*{t}*"
    return t


def style_of(n):
    fn = n["fontName"]
    if isinstance(fn, str):
        fam = "Unbounded" if n["fontSize"] <= 16 else "Old Standard"
        return f"{fam} {n['fontSize']} смеш."
    fam = "Old Standard" if fn["family"].startswith("Old") else "Unbounded"
    st = {"Regular": "", "Bold": " Bold", "Italic": " Italic"}.get(fn["style"], " " + fn["style"])
    return f"{fam}{st} {n['fontSize']}"


def norm(s):
    s = s.replace("\xa0", " ").replace("‑", "-").replace("*", "").replace("[", "").replace("]", "")
    s = s.replace("ё", "е").replace("Ё", "Е") if False else s
    return re.sub(r"\s+", " ", s).strip().lower()


def words(s):
    return set(re.findall(r"[\wё]+(?:-[\wё]+)*", norm(s)))


def fmt(t):
    return t.replace("\n", " ↵ ")


out = []
flags = []
out.append("# Текст сайта из Figma\n")
out.append("Источник — только Figma: десктоп `191:626` (покой и состояния), телефон `258:4034`, планшет `258:4531` и их состояния. "
           "Собрано `tools/figma_text.py` из выгрузок `_figma/*.json` (этап 0, 2026-10-02).\n")
out.append("- `*курсив*` — Old Standard Italic (в H2 — служебное слово, на сайте `<em>`). Курсив смешанных узлов десктопа снят по рендеру "
           "(`_figma/v0_mixed_sheet.png`) и совпадает с отдельными узлами H2 Italic на 390.\n"
           "- ` ↵ ` — разрыв строки внутри узла Figma (на сайте `<br>` или отдельная строка-блок).\n"
           "- `[текст]` — ссылка (в Figma подчёркнута).\n"
           "- Неразрывные пробелы из Figma сохранены в файле как есть (U+00A0).\n"
           "- Регистр — как набран в Figma. Гиганты, капс 12 и метки 11 делаются капсом стилем (`text-transform`), в HTML пишем как здесь.\n"
           "- Колонка «стиль» — гарнитура и кегль в макете 1440, для ориентира; роли — в `tokens.css` / `base.css`.\n")

for title, anchor, d_rest, d_states, m_list, t_list in BLOCKS:
    out.append(f"\n## {title}\n\nЯкорь: `{anchor}`\n")
    seen = set()
    d_all = []
    if d_rest or d_states:
        out.append("\n| ID | стиль 1440 | текст |\n|---|---|---|")
        for sec in d_rest:
            for n in sec:
                t = text_of(n)
                if t in seen:
                    continue
                seen.add(t)
                d_all.append(t)
                out.append(f"| `{n['id']}` | {style_of(n)} | {fmt(t)} |")
        extra = []
        for label, sec in d_states:
            for n in sec:
                t = text_of(n)
                if t in seen:
                    continue
                seen.add(t)
                d_all.append(t)
                extra.append(f"| `{n['id']}` | {style_of(n)} | {fmt(t)} — *из {label}* |")
        out.extend(extra)
    else:
        out.append("\nНа десктопе отдельного кадра нет — текст по 390 / 834.\n")

    # сверка 390 / 834 с десктопом
    def frag_check(lst, width):
        res = []
        nodes = [n for _, sec in lst for n in sec]
        d_concat = norm(" ".join(d_all))
        d_words = words(" ".join(d_all))
        w_all = words(" ".join(n["characters"] for n in nodes))
        miss_frag = []
        for n in nodes:
            c = norm(n["characters"])
            if c and c not in d_concat and c not in {"меню", "+"}:
                miss_frag.append(f"`{n['id']}` «{fmt(n['characters'])}»")
        only_d = sorted(d_words - w_all - EXPECTED.get(title, ("", set()))[1])
        return miss_frag, only_d, nodes

    m_frag, m_only, m_nodes = frag_check(m_list, 390)
    t_frag, t_only, t_nodes = frag_check(t_list, 834)
    if not d_all:
        # нет десктопа — сравнить 390 и 834 между собой и выписать текст 390
        out.append("\n| ID 390 | стиль 390 | текст |\n|---|---|---|")
        s2 = set()
        for n in m_nodes:
            t = text_of(n)
            if t in s2:
                continue
            s2.add(t)
            out.append(f"| `{n['id']}` | {style_of(n)} | {fmt(t)} |")
        mw = words(" ".join(n["characters"] for n in m_nodes))
        tw = words(" ".join(n["characters"] for n in t_nodes))
        diff = (mw ^ tw)
        out.append(f"\nСверка 390 ↔ 834: {'совпадает по словам' if not diff else 'расходится: ' + ', '.join(sorted(diff))}.")
        if diff:
            flags.append(f"{title}: 390 ↔ 834 — {', '.join(sorted(diff))}")
        continue
    lines = []
    for w, frag, only in (("390", m_frag, m_only), ("834", t_frag, t_only)):
        if not frag and not only:
            lines.append(f"- **{w}:** совпадает с десктопом.")
            continue
        if frag:
            lines.append(f"- **{w}: нет на десктопе дословно:** " + "; ".join(frag))
            flags.append(f"{title} · {w}: нет на десктопе дословно — " + "; ".join(frag))
        if only:
            lines.append(f"- **{w}: слова десктопа, которых нет на {w}:** " + ", ".join(only))
            flags.append(f"{title} · {w}: нет слов десктопа — " + ", ".join(only))
    out.append("\n**Сверка с 390 / 834**\n")
    out.extend(lines)

out.append("\n## Флаги сверки (сводка)\n")
out.extend(f"- {f}" for f in flags) if flags else out.append("Расхождений нет.")
(ROOT / "ТЕКСТ.md").write_text("\n".join(out) + "\n", "utf-8")
print(f"ТЕКСТ.md: {len(out)} строк, флагов {len(flags)}")
for f in flags:
    print(" -", f)
