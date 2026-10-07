/* @ds-bundle: {"format":4,"namespace":"ChastnyeBalyDesignSystem_059c2e","components":[{"name":"Button","sourcePath":"components/core/Button.jsx"},{"name":"FormField","sourcePath":"components/core/FormField.jsx"},{"name":"SectionLabel","sourcePath":"components/core/SectionLabel.jsx"},{"name":"TextLink","sourcePath":"components/core/TextLink.jsx"},{"name":"CTABand","sourcePath":"components/layout/CTABand.jsx"},{"name":"Logo","sourcePath":"components/layout/Logo.jsx"},{"name":"QuoteBand","sourcePath":"components/layout/QuoteBand.jsx"},{"name":"SegmentCard","sourcePath":"components/layout/SegmentCard.jsx"},{"name":"SiteHeader","sourcePath":"components/layout/SiteHeader.jsx"},{"name":"StepItem","sourcePath":"components/layout/StepItem.jsx"},{"name":"Wordmark","sourcePath":"components/layout/Wordmark.jsx"}],"sourceHashes":{"components/core/Button.jsx":"579106fb20bc","components/core/FormField.jsx":"51560fc1b124","components/core/SectionLabel.jsx":"969f7a6d5731","components/core/TextLink.jsx":"279a56005e2f","components/layout/CTABand.jsx":"a394c9c78a91","components/layout/Logo.jsx":"e36c5be2274d","components/layout/QuoteBand.jsx":"bb1474b6e532","components/layout/SegmentCard.jsx":"0b7c8922bf5a","components/layout/SiteHeader.jsx":"2f71f9bdaad2","components/layout/StepItem.jsx":"24da556aa58f","components/layout/Wordmark.jsx":"1d6faba9f894","ui_kits/site/Contact.jsx":"b9696767305e","ui_kits/site/Evenings.jsx":"45b452d586d2","ui_kits/site/Home.jsx":"10ade2e9ac8d","ui_kits/site/Process.jsx":"0b86b981cb4d","ui_kits/site/Shell.jsx":"ce4c94db6eee"},"inlinedExternals":[],"unexposedExports":[]} */

(() => {

const __ds_ns = (window.ChastnyeBalyDesignSystem_059c2e = window.ChastnyeBalyDesignSystem_059c2e || {});

const __ds_scope = {};

(__ds_ns.__errors = __ds_ns.__errors || []);

// components/core/Button.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/* Основная кнопка: обводка 1px greige без заливки и без скруглений.
   Hover — полная инверсия: заливка greige, текст цветом фона. 240ms ease. */
function Button({
  children,
  size = 'md',
  as,
  href,
  disabled = false,
  onClick,
  style,
  ...rest
}) {
  const [hover, setHover] = React.useState(false);
  const on = hover && !disabled;
  const Tag = as || (href ? 'a' : 'button');
  return /*#__PURE__*/React.createElement(Tag, _extends({
    href: href,
    disabled: Tag === 'button' ? disabled : undefined,
    onClick: disabled ? undefined : onClick,
    onMouseEnter: () => setHover(true),
    onMouseLeave: () => setHover(false),
    style: {
      display: 'inline-block',
      boxSizing: 'border-box',
      minHeight: 'var(--hit-min)',
      padding: size === 'lg' ? 'var(--pad-button-lg)' : 'var(--pad-button)',
      border: 'var(--border-width) solid var(--border-strong)',
      borderRadius: 'var(--radius)',
      background: on ? 'var(--color-greige)' : 'transparent',
      color: on ? 'var(--text-inverse)' : 'var(--greige-90)',
      fontFamily: 'var(--font-sans)',
      fontSize: 'var(--nav-size)',
      fontWeight: 600,
      letterSpacing: 'var(--button-tracking)',
      textTransform: 'uppercase',
      textDecoration: 'none',
      textAlign: 'center',
      cursor: disabled ? 'default' : 'pointer',
      opacity: disabled ? 0.35 : 1,
      transition: 'var(--transition-hover)',
      ...style
    }
  }, rest), children);
}
Object.assign(__ds_scope, { Button });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Button.jsx", error: String((e && e.message) || e) }); }

// components/core/FormField.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/* Поле формы: только нижняя линия, без рамок и заливок.
   Метка сверху капителью — всегда видна, плейсхолдер её не заменяет. */
function FormField({
  label,
  placeholder,
  value,
  onChange,
  state = 'rest',
  hint,
  type = 'text',
  name,
  style,
  ...rest
}) {
  const line = state === 'error' ? 'var(--field-line-error)' : state === 'focus' ? 'var(--field-line-focus)' : 'var(--field-line-rest)';
  return /*#__PURE__*/React.createElement("label", _extends({
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 10,
      ...style
    }
  }, rest), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-sans)',
      fontSize: 'var(--label-size)',
      fontWeight: 600,
      letterSpacing: 'var(--label-tracking)',
      textTransform: 'uppercase',
      color: state === 'error' ? 'var(--color-accent)' : 'var(--greige-40)'
    }
  }, label), /*#__PURE__*/React.createElement("input", {
    type: type,
    name: name,
    value: value,
    placeholder: placeholder,
    onChange: onChange,
    style: {
      appearance: 'none',
      background: 'transparent',
      border: 0,
      borderBottom: 'var(--border-width) solid ' + line,
      borderRadius: 'var(--radius)',
      padding: 'var(--pad-field)',
      fontFamily: 'var(--font-sans)',
      fontSize: 15,
      fontWeight: 500,
      letterSpacing: '0.3px',
      color: 'var(--greige-90)',
      outline: 'none',
      transition: 'var(--transition-hover)'
    }
  }), hint && /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-sans)',
      fontSize: 'var(--label-size)',
      fontWeight: 500,
      letterSpacing: '0.3px',
      color: state === 'error' ? 'var(--color-accent)' : 'var(--text-muted)'
    }
  }, hint));
}
Object.assign(__ds_scope, { FormField });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/FormField.jsx", error: String((e && e.message) || e) }); }

// components/core/SectionLabel.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/* Метка секции и нумерация: Гротеск 500, трекинг 2.34px, 13px.
   Единственное место, где терракота появляется в тексте.
   Поверх Terra терракота не читается — там метка идёт greige 70%. */
