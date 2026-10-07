"""Скриншоты сайта для сверки (Playwright, chromium и webkit).

Примеры (из Доработка/вёрстка):
  python tools/shots.py                                   # вся страница, все ширины, chromium
  python tools/shots.py -w 390 834 1440 -b chromium webkit
  python tools/shots.py -s "#prep" -o сверка/01            # один блок → сверка/01/site_390.png …
  python tools/shots.py --page Доработка/вёрстка/tools/roles-sample.html -o сверка/роли --name roles

Имена: <name>_<ширина>.png, у webkit — <name>_<ширина>_webkit.png.
На каждой ширине проверяется горизонтальный скролл страницы (его быть не должно).
"""
import argparse
import sys
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

from _serve import PROJECT, SVERKA, WIDTHS, serve, url_for, viewport_height

# Отключает анимации входа и переходы: скриншот покоя
STILL_CSS = """*,*::before,*::after{animation-duration:0s!important;animation-delay:0s!important;
transition-duration:0s!important;transition-delay:0s!important;scroll-behavior:auto!important}"""


def full_page_shot(page, path, dpr):
    """Вся страница — склейка экранов. Страница не прокручивается: body сдвигается вверх на высоту окна (transform),
    каждый кусок снимается как обычный экран. Так раскладка — как при scrollY 0 (sticky на своих местах, шаги закреплений
    не меняются), шапка (fixed внутри body с transform) стоит только наверху.
    Снимок full_page не годится (Р-6): захват за пределами окна пересчитывает раскладку блоков, завязанных на высоту окна, —
    на v5_page_1440 пропали фото hero, Форматов, 02, 03, 04, 07; WebKit к тому же не снимает картинку выше 32 767 px."""
    vh = page.evaluate("innerHeight")
    height = page.evaluate("document.documentElement.scrollHeight")
    page.evaluate("scrollTo({ top: 0, behavior: 'instant' })")
    parts = []
    for k, y in enumerate(range(0, height, vh)):
        page.evaluate("y => (document.body.style.transform = `translateY(${-y}px)`)", y)
        page.wait_for_timeout(150)
        tmp = path.with_suffix(f".part{k}.png")
        page.screenshot(path=str(tmp), timeout=120_000)
        parts.append((tmp, min(vh, height - y)))
    page.evaluate("document.body.style.transform = ''")
    ims = [Image.open(t) for t, _ in parts]
    out = Image.new("RGB", (ims[0].width, round(height * dpr)))
    y = 0
    for im, (_, h) in zip(ims, parts):
        out.paste(im.crop((0, 0, im.width, round(h * dpr))), (0, y))
        y += round(h * dpr)
        im.close()
    out.save(path)
    for t, _ in parts:
        t.unlink()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--page", default="site/index.html", help="страница относительно корня проекта")
    ap.add_argument("-w", "--widths", type=int, nargs="+", default=WIDTHS)
    ap.add_argument("-b", "--browsers", nargs="+", default=["chromium"], choices=["chromium", "webkit"])
    ap.add_argument("-s", "--selector", help="снять один элемент (блок) вместо всей страницы")
    ap.add_argument("-o", "--out", default=str(SVERKA / "_страница"), help="папка (относительно Доработка/вёрстка или абсолютная)")
    ap.add_argument("--name", default="site")
    ap.add_argument("--dpr", type=float, default=1, help="device scale factor")
    ap.add_argument("--viewport", action="store_true", help="только первый экран, без full page")
    ap.add_argument("--motion", action="store_true", help="не гасить анимации (по умолчанию — покой)")
    ap.add_argument("--wait", type=int, default=300, help="пауза после загрузки, мс")
    args = ap.parse_args()

    out = Path(args.out)
    if not out.is_absolute():
        out = SVERKA.parent / out
    out.mkdir(parents=True, exist_ok=True)
    problems = []

    with serve() as base, sync_playwright() as pw:
        url = url_for(base, args.page)
        for bname in args.browsers:
            browser = getattr(pw, bname).launch()
            for w in args.widths:
                ctx = browser.new_context(
                    viewport={"width": w, "height": viewport_height(w)},
                    device_scale_factor=args.dpr,
                    reduced_motion="no-preference" if args.motion else "reduce",
                )
                page = ctx.new_page()
                page.goto(url, wait_until="networkidle")
                if not args.motion:
                    page.add_style_tag(content=STILL_CSS)
                page.evaluate("document.fonts.ready")
                # Ленивые фото ниже первого экрана — загрузить и раскодировать до снимка всей страницы: без decode() фото
                # с decoding="async" (hero, Форматы, 02) в снимке всей страницы chromium выходят пустыми (Р-6)
                page.evaluate("""async () => {
                    document.querySelectorAll('img[loading=lazy]').forEach(i => i.loading = 'eager');
                    await Promise.all([...document.images].map(i => i.complete ? 0 : new Promise(r => { i.onload = i.onerror = r; })));
                    await Promise.all([...document.images].map(i => i.decode().catch(() => 0)));
                }""")
                page.wait_for_timeout(args.wait)

                over = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
                if over > 0:
                    problems.append(f"{bname} {w}: горизонтальный скролл на {over} px")

                suffix = "" if bname == "chromium" else f"_{bname}"
                path = out / f"{args.name}_{w}{suffix}.png"
                if args.selector:
                    el = page.locator(args.selector).first
                    el.scroll_into_view_if_needed()
                    el.screenshot(path=str(path), timeout=120_000)
                elif args.viewport:
                    page.screenshot(path=str(path), timeout=120_000)
                else:
                    full_page_shot(page, path, args.dpr)
                print(path.relative_to(PROJECT) if path.is_relative_to(PROJECT) else path)
                ctx.close()
            browser.close()

    for p in problems:
        print("!!", p)
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
