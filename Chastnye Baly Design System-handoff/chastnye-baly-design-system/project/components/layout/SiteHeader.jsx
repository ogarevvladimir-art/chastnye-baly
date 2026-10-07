import React from 'react';
import { Wordmark } from './Wordmark.jsx';

/* Шапка: прозрачная поверх hero, при скролле — заливка Ink.
   Пункты 50% непрозрачности, активный и hover — 90%. */
export function SiteHeader({
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
  return (
    <header
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: 32,
        padding: 'var(--pad-header)',
        background: surface === 'ink' ? 'var(--surface-page)' : onBrand ? 'var(--surface-brand)' : 'transparent',
        ...style,
      }}
      {...rest}
    >
      <Wordmark tone={onBrand ? 'on-brand' : 'default'} />
      <nav style={{ display: 'flex', gap: 34 }}>
        {items.map((item) => {
          const lit = item === active || item === hover;
          return (
            <a
              key={item}
              href="#"
              onClick={(e) => {
                e.preventDefault();
                if (onNavigate) onNavigate(item);
              }}
              onMouseEnter={() => setHover(item)}
              onMouseLeave={() => setHover(null)}
              style={{
                fontFamily: 'var(--font-sans)',
                fontSize: 'var(--nav-size)',
                fontWeight: 600,
                letterSpacing: 'var(--nav-tracking)',
                textTransform: 'uppercase',
                textDecoration: 'none',
                whiteSpace: 'nowrap',
                color: lit ? 'var(--greige-90)' : onBrand ? 'var(--greige-65)' : 'var(--greige-50)',
                transition: 'var(--transition-hover)',
              }}
            >
              {item}
            </a>
          );
        })}
      </nav>
      {phone && (
        <a
          href={'tel:' + String(phone).replace(/[^+\d]/g, '')}
          style={{
            fontFamily: 'var(--font-sans)',
            fontSize: 'var(--nav-size)',
            fontWeight: 600,
            letterSpacing: 'var(--nav-tracking)',
            textTransform: 'uppercase',
            textDecoration: 'none',
            whiteSpace: 'nowrap',
            color: onBrand ? 'rgba(171,167,154,0.95)' : 'var(--greige-90)',
          }}
        >
          {phone}
        </a>
      )}
    </header>
  );
}
