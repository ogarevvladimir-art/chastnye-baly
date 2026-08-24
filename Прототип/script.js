/* =========================================================
   ЧАСТНЫЕ БАЛЫ — поведение прототипа

   Слои движения:
   · reveal-on-scroll (opacity + translate, stagger через --d) — база;
   · посимвольное появление заголовков (data-gradual);
   · инерционный скролл (Lenis), связанный с тикером GSAP;
   · раскрытие медиа маской снизу вверх + контр-движение картинки;
   · sticky-стопка полос в секции «Люди»;
   · прочерчивающиеся hairline и счётчики в фактах.

   Всё, что движется, отключается при prefers-reduced-motion: reduce.
   ========================================================= */

(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var hasGsapLib   = typeof window.gsap !== 'undefined';
  var canAnimate   = hasGsapLib && !reduceMotion;

  /* Признак живого JS ставит инлайн-скрипт в <head> — до первой отрисовки.
     Здесь только страхуемся, если разметку подключили без него. */
  document.documentElement.classList.add('js');

  /* Один плагин на всё, что ведётся скроллом. Регистрируем до первых
     ScrollTrigger.create() ниже — иначе GSAP ругается в консоль. */
  if (hasGsapLib && window.ScrollTrigger) gsap.registerPlugin(window.ScrollTrigger);
  var hasST = hasGsapLib && !!window.ScrollTrigger;

  /* ---------- 0a. Инерционный скролл (Lenis) ---------- */
  /* Скролл ведёт Lenis, кадры — тикер GSAP: два независимых rAF-цикла
     давали бы рассинхрон между позицией страницы и ScrollTrigger'ами.
     При prefers-reduced-motion Lenis не создаём вовсе — остаётся нативный
     скролл, а класс .no-lenis возвращает scroll-behavior: smooth якорям. */
  var lenis = null;

  if (!reduceMotion && typeof window.Lenis !== 'undefined') {
    lenis = new Lenis({
      duration: 1.15,
      easing: function (t) { return Math.min(1, 1.001 - Math.pow(2, -10 * t)); }
    });

    if (hasGsapLib) {
      gsap.ticker.add(function (time) { lenis.raf(time * 1000); });
      // Тикер не должен «догонять» пропущенные кадры: после лага
      // Lenis получил бы скачок дельты и страница дёрнулась бы
      gsap.ticker.lagSmoothing(0);
      if (hasST) lenis.on('scroll', ScrollTrigger.update);
    } else {
      // Без GSAP крутим Lenis собственным циклом
      var raf = function (time) { lenis.raf(time); requestAnimationFrame(raf); };
      requestAnimationFrame(raf);
    }
  } else {
    document.documentElement.classList.add('no-lenis');
  }

  /* Якорные ссылки: нативный переход обошёл бы Lenis и дёрнул бы страницу.
     Делегируем на документ — ссылки есть и в меню, и в футере, и в контенте. */
  document.addEventListener('click', function (e) {
    var link = e.target.closest ? e.target.closest('a[href^="#"]') : null;
    if (!link) return;

    var hash = link.getAttribute('href');
    if (!hash || hash === '#') return;

    var target = document.getElementById(hash.slice(1));
    if (!target) return;

    // Модификаторы — пользователь открывает в новой вкладке, не мешаем
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button !== 0) return;

    if (lenis) {
      e.preventDefault();
      // Хедер фиксированный: подводим цель под него, а не под самый верх
      lenis.scrollTo(target, { offset: -80, duration: 1.25 });
      // Адрес обновляем сами: preventDefault снял штатное поведение
      if (window.history && history.pushState) history.pushState(null, '', hash);
    }
  });

  /* ---------- 0. Библиотека схем ---------- */
  /* Разворачиваем <symbol> по месту клонированием, а не через <use>:
     содержимое <use> живёт в теневом дереве, и ни наведение в меню
     (.shape-element), ни getTotalLength() до него не дотянутся. */
  document.querySelectorAll('[data-scheme]').forEach(function (host) {
    var symbol = document.getElementById('scheme-' + host.getAttribute('data-scheme'));
    if (!symbol || host.firstElementChild) return;
    Array.prototype.slice.call(symbol.children).forEach(function (node) {
      host.appendChild(node.cloneNode(true));
    });
  });

  /* Длина линии для прочерчивания. getTotalLength() есть у path и line,
     у circle его нет — считаем по радиусу. На скрытых элементах вызов
     безопасен (геометрия не зависит от отрисовки), но метод может
     отсутствовать в старых движках — оборачиваем в try. */
  function lineLength(el) {
    try {
      if (typeof el.getTotalLength === 'function') {
        var len = el.getTotalLength();
        if (len > 0) return len;
      }
    } catch (e) { /* геометрия недоступна — отдаём запасное значение ниже */ }

    if (el.tagName.toLowerCase() === 'circle') {
      return 2 * Math.PI * (parseFloat(el.getAttribute('r')) || 0);
    }
    return 0;
  }

  /* Схемы в контенте: раздаём --len и порядковый --i для каскада.
     Схема служебной полосы (.scheme--track) исключена — её ведёт скролл:
     --len она получает своим кодом, а --i задавал бы засечкам каскадную
     transition-delay, из-за которой они зажигались бы не в такт шагам.
     Тот же :not() стоит и в списке целей observer'а (см. «3b. Reveal»). */
  document.querySelectorAll('.scheme:not(.scheme--track)').forEach(function (scheme) {
    var i = 0;
    scheme.querySelectorAll('[data-draw], [data-dot], [data-tick]').forEach(function (el) {
      if (el.hasAttribute('data-draw')) {
        var len = lineLength(el);
        // 0 — вырожденный случай (нулевая геометрия): пунктир не задаём,
        // иначе линия останется невидимой навсегда
        if (len > 0) el.style.setProperty('--len', len.toFixed(1) + 'px');
      }
      el.style.setProperty('--i', i++);
    });
  });

  /* ---------- 1. Хедер: transparent → solid ---------- */
  var header = document.getElementById('header');

  function onScrollHeader() {
    if (window.scrollY > window.innerHeight * 0.7) {
      header.classList.add('is-solid');
    } else {
      header.classList.remove('is-solid');
    }
  }

  /* ---------- 2. Полноэкранное меню (GSAP) ---------- */
  var menuButton = document.getElementById('menuButton');
  var navOverlay = document.getElementById('navOverlay');

  if (menuButton && navOverlay) {
    var hasGsap = typeof window.gsap !== 'undefined';

    var scrim        = navOverlay.querySelector('.nav-overlay__scrim');
    var panel        = navOverlay.querySelector('.menu-panel');
    var backdrops    = navOverlay.querySelectorAll('.backdrop-layer');
    var navLinks     = navOverlay.querySelectorAll('.nav-link');
    var fadeTargets  = navOverlay.querySelectorAll('[data-menu-fade]');
    var btnTexts     = menuButton.querySelectorAll('.menu-button__text > span');
    var btnIcon      = menuButton.querySelector('.menu-button__icon');
    var shapeItems   = navOverlay.querySelectorAll('.menu-list-item[data-shape]');
    var isMenuOpen   = false;
    var EASE = 'power2.out';
    var DUR  = reduceMotion ? 0.01 : 0.7;

    if (hasGsap) {
      // Кастомный ease референса; при недоступности плагина — штатный power2
      try {
        if (window.CustomEase) {
          gsap.registerPlugin(window.CustomEase);
          if (!gsap.parseEase('menuMain')) {
            CustomEase.create('menuMain', '0.65, 0.01, 0.05, 0.99');
          }
        }
      } catch (e) { /* тихо откатываемся ниже */ }

      if (gsap.parseEase('menuMain')) EASE = 'menuMain';

      /* Наведение на пункт — проявление соответствующей фоновой графики */
      shapeItems.forEach(function (item) {
        var shape = navOverlay.querySelector('.bg-shape-' + item.getAttribute('data-shape'));
        if (!shape) return;
        var els = shape.querySelectorAll('.shape-element');

        item.addEventListener('mouseenter', function () {
          navOverlay.querySelectorAll('.bg-shape').forEach(function (s) {
            s.classList.remove('active');
          });
          shape.classList.add('active');
          gsap.fromTo(els,
            { scale: 0.5, opacity: 0, rotation: -10 },
            { scale: 1, opacity: 1, rotation: 0, duration: 0.6,
              stagger: 0.08, ease: 'back.out(1.7)', overwrite: 'auto' });
        });

        item.addEventListener('mouseleave', function () {
          gsap.to(els, {
            scale: 0.8, opacity: 0, duration: 0.3, ease: 'power2.in',
            overwrite: 'auto',
            onComplete: function () { shape.classList.remove('active'); }
          });
        });
      });
    }

    function openMenu() {
      isMenuOpen = true;
      navOverlay.setAttribute('data-nav', 'open');
      menuButton.setAttribute('aria-expanded', 'true');
      document.body.style.overflow = 'hidden';
      // Lenis двигает страницу сам и overflow: hidden его не останавливает
      if (lenis) lenis.stop();

      if (!hasGsap) return;

      gsap.timeline({ defaults: { ease: EASE, duration: DUR } })
        .set(navOverlay, { display: 'block' })
        .set(panel, { xPercent: 0 }, '<')
        .fromTo(btnTexts, { yPercent: 0 }, { yPercent: -100, stagger: 0.2 })
        .fromTo(btnIcon, { rotate: 0 }, { rotate: 315 }, '<')
        .fromTo(scrim, { autoAlpha: 0 }, { autoAlpha: 1 }, '<')
        .fromTo(backdrops, { xPercent: 101 }, { xPercent: 0, stagger: 0.12, duration: DUR * 0.82 }, '<')
        // Амплитуду сняли под крупный кегель: на 128px прежние 140%/6°
        // выносили слово далеко за маску и разворачивали его слишком заметно
        .fromTo(navLinks, { yPercent: 105, rotate: 3 }, { yPercent: 0, rotate: 0, stagger: 0.05 }, '<+=0.35')
        .fromTo(fadeTargets, { autoAlpha: 0, yPercent: 50 },
                { autoAlpha: 1, yPercent: 0, stagger: 0.04, clearProps: 'all' }, '<+=0.2');
    }

    function closeMenu() {
      if (!isMenuOpen) return;
      isMenuOpen = false;
      navOverlay.setAttribute('data-nav', 'closed');
      menuButton.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
      if (lenis) lenis.start();

      if (!hasGsap) return;

      gsap.timeline({ defaults: { ease: EASE, duration: DUR } })
        .to(scrim, { autoAlpha: 0 })
        .to(panel, { xPercent: 120 }, '<')
        .to(btnTexts, { yPercent: 0 }, '<')
        .to(btnIcon, { rotate: 0 }, '<')
        .set(navOverlay, { display: 'none' });
    }

    menuButton.addEventListener('click', function () {
      isMenuOpen ? closeMenu() : openMenu();
    });

    navOverlay.addEventListener('click', function (e) {
      if (e.target.closest('[data-menu-close]')) closeMenu();
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && isMenuOpen) closeMenu();
    });
  }

  /* ---------- 3. Посимвольное появление заголовков ---------- */
  /* Разбиваем на символы до создания observer'а: он должен увидеть готовые узлы.
     Текст целиком остаётся в aria-label, чтобы скринридер не читал по буквам. */
  document.querySelectorAll('[data-gradual]').forEach(function (title) {
    // <br> текста не даёт — подставляем пробел, иначе слова склеятся в aria-label.
    // Но после дефиса («Вальс-<br>открытие») перенос внутри слова — пробел не нужен.
    var plain = title.innerHTML
      .replace(/-\s*<br\s*\/?>/gi, '-')
      .replace(/<br\s*\/?>/gi, ' ')
      .replace(/<[^>]+>/g, '')
      .replace(/\s+/g, ' ')
      .trim();
    if (!plain) return;

    title.setAttribute('aria-label', plain);
    // Длинные и многострочные набираются быстрее, иначе хвост заметно отстаёт
    if (plain.length > 18 || title.querySelector('br')) title.classList.add('is-long');

    var index = 0;

    // Рекурсивный обход: текст в hero и proc__title лежит внутри .line > span,
    // поэтому одним уровнем childNodes не обойтись
    function split(parent) {
      Array.prototype.slice.call(parent.childNodes).forEach(function (node) {
        // Элемент — спускаемся внутрь, саму обёртку прячем от скринридера
        if (node.nodeType === 1) {
          node.setAttribute('aria-hidden', 'true');
          split(node);
          return;
        }
        if (node.nodeType !== 3) return;

        // Отступы разметки между блочными строками (.line) — не текст заголовка.
        // Без этой проверки переносы строк в HTML становятся пустыми .char
        // и раздувают заголовок по высоте.
        if (!node.nodeValue.trim()) return;

        var frag = document.createDocumentFragment();

        // Режем на слова и пробелы: буквы кладём внутрь .word, пробелы — снаружи,
        // чтобы строка могла переноситься только по пробелам
        node.nodeValue.split(/(\s+)/).forEach(function (part) {
          if (!part) return;

          if (!part.trim()) {
            // Пробел оставляем обычным текстом: inline-block не схлопывается
            // на переносе строки и утаскивает лишние 8px в начало новой строки
            // («Корпоративный / ␣бал»). Такта он тоже не тратит.
            frag.appendChild(document.createTextNode(part));
            return;
          }

          var word = document.createElement('span');
          word.className = 'word';
          word.setAttribute('aria-hidden', 'true');

          part.split('').forEach(function (ch) {
            var span = document.createElement('span');
            span.className = 'char';
            span.textContent = ch;
            span.style.setProperty('--i', index++);
            word.appendChild(span);
          });

          frag.appendChild(word);
        });

        node.parentNode.replaceChild(frag, node);
      });
    }

    split(title);
  });

  /* ---------- 3a-bis. Мега-заголовки во всю ширину ---------- */
  /* Главный приём референса: слово ровно по ширине вьюпорта, буквы упираются
     в края. Ни положение блока, ни кегль в CSS не выразить — оба зависят от
     фактической раскладки и от того, сколько места занимает конкретное слово
     конкретной гарнитурой. Оба шага ниже. */
  var megaTitles = Array.prototype.slice.call(document.querySelectorAll('.t-mega'));

  if (megaTitles.length) {
    var MEGA_BASE = 100;

    /* Шаг 1 — вывести блок к краям экрана.
       Ширина берётся у documentElement, а не у window.innerWidth: последний
       включает полосу прокрутки, и слово вылезло бы под неё.

       Отправная точка — левый край .grid, а не самого заголовка: заголовок
       занимает все треки (grid-column: 1 / -1), то есть в потоке начинается
       ровно от края сетки, зато сам растягивает трек своим max-content —
       его собственный left зависел бы от уже выставленного кегля, и замер
       гонялся бы за своим хвостом. У .grid положение стабильно, и в нём
       уже учтены и --gutter секции, и центрирование по max-width. */
    function placeMega(el) {
      var vw = document.documentElement.clientWidth;
      var grid = el.parentElement;
      if (!grid) return vw;

      var gridLeft = grid.getBoundingClientRect().left;
      el.style.setProperty('--mega-left', (-gridLeft).toFixed(2) + 'px');
      el.style.setProperty('--mega-width', vw + 'px');

      return vw;
    }

    /* Шаг 2 — подобрать кегль. Ставим базовые 100px, читаем фактическую
       ширину набранной строки и умножаем базу на отношение доступной
       ширины к измеренной. Замер идёт по внутреннему <span> с width:
       max-content — у самого .t-mega ширина уже равна ширине экрана
       и о содержимом ничего не сообщает. */
    function fitMega(el) {
      var line = el.firstElementChild;
      if (!line) return;

      var avail = placeMega(el);
      if (!avail) return;

      /* Строка, которой на узком экране разрешено переноситься
         (.t-mega--inline ниже 760px), под приём не подпадает: её ширина
         всегда равна ширине блока, отношение выродилось бы в единицу
         и кегль остался бы базовым. Кегль ей задаёт CSS. */
      if (getComputedStyle(el).whiteSpace !== 'nowrap') {
        el.style.removeProperty('font-size');
        return;
      }

      /* Замер идёт в один синхронный проход, а при prefers-reduced-motion
         глобальное правило доступности вешает на всё transition-duration
         в .01ms. Даже такой transition делает font-size анимируемым:
         сразу после записи getComputedStyle и раскладка отдают ещё старое
         значение, и коэффициент считался бы от чужого кегля.
         Гасим переходы на время замера и возвращаем после. */
      var prevTransition = el.style.transition;
      el.style.transition = 'none';

      el.style.fontSize = MEGA_BASE + 'px';
      var measured = line.getBoundingClientRect().width;

      if (measured) {
        el.style.fontSize = (MEGA_BASE * (avail / measured)).toFixed(2) + 'px';
      } else {
        el.style.removeProperty('font-size');
      }

      // Возврат в следующем кадре: сними мы transition в том же, браузер
      // склеил бы оба изменения и кегль всё-таки поехал бы переходом
      window.requestAnimationFrame(function () {
        if (prevTransition) el.style.transition = prevTransition;
        else el.style.removeProperty('transition');
      });
    }

    function fitAllMega() { megaTitles.forEach(fitMega); }

    fitAllMega();

    /* До готовности шрифтов метрики считаются по системному фолбэку —
       у Manrope другая ширина знака, и слово встало бы не по краям.
       Пересчитываем, когда гарнитура действительно применена. */
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(fitAllMega).catch(function () { /* фолбэк уже стоит */ });
    }

    /* Кадр с медиа внутри строки участвует в замере наравне с буквами,
       но до загрузки его ширина неизвестна. aspect-ratio в CSS задаёт её
       заранее, так что первый замер уже верен; слушатель — страховка
       на случай, если движок посчитает иначе. */
    megaTitles.forEach(function (el) {
      var media = el.querySelector('.inline-media');
      if (!media) return;
      var recheck = function () { fitMega(el); };
      if (media.tagName === 'VIDEO') {
        media.addEventListener('loadedmetadata', recheck, { once: true });
      } else if (!media.complete) {
        media.addEventListener('load', recheck, { once: true });
      }
    });

    // Ресайз через rAF: без троттлинга пересчёт шёл бы на каждое событие
    // окна, а он читает геометрию и заставляет браузер считать раскладку
    var megaTicking = false;
    window.addEventListener('resize', function () {
      if (megaTicking) return;
      megaTicking = true;
      window.requestAnimationFrame(function () {
        megaTicking = false;
        fitAllMega();
      });
    }, { passive: true });
  }

  /* ---------- 3b-2. Заголовки форматов ---------- */
  /* Тот же приём, что у мега-строк, но мерка другая: не ширина экрана,
     а ширина слайда за вычетом полей. Свой подбор нужен потому, что фразы
     сильно разной длины — «Для семьи и близких» 19 знаков против «Для
     компании, партнёров и сотрудников» 37. Общий clamp либо ломает длинную
     на строки (а двухстрочные заголовки здесь смотрятся плохо), либо мельчит
     короткую. Подбор уравнивает их по занимаемой ширине, а не по кеглю:
     обе строки тянутся во всю доступную ширину, как в референсе.

     Результат пишем в --format-size, а не в font-size напрямую: у CSS
     остаётся фолбэк в var() на случай, если скрипт не отработал. */
  var formatTitles = Array.prototype.slice.call(document.querySelectorAll('.t-format'));

  if (formatTitles.length) {
    var FORMAT_BASE = 100;
    /* Потолок кегля. Заголовок теперь в две строки и лежит поверх кадра:
       без ограничения короткое «Частный бал» раздувалось до 200px и
       накрывало фотографию целиком. Считаем от высоты экрана, а не от
       ширины: ограничение здесь именно вертикальное — две строки должны
       занять примерно нижнюю треть кадра, а не весь кадр. */
    function formatMax() {
      return Math.max(48, window.innerHeight * 0.17);
    }

    function fitFormat(el) {
      var line = el.firstElementChild;
      if (!line) return;

      var slide = el.closest('.segment');
      if (!slide) return;

      /* Доступная ширина — внутренняя ширина слайда: его собственные
         padding-inline и есть поля вьюпорта. Читаем у слайда, а не
         у заголовка: заголовок сам растягивается содержимым (max-content),
         и его ширина зависела бы от уже выставленного кегля. */
      var cs = getComputedStyle(slide);
      var avail = slide.getBoundingClientRect().width
        - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
      if (!(avail > 0)) return;

      // Гасим переходы на время замера — иначе font-size анимируется
      // и getComputedStyle сразу после записи вернёт ещё старое значение
      var prevTransition = el.style.transition;
      el.style.transition = 'none';

      el.style.setProperty('--format-size', FORMAT_BASE + 'px');
      var measured = line.getBoundingClientRect().width;

      if (measured) {
        var size = Math.min(FORMAT_BASE * (avail / measured), formatMax());
        el.style.setProperty('--format-size', size.toFixed(2) + 'px');
      } else {
        el.style.removeProperty('--format-size');
      }

      window.requestAnimationFrame(function () {
        if (prevTransition) el.style.transition = prevTransition;
        else el.style.removeProperty('transition');
      });
    }

    function fitAllFormats() { formatTitles.forEach(fitFormat); }

    fitAllFormats();

    // До готовности шрифтов метрики считаются по фолбэку — пересчитываем
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(fitAllFormats).catch(function () { /* фолбэк уже стоит */ });
    }

    var formatTicking = false;
    window.addEventListener('resize', function () {
      if (formatTicking) return;
      formatTicking = true;
      window.requestAnimationFrame(function () {
        formatTicking = false;
        fitAllFormats();
      });
    }, { passive: true });
  }

  /* ---------- 3b-3. Лента форматов: боковой ход от скролла страницы ---------- */
  /* Пользователь крутит страницу вниз — лента едет вбок. Пока секция
     проходит мимо экрана, .segments-stage залипает (sticky в CSS), а мы
     считаем прогресс этого прохода и пишем его в --seg-progress: 0 — виден
     первый формат, 1 — второй.

     Считаем сами, а не через ScrollTrigger.pin: страницу двигает Lenis
     трансформом собственной обёртки, и pin без scrollerProxy разъезжается
     с фактическим положением. getBoundingClientRect читает реальную
     геометрию после трансформа — этот путь верен при любом скроллере. */
  var segScroll = document.getElementById('segments-scroll');

  if (segScroll) {
    var segDots = Array.prototype.slice.call(
      document.querySelectorAll('.segments__dots i')
    );
    var segTicking = false;

    function updateSegments() {
      var rect = segScroll.getBoundingClientRect();

      /* Путь прокрутки = высота контейнера минус экран (лишний экран и есть
         дорога ленты). Прогресс — сколько этого пути уже пройдено. */
      var travel = rect.height - window.innerHeight;
      if (travel <= 0) return;

      var p = -rect.top / travel;
      p = Math.max(0, Math.min(1, p));

      segScroll.style.setProperty('--seg-progress', p.toFixed(4));

      // Засечка переключается на середине пути
      if (segDots.length) {
        var idx = p < .5 ? 0 : 1;
        segDots.forEach(function (dot, i) {
          dot.classList.toggle('is-on', i === idx);
        });
      }
    }

    function requestSegments() {
      if (segTicking) return;
      segTicking = true;
      window.requestAnimationFrame(function () {
        segTicking = false;
        updateSegments();
      });
    }

    window.addEventListener('scroll', requestSegments, { passive: true });
    window.addEventListener('resize', requestSegments, { passive: true });
    // Lenis двигает страницу трансформом — нативный scroll при этом
    // не всегда стреляет, поэтому подписываемся и на его событие
    if (lenis) lenis.on('scroll', requestSegments);

    updateSegments();
  }

  /* ---------- 3b. Reveal on scroll ---------- */
  /* Схемы в карточках делят observer с остальными появлениями: класс .is-in
     у них запускает прочерчивание. Схема служебной полосы исключена —
     её ведёт прогресс скролла в updateProcess(). */
  /* [data-line] тоже здесь: прочерчивание линии запускает тот же класс .is-in.
     Почти все такие элементы и так помечены [data-reveal], но связывать
     приём с чужим атрибутом не стоит — перечисляем явно. */
  /* .t-mega тоже здесь: маска снизу вверх (вместо посимвольного появления,
     которое на таком кегле выглядит рвано) запускается тем же классом .is-in.
     Второй observer заводить не за чем.
     .t-format — та же маска и по той же причине; отдельной целью, а не
     через .is-in родителя: заголовок формата стоит в низу своей статьи,
     и по классу .segment он бы отыграл задолго до появления на экране. */
  var revealTargets = document.querySelectorAll(
    '[data-reveal], [data-gradual], [data-line], .scheme:not(.scheme--track), .t-mega, .t-format'
  );

  if (reduceMotion || !('IntersectionObserver' in window)) {
    revealTargets.forEach(function (el) { el.classList.add('is-in'); });
  } else {
    var revealObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-in');
          revealObserver.unobserve(entry.target);
        }
      });
    }, {
      rootMargin: '0px 0px -12% 0px',
      threshold: 0.12
    });

    revealTargets.forEach(function (el) {
      // Первый экран показываем сразу: нижний rootMargin отрезает подписи hero,
      // и они ждали бы скролла, хотя видны с самого начала
      if (el.closest('.hero')) {
        el.classList.add('is-in');
        return;
      }
      revealObserver.observe(el);
    });
  }

  /* ---------- 3c. Этикет / дресс-код: переключение групп ---------- */
  /* Обе группы лежат в разметке; JS показывает одну. Без JS класс .js не
     появляется, табы скрыты, и обе группы читаются подряд как раньше. */
  var rulesTabs = document.getElementById('rulesTabs');

  if (rulesTabs) {
    var tabButtons = Array.prototype.slice.call(rulesTabs.querySelectorAll('.tab'));
    var section = rulesTabs.closest('.section');
    var panes = Array.prototype.slice.call(section.querySelectorAll('[data-tab]'));

    function activateTab(name) {
      panes.forEach(function (pane) {
        var on = pane.getAttribute('data-tab') === name;
        pane.classList.toggle('is-active', on);

        // Показанный блок observer уже не увидит (он был display:none и,
        // возможно, unobserve'нут) — проявляем его содержимое вручную.
        if (!on) return;
        if (pane.hasAttribute('data-reveal') || pane.hasAttribute('data-gradual')) {
          pane.classList.add('is-in');
        }
        pane.querySelectorAll('[data-reveal], [data-gradual]').forEach(function (el) {
          el.classList.add('is-in');
        });
      });

      tabButtons.forEach(function (btn) {
        btn.setAttribute('aria-selected',
          btn.getAttribute('aria-controls') === 'rules-' + name ? 'true' : 'false');
      });
    }

    tabButtons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        activateTab(btn.getAttribute('aria-controls').replace('rules-', ''));
      });
    });

    // Стрелки между табами — штатное поведение tablist
    rulesTabs.addEventListener('keydown', function (e) {
      if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
      var i = tabButtons.indexOf(document.activeElement);
      if (i < 0) return;
      e.preventDefault();
      var next = tabButtons[(i + (e.key === 'ArrowRight' ? 1 : -1) + tabButtons.length) % tabButtons.length];
      next.focus();
      next.click();
    });

    // Ссылка «Дресс-код» из футера ведёт в ту же секцию и открывает нужный таб
    document.addEventListener('click', function (e) {
      var link = e.target.closest ? e.target.closest('[data-tab-link]') : null;
      if (link) activateTab(link.getAttribute('data-tab-link'));
    });

    // Прямой заход по #dresscode из старых ссылок и закладок
    if (window.location.hash === '#dresscode') {
      activateTab('dresscode');
      // Мгновенно и без анимации: это заход по ссылке, а не переход по странице
      if (lenis) {
        lenis.scrollTo(section, { immediate: true, offset: -80 });
      } else {
        section.scrollIntoView();
      }
    }
  }

  /* ---------- 3d. Раскрытие медиа маской ---------- */
  /* Кадр открывается снизу вверх (clip-path), картинка внутри одновременно
     идёт навстречу маске: из scale 1.3 / yPercent 8 в исходное положение.
     Ощущение — не «блок проявился», а «кадр открылся».

     Раскрытые кадры помечаются классом .is-revealed: параллакс ниже трогает
     только их, иначе два источника писали бы transform картинки одновременно
     и она бы дёргалась в середине раскрытия. */
  var maskedMedia = [];

  if (canAnimate && hasST) {
    /* Кадрирующая коробка — та, у которой overflow: hidden и своё
       соотношение сторон. У .figure-row__media и .step__media обёрткой
       служит вложенный .media, поэтому берём именно его. */
    var maskSelectors = [
      '.media',
      '.segment__media',
      '.music__media',
      '.case__gallery figure'
    ].join(', ');

    // Герой живёт своей жизнью (видео, собственный fade) — исключаем.
    // Вложенные совпадения (.case__gallery figure сама .media) отсеиваем Set'ом.
    var seen = [];
    document.querySelectorAll(maskSelectors).forEach(function (box) {
      if (box.closest('.hero')) return;
      if (seen.indexOf(box) > -1) return;
      var img = box.querySelector('img');
      if (!img) return;
      seen.push(box);
      maskedMedia.push({ box: box, img: img });
    });

    maskedMedia.forEach(function (item) {
      var box = item.box;
      var img = item.img;

      // Класс снимает штатный transition картинки и ховер-зум на время анимации
      box.classList.add('is-masked');

      /* Обёртка, в которой нет ничего кроме этого кадра (.figure-row__media,
         .case__hero), не должна дополнительно уезжать по translateY —
         иначе кадр и открывается маской, и параллельно всплывает.
         Обёртки со своим текстом (.segment, .music__item) не трогаем. */
      var wrap = box.closest('[data-reveal]');
      if (wrap && wrap !== box && !wrap.querySelector('.t-body, .t-h2, .t-h3, .t-label')) {
        wrap.classList.add('is-masked-wrap');
      }

      gsap.set(box, { clipPath: 'inset(100% 0 0 0)' });
      gsap.set(img, { scale: 1.3, yPercent: 8, transformOrigin: 'center center' });

      var tl = gsap.timeline({
        paused: true,
        onComplete: function () {
          // Отдаём картинку параллаксу: GSAP снимает свои инлайновые
          // transform-свойства, дальше её двигает applyParallax()
          gsap.set(img, { clearProps: 'transform' });
          box.classList.remove('is-masked');
          box.classList.add('is-revealed');
        }
      });

      tl.to(box, { clipPath: 'inset(0% 0 0 0)', duration: 1.3, ease: 'expo.out' })
        .to(img, { scale: 1, yPercent: 0, duration: 1.3, ease: 'expo.out' }, '<');

      ScrollTrigger.create({
        trigger: box,
        start: 'top 88%',
        once: true,
        onEnter: function () { tl.play(); }
      });
    });
  }

  /* ---------- 4. Параллакс медиа ---------- */
  var parallaxItems = Array.prototype.slice.call(document.querySelectorAll('[data-parallax]'));
  var ticking = false;

  /* Параллакс не должен спорить с раскрытием маски: пока кадр открывается,
     transform картинки ведёт GSAP. Ищем ближайший кадрирующий бокс и ждём,
     когда с него снимут .is-masked. */
  function parallaxReady(img) {
    var box = img.parentElement;
    return !box || !box.classList.contains('is-masked');
  }

  function applyParallax() {
    var vh = window.innerHeight;
    parallaxItems.forEach(function (el) {
      var rect = el.getBoundingClientRect();
      if (rect.bottom < -200 || rect.top > vh + 200) return;
      // -1 (элемент внизу экрана) → 1 (вверху)
      var progress = (vh / 2 - (rect.top + rect.height / 2)) / (vh / 2);
      var inner = el.querySelector('img');
      if (inner && parallaxReady(inner)) {
        inner.style.transform = 'scale(1.08) translate3d(0,' + (progress * 22).toFixed(2) + 'px,0)';
      }
    });
    ticking = false;
  }

  /* ---------- 5. Процесс: активный шаг и индикатор прогресса ---------- */
  var procSteps = Array.prototype.slice.call(
    document.querySelectorAll('#procSteps .step')
  );
  var procDots = Array.prototype.slice.call(
    document.querySelectorAll('#procDots li')
  );

  /* Схема служебной полосы: та же линия с засечками, что и в карточках,
     но прочерчивается не по появлению, а по прогрессу шагов.
     Единственный индикатор прогресса в блоке — прежняя вторая линия
     (.proc__track-line / #procProgress) удалена как дублирующая. */
  var procScheme = document.getElementById('procScheme');
  var procSchemeLine = procScheme && procScheme.querySelector('[data-draw]');
  var procSchemeTicks = procScheme
    ? Array.prototype.slice.call(procScheme.querySelectorAll('[data-tick]'))
    : [];
  var procSchemeLen = procSchemeLine ? lineLength(procSchemeLine) : 0;

  if (procSchemeLine && procSchemeLen > 0) {
    procSchemeLine.style.setProperty('--len', procSchemeLen.toFixed(1) + 'px');
  }

  /* Засечки к пунктам списка.
     У схемы preserveAspectRatio="none" и viewBox 0 0 24 400, так что
     вертикаль тянется на всю высоту .proc__track: доля высоты трека
     переводится в единицы viewBox умножением на 400. Позиции пунктов
     зависят от кегля и gap, а те — от вьюпорта, поэтому константы cy
     (4/102/200/298/396) с подписями неизбежно расходились. */
  function layoutProcTicks() {
    if (!procScheme || !procSchemeTicks.length || !procDots.length) return;

    var trackEl = procScheme.parentNode;
    if (!trackEl) return;

    var track = trackEl.getBoundingClientRect();
    // Трек скрыт (мобильная раскладка) — считать не от чего
    if (track.height <= 0) return;

    var first = null;
    var last = null;

    procSchemeTicks.forEach(function (tick, i) {
      var dot = procDots[i];
      if (!dot) return;
      var r = dot.getBoundingClientRect();
      // Центр пункта относительно верха трека, в единицах viewBox.
      // Радиус засечки — 3.5, держим её целиком внутри viewBox.
      var cy = Math.max(4, Math.min(396,
        ((r.top + r.height / 2) - track.top) / track.height * 400
      ));
      tick.setAttribute('cy', cy.toFixed(1));
      if (first === null) first = cy;
      last = cy;
    });

    // Линия идёт ровно от первой засечки до последней, а не от края до края:
    // иначе прогресс (доля пройденных шагов) не совпадал бы с точками,
    // к которым он визуально привязан.
    if (procSchemeLine && first !== null && last > first) {
      procSchemeLine.setAttribute('y1', first.toFixed(1));
      procSchemeLine.setAttribute('y2', last.toFixed(1));
      procSchemeLen = lineLength(procSchemeLine);
      if (procSchemeLen > 0) {
        procSchemeLine.style.setProperty('--len', procSchemeLen.toFixed(1) + 'px');
      }
      // Пересчитанная длина меняет и текущий dashoffset
      updateProcess();
    }
  }

  function updateProcess() {
    if (!procSteps.length) return;

    // Активен шаг, пересёкший «линию чтения» — 42% высоты экрана
    var line = window.innerHeight * 0.42;
    var active = -1;

    procSteps.forEach(function (el, i) {
      var rect = el.getBoundingClientRect();
      if (rect.top <= line && rect.bottom > line * 0.4) active = i;
    });

    // До пересечения линии подсвечиваем первый шаг, если он уже в кадре
    if (active === -1) {
      var first = procSteps[0].getBoundingClientRect();
      if (first.top < window.innerHeight && first.bottom > 0) active = 0;
    }

    // Пройденные шаги помечаются так же, как пункты индикатора: рядом
    // висит шкала «3 из 5», а сами шаги жили в бинарной логике.
    procSteps.forEach(function (el, i) {
      el.classList.toggle('is-active', i === active);
      el.classList.toggle('is-done', active > -1 && i < active);
    });

    procDots.forEach(function (el, i) {
      el.classList.toggle('is-active', i === active);
      el.classList.toggle('is-done', active > -1 && i < active);
    });

    // Линия идёт от первой засечки до последней, поэтому доля считается
    // по промежуткам между шагами, а не по их числу: на первом шаге линия
    // ещё не прочерчена, на последнем доходит ровно до нижней засечки.
    // (active + 1) / length давало бы на первом шаге 20% пути до точки,
    // которая уже стоит в его начале.
    var ratio = active < 0 || procSteps.length < 2
      ? 0
      : active / (procSteps.length - 1);

    // Линия схемы прочерчивается сверху вниз на ту же долю,
    // засечки зажигаются по мере прохождения шагов
    if (procSchemeLine && procSchemeLen > 0) {
      procSchemeLine.style.setProperty(
        '--off', (procSchemeLen * (1 - (reduceMotion ? 1 : ratio))).toFixed(1) + 'px'
      );
    }
    procSchemeTicks.forEach(function (tick, i) {
      tick.classList.toggle('is-lit', reduceMotion || i <= active);
    });
  }

  function onScroll() {
    onScrollHeader();
    updateProcess();
    if (!reduceMotion && !ticking) {
      ticking = true;
      window.requestAnimationFrame(applyParallax);
    }
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  // Позиции засечек читают раскладку — пересчитываем их только на ресайзе,
  // а не в каждом кадре прокрутки. Через rAF, как и остальные пересчёты.
  var procTicking = false;
  function scheduleProcTicks() {
    if (procTicking) return;
    procTicking = true;
    window.requestAnimationFrame(function () {
      procTicking = false;
      layoutProcTicks();
    });
  }
  window.addEventListener('resize', function () {
    onScroll();
    scheduleProcTicks();
  }, { passive: true });
  // Lenis скроллит реальное окно, так что нативное событие приходит и без этого,
  // но подписка гарантирует кадр в кадр с его собственным rAF
  if (lenis) lenis.on('scroll', onScroll);
  onScroll();
  layoutProcTicks();
  // Кегль пунктов зависит от гарнитуры: до её загрузки высоты строк другие
  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(layoutProcTicks).catch(function () { /* фолбэк — стартовые cy */ });
  }
  // Кадры шагов крупные и грузятся лениво: до их отрисовки строка ниже
  // собственной высоты, и тики встают по устаревшей геометрии. Пересчёт по
  // факту загрузки каждого — с дедупликацией через тот же rAF, что и resize,
  // иначе пять картинок дадут пять пересчётов в одном кадре.
  procSteps.forEach(function (step) {
    var img = step.querySelector('.step__media img');
    if (!img || img.complete) return;
    img.addEventListener('load', scheduleProcTicks, { once: true, passive: true });
    // Битый путь тоже меняет высоту строки — плейсхолдер остаётся, но кадра нет
    img.addEventListener('error', scheduleProcTicks, { once: true, passive: true });
  });
  if (!reduceMotion) applyParallax();

  /* ---------- 5b. Sticky-стопка полос в «Людях» ---------- */
  /* Полосы липнут к верху экрана и складываются в стопку: следующая наезжает
     на предыдущую, предыдущая уходит вглубь — уменьшается и гаснет.
     Само залипание делает CSS (position: sticky, только на ≥1025px),
     ScrollTrigger отвечает лишь за «глубину» уходящей карточки. */
  var figureStack = document.getElementById('figureStack');

  if (figureStack && canAnimate && hasST) {
    var figureRows = Array.prototype.slice.call(
      figureStack.querySelectorAll('.figure-row')
    );

    // Значение top у sticky задано в CSS через clamp — читаем оттуда,
    // чтобы конец прокрутки совпадал с линией залипания при любой ширине
    var getStickyTop = function () {
      var top = parseFloat(getComputedStyle(figureRows[0]).top);
      return isFinite(top) ? top : 96;
    };

    /* matchMedia от GSAP, а не собственный слушатель: он сам создаёт триггеры
       при входе в брейкпоинт и — главное — при выходе убивает их и снимает
       выставленные scale/opacity. Своим слушателем полосы оставались
       уменьшенными на планшете, где sticky уже выключен и вернуть их нечему. */
    gsap.matchMedia().add('(min-width: 1025px)', function () {
      // Последняя полоса не залипает (ей не на что наезжать) и вглубь не уходит
      figureRows.slice(0, -1).forEach(function (row, i) {
        var next = figureRows[i + 1];

        /* Уменьшение — самой полосе, притухание — плёнке ::after поверх неё.
           Гасить полосу через её собственный opacity нельзя: полупрозрачным
           стал бы и фон, и сквозь карточку просвечивала бы предыдущая. */
        var tl = gsap.timeline({
          scrollTrigger: {
            trigger: next,
            // Отсчёт по фактическому перекрытию: от подхода следующей полосы
            // снизу до момента, когда она сама встала на линию залипания
            start: 'top bottom',
            end: function () { return 'top top+=' + getStickyTop(); },
            scrub: true,
            invalidateOnRefresh: true
          }
        });

        tl.to(row, { scale: 0.96, ease: 'none' }, 0)
          .to(row, { '--stack-dim': 0.4, ease: 'none' }, 0);
      });
    });
  }

  /* ---------- 5c. Счётчики в фактах ---------- */
  /* Число набегает от нуля один раз при входе в кадр. Формат исходного
     текста сохраняем целиком: ведущие нули («01»), знак процента,
     диапазон через тире («30–200»). Нечисловые значения («СПб») не трогаем. */
  var counters = Array.prototype.slice.call(document.querySelectorAll('[data-count]'));

  if (counters.length && canAnimate && hasST) {
    counters.forEach(function (el) {
      var source = el.textContent.trim();
      // Разбираем строку на куски: числа отдельно, всё прочее — как есть
      var parts = source.split(/(\d+)/);
      var numbers = parts.filter(function (p) { return /^\d+$/.test(p); });
      if (!numbers.length) return;

      // Ведущие нули задают ширину поля: «01» должно набегать как 01, а не 1
      var pads = numbers.map(function (n) { return n.length; });

      /* Считаем обычным объектом (n0, n1, …), а не массивом: snap до целых
         у GSAP работает по именованным свойствам, для endArray его нет. */
      var state = {};
      var targets = {};
      var snaps = {};
      numbers.forEach(function (n, k) {
        state['n' + k] = 0;
        targets['n' + k] = Number(n);
        snaps['n' + k] = 1;
      });

      function render() {
        var k = 0;
        el.textContent = parts.map(function (p) {
          if (!/^\d+$/.test(p)) return p;
          var v = String(state['n' + k]);
          while (v.length < pads[k]) v = '0' + v;
          k++;
          return v;
        }).join('');
      }

      // Резервируем место сразу: иначе строка «180» стартует с «0»
      // и подпись справа заметно съезжает по ширине
      el.style.minWidth = el.getBoundingClientRect().width.toFixed(1) + 'px';
      el.style.display = 'inline-block';
      render();

      ScrollTrigger.create({
        trigger: el,
        start: 'top 90%',
        once: true,               // пересчёта при повторном скролле не будет
        onEnter: function () {
          var vars = {
            duration: 1.4,
            ease: 'power2.out',
            snap: snaps,
            onUpdate: render,
            onComplete: function () {
              // Точное исходное значение вместо накопленной дробной ошибки
              el.textContent = source;
            }
          };
          for (var key in targets) vars[key] = targets[key];
          gsap.to(state, vars);
        }
      });
    });
  }

  /* ---------- 6. Горизонтальная лента: колесо и перетаскивание ---------- */
  var rail = document.getElementById('rail');

  if (rail) {
    // Вертикальное колесо прокручивает ленту, пока она не дошла до края
    rail.addEventListener('wheel', function (e) {
      if (Math.abs(e.deltaY) <= Math.abs(e.deltaX)) return;
      var atStart = rail.scrollLeft <= 0;
      var atEnd = rail.scrollLeft + rail.clientWidth >= rail.scrollWidth - 1;
      if ((e.deltaY < 0 && atStart) || (e.deltaY > 0 && atEnd)) return;
      e.preventDefault();
      rail.scrollLeft += e.deltaY;
    }, { passive: false });

    // Перетаскивание мышью
    var isDown = false, startX = 0, startScroll = 0;

    rail.addEventListener('pointerdown', function (e) {
      if (e.pointerType === 'touch') return;
      isDown = true;
      startX = e.clientX;
      startScroll = rail.scrollLeft;
      rail.setPointerCapture(e.pointerId);
      rail.style.cursor = 'grabbing';
    });

    rail.addEventListener('pointermove', function (e) {
      if (!isDown) return;
      rail.scrollLeft = startScroll - (e.clientX - startX);
    });

    ['pointerup', 'pointercancel'].forEach(function (evt) {
      rail.addEventListener(evt, function () {
        isDown = false;
        rail.style.cursor = '';
      });
    });
  }

  /* ---------- 7. Форма — заглушка прототипа ---------- */
  var form = document.getElementById('contactForm');
  var status = document.getElementById('formStatus');

  if (form && status) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var name = form.elements.name.value.trim();
      var contact = form.elements.contact.value.trim();

      if (!name || !contact) {
        status.textContent = 'Заполните имя и контакт — мы свяжемся с вами.';
        return;
      }

      status.textContent = 'Спасибо, ' + name + '. Мы позвоним или напишем в ближайшее время.';
      form.reset();
    });
  }

  /* ---------- 8. Фоновое видео героя ---------- */
  var heroVideo = document.querySelector('.hero__video');

  if (heroVideo) {
    // Показываем видео только когда есть первый кадр — иначе в кадре подложка
    var showVideo = function () { heroVideo.setAttribute('data-ready', ''); };

    if (heroVideo.readyState >= 2) {
      showVideo();
    } else {
      heroVideo.addEventListener('loadeddata', showVideo, { once: true });
    }

    /* Очень медленный отъезд камеры: 1.12 → 1 за 20 секунд, линейно.
       На глаз это не читается как анимация — просто петля перестаёт
       ощущаться статичной. Yoyo, чтобы масштаб не прыгал на стыке циклов. */
    if (canAnimate) {
      gsap.fromTo(heroVideo,
        { scale: 1.12 },
        { scale: 1, duration: 20, ease: 'none', repeat: -1, yoyo: true });
    }

    if (reduceMotion) {
      // Статичный кадр вместо цикла
      heroVideo.removeAttribute('loop');
      heroVideo.pause();
    } else {
      // Safari/iOS могут отклонить autoplay — пробуем ещё раз явно
      var play = heroVideo.play();
      if (play && typeof play.catch === 'function') {
        play.catch(function () {
          var retry = function () {
            heroVideo.play().catch(function () {});
            document.removeEventListener('pointerdown', retry);
          };
          document.addEventListener('pointerdown', retry, { once: true });
        });
      }

      // Не крутим видео вхолостую, когда герой ушёл из вида
      if ('IntersectionObserver' in window) {
        new IntersectionObserver(function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) {
              heroVideo.play().catch(function () {});
            } else {
              heroVideo.pause();
            }
          });
        }, { threshold: 0.1 }).observe(heroVideo);
      }
    }
  }

})();
