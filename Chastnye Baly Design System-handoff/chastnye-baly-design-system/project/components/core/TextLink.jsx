import React from 'react';

/* Текстовая ссылка: антиква строчными, стрелка слева, подчёркивание.
   Hover — линия растёт до 100%. */
export function TextLink({ children, href, onClick, size, showArrow = true, tone = 'default', style, ...rest }) {
  const [hover, setHover] = React.useState(false);
  const ink = tone === 'on-brand' ? 'var(--greige-90)' : 'var(--greige-90)';
  return (
    <a
      href={href}
      onClick={onClick}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{
        display: 'inline-flex',
        flexDirection: 'column',
        alignSelf: 'flex-start',
        gap: 6,
        color: ink,
        textDecoration: 'none',
        cursor: 'pointer',
        ...style,
      }}
      {...rest}
    >
      <span style={{ display: 'inline-flex', alignItems: 'center', gap: 12 }}>
        {showArrow && (
          <svg width="26" height="14" viewBox="0 0 26 14" fill="none" stroke="currentColor" strokeWidth="1.2" style={{ flexShrink: 0 }}>
            <path d="M0 7h24M18 1l6 6-6 6" />
          </svg>
        )}
        <span
          style={{
            fontFamily: 'var(--font-display)',
            fontSize: size || 'var(--link-size)',
            lineHeight: 1,
            letterSpacing: 'var(--link-tracking)',
          }}
        >
          {children}
        </span>
      </span>
      <span
        style={{
          height: 'var(--border-width)',
          width: hover ? '100%' : '62%',
          background: 'var(--greige-40)',
          transition: 'width var(--duration-line) var(--easing)',
        }}
      />
    </a>
  );
}