function SectionLabel({
  number,
  children,
  tone = 'accent',
  style,
  ...rest
}) {
  const text = [number, children].filter(Boolean);
  return /*#__PURE__*/React.createElement("div", _extends({
    style: {
      fontFamily: 'var(--font-sans)',
      fontSize: 'var(--number-size)',
      fontWeight: 'var(--number-weight)',
      lineHeight: 'var(--number-leading)',
      letterSpacing: 'var(--number-tracking)',
      color: tone === 'accent' ? 'var(--text-accent)' : 'rgba(171,167,154,0.7)',
      ...style
    }
  }, rest), text.length === 2 ? number + ' — ' + children : text[0]);
}
Object.assign(__ds_scope, { SectionLabel });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/SectionLabel.jsx", error: String((e && e.message) || e) }); }

// components/core/TextLink.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/* Текстовая ссылка: антиква строчными, стрелка слева, подчёркивание.
   Hover — линия растёт до 100%. */
function TextLink({
  children,
  href,
  onClick,
  size,
  showArrow = true,
  tone = 'default',
  style,
  ...rest
}) {
  const [hover, setHover] = React.useState(false);
  const ink = tone === 'on-brand' ? 'var(--greige-90)' : 'var(--greige-90)';
  return /*#__PURE__*/React.createElement("a", _extends({
    href: href,
    onClick: onClick,
    onMouseEnter: () => setHover(true),
    onMouseLeave: () => setHover(false),
    style: {
      display: 'inline-flex',
      flexDirection: 'column',
      alignSelf: 'flex-start',
      gap: 6,
      color: ink,
      textDecoration: 'none',
      cursor: 'pointer',
      ...style
    }
  }, rest), /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: 12
    }
  }, showArrow && /*#__PURE__*/React.createElement("svg", {
    width: "26",
    height: "14",
    viewBox: "0 0 26 14",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: "1.2",
    style: {
      flexShrink: 0
    }
  }, /*#__PURE__*/React.createElement("path", {
    d: "M0 7h24M18 1l6 6-6 6"
  })), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-display)',
      fontSize: size || 'var(--link-size)',
      lineHeight: 1,
      letterSpacing: 'var(--link-tracking)'
    }
  }, children)), /*#__PURE__*/React.createElement("span", {
    style: {
      height: 'var(--border-width)',
      width: hover ? '100%' : '62%',
      background: 'var(--greige-40)',
      transition: 'width var(--duration-line) var(--easing)'
    }
  }));
}
Object.assign(__ds_scope, { TextLink });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/TextLink.jsx", error: String((e && e.message) || e) }); }

// components/layout/CTABand.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/* Финальная полоса на Terra: метка, крупный H1 капителью, кнопка справа.
   Terra открывает и закрывает страницу. */
function CTABand({
  label,
  number,
  title,
  action = 'Оставить заявку',
  onAction,
  style,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("section", _extends({
    style: {
      display: 'flex',
      alignItems: 'flex-end',
      justifyContent: 'space-between',
      gap: 48,
      padding: 'var(--pad-band-v) var(--page-pad-1200)',
      background: 'var(--surface-brand)',
      ...style
    }
  }, rest), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 26
    }
  }, (label || number) && /*#__PURE__*/React.createElement(__ds_scope.SectionLabel, {
    number: number,
    tone: "on-brand"
  }, label), /*#__PURE__*/React.createElement("h2", {
    style: {
      margin: 0,
      fontFamily: 'var(--h1-family)',
      fontWeight: 'var(--h1-weight)',
      fontSize: 92,
      lineHeight: 'var(--h1-leading)',
      letterSpacing: 'var(--h1-tracking)',
      textTransform: 'uppercase',
      color: 'rgba(171,167,154,0.95)'
    }
  }, title)), /*#__PURE__*/React.createElement(__ds_scope.Button, {
    size: "lg",
    onClick: onAction,
    style: {
      flexShrink: 0
    }
  }, action));
}
Object.assign(__ds_scope, { CTABand });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/layout/CTABand.jsx", error: String((e && e.message) || e) }); }

// components/layout/Logo.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/* Логотип «Plyaskin Events» — PNG с прозрачным фоном, знак набран золотисто-охристой
   антиквой в две строки. Присланный файл — единственная версия знака.

   Путь к файлу считается от тега <script src=".../_ds_bundle.js">, чтобы знак
   находился с любой страницы-потребителя; при необходимости передайте src вручную. */
const LOGO_PATH = 'assets/logo-plyaskin-events.png';
function resolveLogo() {
  try {
    const tag = Array.from(document.querySelectorAll('script[src]')).find(s => s.getAttribute('src').indexOf('_ds_bundle.js') >= 0);
    if (tag) return new URL(LOGO_PATH, new URL(tag.src, document.baseURI)).href;
  } catch (e) {}
  return LOGO_PATH;
}
function Logo({
  height = 56,
  src,
  alt = 'Plyaskin Events',
  style,
  ...rest
}) {
  const url = React.useMemo(() => src || resolveLogo(), [src]);
  return /*#__PURE__*/React.createElement("img", _extends({
    src: url,
    alt: alt,
    style: {
      height,
      width: 'auto',
      display: 'block',
      ...style
    }
  }, rest));
}
Object.assign(__ds_scope, { Logo });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/layout/Logo.jsx", error: String((e && e.message) || e) }); }

// components/layout/QuoteBand.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/* Полоса-передышка на Ash: врезка курсивом сверху, крупная антиква под ней.
   Ставится между двумя Ink-секциями. */
