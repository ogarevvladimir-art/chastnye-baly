const { SectionLabel, SegmentCard, CTABand } = window.ChastnyeBalyDesignSystem_059c2e;

function EveningsScreen({ onNavigate }) {
  return (
    <>
      <Section style={{ paddingTop: 96 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 72 }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 34 }}>
            <SectionLabel number="03">ВЕЧЕРА</SectionLabel>
            <h1 style={{ margin: 0, fontFamily: 'var(--h1-family)', fontWeight: 700, fontSize: 130, lineHeight: 1, letterSpacing: 0, textTransform: 'uppercase', color: 'var(--text-title)' }}>Вечера</h1>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0,1fr))', gap: 'var(--grid-gap)' }}>
            <SegmentCard number="01" title="Частный бал" subtitle="для семьи и близких">Свадьба, юбилей, день рождения — событие, за которым стоит целая история семьи.</SegmentCard>
            <SegmentCard number="02" title="Корпоративный бал" subtitle="для компании и партнёров" surface="brand">Годовщина компании, новогодний приём, вечер в честь партнёров.</SegmentCard>
          </div>
          <MediaPlaceholder note="Галерея прошедших вечеров — фотографий в исходных материалах нет" />
        </div>
      </Section>
      <CTABand number="05" label="СВЯЗАТЬСЯ" title={<>Расскажите<br />о вечере</>} onAction={() => onNavigate('Связаться')} />
    </>
  );
}

Object.assign(window, { EveningsScreen });
