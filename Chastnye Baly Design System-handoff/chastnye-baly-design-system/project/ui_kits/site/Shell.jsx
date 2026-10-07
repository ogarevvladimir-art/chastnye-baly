const { SiteHeader, Wordmark, Logo } = window.ChastnyeBalyDesignSystem_059c2e;

const shellPad = { paddingLeft: 'var(--page-pad-1200)', paddingRight: 'var(--page-pad-1200)' };

function PageShell({ nav, active, phone, onNavigate, headerSurface = 'transparent', children }) {
  return (
    <div style={{ background: 'var(--surface-page)', color: 'var(--greige-90)', fontFamily: 'var(--font-sans)', minHeight: '100%' }}>
      <div style={{ background: headerSurface === 'brand' ? 'var(--surface-brand)' : 'var(--surface-page)' }}>
        <div style={{ ...shellPad, paddingTop: 0, paddingBottom: 0 }}>
          <SiteHeader items={nav} active={active} phone={phone} surface={headerSurface} onNavigate={onNavigate} style={{ paddingLeft: 0, paddingRight: 0 }} />
        </div>
      </div>
      {children}
      <footer style={{ ...shellPad, paddingTop: 44, paddingBottom: 44, borderTop: '1px solid var(--line-section)', display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', gap: 24 }}>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 28 }}>
          <Wordmark />
          <Logo height={34} style={{ opacity: 0.9 }} />
        </div>
        <div style={{ display: 'flex', gap: 28, fontSize: 'var(--nav-size)', fontWeight: 600, letterSpacing: 'var(--nav-tracking)', textTransform: 'uppercase', color: 'var(--text-body)' }}>
          <span>ballevent.ru</span>
          <span>{phone}</span>
        </div>
      </footer>
    </div>
  );
}

function Section({ surface = 'ink', children, style }) {
  const bg = surface === 'brand' ? 'var(--surface-brand)' : surface === 'rest' ? 'var(--surface-rest)' : 'var(--surface-page)';
  return (
    <section style={{ background: bg, paddingLeft: 'var(--page-pad-1200)', paddingRight: 'var(--page-pad-1200)', paddingTop: 'var(--pad-section-v)', paddingBottom: 'var(--pad-section-v)', ...style }}>
      {children}
    </section>
  );
}

function SectionHead({ number, label, title, lead }) {
  const { SectionLabel } = window.ChastnyeBalyDesignSystem_059c2e;
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(12, minmax(0,1fr))', gap: 'var(--grid-gap)', alignItems: 'start' }}>
      <div style={{ gridColumn: 'span 3' }}><SectionLabel number={number}>{label}</SectionLabel></div>
      <div style={{ gridColumn: 'span 9', display: 'flex', flexDirection: 'column', gap: 34 }}>
        <h2 style={{ margin: 0, fontFamily: 'var(--h2-family)', fontWeight: 400, fontSize: 88, lineHeight: 0.8, letterSpacing: '-5px', color: 'var(--text-title)' }}>{title}</h2>
        {lead && (
          <p style={{ margin: 0, maxWidth: 'var(--measure-lead)', fontFamily: 'var(--text-family)', fontSize: 'var(--text-size)', fontWeight: 600, lineHeight: 1.7, letterSpacing: 'var(--text-tracking)', textTransform: 'uppercase', color: 'var(--text-body)' }}>{lead}</p>
        )}
      </div>
    </div>
  );
}

/* Плашка на месте изображения: фотографий и видео в исходных материалах нет. */
function MediaPlaceholder({ note, height = 420 }) {
  return (
    <div style={{ height, border: '1px solid var(--line-row)', display: 'flex', alignItems: 'flex-end', padding: 20, boxSizing: 'border-box' }}>
      <span style={{ fontSize: 11, fontWeight: 500, letterSpacing: '0.5px', textTransform: 'uppercase', color: 'var(--text-muted)' }}>{note}</span>
    </div>
  );
}

Object.assign(window, { PageShell, Section, SectionHead, MediaPlaceholder });
