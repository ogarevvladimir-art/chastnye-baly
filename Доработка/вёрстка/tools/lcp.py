"""Замер LCP первого экрана (Chromium): без замедления и с замедлением (CPU ×4, сеть ≈ Fast 3G).

  python tools/lcp.py                 # 1440×900 и 390×844, по 3 прогона, медиана
  python tools/lcp.py -n 5 -w 1440

Печатает LCP (мс) и элемент. Кэш выключен (сервер отдаёт no-store, у каждого прогона новый контекст).
"""
import argparse
import statistics

from playwright.sync_api import sync_playwright

from _serve import serve, url_for

SLOW_NET = {"offline": False, "latency": 150, "downloadThroughput": 1.6 * 1024 * 1024 / 8, "uploadThroughput": 750 * 1024 / 8}

JS = """() => new Promise((done) => {
  let last = null;
  new PerformanceObserver((l) => { for (const e of l.getEntries()) last = e; }).observe({ type: 'largest-contentful-paint', buffered: true });
  setTimeout(() => done(last && { t: Math.round(last.startTime), el: last.element ? (last.element.className || last.element.tagName) + ' «' + (last.element.textContent || '').trim().slice(0, 20) + '»' : last.url }), 1500);
})"""


def run(b, base, w, h, slow):
    ctx = b.new_context(viewport={"width": w, "height": h})
    p = ctx.new_page()
    if slow:
        cdp = ctx.new_cdp_session(p)
        cdp.send("Network.enable")
        cdp.send("Network.emulateNetworkConditions", SLOW_NET)
        cdp.send("Emulation.setCPUThrottlingRate", {"rate": 4})
    p.goto(url_for(base, "site/index.html"), wait_until="load", timeout=120000)
    p.wait_for_timeout(1000)
    r = p.evaluate(JS)
    ctx.close()
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", type=int, default=3)
    ap.add_argument("-w", type=int, nargs="*", default=[1440, 390])
    args = ap.parse_args()
    with serve() as base, sync_playwright() as pw:
        b = pw.chromium.launch()
        for w in args.w:
            h = 900 if w >= 1024 else 844
            for slow in (False, True):
                rs = [run(b, base, w, h, slow) for _ in range(args.n)]
                ts = [r["t"] for r in rs if r]
                print(f"{w}×{h} {'замедление' if slow else 'без замедления'}: LCP {statistics.median(ts)} мс "
                      f"(прогоны {ts}) — {rs[-1]['el'] if rs[-1] else '—'}")
        b.close()


if __name__ == "__main__":
    main()
