// Шапка «Над светлым». Светлые зоны — элементы с data-header="light" (панель 08, дальше панель формы). Каждая часть шапки
// (логотип и «Меню») получает data-over="light", если на линии центра шапки под её серединой
// светлая зона: на планшете и десктопе панель 08 закрывает не всю ширину, и логотип над Ink должен остаться светлым.
// Смена цвета — 0,2 с в CSS. На шапке data-variant="light", когда над светлым стоит «Меню» (правый край).
// Пока ни одна зона не пересекает линию шапки (IntersectionObserver), на прокрутке ничего не считается.

export function initHeader() {
  const header = document.querySelector(".site-header");
  const lights = [...document.querySelectorAll('[data-header="light"]')];
  if (!header || !lights.length) return;

  const parts = [...header.querySelectorAll(".site-header__logo, .site-header__menu")];
  const menu = header.querySelector(".site-header__menu");
  const under = new Set();
  let io;
  let raf = 0;

  const paint = () => {
    raf = 0;
    const y = header.offsetHeight / 2;
    const zones = [...under].map((el) => el.getBoundingClientRect()).filter((r) => r.top <= y && r.bottom >= y);
    for (const p of parts) {
      const r = p.getBoundingClientRect();
      const x = r.left + r.width / 2;
      const over = r.width > 0 && zones.some((z) => x >= z.left && x <= z.right);
      if (over !== (p.dataset.over === "light")) over ? (p.dataset.over = "light") : delete p.dataset.over;
    }
    header.dataset.variant = menu?.dataset.over === "light" ? "light" : "dark";
  };
  const schedule = () => raf || (raf = requestAnimationFrame(paint));

  const setup = () => {
    io?.disconnect();
    under.clear();
    const c = Math.round(header.offsetHeight / 2);
    io = new IntersectionObserver((entries) => {
      for (const e of entries) e.isIntersecting ? under.add(e.target) : under.delete(e.target);
      schedule();
    }, { rootMargin: `-${c}px 0px -${Math.max(0, innerHeight - c - 1)}px 0px` });
    lights.forEach((s) => io.observe(s));
  };

  setup();
  addEventListener("scroll", () => under.size && schedule(), { passive: true });
  let t;
  addEventListener("resize", () => {
    clearTimeout(t);
    t = setTimeout(setup, 150);
  });
}
