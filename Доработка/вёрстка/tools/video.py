"""Видео прокрутки страницы (Playwright record_video) — сверка анимаций входа с раскадровками.

  python tools/video.py -w 390                      # вся страница сверху вниз
  python tools/video.py -w 1440 -s "#prep" -d 1600  # от блока 01 на 1600 px
  python tools/video.py -w 390 --speed 600 --pause 1500

Анимации не гасятся. Скролл — шагами по 40 px (как замер ore), скорость в px/с.
Файл: сверка/_видео/<name>_<ширина>.webm
"""
import argparse
import shutil
from pathlib import Path

from playwright.sync_api import sync_playwright

from _serve import PROJECT, SVERKA, serve, url_for, viewport_height


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--page", default="site/index.html")
    ap.add_argument("-w", "--width", type=int, default=390)
    ap.add_argument("-b", "--browser", default="chromium", choices=["chromium", "webkit"])
    ap.add_argument("-s", "--selector", help="начать с верха этого элемента")
    ap.add_argument("-d", "--distance", type=int, default=0, help="сколько прокрутить, px (0 — до конца)")
    ap.add_argument("--speed", type=int, default=800, help="px в секунду")
    ap.add_argument("--step", type=int, default=40)
    ap.add_argument("--pause", type=int, default=1000, help="пауза в начале и в конце, мс")
    ap.add_argument("--name", default="scroll")
    args = ap.parse_args()

    out_dir = SVERKA / "_видео"
    tmp = out_dir / "_tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    size = {"width": args.width, "height": viewport_height(args.width)}

    with serve() as base, sync_playwright() as pw:
        browser = getattr(pw, args.browser).launch()
        ctx = browser.new_context(viewport=size, record_video_dir=str(tmp), record_video_size=size)
        page = ctx.new_page()
        page.goto(url_for(base, args.page), wait_until="networkidle")
        page.evaluate("document.fonts.ready")
        start = 0
        if args.selector:
            start = page.evaluate(
                "s => document.querySelector(s).getBoundingClientRect().top + scrollY", args.selector)
            page.evaluate("y => scrollTo(0, y)", start)
        total = page.evaluate("document.documentElement.scrollHeight - innerHeight")
        end = min(total, start + args.distance) if args.distance else total
        page.wait_for_timeout(args.pause)
        dt = round(1000 * args.step / args.speed)
        y = start
        while y < end:
            y = min(end, y + args.step)
            page.evaluate("y => scrollTo(0, y)", y)
            page.wait_for_timeout(dt)
        page.wait_for_timeout(args.pause)
        video = page.video
        ctx.close()
        browser.close()
        src = Path(video.path())

    suffix = "" if args.browser == "chromium" else f"_{args.browser}"
    dst = out_dir / f"{args.name}_{args.width}{suffix}.webm"
    shutil.move(str(src), dst)
    shutil.rmtree(tmp, ignore_errors=True)
    print(dst.relative_to(PROJECT))


if __name__ == "__main__":
    main()
