"""Локальный сервер от корня проекта — смотреть сайт и служебные страницы в браузере или с телефона.

  python tools/serve.py            # http://127.0.0.1:8080/site/  и  …/Доработка/вёрстка/tools/roles.html
  python tools/serve.py --lan      # доступ с телефона по локальной сети: http://<IP компьютера>:8080/site/
"""
import argparse
import functools
import http.server
import socket
from urllib.parse import quote

from _serve import PROJECT, _Quiet


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--lan", action="store_true")
    args = ap.parse_args()
    host = "0.0.0.0" if args.lan else "127.0.0.1"
    handler = functools.partial(_Quiet, directory=str(PROJECT))
    shown = socket.gethostbyname(socket.gethostname()) if args.lan else "127.0.0.1"
    print(f"Сайт:  http://{shown}:{args.port}/site/")
    print(f"Роли:  http://{shown}:{args.port}/{quote('Доработка/вёрстка/tools/roles.html')}")
    http.server.ThreadingHTTPServer((host, args.port), handler).serve_forever()


if __name__ == "__main__":
    main()
