/* =========================================================
   ЧАСТНЫЕ БАЛЫ — поведение прототипа

   Слои движения (этап 15 свёл их к одному таймингу 240ms ease):
   · reveal-on-scroll — чистая прозрачность 0 → 1, без сдвига и каскада;
   · инерционный скролл (Lenis), связанный с тикером GSAP;
   · выезд мега-строки из-под маски — единственное движение сверх системы,
     оставленное решением владельца как ведущий приём сайта;
   · sticky-стопка полос в секции «Люди»;
   · прочерчивающиеся hairline (рост линии — роль из системы).

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

  /* ---------- 0. Шкала движения ---------- */
  /* Пять ступеней длительности, шаг каскада и кривые объявлены один раз —
     в :root (styles.css, «Шкала движения»). Читаем их оттуда, а не держим
     здесь вторую копию: две копии одной шкалы разъезжаются на первой же
     правке, и половина сайта начинает двигаться не как вторая половина.
     CSS считает в миллисекундах, GSAP — в секундах; перевод здесь. */
  var rootCS = window.getComputedStyle(document.documentElement);

  /* ---------- 0a. Готовность гарнитур ---------- */
  /* Заголовки с посимвольным появлением показываются не раньше, чем придут
     веб-шрифты. Причина не в красоте первого кадра, а в вёрстке: запасная
     гарнитура шире, и «Частные балы» в 130 px не помещаются в свою колонку —
     строка уезжает на вторую, первый экран становится выше на 114 px, а с
     приходом Manrope собирается обратно. Пока заголовок спрятан и его строки
     не переносятся (styles.css, A1a), высота коробки от гарнитуры не зависит
     и сдвигать нечего.

     Ждать почти не приходится: таблица стилей шрифтов и так блокирует
     отрисовку, остаются сами файлы. Сторож — на случай, если ready не придёт
     вовсе (сеть отвалилась, шрифты вырезаны прокси): заголовок обязан
     появиться в любом случае, пусть и запасной гарнитурой. */
  var FONTS_GUARD = 900;

  function whenFontsReady(fn) {
    if (!document.fonts || !document.fonts.ready) return fn();
    var called = false;
    var run = function () {
      if (called) return;
      called = true;
      fn();
    };
    document.fonts.ready.then(run, run);
    window.setTimeout(run, FONTS_GUARD);
  }

  /* ---------- Этап 19. Заголовок героя: притирка фолбэка ----------

     Хвост «сдвиг заголовка героя» с самого начала работы. Разбор целиком —
     в styles.css у правила .hero__title .line; здесь исполнение.

     Коротко: до этапа 15 заголовок нёс data-gradual и был разобран
     на span'ы по знакам, отчего его высота была задана с первого кадра.
     Приём сняли — и заголовок стал обычным текстом, который до прихода
     Old Standard TT / Manrope набирается фолбэком. Фолбэк шире, строка
     переносилась на две, высота скакала со 228,8 на 114,4. Это и был
     весь CLS: 0,0376 на 1440 при нуле на версии до этапа 13.

     CSS уже запретил перенос (white-space: nowrap). Осталось второе:
     фолбэк шире поля, и без притирки его просто срезало бы краем —
     на 1024 заголовок читался «ЧАСТНЫЕ БАЛ». Здесь считается,
     насколько строку сжать по горизонтали, чтобы она влезла целиком.

     Коэффициент только УМЕНЬШАЕТ (min(1, …)): растягивать строку шире
     набранной незачем — кегль задан clamp'ом и это его работа.
     У настоящей гарнитуры набор у́же поля, коэффициент выходит ровно 1,
     и в установившемся состоянии не меняется ничего.

     Считается дважды: сразу (пока стоит фолбэк) и по готовности
     гарнитур — через whenFontsReady, у которого есть страховка
     по таймауту на случай, если шрифты не придут вовсе. */
  function fitHeroLines() {
    var lines = document.querySelectorAll('.hero__title .line');
    if (!lines.length) return;

    for (var i = 0; i < lines.length; i++) {
      var line = lines[i];
      var span = line.firstElementChild;
      if (!span) continue;

      /* Замер идёт при коэффициенте 1: getBoundingClientRect отдаёт
         ширину УЖЕ С УЧЁТОМ transform, и мерить сжатую строку значило бы
         считать коэффициент от собственного прошлого результата. */
      span.style.setProperty('--fit-x', '1');

      var avail = line.clientWidth;
      var need  = span.getBoundingClientRect().width;
      if (!avail || !need) continue;

      span.style.setProperty('--fit-x', Math.min(1, avail / need).toFixed(4));
    }
  }

  fitHeroLines();
  whenFontsReady(fitHeroLines);

  var heroFitTicking = false;
  window.addEventListener('resize', function () {
    if (heroFitTicking) return;
    heroFitTicking = true;
    window.requestAnimationFrame(function () {
      heroFitTicking = false;
      fitHeroLines();
    });
  }, { passive: true });

  function motionSec(token) {
    var v = rootCS.getPropertyValue(token).trim();
    // Стилей нет — движения тоже: анимировать нечего, ставим мгновенно
    if (!v) return 0;
    var n = parseFloat(v);
    if (isNaN(n)) return 0;
    return v.slice(-2) === 'ms' ? n / 1000 : n;
  }

  /* Кривая берётся из того же токена и отдаётся CustomEase, чтобы твин
     и CSS-переход шли по одной геометрии, а не «примерно похоже».
     Без плагина (или при неразборчивом значении) — ближайший штатный ease.

     Токен системы — ключевое слово `ease`, а не cubic-bezier. У CSS это
     ровно cubic-bezier(.25, .1, .25, 1); собственного эквивалента у GSAP
     нет (его 'power1.inOut' заметно симметричнее), поэтому раскрываем
     ключевые слова в их спецификационные координаты и дальше идём
     тем же путём, что и любая явная кривая. */
  var CSS_KEYWORD_EASE = {
    'ease':        [.25, .1, .25, 1],
    'ease-in':     [.42, 0, 1, 1],
    'ease-out':    [0, 0, .58, 1],
    'ease-in-out': [.42, 0, .58, 1],
    'linear':      [0, 0, 1, 1]
  };

  function motionEase(token, fallback) {
    if (!hasGsapLib) return fallback;
    var id = token.replace(/^--/, '');
    try {
      var raw = rootCS.getPropertyValue(token).trim();
      var nums = CSS_KEYWORD_EASE[raw] || raw.match(/-?\d*\.?\d+/g);
      if (!window.CustomEase || !nums || nums.length !== 4) {
        // Без CustomEase ключевое слово CSS всё же понимает сам GSAP
        return (raw && gsap.parseEase(raw)) ? raw : fallback;
      }
      gsap.registerPlugin(window.CustomEase);
      CustomEase.create(id, nums.join(','));
      return gsap.parseEase(id) ? id : fallback;
    } catch (e) {
      return fallback;
    }
  }

  /* Одна длительность и одна кривая на всё, что ведёт GSAP, — те же самые,
     что и у переходов в CSS: шкала объявлена в styles.css (раздел 1)
     и читается отсюда, копии значений в JS нет. */
  var DUR_MOTION = motionSec('--duration-hover');

  var EASE_MOTION = motionEase('--easing', 'power1.inOut');

  /* Инерция скролла — не переход интерфейса, и под 240ms её не подвести:
     это физика прокрутки, а не появление или отклик элемента. Держим
     прежнюю величину явным числом, чтобы снятая шкала её не задела.
     Вынесено в журнал как открытый вопрос к этапу 16. */
  var SCROLL_GLIDE = 1.3;

  /* ---------- 0a. Инерционный скролл (Lenis) ---------- */
  /* Скролл ведёт Lenis, кадры — тикер GSAP: два независимых rAF-цикла
     давали бы рассинхрон между позицией страницы и ScrollTrigger'ами.
     При prefers-reduced-motion Lenis не создаём вовсе — остаётся нативный
     скролл, а класс .no-lenis возвращает scroll-behavior: smooth якорям. */
  var lenis = null;

  if (!reduceMotion && typeof window.Lenis !== 'undefined') {
    lenis = new Lenis({
      // Инерция скролла — самое медленное движение на странице, ступень 5
      duration: SCROLL_GLIDE,
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

  /* ---------- 0b. Шина скролла ---------- */
  /* Всё, что ведётся прокруткой (шапка, лента форматов, «Подход», шкала
     вечера, параллакс), читает геометрию через getBoundingClientRect.
     Каждая своя подписка = своя точка чтения в кадре, а чтение после чужой
     записи в стили заставляет браузер пересобирать раскладку заново.
     Поэтому подписка одна, а задачи выстроены в очередь: за кадр раскладка
     считается один раз, и порядок вызовов предсказуем.

     ScrollTrigger сюда не заводим — GSAP ждёт свой ScrollTrigger.update
     прямо на событии Lenis (см. выше), и задержка на кадр рассинхронила бы
     его с позицией страницы. */
  var scrollTasks = [];
  var scrollTicking = false;

  function runScrollTasks() {
    scrollTicking = false;
    for (var i = 0; i < scrollTasks.length; i++) scrollTasks[i]();
  }

  function requestScrollFrame() {
    if (scrollTicking) return;
    scrollTicking = true;
    window.requestAnimationFrame(runScrollTasks);
  }

  /* immediate прогоняет задачу сразу: стартовое состояние (класс шапки,
     позиция ленты, заливка индикаторов) должно быть верным до первого
     движения мыши, а не появляться от него. */
  function onScrollTask(fn, immediate) {
    scrollTasks.push(fn);
    if (immediate) fn();
  }

  window.addEventListener('scroll', requestScrollFrame, { passive: true });
  // Lenis двигает страницу сам — нативный scroll при этом не всегда стреляет,
  // а его собственное событие приходит кадр в кадр с его rAF
  if (lenis) lenis.on('scroll', requestScrollFrame);

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
      lenis.scrollTo(target, { offset: -80, duration: SCROLL_GLIDE });
      // Адрес обновляем сами: preventDefault снял штатное поведение
      if (window.history && history.pushState) history.pushState(null, '', hash);
    }
  });

  /* ---------- 0c. Источники видео ---------- */
  /* Каждое video[data-sources] перечисляет варианты одной и той же петли
     от лёгкого к тяжёлому. Перебор ведём сами, потому что штатный <source>
     эту задачу не решает: браузер выбирает вариант по MIME-типу и наличие
     файла не проверяет — на 404 считает источник рабочим, останавливается
     на нём и остаётся с пустым кадром, дальше по списку не идёт.
     Поэтому спрашиваем HEAD и берём первый существующий.

     Если не нашлось ничего (сейчас это норма — облегчённых версий ещё нет),
     src не ставим вовсе: у обоих видео постером стоит тот самый кадр,
     который показывает петля, и элемент остаётся с ним. Отдельного
     фолбэка на разметке для этого не нужно.

     Флаг data-loop-ready снимает с элемента ожидание: обработчики петли
     (герой) ждут его, чтобы не дёргать play() по пустому src. */
  function resolveVideoSources(video) {
    var list = (video.getAttribute('data-sources') || '')
      .split(',')
      .map(function (s) { return s.trim(); })
      .filter(Boolean);

    if (!list.length) return Promise.resolve(false);

    /* fetch есть не везде, где работает остальная страница; без него
       перебирать нечем — берём первый вариант и полагаемся на постер,
       если файла не окажется. */
    if (typeof window.fetch !== 'function') {
      video.src = list[0];
      return Promise.resolve(true);
    }

    var next = function (i) {
      if (i >= list.length) return Promise.resolve(false);
      return fetch(list[i], { method: 'HEAD' })
        .then(function (res) {
          if (!res.ok) return next(i + 1);
          video.src = list[i];
          // preload="metadata" сам по себе новый src не подхватывает
          video.load();
          return true;
        })
        .catch(function () { return next(i + 1); });
    };

    return next(0);
  }

  /* Обещание кладём на сам элемент: перебор идёт для всех video[data-sources]
     разом (ниже), а раздел 8 ждёт исхода конкретно для героя. Без кэша
     он запустил бы вторую серию HEAD-запросов по тому же списку.
     data-loop-ready — тот же исход в разметке, для отладки и стилей. */
  function initVideoSources(video) {
    if (!video._sourcesReady) {
      video._sourcesReady = resolveVideoSources(video).then(function (found) {
        video.setAttribute('data-loop-ready', found ? 'src' : 'poster');
        return found;
      });
    }
    return video._sourcesReady;
  }

  document.querySelectorAll('video[data-sources]').forEach(function (video) {
    /* Петля в строке текста при prefers-reduced-motion не нужна совсем:
       постер уже в кадре, качать файл ради статичной картинки незачем.
       Герой — исключение, он глушит петлю сам (см. раздел 8): там видео
       нужно и неподвижным, ради глубины кадра под заголовком. */
    if (reduceMotion && !video.classList.contains('hero__video')) {
      video.removeAttribute('autoplay');
      video.removeAttribute('loop');
      video.setAttribute('data-loop-ready', 'poster');
      video._sourcesReady = Promise.resolve(false);
      return;
    }
    initVideoSources(video);
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
    var shapeItems   = navOverlay.querySelectorAll('.menu-list-item[data-shape]');
    var isMenuOpen   = false;
    /* Раскрытие меню идёт тем же одним таймингом, что и всё остальное:
       240ms ease. Этап 15 снял отсюда каскад (stagger), выезды пунктов
       снизу с поворотом, всплытие подписей и въезд штор сбоку — меню было
       самым крупным местом, где жили приёмы, которых в системе нет.
       Осталась смена прозрачности: панель есть или её нет. */
    var EASE = EASE_MOTION;
    var DUR  = reduceMotion ? 0 : DUR_MOTION;

    if (hasGsap) {
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
          /* Ни пружины, ни каскада, ни масштаба с поворотом: графика
             просто проявляется — единственное, что система разрешает. */
          gsap.fromTo(els,
            { opacity: 0 },
            { opacity: 1, duration: DUR_MOTION, ease: EASE_MOTION,
              overwrite: 'auto' });
        });

        item.addEventListener('mouseleave', function () {
          gsap.to(els, {
            opacity: 0, duration: DUR_MOTION, ease: EASE_MOTION,
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

      /* Всё появляется разом и одной прозрачностью. Шторы и панель ставятся
         на место без хода: их положение — раскладка, а не движение.
         Смена значка кнопки идёт тем же fade, поворот на 315° снят. */
      gsap.timeline({ defaults: { ease: EASE, duration: DUR } })
        .set(navOverlay, { display: 'block' })
        .set(panel, { xPercent: 0 }, '<')
        .set(backdrops, { xPercent: 0 }, '<')
        .fromTo(scrim, { autoAlpha: 0 }, { autoAlpha: 1 })
        .fromTo(navLinks, { autoAlpha: 0 }, { autoAlpha: 1 }, '<')
        .fromTo(fadeTargets, { autoAlpha: 0 },
                { autoAlpha: 1, clearProps: 'all' }, '<');
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
        .to(navLinks, { autoAlpha: 0 }, '<')
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

    /* ---------- Этап 19. Текущий раздел в меню ----------

       Хвост с этапа 8: место под правило было оставлено в styles.css
       (.nav-link[aria-current] .nav-link__text), но ставить его было
       не на чем — слежения за прокруткой в файле не было.

       Что делает: помечает пункт меню того раздела, в котором сейчас
       стоит страница. Метка — атрибут aria-current="true"; цвет вешает
       CSS, здесь только факт «мы в этом разделе». Терракота по системе
       допустима как метка раздела, и теперь она значит ровно это.

       ПОЧЕМУ IntersectionObserver, А НЕ ЗАМЕР НА КАЖДЫЙ КАДР ПРОКРУТКИ.
       Тем же приёмом в файле сделаны появления (раздел 3) и пауза
       героя за кадром: наблюдатель будит браузер только на пересечении
       границы, а не 60 раз в секунду. Прокрутку здесь ведёт Lenis,
       и вешать на неё ещё один синхронный замер геометрии значило бы
       платить кадрами за подсветку, которой в закрытом меню не видно.

       ПОЧЕМУ ПОЛОСА, А НЕ ТОЧКА. Разделы разной высоты, и на стыке
       двух в кадре всегда два сразу. Считаем текущим тот, что накрывает
       ЛИНИЮ В ТРЕТИ ЭКРАНА СВЕРХУ: rootMargin отрезает от корневой
       области всё, кроме узкой полосы на этой высоте, и пересекается
       с ней в каждый момент ровно один раздел. Треть, а не середина:
       читают верх экрана, и раздел должен помечаться, когда его
       заголовок пришёл, а не когда он дошёл до середины.

       ПОРЯДОК ВАЖЕН. entries приходят не в порядке страницы, поэтому
       из накрывающих линию берём не «последний в списке», а тот,
       что ниже всех по документу: при быстрой прокрутке в одну пачку
       попадают вход одного раздела и выход другого.

       БЕЗ JS и без IntersectionObserver метки просто нет — все девять
       пунктов идут одинаковым грежем, как и до этапа. Это не потеря
       содержания: пункт и так назван словом и номером. */
    var navSectionLinks = navOverlay.querySelectorAll('.nav-link[href^="#"]');

    if (navSectionLinks.length && 'IntersectionObserver' in window) {
      var navBySection = {};
      var navWatched = [];

      navSectionLinks.forEach(function (link) {
        var id = (link.getAttribute('href') || '').slice(1);
        if (!id) return;
        var section = document.getElementById(id);
        if (!section) return;
        navBySection[id] = link;
        navWatched.push(section);
      });

      if (navWatched.length) {
        var navCurrentId = null;
        /* Что сейчас пересекает линию. Держим множеством, а не одним
           значением: разделы входят и выходят разными событиями, и на
           стыке важно знать всех, кто накрывает линию, чтобы выбрать
           нижнего по документу. */
        var navHits = {};

        function navApply() {
          var pick = null, pickTop = -Infinity, id;

          for (id in navHits) {
            if (!navHits[id]) continue;
            var box = document.getElementById(id);
            if (!box) continue;
            var top = box.getBoundingClientRect().top;
            /* Ниже всех по документу — то есть с наибольшим top среди
               тех, кто линию уже накрыл. */
            if (top > pickTop) { pickTop = top; pick = id; }
          }

          if (pick === navCurrentId) return;

          if (navCurrentId && navBySection[navCurrentId])
            navBySection[navCurrentId].removeAttribute('aria-current');

          navCurrentId = pick;

          if (navCurrentId && navBySection[navCurrentId])
            navBySection[navCurrentId].setAttribute('aria-current', 'true');
        }

        var navObserver = new IntersectionObserver(function (entries) {
          entries.forEach(function (entry) {
            navHits[entry.target.id] = entry.isIntersecting;
          });
          navApply();
        }, {
          /* Полоса на трети экрана сверху: сверху отрезаем 33%,
             снизу — оставшиеся 67% минус пара пикселей на саму полосу. */
          rootMargin: '-33% 0px -66% 0px',
          threshold: 0
        });

        navWatched.forEach(function (section) { navObserver.observe(section); });
      }
    }

    /* ---------- Этап 19. Правый край лестницы меню (задача 2.7) ----------

       РЕШЕНИЕ: ровный правый край НЕ ДЕЛАЕТСЯ. Ниже — почему, потому что
       задача висит с этапа 8 и её надо снять с доски, а не передать дальше
       десятым этапом.

       ЧТО ТРЕБОВАЛОСЬ. Девять пунктов идут лестницей: каждый следующий
       начинается правее предыдущего (--step, 0…30cqw). Правые концы слов
       при этом падают куда придётся: на 1440 «Форматы» кончаются на 333,
       «До вечера» на 585, «О нас» на 632. Разброс 299px. Задание просило
       пересчитать формулу --menu-size так, чтобы край стал ровным.

       ЧТО ВСКРЫЛ ЗАМЕР — три вещи, и последняя закрывает вопрос.

       1. Девять членов «по ширине» в --menu-size не выбирались НИ РАЗУ.
          На всех пяти ширинах и на всех проверенных высотах экрана
          (900, 1080, 1440, 720) побеждал высотный член. На 1440x900:
          высотный отдаёт 50,03px, самый тесный из девяти width-членов —
          193,6px. Они не соревновались, они молчали. Половина формулы
          описывала ограничение, которое не наступает; она снята
          (см. styles.css).

       2. Коэффициент .58 («ширина прописной Manrope Extra-Bold») неверен.
          Фактическая ширина слова на единицу кегля: «Звук» 2,42,
          «О нас» 2,90, «Люди» 2,99, «Вечера» 3,54, «Подход» 4,13,
          «Правила» 4,51, «Форматы» 4,87, «До вечера» 5,13,
          «Структура» 5,48. Модель «все знаки одной ширины» ошибается
          на «Люди» на 29 %: она не знает, из каких букв набрано слово.

       3. ГЛАВНОЕ. Ровного края нет ни при каком кегле — это арифметика.
          Чтобы девять слов кончались на одной вертикали E, кегль каждого
          обязан быть (E − step) / unit. Отношение самого крупного кегля
          к самому мелкому при этом НЕ ОПУСКАЕТСЯ НИЖЕ 2,2 ни на одной
          ширине и ни при каком положении края:

            ширина 1440, край 650px  — кегли 72,5…189,8, отношение 2,62
            ширина 1440, край 1301px — кегли 200,8…458,6, отношение 2,28
            ширина  390, край 338px  — кегли  54,0…119,9, отношение 2,22
            ширина 2560, край 2392px — кегли 375,2…855,4, отношение 2,28

          То есть «Звук» обязан быть вдвое с лишним крупнее «Структуры» —
          всегда. Причина в пункте 2: разброс собственной ширины слов
          (2,42 против 5,48) и есть тот множитель, который ровный край
          перекладывает в кегли. Ниже некоторого края часть кеглей уходит
          в МИНУС («О нас» на 1440 при крае 390px: −7,5px) — ступень
          каскада там уже правее требуемого края.

          Перебор всех положений края шагом в пиксель на трёх ширинах:
          края, при котором все девять кеглей положительны И отношение
          не больше 1,67, не существует НИ ОДНОГО.

       ЧТО БЫЛО БЫ ЦЕНОЙ. Три варианта, все хуже нынешнего:
         — свой кегль каждому пункту: разнобой 2,2× в списке из девяти
           слов; читается не как лестница, а как случайный набор кеглей,
           и ломает «кегль — то, что разводит пункты между собой»
           (задача 2.6, этап 8);
         — выключка вправо (край ровный по построению): убивает сам
           каскад, ради которого ступень и заводилась;
         — растяжка слов по ширине (scaleX / font-stretch): меняет
           рисунок гарнитуры, а гарнитуры этап не трогает.

       ЧТО ОСТАВЛЕНО. Общий кегль и неровный правый край — то есть
       нынешнее положение. Лестница читается слева, по ступеням и номерам;
       правый край в этой композиции не несёт роли — он не линия, вдоль
       которой что-то выстроено, а просто конец слова.

       Снято при этом только мёртвое: девять width-членов и --fit.
       Кегль от этого не изменился ни на одной из пяти ширин (проверено:
       50,03px на 768/1024/1440/2560 и 40px на 390 — до и после).

       Задача 2.7 закрывается этим разбором, а не правкой. */
  }

  /* ---------- 3a-bis. Мега-заголовки во всю ширину ---------- */
  /* Главный приём референса: слово ровно по ширине вьюпорта, буквы упираются
     в края. Ни положение блока, ни кегль в CSS не выразить — оба зависят от
     фактической раскладки и от того, сколько места занимает конкретное слово
     конкретной гарнитурой. Оба шага ниже. */
  var megaTitles = Array.prototype.slice.call(document.querySelectorAll('.t-mega'));

  if (megaTitles.length) {
    var MEGA_BASE = 100;

    /* Просвет по краям (задача 2.2). Доля ширины экрана — чтобы поле росло
       вместе с кеглем, — но не меньше четырёх пикселей: на 320px восемь
       десятых процента дают 2,6px, а это уже не просвет, а погрешность. */
    var MEGA_GAP_RATIO = .008;
    var MEGA_GAP_MIN = 4;

    /* Канвас нужен ровно за одним: он единственный отдаёт границы краски,
       а не сумму ширин знаков. Один на все семь строк. */
    var megaInk = (function () {
      try { return document.createElement('canvas').getContext('2d'); }
      catch (e) { return null; }
    })();
    /* null — ещё не проверяли, умеет ли движок ctx.letterSpacing */
    var megaInkOk = null;

    /* Боковые свесы краски при текущем кегле элемента.
       left  — от начала строки до первой краски: у первого знака есть
               собственный отступ гарнитуры (у «В» это .0625em);
       right — насколько краска последней буквы выходит за конец строки:
               отрицательный трекинг вычитается и после неё, поэтому
               ширина строки меньше ширины краски.
       Замер на кегле 440px: 27px слева против −11px справа. То есть слово
       не только стояло не по центру — справа его резала собственная маска.
       Без этих двух чисел «равное поле с обеих сторон» не считается:
       по коробке строки поля выйдут равными, по буквам — нет.

       Кадр внутри строки в канвас не попадал бы, и это не мешало: он стоял
       в середине, и от его отсутствия одинаково уменьшались и
       actualBoundingBoxRight, и width — разность, то есть сам свес,
       не менялась. Ни кадра, ни строки-исключения больше нет (этап 16
       снял «ТАНЦМЕЙСТЕР ВЕДЁТ ЗАЛ» с приёма), но рассуждение оставлено:
       вернётся петля — вернётся и случай.

       exact — можно ли сверить ширину канваса с раскладкой (в строке нет
       кадра). Расхождение больше процента значит, что движок не применил
       letterSpacing или взял другую гарнитуру: тогда свесы считать нечем,
       возвращаем нули и обходимся одним просветом. */
    function megaBearings(el, advance, exact) {
      var none = { left: 0, right: 0 };
      if (!megaInk || megaInkOk === false) return none;

      var cs = getComputedStyle(el);
      var text = (el.textContent || '').replace(/\s+/g, ' ').trim();
      if (!text) return none;
      if (cs.textTransform === 'uppercase') text = text.toUpperCase();

      megaInk.font = cs.fontStyle + ' ' + cs.fontWeight + ' ' +
                     parseFloat(cs.fontSize) + 'px ' + cs.fontFamily;
      try { megaInk.letterSpacing = cs.letterSpacing; } catch (e) { megaInkOk = false; return none; }

      var m;
      try { m = megaInk.measureText(text); } catch (e) { megaInkOk = false; return none; }
      if (!m || typeof m.actualBoundingBoxRight !== 'number') { megaInkOk = false; return none; }

      if (exact) {
        megaInkOk = Math.abs(m.width - advance) <= Math.max(1, advance * .01);
        if (!megaInkOk) return none;
      }

      return { left: -m.actualBoundingBoxLeft, right: m.actualBoundingBoxRight - m.width };
    }

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

      /* Строка, которой разрешено переноситься, под приём не подпадает:
         её ширина всегда равна ширине блока, отношение выродилось бы
         в единицу и кегль остался бы базовым — кегль такой строке
         задаёт CSS.

         Этап 16 снял единственную такую строку (.t-mega--inline,
         «ТАНЦМЕЙСТЕР ВЕДЁТ ЗАЛ» ниже 760px): все пять оставшихся
         мега-строк идут в nowrap на всех ширинах, и ветка сейчас
         не срабатывает ни разу. Оставлена намеренно — она сторожит
         инвариант приёма («кегль считаем только по строке в одну
         линию»), а не ту конкретную строку. */
      if (getComputedStyle(el).whiteSpace !== 'nowrap') {
        el.style.removeProperty('font-size');
        el.style.removeProperty('--mega-inset');
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
        /* Сверку канвы с раскладкой (megaBearings, ветка exact) раньше
           отключала одна строка — та, внутри которой стоял кадр
           .inline-media: канва меряет только текст и о ширине кадра
           не знает, отношение не сошлось бы и свесы обнулились.
           Элемент снят задачей 1.2, медиа внутри строк больше нет,
           и сверка идёт на всех строках — этапом 16 их стало пять.
           Снятие .t-mega--inline условия не касается: exact выключал
           не класс, а кадр внутри строки, а кадра нет с этапа 9.
           Держим true явной константой, а не убираем параметр:
           вернётся петля — вернётся и условие. */
        var exact = true;
        var gap = Math.max(avail * MEGA_GAP_RATIO, MEGA_GAP_MIN);

        /* Проход первый — кегль. Вписывается в экран не коробка строки,
           а её краска: к измеренной ширине прибавляются оба свеса,
           и по этой величине берётся отношение. */
        var bear = megaBearings(el, measured, exact);
        var ink = measured - bear.left + bear.right;
        el.style.fontSize =
          (MEGA_BASE * (ink > 0 ? (avail - gap * 2) / ink : avail / measured)).toFixed(2) + 'px';

        /* Проход второй — положение. Границы краски движок отдаёт
           с точностью до пикселя, и полпикселя, измеренные на базовых
           100px, разъезжаются в два-три на кегле 500px: поля вышли бы
           заметно разными. Поэтому свесы перемеряются на настоящем
           кегле, а остаток ширины раскладывается поровну — так поля
           слева и справа равны по построению, а не по расчёту.
           Сдвиг ставится margin'ом строки, а не padding'ом элемента:
           элемент — сама маска, его коробка должна остаться во всю
           ширину экрана. */
        var finalWidth = line.getBoundingClientRect().width;
        var finalBear = megaBearings(el, finalWidth, exact);
        var finalInk = finalWidth - finalBear.left + finalBear.right;
        el.style.setProperty('--mega-inset',
          ((avail - finalInk) / 2 - finalBear.left).toFixed(2) + 'px');
      } else {
        el.style.removeProperty('font-size');
        el.style.removeProperty('--mega-inset');
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

    /* Здесь стоял пересчёт кегля по loadedmetadata / load кадра
       .inline-media: до прихода метаданных ширина медиа неизвестна,
       и замер строки мог оказаться неверным. Кадр снят задачей 1.2,
       ждать в мега-строках больше нечего — все семь набраны текстом,
       и их ширина известна сразу после готовности гарнитур
       (document.fonts.ready выше). Вернётся петля — вернётся и слушатель. */

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
    /* Дорожки индикатора наливаются на CSS: --seg-progress наследуется от
       .segments-scroll, и заливка идёт кадр в кадр со скроллом сама.
       Скрипту остаётся номер формата — он меняется дважды за весь путь,
       и трогать DOM на каждом кадре ради него незачем. */
    var segNum = document.getElementById('segments-num');
    var segIdx = -1;

    /* Доля пути с каждого края, на которой лента стоит. Переход должен
       читаться сменой кадра: слайд выходит, останавливается и даёт себя
       прочитать, и только потом уезжает. Без остановок то же расстояние
       превращается в непрерывное сползание — глазу не за что зацепиться. */
    /* Этап 18. Доля паузы поднята с .22 до .32 вместе с сокращением
       пути ленты (styles.css, .segments-scroll: 320svh -> 220svh).
       Обе величины держат один и тот же эффект — неподвижность слайда
       по краям, — и менять их порознь нельзя: короче путь при прежней
       доле означал бы, что лента трогается сразу. */
    var SEG_HOLD = .32;

    /* Разгон и торможение на стыках с паузами. Линейный прогресс на границе
       паузы трогает ленту рывком с полной скоростью — движение начинается
       не оттуда, где оно на самом деле началось. */
    function segEase(t) {
      return t < .5
        ? 2 * t * t
        : 1 - Math.pow(-2 * t + 2, 2) / 2;
    }

    /* Подсказка браузеру живёт ровно столько, сколько лента может ехать, —
       то есть пока её секция проходит мимо экрана. Постоянный will-change
       в CSS держал бы композитный слой всю сессию (этап 15: «will-change
       в покое — ноль»), а лента стоит почти всё время. */
    var segLive = false;

    function setSegLive(on) {
      if (on === segLive) return;
      segLive = on;
      segScroll.classList.toggle('is-sliding', on);
    }

    function updateSegments() {
      var rect = segScroll.getBoundingClientRect();

      /* Путь прокрутки = высота контейнера минус экран (лишний экран и есть
         дорога ленты). Прогресс — сколько этого пути уже пройдено. */
      var travel = rect.height - window.innerHeight;
      if (travel <= 0) { setSegLive(false); return; }

      setSegLive(rect.bottom > 0 && rect.top < window.innerHeight);

      var raw = -rect.top / travel;
      raw = Math.max(0, Math.min(1, raw));

      /* Сырой прогресс — доля прокрутки, рабочий — доля самого перехода.
         Края пути уходят в паузы, движение живёт только в середине;
         зажим и даёт неподвижность на обоих краях. */
      var p = (raw - SEG_HOLD) / (1 - SEG_HOLD * 2);
      p = segEase(Math.max(0, Math.min(1, p)));

      segScroll.style.setProperty('--seg-progress', p.toFixed(4));

      /* Номер переключается на середине хода ленты, а не прокрутки:
         середина прокрутки теперь приходится на движение, но считать её
         серединой перехода нельзя — паузы по краям не равны сами себе.
         Та же половина, на которой заполняется первая дорожка, — номер
         и заливка меняются одним и тем же порогом. */
      if (segNum) {
        var idx = p < .5 ? 0 : 1;
        if (idx !== segIdx) {
          segIdx = idx;
          segNum.textContent = idx === 0 ? '01' : '02';
        }
      }
    }

    onScrollTask(updateSegments, true);
    // Ресайз редок и приходит вне потока прокрутки — гонять его
    // через кадровый тикер незачем
    window.addEventListener('resize', updateSegments, { passive: true });
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
    '[data-reveal], [data-line], .scheme:not(.scheme--track), .t-mega, .t-format'
  );

  /* Подсказка браузеру (will-change) живёт ровно столько, сколько идёт
     появление, — за это отвечает класс .is-animating. Раньше она стояла
     в CSS постоянно: 544 узла держали композитные слои с загрузки и до
     конца сессии, из них 431 — отдельные буквы заголовков.

     Снимаем по transitionend, а не по таймеру: у букв каскад задержек,
     последняя доигрывает почти на секунду позже первой, и любое
     фиксированное число пришлось бы держать синхронно со шкалой.
     Сторож на случай, если transitionend не придёт вовсе (элемент увели
     в display: none, вкладка ушла в фон на время перехода) — иначе
     подсказка залипнет навсегда, то есть вернётся ровно то, что чиним. */
  var ANIM_GUARD = 4000;

  function markAnimating(el) {
    // Табы «Правил» переключаются сколько угодно раз — второй слушатель
    // на тот же элемент не нужен
    if (el.classList.contains('is-animating')) return;
    el.classList.add('is-animating');

    var done = function () {
      el.classList.remove('is-animating');
      el.removeEventListener('transitionend', onEnd);
      window.clearTimeout(guard);
    };
    // Всплывшее событие от буквы приходит на сам заголовок — этого и ждём:
    // последнее по времени и есть конец набора
    var onEnd = function () {
      window.clearTimeout(settle);
      // Ещё один такт: следом идут события остальных букв того же кадра
      settle = window.setTimeout(done, 60);
    };
    var settle = 0;
    var guard = window.setTimeout(done, ANIM_GUARD);

    el.addEventListener('transitionend', onEnd);
  }

  if (reduceMotion || !('IntersectionObserver' in window)) {
    // Появления нет — нечего и подсказывать
    revealTargets.forEach(function (el) { el.classList.add('is-in'); });
  } else {
    var revealObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          markAnimating(entry.target);
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
        // Через очередь готовности гарнитур: обратные вызовы идут в порядке
        // подписки, поэтому заголовок стартует уже правильной гарнитурой.
        whenFontsReady(function () {
          markAnimating(el);
          el.classList.add('is-in');
        });
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
        if (pane.hasAttribute('data-reveal')) {
          if (!reduceMotion) markAnimating(pane);
          pane.classList.add('is-in');
        }
        pane.querySelectorAll('[data-reveal]').forEach(function (el) {
          if (!reduceMotion) markAnimating(el);
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
  }

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
  onScrollTask(onScroll, true);
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
        /* Подсказка браузеру живёт ровно на своём отрезке прокрутки:
           класс ставится, когда полоса действительно начинает уходить
           вглубь, и снимается на обоих концах. В CSS постоянного
           will-change больше нет (этап 15: «will-change в покое — ноль»). */
        var setDepth = function (on) {
          row.classList.toggle('is-stacking', on);
        };

        var tl = gsap.timeline({
          scrollTrigger: {
            trigger: next,
            // Отсчёт по фактическому перекрытию: от подхода следующей полосы
            // снизу до момента, когда она сама встала на линию залипания
            start: 'top bottom',
            end: function () { return 'top top+=' + getStickyTop(); },
            scrub: true,
            invalidateOnRefresh: true,
            onToggle: function (self) { setDepth(self.isActive); }
          }
        });

        tl.to(row, { scale: 0.96, ease: 'none' }, 0)
          .to(row, { '--stack-dim': 0.4, ease: 'none' }, 0);
      });

      /* Выход из брейкпоинта убивает триггеры, но класс снять некому:
         на планшете полоса осталась бы с подсказкой навсегда. */
      return function () {
        figureRows.forEach(function (row) { row.classList.remove('is-stacking'); });
      };
    });
  }

  /* ---------- 6. Шкала вечера: пропорции, засечки, активный этап ----------
     Пришло на смену обработчикам горизонтальной ленты (колесо +
     перетаскивание): ленты в «Как проходит вечер» больше нет, шкала
     листается обычным скроллом страницы и своего ввода не требует.

     Здесь три задачи:
       а) высота пункта пропорциональна длительности этапа (--data-span);
       б) засечки схемы встают напротив своих пунктов;
       в) активный пункт подсвечивается, линия прочерчивается по скроллу.
     Механика (б) и (в) — та же, что у «Подхода» (см. блок 5): один язык
     «шага» на два блока. */
  var timeline = document.getElementById('timeline');
  var timelineItems = timeline
    ? Array.prototype.slice.call(timeline.querySelectorAll('.timeline__item'))
    : [];

  var evScheme = document.getElementById('eveningScheme');
  var evLine = evScheme && evScheme.querySelector('[data-draw]');
  var evTicks = evScheme
    ? Array.prototype.slice.call(evScheme.querySelectorAll('[data-tick]'))
    : [];
  var evLen = evLine ? lineLength(evLine) : 0;

  if (evLine && evLen > 0) {
    evLine.style.setProperty('--len', evLen.toFixed(1) + 'px');
  }

  /* Пропорции: минуты этапа переводятся в нижний отступ пункта.
     Линейно от длительности отступ брать нельзя — 120-минутная
     танцевальная программа дала бы шестикратный разрыв, и половина
     шкалы стала бы пустотой. Берём корень: разница остаётся читаемой
     (программа заметно длиннее выхода на вальс), но не разрывает блок.

     База и размах — в px от вьюпорта, чтобы шкала дышала вместе
     с остальной страницей. */
  function layoutTimelineGaps() {
    if (!timelineItems.length) return;

    var vw = window.innerWidth;

    // Ниже 1025px шкала идёт одной колонкой без линии (см. styles.css,
    // @media max-width: 1024px): объяснить разнобой пустот там нечем,
    // поэтому инлайновый --gap снимаем и шаг задаёт CSS.
    if (vw <= 1024) {
      timelineItems.forEach(function (el) { el.style.removeProperty('--gap'); });
      return;
    }

    /* Этап 18. База и размах сняты с вьюпорта и посажены на шкалу
       системы: база — интервал «заголовок → текст» (44), размах —
       интервал «блок → блок» (80). Пропорция длительности при этом
       цела: шаг по-прежнему растёт как sqrt(доли), просто теперь он
       ходит между 44 и 124 px, а не между 64,8 и 172,8 на 1440
       и не между 88 и 238 на 2560, куда его уводил vw.
       Именно этот множитель делал «Структуру» самой высокой секцией
       страницы: у восьми пунктов лишнее набегало восемь раз.
       Величины читаются из CSS, чтобы шкала жила в одном месте. */
    var cs = getComputedStyle(document.documentElement);
    var base = parseFloat(cs.getPropertyValue('--space-44')) || 44;
    var range = parseFloat(cs.getPropertyValue('--space-80')) || 80;

    var spans = timelineItems.map(function (el) {
      return Math.max(1, parseFloat(el.getAttribute('data-span')) || 1);
    });
    var maxSpan = Math.max.apply(null, spans);

    timelineItems.forEach(function (el, i) {
      // sqrt(доля от самого длинного этапа) — 0 у самого короткого пункта
      // не даёт: минимальная доля всё равно положительна, и слипания нет.
      var k = Math.sqrt(spans[i] / maxSpan);
      var gap = base + range * k;

      /* У пунктов с врезкой высоту строки задаёт кадр, а не текст: он
         вдвое выше абзаца, и рассчитанный отступ ложился бы поверх уже
         пустой строки — под вальсом-открытием получалась дыра в экран.
         Вычитаем перевес кадра над текстом, но не уходим ниже базы. */
      var media = el.querySelector('.timeline__media');
      if (media) {
        var body = el.querySelector('.timeline__body');
        var over = media.getBoundingClientRect().height -
                   (body ? body.getBoundingClientRect().height : 0);
        if (over > 0) gap = Math.max(base * 0.5, gap - over);
      }

      el.style.setProperty('--gap', gap.toFixed(1) + 'px');
    });
  }

  /* Засечки к пунктам — тот же расчёт, что layoutProcTicks:
     preserveAspectRatio="none" и viewBox 0 0 24 400, доля высоты трека
     переводится в единицы viewBox умножением на 400. Позиции пунктов
     зависят от кегля, gap и загруженных кадров — константы cy в разметке
     держатся только как стартовое приближение. */
  function layoutEveningTicks() {
    if (!evScheme || !evTicks.length || !timelineItems.length) return;

    var trackEl = evScheme.parentNode;
    if (!trackEl) return;

    var track = trackEl.getBoundingClientRect();
    if (track.height <= 0) return; // трек скрыт (мобильная раскладка)

    var first = null;
    var last = null;

    evTicks.forEach(function (tick, i) {
      var item = timelineItems[i];
      if (!item) return;
      // Засечка встаёт напротив заголовка пункта, а не по центру его бокса:
      // у пунктов разная высота (в этом весь смысл шкалы), и центр уводил бы
      // точку от строки, к которой она относится.
      var anchor = item.querySelector('.timeline__num') || item;
      var r = anchor.getBoundingClientRect();
      var cy = Math.max(4, Math.min(396,
        ((r.top + r.height / 2) - track.top) / track.height * 400
      ));
      tick.setAttribute('cy', cy.toFixed(1));
      if (first === null) first = cy;
      last = cy;
    });

    if (evLine && first !== null && last > first) {
      evLine.setAttribute('y1', first.toFixed(1));
      evLine.setAttribute('y2', last.toFixed(1));
      evLen = lineLength(evLine);
      if (evLen > 0) {
        evLine.style.setProperty('--len', evLen.toFixed(1) + 'px');
      }
      updateTimeline();
    }
  }

  function updateTimeline() {
    if (!timelineItems.length) return;

    // Та же «линия чтения» на 42% высоты экрана, что и у шагов «Подхода»
    var line = window.innerHeight * 0.42;
    var active = -1;

    timelineItems.forEach(function (el, i) {
      var rect = el.getBoundingClientRect();
      if (rect.top <= line && rect.bottom > line * 0.4) active = i;
    });

    if (active === -1) {
      var firstRect = timelineItems[0].getBoundingClientRect();
      if (firstRect.top < window.innerHeight && firstRect.bottom > 0) active = 0;
    }

    timelineItems.forEach(function (el, i) {
      el.classList.toggle('is-active', i === active);
      el.classList.toggle('is-done', active > -1 && i < active);
    });

    // Доля по промежуткам между засечками, а не по их числу: линия идёт
    // от первой точки до последней, и на первом этапе прочерчивать нечего.
    var ratio = active < 0 || timelineItems.length < 2
      ? 0
      : active / (timelineItems.length - 1);

    if (evLine && evLen > 0) {
      evLine.style.setProperty(
        '--off', (evLen * (1 - (reduceMotion ? 1 : ratio))).toFixed(1) + 'px'
      );
    }
    evTicks.forEach(function (tick, i) {
      tick.classList.toggle('is-lit', reduceMotion || i <= active);
    });
  }

  /* Пересчёт раскладки шкалы — с дедупликацией через rAF, как у засечек
     «Подхода»: ресайз, загрузка гарнитуры и двух врезок иначе дали бы
     несколько пересчётов в одном кадре. Пропорции считаются раньше
     засечек: те читают уже разложенную геометрию. */
  var evTicking = false;
  function scheduleTimeline() {
    if (evTicking) return;
    evTicking = true;
    window.requestAnimationFrame(function () {
      evTicking = false;
      layoutTimelineGaps();
      layoutEveningTicks();
    });
  }

  if (timeline) {
    layoutTimelineGaps();
    layoutEveningTicks();

    onScrollTask(updateTimeline, true);
    window.addEventListener('resize', scheduleTimeline, { passive: true });

    // Кегль пунктов зависит от гарнитуры: до её загрузки высоты строк другие
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(scheduleTimeline).catch(function () { /* стартовые cy */ });
    }
    // Врезки грузятся лениво и меняют высоту своего пункта
    timeline.querySelectorAll('.timeline__media img').forEach(function (img) {
      if (img.complete) return;
      img.addEventListener('load', scheduleTimeline, { once: true, passive: true });
      img.addEventListener('error', scheduleTimeline, { once: true, passive: true });
    });
  }

  /* ---------- 7. Форма — отправка заявки (задача 3.3) ----------

     ЕДИНСТВЕННАЯ ТОЧКА НАСТРОЙКИ — константа LEAD ниже.
     Приёмник выбран: CRM (Bitrix24 / amoCRM). Адрес вебхука на момент
     правки не выдан, поэтому endpoint пуст, и это не поломка, а режим:
     при пустом адресе форма проверяет ввод и честно говорит, что приём
     заявок ещё не подключён, вместо того чтобы делать вид, будто письмо
     ушло. Именно так вела себя прежняя заглушка — она отвечала
     «спасибо», не отправив ничего.

     Чтобы включить приём, достаточно вписать адрес в endpoint.
     Остальной код трогать не нужно.

     ПРО КЛЮЧ. Вебхук Bitrix24 вида
       https://портал.bitrix24.ru/rest/1/КЛЮЧ/crm.lead.add.json
     это и есть ключ к порталу: он попадёт в исходники страницы и будет
     виден любому. Тот, кто его нашёл, сможет слать в CRM что угодно.
     Поэтому у endpoint два законных значения:
       — адрес своей прокси-функции (ключ остаётся на сервере) — верный путь;
       — прямой адрес вебхука — быстрее, но ключ открыт; тогда в CRM
         стоит завести отдельный вебхук только с правом crm.lead.add
         и держать наготове его отзыв.
     Выбор за владельцем; код одинаков для обоих. */
  var LEAD = {
    /* Куда слать. Пусто — приём не подключён (см. выше). */
    endpoint: '',

    /* Формат полезной нагрузки:
         'bitrix' — тело под crm.lead.add (fields: {TITLE, NAME, COMMENTS, ...});
         'plain'  — плоский JSON {name, contact, about, page, ts}
                    для прокси, amoCRM или форм-сервиса. */
    format: 'bitrix',

    /* Сколько ждать ответа. Без предела вкладка с мёртвой сетью
       крутила бы «отправляем» бесконечно. 15 с — с запасом больше
       обычного ответа Bitrix и меньше терпения человека. */
    timeout: 15000
  };

  var form = document.getElementById('contactForm');
  var status = document.getElementById('formStatus');

  if (form && status) {
    var submitBtn = form.querySelector('.submit');
    var btnLabel = submitBtn ? submitBtn.textContent : '';
    var sending = false;

    /* Сообщение и его вид ставятся вместе: класс несёт цвет, текст —
       смысл. Цвет не единственный признак — читающий текст поймёт
       без него, а диктору роль status зачитает саму фразу. */
    var say = function (text, kind) {
      status.textContent = text;
      status.classList.remove('is-error', 'is-ok');
      if (kind) status.classList.add(kind);
    };

    /* Тело запроса собирается по формату из LEAD. Страница и время
       кладутся всегда: по ним в CRM видно, откуда пришла заявка. */
    var buildPayload = function (d) {
      if (LEAD.format === 'bitrix') {
        return {
          fields: {
            TITLE: 'Заявка с сайта «Частные балы» — ' + d.name,
            NAME: d.name,
            COMMENTS: (d.about || 'Без описания') +
                      '\n\nКонтакт: ' + d.contact +
                      '\nСтраница: ' + d.page,
            SOURCE_ID: 'WEB',
            OPENED: 'Y',
            ASSIGNED_BY_ID: 1
          },
          params: { REGISTER_SONET_EVENT: 'Y' }
        };
      }
      return d;
    };

    /* fetch с пределом ожидания. AbortController есть везде, где есть
       fetch, но проверка оставлена: без него запрос уйдёт без таймаута,
       и это лучше, чем отказ отправлять вовсе. */
    var postLead = function (body) {
      var ctrl = window.AbortController ? new AbortController() : null;
      var timer = ctrl ? setTimeout(function () { ctrl.abort(); }, LEAD.timeout) : null;

      return fetch(LEAD.endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
        signal: ctrl ? ctrl.signal : undefined
      }).then(function (res) {
        if (timer) clearTimeout(timer);
        /* fetch не считает 4xx и 5xx ошибкой — проверяем сами,
           иначе «отправлено» показалось бы и на ответе 500. */
        if (!res.ok) {
          var err = new Error('HTTP ' + res.status);
          err.code = res.status;
          throw err;
        }
        return res;
      }).catch(function (e) {
        if (timer) clearTimeout(timer);
        throw e;
      });
    };

    /* Сообщение об ошибке говорит, что делать, а не «что-то пошло не
       так». Телефон и почта берутся из блока контактов на этой же
       странице: одна правка координат — и здесь они тоже верные. */
    var fallbackContacts = function () {
      var tel = document.querySelector('.contact__direct a[href^="tel:"]');
      var mail = document.querySelector('.contact__direct a[href^="mailto:"]');
      var parts = [];
      if (tel) parts.push(tel.textContent.trim());
      if (mail) parts.push(mail.textContent.trim());
      return parts.length ? parts.join(' или ') : '';
    };

    var errorText = function (e) {
      var where = fallbackContacts();
      var tail = where
        ? ' Напишите или позвоните нам напрямую: ' + where + ' — заявку примем так же.'
        : '';

      /* Причины разделены: пользователю важно, чинить ли ему связь
         или ждать нас. Обещать «попробуйте позже» при упавшем сервере
         бессмысленно, если он не знает, что делать сейчас. */
      if (e && e.name === 'AbortError') {
        return 'Ответ не пришёл за 15 секунд — возможно, связь медленная. ' +
               'Попробуйте отправить ещё раз.' + tail;
      }
      if (e && e.code >= 500) {
        return 'Заявка не ушла: сторона приёма не отвечает. ' +
               'Это на нашей стороне.' + tail;
      }
      if (e && e.code) {
        return 'Заявка не ушла (ошибка ' + e.code + ').' + tail;
      }
      /* Сюда попадает и обрыв сети, и блокировка запроса расширением,
         и промах CORS — по внешним признакам они неразличимы. */
      return 'Заявка не ушла — похоже, нет связи с сервером. ' +
             'Проверьте интернет и попробуйте ещё раз.' + tail;
    };

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (sending) return;             /* двойной Enter по полю */

      var name = form.elements.name.value.trim();
      var contact = form.elements.contact.value.trim();
      var about = form.elements.about.value.trim();
      var trap = form.elements.website ? form.elements.website.value : '';
      var consent = form.elements.consent;

      /* Ловушка сработала: отвечаем как при успехе и никуда не шлём.
         Бот не должен узнать, что его отсеяли. */
      if (trap) {
        say('Спасибо, ' + (name || 'мы получили заявку') +
            '. Мы свяжемся с вами в ближайшее время.', 'is-ok');
        form.reset();
        return;
      }

      if (!name || !contact) {
        say('Заполните имя и контакт — без них мы не сможем ответить.', 'is-error');
        (name ? form.elements.contact : form.elements.name).focus();
        return;
      }
      /* Проверка согласия своя, а не штатная: novalidate на форме
         отключает встроенные подсказки браузера, и без этой ветки
         required на галочке ничего бы не сделал. */
      if (consent && !consent.checked) {
        say('Отметьте согласие на обработку данных — без него мы не вправе ' +
            'принять заявку.', 'is-error');
        consent.focus();
        return;
      }

      /* Приёмник ещё не подключён. Честный ответ вместо ложного
         «спасибо»: человек увидит, что связаться нужно иначе. */
      if (!LEAD.endpoint) {
        say('Форма пока не подключена к приёму заявок. ' +
            'Напишите или позвоните нам: ' + (fallbackContacts() || 'см. контакты выше') +
            ' — мы ответим.', 'is-error');
        return;
      }

      sending = true;
      if (submitBtn) {
        submitBtn.classList.add('is-sending');
        submitBtn.disabled = true;     /* и класс, и атрибут: правило в CSS ловит оба */
        submitBtn.textContent = 'отправляем';
      }
      say('Отправляем заявку…');

      postLead(buildPayload({
        name: name,
        contact: contact,
        about: about,
        page: location.href,
        ts: new Date().toISOString()
      })).then(function () {
        say('Спасибо, ' + name + '. Заявка у нас — позвоним или напишем ' +
            'в ближайшее время.', 'is-ok');
        form.reset();
      }).catch(function (err) {
        /* Введённое НЕ стираем: человеку не придётся набирать заново,
           повторная отправка — один клик. */
        say(errorText(err), 'is-error');
      }).then(function () {
        /* Возврат кнопки в оба исхода — иначе после ошибки она
           осталась бы навсегда выключенной. */
        sending = false;
        if (submitBtn) {
          submitBtn.classList.remove('is-sending');
          submitBtn.disabled = false;
          submitBtn.textContent = btnLabel;
        }
      });
    });
  }

  /* ---------- 8. Фоновое видео героя ---------- */
  var heroVideo = document.querySelector('.hero__video');

  if (heroVideo) {
    /* Показываем элемент, когда в нём есть что показывать: первый кадр
       петли — или постер, если ни один источник не нашёлся. Без этого
       .hero__video так и остался бы на opacity: 0, и в кадре стояла бы
       голая подложка вместо кадра бала. */
    var showVideo = function () { heroVideo.setAttribute('data-ready', ''); };

    if (heroVideo.readyState >= 2) {
      showVideo();
    } else {
      heroVideo.addEventListener('loadeddata', showVideo, { once: true });
    }

    /* Медленный отъезд камеры (1.12 → 1 бесконечным yoyo) снят этапом 15
       вместе с токеном --dur-ambient. Твин и так не жил: герой на период
       доработки стоит фотографией, <video> в разметке закомментирован,
       и весь этот раздел не выполняется вовсе. Возвращать петлю масштаба
       вместе с видео не следует — система такого движения не знает.

       Наблюдатель за героем остаётся и теперь отвечает только за
       воспроизведение: за кадром петля не крутится впустую. Заводится
       он сразу, а воспроизведение подключается к нему, когда появляется
       что играть. */
    var heroPlayable = false;
    var heroCanObserve = 'IntersectionObserver' in window;
    // Пока наблюдатель не отчитался, считаем героя видимым: он в первом экране
    var heroVisible = true;

    if (heroCanObserve) {
      new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          heroVisible = entry.isIntersecting;
          if (heroVisible) {
            if (heroPlayable) heroVideo.play().catch(function () {});
          } else {
            if (heroPlayable) heroVideo.pause();
          }
        });
      }, { threshold: 0.1 }).observe(heroVideo);
    }

    /* Ждём перебора источников (раздел 0c): до него src пуст, и play()
       ушёл бы вхолостую. Исход «постер» — тоже исход: показываем кадр
       и петлёй больше не занимаемся. */
    initVideoSources(heroVideo).then(function (found) {
      if (!found) {
        showVideo();
        return;
      }

      if (reduceMotion) {
        // Статичный кадр вместо цикла: видео нужно ради глубины, не движения
        heroVideo.removeAttribute('loop');
        heroVideo.pause();
        return;
      }

      // Дальше воспроизведением распоряжается наблюдатель выше
      heroPlayable = true;

      // Источники доехали, когда герой уже уехал с экрана, — не запускаем:
      // наблюдатель сам включит петлю, когда пользователь вернётся наверх
      if (!heroVisible) return;

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
    });
  }

})();