function QuoteBand({
  eyebrow,
  children,
  surface = 'rest',
  style,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("section", _extends({
    style: {
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      textAlign: 'center',
      gap: 26,
      padding: 'var(--pad-band-v) var(--page-pad-1200)',
      background: surface === 'brand' ? 'var(--surface-brand)' : surface === 'ink' ? 'var(--surface-page)' : 'var(--surface-rest)',
      ...style
    }
  }, rest), eyebrow && /*#__PURE__*/React.createElement("div", {
    style: {
      fontFamily: 'var(--micro-family)',
      fontStyle: 'var(--micro-style)',
      fontSize: 'var(--micro-size)',
      lineHeight: 'var(--micro-leading)',
      letterSpacing: 'var(--micro-tracking)',
      color: 'var(--greige-90)'
    }
  }, eyebrow), /*#__PURE__*/React.createElement("blockquote", {
    style: {
      margin: 0,
      maxWidth: 'var(--measure-quote)',
      fontFamily: 'var(--h2-family)',
      fontWeight: 'var(--h2-weight)',
      fontSize: 76,
      lineHeight: 0.85,
      letterSpacing: -4,
      color: 'var(--text-title)'
    }
  }, children));
}
Object.assign(__ds_scope, { QuoteBand });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/layout/QuoteBand.jsx", error: String((e && e.message) || e) }); }

// components/layout/SegmentCard.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/* Карточка сегмента. Порядок сверху вниз всегда один:
   номер → название → врезка курсивом → описание.
   Поверх Terra прозрачность текста поднимается на шаг — фон светлее. */
function SegmentCard({
  number,
  title,
  subtitle,
  children,
  surface = 'card',
  style,
  ...rest
}) {
  const onBrand = surface === 'brand';
  return /*#__PURE__*/React.createElement("article", _extends({
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 22,
      minHeight: 300,
      padding: 'var(--pad-card)',
      background: onBrand ? 'var(--surface-brand)' : 'var(--surface-card)',
      borderRadius: 'var(--radius)',
      ...style
    }
  }, rest), number && /*#__PURE__*/React.createElement(__ds_scope.SectionLabel, {
    number: number,
    tone: onBrand ? 'on-brand' : 'accent'
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 10
    }
  }, /*#__PURE__*/React.createElement("h3", {
    style: {
      margin: 0,
      fontFamily: 'var(--h3-family)',
      fontWeight: 'var(--h3-weight)',
      fontSize: 40,
      lineHeight: 'var(--h3-leading)',
      letterSpacing: 'var(--h3-tracking)',
      textTransform: 'uppercase',
      color: onBrand ? 'var(--greige-90)' : 'var(--text-subtitle)'
    }
  }, title), subtitle && /*#__PURE__*/React.createElement("div", {
    style: {
      fontFamily: 'var(--micro-family)',
      fontStyle: 'var(--micro-style)',
      fontSize: 'var(--micro-size)',
      lineHeight: 'var(--micro-leading)',
      letterSpacing: 'var(--micro-tracking)',
      color: 'var(--greige-90)'
    }
  }, subtitle)), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      fontFamily: 'var(--text-family)',
      fontSize: 'var(--text-size)',
      fontWeight: 'var(--text-weight)',
      lineHeight: 1.7,
      letterSpacing: 'var(--text-tracking)',
      textTransform: 'uppercase',
      color: onBrand ? 'var(--text-on-brand-body)' : 'var(--text-body)'
    }
  }, children));
}
Object.assign(__ds_scope, { SegmentCard });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/layout/SegmentCard.jsx", error: String((e && e.message) || e) }); }

// components/layout/StepItem.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/* Шаг подготовки: линия сверху, номер, название капителью, описание.
   Раскладка 4+4+4 в колоночной сетке. */
function StepItem({
  number,
  title,
  children,
  style,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("div", _extends({
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 20,
      borderTop: 'var(--border-width) solid var(--line-section)',
      paddingTop: 'var(--space-24)',
      ...style
    }
  }, rest), number && /*#__PURE__*/React.createElement(__ds_scope.SectionLabel, {
    number: number
  }), /*#__PURE__*/React.createElement("h3", {
    style: {
      margin: 0,
      fontFamily: 'var(--h3-family)',
      fontWeight: 'var(--h3-weight)',
      fontSize: 34,
      lineHeight: 'var(--h3-leading)',
      letterSpacing: 'var(--h3-tracking)',
      textTransform: 'uppercase',
      color: 'var(--text-subtitle)'
    }
  }, title), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      fontFamily: 'var(--text-family)',
      fontSize: 'var(--text-size)',
      fontWeight: 'var(--text-weight)',
      lineHeight: 1.7,
      letterSpacing: 'var(--text-tracking)',
      textTransform: 'uppercase',
      color: 'var(--text-body)'
    }
  }, children));
}
Object.assign(__ds_scope, { StepItem });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/layout/StepItem.jsx", error: String((e && e.message) || e) }); }

// components/layout/Wordmark.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/* Логотипа в исходных материалах нет — знак бренда это набор антиквой.
   Значения сняты с шапки макета: Old Standard TT 24px, трекинг −1px. */
function Wordmark({
  size = 24,
  tone = 'default',
  style,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("span", _extends({
    style: {
      fontFamily: 'var(--font-display)',
      fontWeight: 400,
      fontSize: size,
      lineHeight: 1,
      letterSpacing: size >= 60 ? '-4px' : '-1px',
      whiteSpace: 'nowrap',
      color: tone === 'on-brand' ? 'rgba(171,167,154,0.95)' : 'var(--greige-90)',
      ...style
    }
  }, rest), "\u0427\u0430\u0441\u0442\u043D\u044B\u0435\xA0\u0431\u0430\u043B\u044B");
}
Object.assign(__ds_scope, { Wordmark });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/layout/Wordmark.jsx", error: String((e && e.message) || e) }); }

// components/layout/SiteHeader.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/* Шапка: прозрачная поверх hero, при скролле — заливка Ink.
   Пункты 50% непрозрачности, активный и hover — 90%. */
function SiteHeader({
  items = [],
  active,
  phone,
  surface = 'transparent',
  onNavigate,
  style,
  ...rest
}) {
  const [hover, setHover] = React.useState(null);
  const onBrand = surface === 'brand';
  return /*#__PURE__*/React.createElement("header", _extends({
    style: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      gap: 32,
      padding: 'var(--pad-header)',
      background: surface === 'ink' ? 'var(--surface-page)' : onBrand ? 'var(--surface-brand)' : 'transparent',
      ...style
    }
  }, rest), /*#__PURE__*/React.createElement(__ds_scope.Wordmark, {
    tone: onBrand ? 'on-brand' : 'default'
  }), /*#__PURE__*/React.createElement("nav", {
    style: {
      display: 'flex',
      gap: 34
    }
  }, items.map(item => {
    const lit = item === active || item === hover;
    return /*#__PURE__*/React.createElement("a", {
      key: item,
      href: "#",
      onClick: e => {
        e.preventDefault();
        if (onNavigate) onNavigate(item);
      },
      onMouseEnter: () => setHover(item),
      onMouseLeave: () => setHover(null),
      style: {
        fontFamily: 'var(--font-sans)',
        fontSize: 'var(--nav-size)',
        fontWeight: 600,
        letterSpacing: 'var(--nav-tracking)',
        textTransform: 'uppercase',
        textDecoration: 'none',
        whiteSpace: 'nowrap',
        color: lit ? 'var(--greige-90)' : onBrand ? 'var(--greige-65)' : 'var(--greige-50)',
        transition: 'var(--transition-hover)'
      }
    }, item);
  })), phone && /*#__PURE__*/React.createElement("a", {
    href: 'tel:' + String(phone).replace(/[^+\d]/g, ''),
    style: {
      fontFamily: 'var(--font-sans)',
      fontSize: 'var(--nav-size)',
      fontWeight: 600,
      letterSpacing: 'var(--nav-tracking)',
      textTransform: 'uppercase',
      textDecoration: 'none',
      whiteSpace: 'nowrap',
      color: onBrand ? 'rgba(171,167,154,0.95)' : 'var(--greige-90)'
    }
  }, phone));
}
Object.assign(__ds_scope, { SiteHeader });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/layout/SiteHeader.jsx", error: String((e && e.message) || e) }); }

