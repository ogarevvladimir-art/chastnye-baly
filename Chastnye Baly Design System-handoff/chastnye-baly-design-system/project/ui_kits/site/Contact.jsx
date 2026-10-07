const { SectionLabel, FormField, Button } = window.ChastnyeBalyDesignSystem_059c2e;

function ContactScreen() {
  const [form, setForm] = React.useState({ name: '', phone: '', mail: '' });
  const [focused, setFocused] = React.useState(null);
  const [error, setError] = React.useState(null);
  const [sent, setSent] = React.useState(false);
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });
  const state = (k) => (error === k ? 'error' : focused === k ? 'focus' : 'rest');

  const submit = () => {
    if (!form.name.trim()) return setError('name');
    if (!form.mail.includes('@')) return setError('mail');
    setError(null);
    setSent(true);
  };

  return (
    <Section style={{ paddingTop: 96 }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(12, minmax(0,1fr))', gap: 'var(--grid-gap)', alignItems: 'start' }}>
        <div style={{ gridColumn: 'span 5', display: 'flex', flexDirection: 'column', gap: 34 }}>
          <SectionLabel number="05">СВЯЗАТЬСЯ</SectionLabel>
          <h1 style={{ margin: 0, fontFamily: 'var(--h2-family)', fontWeight: 400, fontSize: 88, lineHeight: 0.8, letterSpacing: '-5px', color: 'var(--text-title)' }}>Расскажите<br />о вечере</h1>
          <p style={{ margin: 0, fontFamily: 'var(--text-family)', fontSize: 'var(--text-size)', fontWeight: 600, lineHeight: 1.7, letterSpacing: 'var(--text-tracking)', textTransform: 'uppercase', color: 'var(--text-body)' }}>Мы начинаем с разговора — оставьте контакты, и мы позвоним.</p>
        </div>
        <div style={{ gridColumn: '7 / span 6' }}>
          {sent ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 18, borderTop: '1px solid var(--line-section)', paddingTop: 34 }}>
              <div style={{ fontFamily: 'var(--micro-family)', fontStyle: 'italic', fontSize: 'var(--micro-size)', letterSpacing: 'var(--micro-tracking)', lineHeight: 1, color: 'var(--greige-90)' }}>спасибо, {form.name || 'мы получили заявку'}</div>
              <div style={{ fontFamily: 'var(--h2-family)', fontSize: 56, lineHeight: 0.85, letterSpacing: '-3px', color: 'var(--text-title)' }}>Мы позвоним<br />в течение дня</div>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 34 }}>
              <FormField label="Имя" placeholder="Как к вам обращаться" value={form.name} onChange={set('name')} state={state('name')} hint={error === 'name' ? 'Заполните поле' : undefined}
                onFocus={() => setFocused('name')} onBlur={() => setFocused(null)} />
              <FormField label="Телефон" placeholder="+7" value={form.phone} onChange={set('phone')} state={state('phone')}
                onFocus={() => setFocused('phone')} onBlur={() => setFocused(null)} />
              <FormField label="E-mail" placeholder="ivanov@" value={form.mail} onChange={set('mail')} state={state('mail')} hint={error === 'mail' ? 'Проверьте адрес' : undefined}
                onFocus={() => setFocused('mail')} onBlur={() => setFocused(null)} />
              <Button onClick={submit} style={{ alignSelf: 'flex-start' }}>Оставить заявку</Button>
            </div>
          )}
        </div>
      </div>
    </Section>
  );
}

Object.assign(window, { ContactScreen });
