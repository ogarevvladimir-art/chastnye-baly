"""Разметка <picture> по сводке фото (photos_site.json, этап 1) — чтобы не набирать source вручную.

  python tools/picture.py evening/step-01 --sizes m="min(448px, calc(100vw - 32px))" t="calc(50vw - 32px)" d="55.6vw" \
         --alt "Гости в зале" [--lazy] [--only m,t] [--indent 10]

Раскладка, которой нет в --only, получает пустой 1×1 GIF: браузер на этой ширине ничего не грузит
(пример: фото карточек 03 на десктопе, где вместо них — сцена). Порядок source: d → t → m, внутри avif → webp → jpg.
"""
import argparse
import json
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
SITE = TOOLS.parents[2] / "site"
EMPTY = "data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="
MEDIA = {"d": "(min-width: 1024px)", "t": "(min-width: 600px)", "m": None}


def picture(key, sizes, alt, lazy, only, indent, cls=None):
    info = json.loads((TOOLS / "photos_site.json").read_text(encoding="utf-8"))[key]["layouts"]
    pad = " " * indent
    c = f' class="{cls}"' if cls else ""
    out = [f"{pad}<picture{c}>"]
    fallback = None
    for lay in ("d", "t", "m"):
        if lay not in info:
            continue
        media = MEDIA[lay]
        m = f' media="{media}"' if media else ""
        name = key.split("/")[-1]
        folder = key.split("/")[0]
        widths = [w for w in info[lay]["widths"] if (SITE / "img" / folder / f"{name}-{lay}-{w}.jpg").exists()]
        s = sizes.get(lay, "100vw")
        if only and lay not in only:
            out.append(f'{pad}  <source{m} srcset="{EMPTY}">')
            if lay == "m":
                fallback = (f"img/{folder}/{name}-m-{widths[0]}.jpg {widths[0]}w", s, widths, info[lay]["frame"], folder, name)
            continue
        for ext, typ in (("avif", "image/avif"), ("webp", "image/webp"), ("jpg", None)):
            srcset = ", ".join(f"img/{folder}/{name}-{lay}-{w}.{ext} {w}w" for w in widths)
            if lay == "m" and ext == "jpg":
                fallback = (srcset, s, widths, info[lay]["frame"], folder, name)
                continue
            t = f' type="{typ}"' if typ else ""
            out.append(f'{pad}  <source{m}{t} srcset="{srcset}" sizes="{s}">')
    if fallback is None:
        # Раскладки телефона нет (слот D 10): на телефоне пустой GIF, размеры — по планшету
        frame = info["t"]["frame"]
        attrs = f'width="{frame[0]}" height="{frame[1]}" alt="{alt}"' + (' loading="lazy"' if lazy else "")
        out.append(f'{pad}  <img src="{EMPTY}" {attrs} decoding="async">')
        out.append(f"{pad}</picture>")
        return "\n".join(out)
    srcset, s, widths, frame, folder, name = fallback
    attrs = f'width="{frame[0]}" height="{frame[1]}" alt="{alt}"'
    attrs += ' loading="lazy"' if lazy else ""
    out.append(f'{pad}  <img src="img/{folder}/{name}-m-{widths[0]}.jpg" srcset="{srcset}"')
    out.append(f'{pad}       sizes="{s}" {attrs} decoding="async">')
    out.append(f"{pad}</picture>")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("key")
    ap.add_argument("--sizes", nargs="*", default=[])
    ap.add_argument("--alt", default="")
    ap.add_argument("--lazy", action="store_true")
    ap.add_argument("--only", default="")
    ap.add_argument("--indent", type=int, default=0)
    ap.add_argument("--cls")
    a = ap.parse_args()
    sizes = dict(s.split("=", 1) for s in a.sizes)
    only = set(a.only.split(",")) if a.only else None
    print(picture(a.key, sizes, a.alt, a.lazy, only, a.indent, a.cls))


if __name__ == "__main__":
    main()
