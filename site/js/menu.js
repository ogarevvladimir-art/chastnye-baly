// Меню: шторка на весь экран (CSS — layout.css, состояния data-state). «Меню» ↔ «Закрыть» перебором букв за 0,2 с.
// Фокус удерживается в шапке и меню, Esc закрывает и возвращает фокус на кнопку, скролл страницы заблокирован без прыжка
// (scrollbar-gutter: stable на время блокировки). Пункт закрывает шторку и сразу ведёт к якорю, «Связаться» — открывает лист формы.
// Пока меню открыто, страница под ним (main, подвал, «К содержанию») — inert: вне меню остаётся только шапка с «Закрыть».
// Пункт, по которому кликнули, помечается data-picked: на десктопе его гигант уезжает со шторкой, остальные скрыты (layout.css).

import { reducedMotion } from "./motion.js";

const LETTERS = "АБВГДЕЖЗИКЛМНОПРСТУФХЦЧШЩЭЮЯ";
const CLOSE_MS = 750;

export function initMenu() {
  const html = document.documentElement;
  const btn = document.querySelector(".site-header__menu");
  const label = btn?.querySelector(".site-header__menu-text");
  const menu = document.getElementById("menu");
  if (!btn || !label || !menu) return;

  const links = [...menu.querySelectorAll("a")];
  const page = [...document.querySelectorAll("main, body > footer, .skip")];
  const setPage = (off) => page.forEach((el) => (el.inert = off));
  let raf = 0;
  let closeTimer = 0;

  // Перебор слева направо: буква i встаёт на место, когда пройдено (i + 1) / длины времени, до этого — случайная заглавная
  function scramble(to) {
    cancelAnimationFrame(raf);
    if (reducedMotion.matches) {
      label.textContent = to;
      return;
    }
    const start = performance.now();
    const step = (t) => {
      const p = Math.min(1, (t - start) / 200);
      let out = "";
      for (let i = 0; i < to.length; i++) {
        out += p >= (i + 1) / to.length ? to[i] : LETTERS[(Math.random() * LETTERS.length) | 0];
      }
      label.textContent = out;
      if (p < 1) raf = requestAnimationFrame(step);
    };
    raf = requestAnimationFrame(step);
  }

  const isOpen = () => menu.dataset.state === "open";

  function open() {
    clearTimeout(closeTimer);
    menu.inert = false;
    menu.querySelector("[data-picked]")?.removeAttribute("data-picked");
    setPage(true);
    html.dataset.menu = "";
    html.classList.add("is-locked");
    menu.dataset.state = "open";
    btn.setAttribute("aria-expanded", "true");
    btn.setAttribute("aria-label", "Закрыть");
    scramble("Закрыть");
    const first = menu.querySelector(".menu__item");
    requestAnimationFrame(() => first?.focus({ preventScroll: true }));
  }

  function close({ returnFocus = true } = {}) {
    if (!isOpen()) return;
    menu.dataset.state = "closing";
    setPage(false);
    html.classList.remove("is-locked");
    btn.setAttribute("aria-expanded", "false");
    btn.setAttribute("aria-label", "Меню");
    scramble("Меню");
    if (returnFocus) btn.focus({ preventScroll: true });
    closeTimer = setTimeout(() => {
      menu.dataset.state = "closed";
      menu.inert = true;
      delete html.dataset.menu;
    }, reducedMotion.matches ? 150 : CLOSE_MS);
  }

  btn.addEventListener("click", () => (isOpen() ? close() : open()));

  // Пункт: закрыть и сразу к якорю (scroll-padding-top — высота шапки)
  menu.addEventListener("click", (e) => {
    const a = e.target.closest('a[href^="#"]');
    if (!a) return;
    a.dataset.picked = "";
    // «Связаться» открывает лист формы (form.js): здесь только закрыть шторку
    if (a.hasAttribute("data-form")) {
      close({ returnFocus: false });
      return;
    }
    const target = document.querySelector(a.getAttribute("href"));
    if (!target) return;
    e.preventDefault();
    close({ returnFocus: false });
    history.pushState(null, "", a.getAttribute("href"));
    target.scrollIntoView({ behavior: reducedMotion.matches ? "auto" : "smooth", block: "start" });
    if (!target.hasAttribute("tabindex")) target.setAttribute("tabindex", "-1");
    target.focus({ preventScroll: true });
  });

  document.addEventListener("keydown", (e) => {
    if (!isOpen()) return;
    if (e.key === "Escape") {
      e.preventDefault();
      close();
      return;
    }
    if (e.key !== "Tab") return;
    // Кольцо ведём сами: Safari по умолчанию не ставит фокус Tab-ом на ссылки и увёл бы фокус под шторку
    e.preventDefault();
    const ring = [btn, ...links];
    const i = ring.indexOf(document.activeElement);
    const next = i === -1 ? 0 : (i + (e.shiftKey ? -1 : 1) + ring.length) % ring.length;
    ring[next].focus();
  });
}
