import React from 'react';
import { SectionLabel } from '../core/SectionLabel.jsx';
import { Button } from '../core/Button.jsx';

/* Финальная полоса на Terra: метка, крупный H1 капителью, кнопка справа.
   Terra открывает и закрывает страницу. */
export function CTABand({ label, number, title, action = 'Оставить заявку', onAction, style, ...rest }) {
  return (
    <section
      style={{
        display: 'flex',
        alignItems: 'flex-end',
        justifyContent: 'space-between',
        gap: 48,
        padding: 'var(--pad-band-v) var(--page-pad-1200)',
        background: 'var(--surface-brand)',
        ...style,
      }}
      {...rest}
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: 26 }}>
        {(label || number) && (
          <SectionLabel number={number} tone="on-brand">
            {label}
          </SectionLabel>
        )}
        <h2
          style={{
            margin: 0,
            fontFamily: 'var(--h1-family)',
            fontWeight: 'var(--h1-weight)',
            fontSize: 92,
            lineHeight: 'var(--h1-leading)',
            letterSpacing: 'var(--h1-tracking)',
            textTransform: 'uppercase',
            color: 'rgba(171,167,154,0.95)',
          }}
        >
          {title}
        </h2>
      </div>
      <Button size="lg" onClick={onAction} style={{ flexShrink: 0 }}>
        {action}
      </Button>
    </section>
  );
}
