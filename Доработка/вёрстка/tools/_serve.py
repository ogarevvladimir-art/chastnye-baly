"""Общее для инструментов: пути проекта и локальный http-сервер от корня «Частные балы сайт/».

Сервер нужен, чтобы шрифты и модули грузились как на хостинге (file:// режет шрифты и ES-модули).
"""
import contextlib
import functools
import http.server
import threading
from pathlib import Path
from urllib.parse import quote

TOOLS = Path(__file__).resolve().parent
VERSTKA = TOOLS.parent                      # Доработка/вёрстка
PROJECT = TOOLS.parents[2]                  # Частные балы сайт
SITE = PROJECT / "site"
SVERKA = VERSTKA / "сверка"

WIDTHS = [360, 390, 600, 834, 1023, 1024, 1280, 1440, 1920]   # ОБЩЕЕ, «Брейкпойнты и масштаб»


def viewport_height(width):
    """Высота окна по устройству макета: iPhone 14 844, iPad Pro 11″ 1194, десктоп 900."""
    if width < 600:
        return 844
    if width < 1024:
        return 1194
    return 900


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


@contextlib.contextmanager
def serve(root=PROJECT):
    handler = functools.partial(_Quiet, directory=str(root))
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{httpd.server_address[1]}"
    finally:
        httpd.shutdown()


def url_for(base, path):
    """path — файл внутри проекта (Path или строка относительно корня проекта)."""
    p = Path(path)
    if p.is_absolute():
        p = p.resolve().relative_to(PROJECT)
    return base + "/" + quote(p.as_posix())