// ui_kits/site/Contact.jsx
try { (() => {
const {
  SectionLabel,
  FormField,
  Button
} = window.ChastnyeBalyDesignSystem_059c2e;
function ContactScreen() {
  const [form, setForm] = React.useState({
    name: '',
    phone: '',
    mail: ''
  });
  const [focused, setFocused] = React.useState(null);
  const [error, setError] = React.useState(null);
  const [sent, setSent] = React.useState(false);
  const set = k => e => setForm({
    ...form,
    [k]: e.target.value
  });
  const state = k => error === k ? 'error' : focused === k ? 'focus' : 'rest';
  const submit = () => {
    if (!form.name.trim()) return setError('name');
    if (!form.mail.includes('@')) return setError('mail');
    setError(null);
    setSent(true);
  };
  return /*#__PURE__*/React.createElement(Section, {
    style: {
      paddingTop: 96
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(12, minmax(0,1fr))',
      gap: 'var(--grid-gap)',
      alignItems: 'start'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      gridColumn: 'span 5',
      display: 'flex',
      flexDirection: 'column',
      gap: 34
    }
  }, /*#__PURE__*/React.createElement(SectionLabel, {
    number: "05"
  }, "\u0421\u0412\u042F\u0417\u0410\u0422\u042C\u0421\u042F"), /*#__PURE__*/React.createElement("h1", {
    style: {
      margin: 0,
      fontFamily: 'var(--h2-family)',
      fontWeight: 400,
      fontSize: 88,
      lineHeight: 0.8,
      letterSpacing: '-5px',
      color: 'var(--text-title)'
    }
  }, "\u0420\u0430\u0441\u0441\u043A\u0430\u0436\u0438\u0442\u0435", /*#__PURE__*/React.createElement("br", null), "\u043E \u0432\u0435\u0447\u0435\u0440\u0435"), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      fontFamily: 'var(--text-family)',
      fontSize: 'var(--text-size)',
      fontWeight: 600,
      lineHeight: 1.7,
      letterSpacing: 'var(--text-tracking)',
      textTransform: 'uppercase',
      color: 'var(--text-body)'
    }
  }, "\u041C\u044B \u043D\u0430\u0447\u0438\u043D\u0430\u0435\u043C \u0441 \u0440\u0430\u0437\u0433\u043E\u0432\u043E\u0440\u0430 \u2014 \u043E\u0441\u0442\u0430\u0432\u044C\u0442\u0435 \u043A\u043E\u043D\u0442\u0430\u043A\u0442\u044B, \u0438 \u043C\u044B \u043F\u043E\u0437\u0432\u043E\u043D\u0438\u043C.")), /*#__PURE__*/React.createElement("div", {
    style: {
      gridColumn: '7 / span 6'
    }
  }, sent ? /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 18,
      borderTop: '1px solid var(--line-section)',
      paddingTop: 34
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      fontFamily: 'var(--micro-family)',
      fontStyle: 'italic',
      fontSize: 'var(--micro-size)',
      letterSpacing: 'var(--micro-tracking)',
      lineHeight: 1,
      color: 'var(--greige-90)'
    }
  }, "\u0441\u043F\u0430\u0441\u0438\u0431\u043E, ", form.name || 'мы получили заявку'), /*#__PURE__*/React.createElement("div", {
    style: {
      fontFamily: 'var(--h2-family)',
      fontSize: 56,
      lineHeight: 0.85,
      letterSpacing: '-3px',
      color: 'var(--text-title)'
    }
  }, "\u041C\u044B \u043F\u043E\u0437\u0432\u043E\u043D\u0438\u043C", /*#__PURE__*/React.createElement("br", null), "\u0432 \u0442\u0435\u0447\u0435\u043D\u0438\u0435 \u0434\u043D\u044F")) : /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 34
    }
  }, /*#__PURE__*/React.createElement(FormField, {
    label: "\u0418\u043C\u044F",
    placeholder: "\u041A\u0430\u043A \u043A \u0432\u0430\u043C \u043E\u0431\u0440\u0430\u0449\u0430\u0442\u044C\u0441\u044F",
    value: form.name,
    onChange: set('name'),
    state: state('name'),
    hint: error === 'name' ? 'Заполните поле' : undefined,
    onFocus: () => setFocused('name'),
    onBlur: () => setFocused(null)
  }), /*#__PURE__*/React.createElement(FormField, {
    label: "\u0422\u0435\u043B\u0435\u0444\u043E\u043D",
    placeholder: "+7",
    value: form.phone,
    onChange: set('phone'),
    state: state('phone'),
    onFocus: () => setFocused('phone'),
    onBlur: () => setFocused(null)
  }), /*#__PURE__*/React.createElement(FormField, {
    label: "E-mail",
    placeholder: "ivanov@",
    value: form.mail,
    onChange: set('mail'),
    state: state('mail'),
    hint: error === 'mail' ? 'Проверьте адрес' : undefined,
    onFocus: () => setFocused('mail'),
    onBlur: () => setFocused(null)
  }), /*#__PURE__*/React.createElement(Button, {
    onClick: submit,
    style: {
      alignSelf: 'flex-start'
    }
  }, "\u041E\u0441\u0442\u0430\u0432\u0438\u0442\u044C \u0437\u0430\u044F\u0432\u043A\u0443")))));
}
Object.assign(window, {
  ContactScreen
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/site/Contact.jsx", error: String((e && e.message) || e) }); }

// ui_kits/site/Evenings.jsx
try { (() => {
const {
  SectionLabel,
  SegmentCard,
  CTABand
} = window.ChastnyeBalyDesignSystem_059c2e;
function EveningsScreen({
  onNavigate
}) {
  return /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(Section, {
    style: {
      paddingTop: 96
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 72
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 34
    }
  }, /*#__PURE__*/React.createElement(SectionLabel, {
    number: "03"
  }, "\u0412\u0415\u0427\u0415\u0420\u0410"), /*#__PURE__*/React.createElement("h1", {
    style: {
      margin: 0,
      fontFamily: 'var(--h1-family)',
      fontWeight: 700,
      fontSize: 130,
      lineHeight: 1,
      letterSpacing: 0,
      textTransform: 'uppercase',
      color: 'var(--text-title)'
    }
  }, "\u0412\u0435\u0447\u0435\u0440\u0430")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(2, minmax(0,1fr))',
      gap: 'var(--grid-gap)'
    }
  }, /*#__PURE__*/React.createElement(SegmentCard, {
    number: "01",
    title: "\u0427\u0430\u0441\u0442\u043D\u044B\u0439 \u0431\u0430\u043B",
    subtitle: "\u0434\u043B\u044F \u0441\u0435\u043C\u044C\u0438 \u0438 \u0431\u043B\u0438\u0437\u043A\u0438\u0445"
  }, "\u0421\u0432\u0430\u0434\u044C\u0431\u0430, \u044E\u0431\u0438\u043B\u0435\u0439, \u0434\u0435\u043D\u044C \u0440\u043E\u0436\u0434\u0435\u043D\u0438\u044F \u2014 \u0441\u043E\u0431\u044B\u0442\u0438\u0435, \u0437\u0430 \u043A\u043E\u0442\u043E\u0440\u044B\u043C \u0441\u0442\u043E\u0438\u0442 \u0446\u0435\u043B\u0430\u044F \u0438\u0441\u0442\u043E\u0440\u0438\u044F \u0441\u0435\u043C\u044C\u0438."), /*#__PURE__*/React.createElement(SegmentCard, {
    number: "02",
    title: "\u041A\u043E\u0440\u043F\u043E\u0440\u0430\u0442\u0438\u0432\u043D\u044B\u0439 \u0431\u0430\u043B",
    subtitle: "\u0434\u043B\u044F \u043A\u043E\u043C\u043F\u0430\u043D\u0438\u0438 \u0438 \u043F\u0430\u0440\u0442\u043D\u0451\u0440\u043E\u0432",
    surface: "brand"
  }, "\u0413\u043E\u0434\u043E\u0432\u0449\u0438\u043D\u0430 \u043A\u043E\u043C\u043F\u0430\u043D\u0438\u0438, \u043D\u043E\u0432\u043E\u0433\u043E\u0434\u043D\u0438\u0439 \u043F\u0440\u0438\u0451\u043C, \u0432\u0435\u0447\u0435\u0440 \u0432 \u0447\u0435\u0441\u0442\u044C \u043F\u0430\u0440\u0442\u043D\u0451\u0440\u043E\u0432.")), /*#__PURE__*/React.createElement(MediaPlaceholder, {
    note: "\u0413\u0430\u043B\u0435\u0440\u0435\u044F \u043F\u0440\u043E\u0448\u0435\u0434\u0448\u0438\u0445 \u0432\u0435\u0447\u0435\u0440\u043E\u0432 \u2014 \u0444\u043E\u0442\u043E\u0433\u0440\u0430\u0444\u0438\u0439 \u0432 \u0438\u0441\u0445\u043E\u0434\u043D\u044B\u0445 \u043C\u0430\u0442\u0435\u0440\u0438\u0430\u043B\u0430\u0445 \u043D\u0435\u0442"
  }))), /*#__PURE__*/React.createElement(CTABand, {
    number: "05",
    label: "\u0421\u0412\u042F\u0417\u0410\u0422\u042C\u0421\u042F",
    title: /*#__PURE__*/React.createElement(React.Fragment, null, "\u0420\u0430\u0441\u0441\u043A\u0430\u0436\u0438\u0442\u0435", /*#__PURE__*/React.createElement("br", null), "\u043E \u0432\u0435\u0447\u0435\u0440\u0435"),
    onAction: () => onNavigate('Связаться')
  }));
}
Object.assign(window, {
  EveningsScreen
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/site/Evenings.jsx", error: String((e && e.message) || e) }); }

// ui_kits/site/Home.jsx
try { (() => {
const {
  SectionLabel,
  TextLink,
  SegmentCard,
  StepItem,
  QuoteBand,
  CTABand
} = window.ChastnyeBalyDesignSystem_059c2e;
function HomeScreen({
  onNavigate
}) {
  return /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("div", {
    style: {
      background: 'var(--surface-brand)',
      paddingLeft: 'var(--page-pad-1200)',
      paddingRight: 'var(--page-pad-1200)',
      paddingTop: 132,
      paddingBottom: 88,
      display: 'flex',
      flexDirection: 'column',
      gap: 34,
      minHeight: 520,
      boxSizing: 'border-box'
    }
  }, /*#__PURE__*/React.createElement(SectionLabel, {
    number: "01",
    tone: "on-brand"
  }, "\u0427\u0410\u0421\u0422\u041D\u042B\u0415 \u0411\u0410\u041B\u042B"), /*#__PURE__*/React.createElement("h1", {
    style: {
      margin: 0,
      fontFamily: 'var(--h2-family)',
      fontWeight: 400,
      fontSize: 118,
      lineHeight: 0.8,
      letterSpacing: '-6px',
      color: 'rgba(171,167,154,0.95)'
    }
  }, "\u0412\u0430\u0448\u0430 \u0438\u0441\u0442\u043E\u0440\u0438\u044F.", /*#__PURE__*/React.createElement("br", null), "\u0412\u0430\u0448 \u0432\u0435\u0447\u0435\u0440."), /*#__PURE__*/React.createElement(TextLink, {
    onClick: () => onNavigate('Связаться')
  }, "\u043E\u0431\u0441\u0443\u0434\u0438\u0442\u044C \u0432\u0435\u0447\u0435\u0440")), /*#__PURE__*/React.createElement(Section, null, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 72
    }
  }, /*#__PURE__*/React.createElement(SectionHead, {
    number: "02",
    label: "\u041F\u041E\u0414\u0413\u041E\u0422\u041E\u0412\u041A\u0410",
    title: /*#__PURE__*/React.createElement(React.Fragment, null, "\u041A\u0430\u043A \u043C\u044B \u0433\u043E\u0442\u043E\u0432\u0438\u043C", /*#__PURE__*/React.createElement("br", null), "\u0432\u0430\u0448 \u0432\u0435\u0447\u0435\u0440"),
    lead: "\u041C\u044B \u043D\u0435 \u043D\u0430\u0447\u0438\u043D\u0430\u0435\u043C \u0441 \u0430\u043D\u043A\u0435\u0442\u044B \u0438 \u043D\u0435 \u0437\u0430\u043A\u0430\u043D\u0447\u0438\u0432\u0430\u0435\u043C \u0434\u043E\u0433\u043E\u0432\u043E\u0440\u043E\u043C. \u041C\u044B \u043D\u0430\u0447\u0438\u043D\u0430\u0435\u043C \u0441 \u0440\u0430\u0437\u0433\u043E\u0432\u043E\u0440\u0430."
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(3, minmax(0,1fr))',
      gap: 'var(--grid-gap)'
    }
  }, /*#__PURE__*/React.createElement(StepItem, {
    number: "01",
    title: "\u0420\u0430\u0437\u0433\u043E\u0432\u043E\u0440"
  }, "\u0412\u044B \u0440\u0430\u0441\u0441\u043A\u0430\u0437\u044B\u0432\u0430\u0435\u0442\u0435 \u043E \u0441\u0432\u043E\u0451\u043C \u0432\u0435\u0447\u0435\u0440\u0435 \u2014 \u0434\u043B\u044F \u043A\u043E\u0433\u043E \u043E\u043D, \u043F\u043E\u0447\u0435\u043C\u0443 \u0438\u043C\u0435\u043D\u043D\u043E \u0431\u0430\u043B, \u0447\u0442\u043E \u0434\u043B\u044F \u0432\u0430\u0441 \u0432\u0430\u0436\u043D\u043E."), /*#__PURE__*/React.createElement(StepItem, {
    number: "02",
    title: "\u0421\u0446\u0435\u043D\u0430\u0440\u0438\u0439"
  }, "\u041C\u044B \u0441\u043E\u0431\u0438\u0440\u0430\u0435\u043C \u0432\u0435\u0447\u0435\u0440 \u0438\u0437 \u0442\u043E\u0433\u043E, \u0447\u0442\u043E \u0443\u0441\u043B\u044B\u0448\u0430\u043B\u0438: \u043C\u0443\u0437\u044B\u043A\u0430, \u0442\u0430\u043D\u0446\u044B, \u043F\u043E\u0440\u044F\u0434\u043E\u043A, \u043F\u0430\u0443\u0437\u044B."), /*#__PURE__*/React.createElement(StepItem, {
    number: "03",
    title: "\u0420\u0435\u043F\u0435\u0442\u0438\u0446\u0438\u0438"
  }, "\u0422\u0430\u043D\u0446\u043C\u0435\u0439\u0441\u0442\u0435\u0440 \u0438 \u0430\u0441\u0441\u0438\u0441\u0442\u0435\u043D\u0442 \u0433\u043E\u0442\u043E\u0432\u044F\u0442 \u0432\u0430\u0441 \u0438 \u0433\u043E\u0441\u0442\u0435\u0439 \u2014 \u0432 \u0432\u0430\u0448\u0435\u043C \u0442\u0435\u043C\u043F\u0435, \u0430 \u043D\u0435 \u043F\u043E \u043F\u0440\u043E\u0433\u0440\u0430\u043C\u043C\u0435.")))), /*#__PURE__*/React.createElement(Section, {
    style: {
      paddingTop: 0
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 44
    }
  }, /*#__PURE__*/React.createElement(SectionLabel, {
    number: "03"
  }, "\u0412\u0415\u0427\u0415\u0420\u0410"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(2, minmax(0,1fr))',
      gap: 'var(--grid-gap)'
    }
  }, /*#__PURE__*/React.createElement(SegmentCard, {
    number: "01",
    title: "\u0427\u0430\u0441\u0442\u043D\u044B\u0439 \u0431\u0430\u043B",
    subtitle: "\u0434\u043B\u044F \u0441\u0435\u043C\u044C\u0438 \u0438 \u0431\u043B\u0438\u0437\u043A\u0438\u0445"
  }, "\u0421\u0432\u0430\u0434\u044C\u0431\u0430, \u044E\u0431\u0438\u043B\u0435\u0439, \u0434\u0435\u043D\u044C \u0440\u043E\u0436\u0434\u0435\u043D\u0438\u044F \u2014 \u0441\u043E\u0431\u044B\u0442\u0438\u0435, \u0437\u0430 \u043A\u043E\u0442\u043E\u0440\u044B\u043C \u0441\u0442\u043E\u0438\u0442 \u0446\u0435\u043B\u0430\u044F \u0438\u0441\u0442\u043E\u0440\u0438\u044F \u0441\u0435\u043C\u044C\u0438."), /*#__PURE__*/React.createElement(SegmentCard, {
    number: "02",
    title: "\u041A\u043E\u0440\u043F\u043E\u0440\u0430\u0442\u0438\u0432\u043D\u044B\u0439 \u0431\u0430\u043B",
    subtitle: "\u0434\u043B\u044F \u043A\u043E\u043C\u043F\u0430\u043D\u0438\u0438 \u0438 \u043F\u0430\u0440\u0442\u043D\u0451\u0440\u043E\u0432",
    surface: "brand"
  }, "\u0413\u043E\u0434\u043E\u0432\u0449\u0438\u043D\u0430 \u043A\u043E\u043C\u043F\u0430\u043D\u0438\u0438, \u043D\u043E\u0432\u043E\u0433\u043E\u0434\u043D\u0438\u0439 \u043F\u0440\u0438\u0451\u043C, \u0432\u0435\u0447\u0435\u0440 \u0432 \u0447\u0435\u0441\u0442\u044C \u043F\u0430\u0440\u0442\u043D\u0451\u0440\u043E\u0432.")))), /*#__PURE__*/React.createElement(QuoteBand, {
    eyebrow: "\u043C\u044B \u043D\u0430\u0443\u0447\u0438\u043B\u0438\u0441\u044C \u0442\u0430\u043D\u0446\u0435\u0432\u0430\u0442\u044C \u0432\u0430\u043B\u044C\u0441"
  }, "\u0447\u0442\u043E\u0431\u044B \u0432\u0435\u0447\u0435\u0440 \u0441\u0442\u0430\u043B \u0442\u0435\u043C,", /*#__PURE__*/React.createElement("br", null), "\u0447\u0442\u043E \u0432\u0441\u043F\u043E\u043C\u0438\u043D\u0430\u044E\u0442 \u0433\u043E\u0434\u0430\u043C\u0438"), /*#__PURE__*/React.createElement(CTABand, {
    number: "05",
    label: "\u0421\u0412\u042F\u0417\u0410\u0422\u042C\u0421\u042F",
    title: /*#__PURE__*/React.createElement(React.Fragment, null, "\u0420\u0430\u0441\u0441\u043A\u0430\u0436\u0438\u0442\u0435", /*#__PURE__*/React.createElement("br", null), "\u043E \u0432\u0435\u0447\u0435\u0440\u0435"),
    onAction: () => onNavigate('Связаться')
  }));
}
Object.assign(window, {
  HomeScreen
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/site/Home.jsx", error: String((e && e.message) || e) }); }

// ui_kits/site/Process.jsx
try { (() => {
const {
  StepItem,
  QuoteBand,
  CTABand,
  TextLink
} = window.ChastnyeBalyDesignSystem_059c2e;
function ProcessScreen({
  onNavigate
}) {
  return /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(Section, {
    style: {
      paddingTop: 96
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 72
    }
  }, /*#__PURE__*/React.createElement(SectionHead, {
    number: "02",
    label: "\u041A\u0410\u041A \u042D\u0422\u041E \u041F\u0420\u041E\u0418\u0421\u0425\u041E\u0414\u0418\u0422",
    title: /*#__PURE__*/React.createElement(React.Fragment, null, "\u041A\u0430\u043A \u043C\u044B \u0433\u043E\u0442\u043E\u0432\u0438\u043C", /*#__PURE__*/React.createElement("br", null), "\u0432\u0430\u0448 \u0432\u0435\u0447\u0435\u0440"),
    lead: "\u041C\u044B \u043D\u0435 \u043D\u0430\u0447\u0438\u043D\u0430\u0435\u043C \u0441 \u0430\u043D\u043A\u0435\u0442\u044B \u0438 \u043D\u0435 \u0437\u0430\u043A\u0430\u043D\u0447\u0438\u0432\u0430\u0435\u043C \u0434\u043E\u0433\u043E\u0432\u043E\u0440\u043E\u043C. \u041C\u044B \u043D\u0430\u0447\u0438\u043D\u0430\u0435\u043C \u0441 \u0440\u0430\u0437\u0433\u043E\u0432\u043E\u0440\u0430. \u0412\u044B \u0440\u0430\u0441\u0441\u043A\u0430\u0437\u044B\u0432\u0430\u0435\u0442\u0435 \u043E \u0441\u0432\u043E\u0451\u043C \u0432\u0435\u0447\u0435\u0440\u0435 \u2014 \u0434\u043B\u044F \u043A\u043E\u0433\u043E \u043E\u043D, \u043F\u043E\u0447\u0435\u043C\u0443 \u0438\u043C\u0435\u043D\u043D\u043E \u0431\u0430\u043B, \u0447\u0442\u043E \u0434\u043B\u044F \u0432\u0430\u0441 \u0432\u0430\u0436\u043D\u043E."
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(3, minmax(0,1fr))',
      gap: 'var(--grid-gap)'
    }
  }, /*#__PURE__*/React.createElement(StepItem, {
    number: "01",
    title: "\u0420\u0430\u0437\u0433\u043E\u0432\u043E\u0440"
  }, "\u0412\u044B \u0440\u0430\u0441\u0441\u043A\u0430\u0437\u044B\u0432\u0430\u0435\u0442\u0435 \u043E \u0441\u0432\u043E\u0451\u043C \u0432\u0435\u0447\u0435\u0440\u0435 \u2014 \u0434\u043B\u044F \u043A\u043E\u0433\u043E \u043E\u043D, \u043F\u043E\u0447\u0435\u043C\u0443 \u0438\u043C\u0435\u043D\u043D\u043E \u0431\u0430\u043B, \u0447\u0442\u043E \u0434\u043B\u044F \u0432\u0430\u0441 \u0432\u0430\u0436\u043D\u043E."), /*#__PURE__*/React.createElement(StepItem, {
    number: "02",
    title: "\u0421\u0446\u0435\u043D\u0430\u0440\u0438\u0439"
  }, "\u041C\u044B \u0441\u043E\u0431\u0438\u0440\u0430\u0435\u043C \u0432\u0435\u0447\u0435\u0440 \u0438\u0437 \u0442\u043E\u0433\u043E, \u0447\u0442\u043E \u0443\u0441\u043B\u044B\u0448\u0430\u043B\u0438: \u043C\u0443\u0437\u044B\u043A\u0430, \u0442\u0430\u043D\u0446\u044B, \u043F\u043E\u0440\u044F\u0434\u043E\u043A, \u043F\u0430\u0443\u0437\u044B."), /*#__PURE__*/React.createElement(StepItem, {
    number: "03",
    title: "\u0420\u0435\u043F\u0435\u0442\u0438\u0446\u0438\u0438"
  }, "\u0422\u0430\u043D\u0446\u043C\u0435\u0439\u0441\u0442\u0435\u0440 \u0438 \u0430\u0441\u0441\u0438\u0441\u0442\u0435\u043D\u0442 \u0433\u043E\u0442\u043E\u0432\u044F\u0442 \u0432\u0430\u0441 \u0438 \u0433\u043E\u0441\u0442\u0435\u0439 \u2014 \u0432 \u0432\u0430\u0448\u0435\u043C \u0442\u0435\u043C\u043F\u0435, \u0430 \u043D\u0435 \u043F\u043E \u043F\u0440\u043E\u0433\u0440\u0430\u043C\u043C\u0435.")), /*#__PURE__*/React.createElement(MediaPlaceholder, {
    note: "\u041C\u0435\u0441\u0442\u043E \u043F\u043E\u0434 \u043F\u043E\u043B\u043D\u043E\u0448\u0438\u0440\u0438\u043D\u043D\u0443\u044E \u0444\u043E\u0442\u043E\u0433\u0440\u0430\u0444\u0438\u044E \u0440\u0435\u043F\u0435\u0442\u0438\u0446\u0438\u0438 \u2014 \u0438\u0437\u043E\u0431\u0440\u0430\u0436\u0435\u043D\u0438\u0439 \u0432 \u0438\u0441\u0445\u043E\u0434\u043D\u044B\u0445 \u043C\u0430\u0442\u0435\u0440\u0438\u0430\u043B\u0430\u0445 \u043D\u0435\u0442",
    height: 360
  }), /*#__PURE__*/React.createElement(TextLink, {
    onClick: () => onNavigate('Связаться')
  }, "\u043E\u0431\u0441\u0443\u0434\u0438\u0442\u044C \u0432\u0435\u0447\u0435\u0440"))), /*#__PURE__*/React.createElement(QuoteBand, {
    eyebrow: "\u043C\u044B \u043D\u0430\u0443\u0447\u0438\u043B\u0438\u0441\u044C \u0442\u0430\u043D\u0446\u0435\u0432\u0430\u0442\u044C \u0432\u0430\u043B\u044C\u0441"
  }, "\u0447\u0442\u043E\u0431\u044B \u0432\u0435\u0447\u0435\u0440 \u0441\u0442\u0430\u043B \u0442\u0435\u043C,", /*#__PURE__*/React.createElement("br", null), "\u0447\u0442\u043E \u0432\u0441\u043F\u043E\u043C\u0438\u043D\u0430\u044E\u0442 \u0433\u043E\u0434\u0430\u043C\u0438"), /*#__PURE__*/React.createElement(CTABand, {
    number: "05",
    label: "\u0421\u0412\u042F\u0417\u0410\u0422\u042C\u0421\u042F",
    title: /*#__PURE__*/React.createElement(React.Fragment, null, "\u0420\u0430\u0441\u0441\u043A\u0430\u0436\u0438\u0442\u0435", /*#__PURE__*/React.createElement("br", null), "\u043E \u0432\u0435\u0447\u0435\u0440\u0435"),
    onAction: () => onNavigate('Связаться')
  }));
}
Object.assign(window, {
  ProcessScreen
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/site/Process.jsx", error: String((e && e.message) || e) }); }

// ui_kits/site/Shell.jsx
try { (() => {
const {
  SiteHeader,
  Wordmark,
  Logo
} = window.ChastnyeBalyDesignSystem_059c2e;
const shellPad = {
  paddingLeft: 'var(--page-pad-1200)',
  paddingRight: 'var(--page-pad-1200)'
};
function PageShell({
  nav,
  active,
  phone,
  onNavigate,
  headerSurface = 'transparent',
  children
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      background: 'var(--surface-page)',
      color: 'var(--greige-90)',
      fontFamily: 'var(--font-sans)',
      minHeight: '100%'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      background: headerSurface === 'brand' ? 'var(--surface-brand)' : 'var(--surface-page)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      ...shellPad,
      paddingTop: 0,
      paddingBottom: 0
    }
  }, /*#__PURE__*/React.createElement(SiteHeader, {
    items: nav,
    active: active,
    phone: phone,
    surface: headerSurface,
    onNavigate: onNavigate,
    style: {
      paddingLeft: 0,
      paddingRight: 0
    }
  }))), children, /*#__PURE__*/React.createElement("footer", {
    style: {
      ...shellPad,
      paddingTop: 44,
      paddingBottom: 44,
      borderTop: '1px solid var(--line-section)',
      display: 'flex',
      alignItems: 'baseline',
      justifyContent: 'space-between',
      gap: 24
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'baseline',
      gap: 28
    }
  }, /*#__PURE__*/React.createElement(Wordmark, null), /*#__PURE__*/React.createElement(Logo, {
    height: 34,
    style: {
      opacity: 0.9
    }
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 28,
      fontSize: 'var(--nav-size)',
      fontWeight: 600,
      letterSpacing: 'var(--nav-tracking)',
      textTransform: 'uppercase',
      color: 'var(--text-body)'
    }
  }, /*#__PURE__*/React.createElement("span", null, "ballevent.ru"), /*#__PURE__*/React.createElement("span", null, phone))));
}
function Section({
  surface = 'ink',
  children,
  style
}) {
  const bg = surface === 'brand' ? 'var(--surface-brand)' : surface === 'rest' ? 'var(--surface-rest)' : 'var(--surface-page)';
  return /*#__PURE__*/React.createElement("section", {
    style: {
      background: bg,
      paddingLeft: 'var(--page-pad-1200)',
      paddingRight: 'var(--page-pad-1200)',
      paddingTop: 'var(--pad-section-v)',
      paddingBottom: 'var(--pad-section-v)',
      ...style
    }
  }, children);
}
function SectionHead({
  number,
  label,
  title,
  lead
}) {
  const {
    SectionLabel
  } = window.ChastnyeBalyDesignSystem_059c2e;
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(12, minmax(0,1fr))',
      gap: 'var(--grid-gap)',
      alignItems: 'start'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      gridColumn: 'span 3'
    }
  }, /*#__PURE__*/React.createElement(SectionLabel, {
    number: number
  }, label)), /*#__PURE__*/React.createElement("div", {
    style: {
      gridColumn: 'span 9',
      display: 'flex',
      flexDirection: 'column',
      gap: 34
    }
  }, /*#__PURE__*/React.createElement("h2", {
    style: {
      margin: 0,
      fontFamily: 'var(--h2-family)',
      fontWeight: 400,
      fontSize: 88,
      lineHeight: 0.8,
      letterSpacing: '-5px',
      color: 'var(--text-title)'
    }
  }, title), lead && /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      maxWidth: 'var(--measure-lead)',
      fontFamily: 'var(--text-family)',
      fontSize: 'var(--text-size)',
      fontWeight: 600,
      lineHeight: 1.7,
      letterSpacing: 'var(--text-tracking)',
      textTransform: 'uppercase',
      color: 'var(--text-body)'
    }
  }, lead)));
}

