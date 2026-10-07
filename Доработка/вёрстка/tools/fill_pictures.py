"""Подстановка <picture> в разметку: строка-маркер {{pic key | sizes m=… t=… d=… | alt}} заменяется выводом picture.py.

  python tools/fill_pictures.py черновик.html > готово.html

Отступ берётся по маркеру. Все фото — lazy.
"""
import re
import sys
from pathlib import Path

from picture import picture

PAT = re.compile(r"^(?P<pad>[ \t]*)\{\{pic (?P<key>\S+) \| (?P<sizes>.*?) \| (?P<alt>.*?)\}\}[ \t]*$", re.M)


def sub(m):
    sizes = dict(re.findall(r'(\w)="([^"]*)"', m["sizes"]))
    return picture(m["key"], sizes, m["alt"], True, None, len(m["pad"]))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print(PAT.sub(sub, Path(sys.argv[1]).read_text(encoding="utf-8")), end="")
