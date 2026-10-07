import React from 'react';

/* Полоса-передышка на Ash: врезка курсивом сверху, крупная антиква под ней.
   Ставится между двумя Ink-секциями. */
export function QuoteBand({ eyebrow, children, surface = 'rest', style, ...rest }) {
  return (
    <section
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        textAlign: 'center',
        gap: 26,
        padding: 'var(--pad-band-v) var(--page-pad-1200)',
        background: surface === 'brand' ? 'var(--surface-brand)' : surface === 'ink' ? 'var(--surface-page)' : 'var(--surface-rest)',
        ...style,
      }}
      {...rest}
    >
      {eyebrow && (
        <div
          style={{
            fontFamily: 'var(--micro-family)',
            fontStyle: 'var(--micro-style)',
            fontSize: 'var(--micro-size)',
            lineHeight: 'var(--micro-leading)',
            letterSpacing: 'var(--micro-tracking)',
            color: 'var(--greige-90)',
          }}
        >
          {eyebrow}
        </div>
      )}
      <blockquote
        style={{
          margin: 0,
          maxWidth: 'var(--measure-quote)',
          fontFamily: 'var(--h2-family)',
          fontWeight: 'var(--h2-weight)',
          fontSize: 76,
          lineHeight: 0.85,
          letterSpacing: -4,
          color: 'var(--text-title)',
        }}
      >
        {children}
      </blockquote>
    </section>
  );
}
