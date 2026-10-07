const { SectionLabel, TextLink, SegmentCard, StepItem, QuoteBand, CTABand } = window.ChastnyeBalyDesignSystem_059c2e;

function HomeScreen({ onNavigate }) {
  return (
    <>
      <div style={{ background: 'var(--surface-brand)', paddingLeft: 'var(--page-pad-1200)', paddingRight: 'var(--page-pad-1200)', paddingTop: 132, paddingBottom: 88, display: 'flex', flexDirection: 'column', gap: 34, minHeight: 520, boxSizing: 'border-box' }}>
        <SectionLabel number="01" tone="on-brand">ЧАСТНЫЕ БАЛЫ</SectionLabel>
        <h1 style={{ margin: 0, fontFamily: 'var(--h2-family)', fontWeight: 400, fontSize: 118, lineHeight: 0.8, letterSpacing: '-6px', color: 'rgba(171,167,154,0.95)' }}>Ваша история.<br />Ваш вечер.</h1>
        <TextLink onClick={() => onNavigate('Связаться')}>обсудить вечер</TextLink>
      </div>

      <Section>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 72 }}>
          <SectionHead number="02" label="ПОДГОТОВКА" title={<>Как мы готовим<br />ваш вечер</>} lead="Мы не начинаем с анкеты и не заканчиваем договором. Мы начинаем с разговора." />
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(0,1fr))', gap: 'var(--grid-gap)' }}>
            <StepItem number="01" title="Разговор">Вы рассказываете о своём вечере — для кого он, почему именно бал, что для вас важно.</StepItem>
            <StepItem number="02" title="Сценарий">Мы собираем вечер из того, что услышали: музыка, танцы, порядок, паузы.</StepItem>
            <StepItem number="03" title="Репетиции">Танцмейстер и ассистент готовят вас и гостей — в вашем темпе, а не по программе.</StepItem>
          </div>
        </div>
      </Section>

      <Section style={{ paddingTop: 0 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 44 }}>
          <SectionLabel number="03">ВЕЧЕРА</SectionLabel>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0,1fr))', gap: 'var(--grid-gap)' }}>
            <SegmentCard number="01" title="Частный бал" subtitle="для семьи и близких">Свадьба, юбилей, день рождения — событие, за которым стоит целая история семьи.</SegmentCard>
            <SegmentCard number="02" title="Корпоративный бал" subtitle="для компании и партнёров" surface="brand">Годовщина компании, новогодний приём, вечер в честь партнёров.</SegmentCard>
          </div>
        </div>
      </Section>

      <QuoteBand eyebrow="мы научились танцевать вальс">чтобы вечер стал тем,<br />что вспоминают годами</QuoteBand>

      <CTABand number="05" label="СВЯЗАТЬСЯ" title={<>Расскажите<br />о вечере</>} onAction={() => onNavigate('Связаться')} />
    </>
  );
}

Object.assign(window, { HomeScreen });
