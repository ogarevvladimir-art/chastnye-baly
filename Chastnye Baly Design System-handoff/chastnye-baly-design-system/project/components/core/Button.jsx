import React from 'react';

/* Основная кнопка: обводка 1px greige без заливки и без скруглений.
   Hover — полная инверсия: заливка greige, текст цветом фона. 240ms ease. */
export function Button({ children, size = 'md', as, href, disabled = false, onClick, style, ...rest }) {
  const [hover, setHover] = React.useState(false);
  const on = hover && !disabled;
  const Tag = as || (href ? 'a' : 'button');
  return (
    <Tag
      href={href}
      disabled={Tag === 'button' ? disabled : undefined}
      onClick={disabled ? undefined : onClick}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{
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
        ...style,
      }}
      {...rest}
    >
      {children}
    </Tag>
  );
}