/* Плашка на месте изображения: фотографий и видео в исходных материалах нет. */
function MediaPlaceholder({
  note,
  height = 420
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      height,
      border: '1px solid var(--line-row)',
      display: 'flex',
      alignItems: 'flex-end',
      padding: 20,
      boxSizing: 'border-box'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 11,
      fontWeight: 500,
      letterSpacing: '0.5px',
      textTransform: 'uppercase',
      color: 'var(--text-muted)'
    }
  }, note));
}
Object.assign(window, {
  PageShell,
  Section,
  SectionHead,
  MediaPlaceholder
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/site/Shell.jsx", error: String((e && e.message) || e) }); }

__ds_ns.Button = __ds_scope.Button;

__ds_ns.FormField = __ds_scope.FormField;

__ds_ns.SectionLabel = __ds_scope.SectionLabel;

__ds_ns.TextLink = __ds_scope.TextLink;

__ds_ns.CTABand = __ds_scope.CTABand;

__ds_ns.Logo = __ds_scope.Logo;

__ds_ns.QuoteBand = __ds_scope.QuoteBand;

__ds_ns.SegmentCard = __ds_scope.SegmentCard;

__ds_ns.SiteHeader = __ds_scope.SiteHeader;

__ds_ns.StepItem = __ds_scope.StepItem;

__ds_ns.Wordmark = __ds_scope.Wordmark;

})();
