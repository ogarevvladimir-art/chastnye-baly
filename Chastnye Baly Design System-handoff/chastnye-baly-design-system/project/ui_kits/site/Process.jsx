const { StepItem, QuoteBand, CTABand, TextLink } = window.ChastnyeBalyDesignSystem_059c2e;

function ProcessScreen({ onNavigate }) {
  return (
    <>
      <Section style={{ paddingTop: 96 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 72 }}>
          <SectionHead number="02" label="КАК ЭТО ПРОИСХОДИТ" title={<>Как мы готовим<br />ваш вечер</>} lead="Мы не начинаем с анкеты и не заканчиваем договором. Мы начинаем с разговора. Вы рассказываете о своём вечере — для кого он, почему именно бал, что для вас важно." />
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(0,1fr))', gap: 'var(--grid-gap)' }}>
            <StepItem number="01" title="Разговор">Вы рассказываете о своём вечере — для кого он, почему именно бал, что для вас важно.</StepItem>
            <StepItem number="02" title="Сценарий">Мы собираем вечер из того, что услышали: музыка, танцы, порядок, паузы.</StepItem>
            <StepItem number="03" title="Репетиции">Танцмейстер и ассистент готовят вас и гостей — в вашем темпе, а не по программе.</StepItem>
          </div>
          <MediaPlaceholder note="Место под полноширинную фотографию репетиции — изображений в исходных материалах нет" height={360} />
          <TextLink onClick={() => onNavigate('Связаться')}>обсудить вечер</TextLink>
        </div>
      </Section>

      <QuoteBand eyebrow="мы научились танцевать вальс">чтобы вечер стал тем,<br />что вспоминают годами</QuoteBand>

      <CTABand number="05" label="СВЯЗАТЬСЯ" title={<>Расскажите<br />о вечере</>} onAction={() => onNavigate('Связаться')} />
    </>
  );
}

Object.assign(window, { ProcessScreen });
