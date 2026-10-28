# Status — updated 2026-10-28

## Now

**Decision 2026-10-28: the site moves to Tilda; work continues there.** Ц5 and Д5 / Д6 are paused.
Next session — draft the migration plan (see «Next step»). The hand-built site in `site/` stays as the reference build.

| Stage | State |
|---|---|
| Д1–Д4, Д3а–Д3в | Closed / built (2026-10-04 … 10-06), except Р-12 (below); details in `Доработка/вёрстка/журнал/` |
| Ц1 — screen library, rules, copy cuts | Accepted 2026-10-07 (section `352:2036`, copy `ТЕКСТ-короткий.md`) |
| Ц2 — pilot 08 «Этикет» | Closed 2026-10-23 |
| Ц3 — 07 «Уроки», 02 «Вечер» | Closed 2026-10-27 (`Доработка/целостность/журнал/Ц3.md`) |
| Ц4 — finale 11–12 «ВАШ / ВЕЧЕР» (type F) | Closed 2026-10-28 (`Доработка/целостность/журнал/Ц4.md`) |
| Ц5 — clean-up 03, 04, 05, 06, 09, 10 | **Paused** 2026-10-28: audit + user decisions done; 05 sheet `409:3142` waits for A / B (`Доработка/целостность/ЖУРНАЛ.md`) |
| Д5 — header hides on scroll, shading (П-09, Р-5) | Paused (after Ц5) |
| Д6 — overall check | Paused (after Д5) |

## Waiting for the user

1. 05 «Шоу» header: variant A («Шапка 3») or B («Шапка 1», recommended) — when Ц5 resumes (in Tilda or here).
2. "Yes" to deleting `site/logo/` — three unused SVGs (Р-12).
3. Walkthrough of the adaptive prototype in Figma Mirror → "Adaptive closed" in `Доработка/адаптив/ЖУРНАЛ.md`.

## Next step

New session: **plan of the move to Tilda** (skill `tilda-developer`, Tilda MCP). Audit first, then questions to the user, then stages. Inputs:
- the build in `site/` (one page, `index.html` + `css/blocks.css` + `js/*.js`, images in `site/img/`), behaviour and decisions —
  `Доработка/вёрстка/ОБЩЕЕ.md`, techniques — `ПРИЁМЫ.md`, copy — `Доработка/вёрстка/ТЕКСТ.md`;
- Figma `191:626` + adaptive 390 / 834 + the Ц2–Ц4 sections (source of truth for design);
- what Tilda must cover: fit-to-screen desktop (Д2), sticky / scroll-switching blocks (02, 05, 10), hover reveals (01, 04),
  the form (stage 6 items: where submissions go, privacy, analytics), fonts (Unbounded, Old Standard TT), photo formats.
- Questions to settle in the plan: Zero Block vs custom code per block; where Ц5 continues (Tilda or Figma first); domain and hosting.

## Done outside the stages

- 2026-10-23 Figma clean-up: Page 2 holds only the live design; drafts → page «Drafts», check windows → page «Окна» (`Доработка/чистка-figma/ПЛАН-ЧИСТКИ.md`).

## Deferred

- Stage 6: where form submissions go (`send.php`), form texts (`data-stub` placeholders), privacy, analytics and cookies.
- Stage 7: JS 45 KB vs a 40 KB budget, domain for canonical / OG / sitemap, real phone and email.
- Acceptance of stages 2–5 as a whole — in Д6.
