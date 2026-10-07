# Chastnye Baly («Частные балы») — website

One-page site for Plyaskin group: design in Figma → build in `site/` → Russian hosting with PHP.
Standing project rules live here. Where we stopped — `STATUS.md`.

## Language and names

- Working docs are in English (fewer tokens). Write new entries in English.
- Keep in Russian, verbatim: site copy, Figma section/frame names, block names («Форматы», «Вечер»…), words set in giant type, user quotes.
- File and folder names stay Russian (scripts and links depend on them). Glossary: `ОБЩЕЕ` — overview, `ПЛАН-ДОРАБОТКИ` — rework plan,
  `ПРАВКИ` — edits log, `ЖУРНАЛ` — journal, `журнал/` — closed-stage journals, `ПРИЁМЫ` — code techniques, `ТЕКСТ` — site copy,
  `ЭТАПЫ` — stages 0–7, `ПЕРЕДАЧА` — adaptive handoff, `Доработка/вёрстка/` — build work folder, `сверка/` — comparison output.
- IDs stay as they are: rework stages `Д1`–`Д6`, edits `П-01`…, review findings `Р-1`…, tags like `Д3б-принят`.

## Session start

1. `STATUS.md` — current stage, what waits for the user, next step.
2. Current work files (`Доработка/вёрстка/`):
   - `ОБЩЕЕ.md` — user decisions, source of truth, stack, behaviour, what not to touch;
   - `ПЛАН-ДОРАБОТКИ.md` — stages Д1–Д6, **current stage section only**;
   - `ПРАВКИ.md` — entries of the current stage;
   - `ЖУРНАЛ.md` — current work; closed stages — `журнал/<stage>.md`, open only the one needed (closed ones are in Russian);
   - `ПРИЁМЫ.md` — code rules by stage, only when building or fixing a block.
3. Figma work — skill `figma-express-pitfalls`; site checks and comparison — skill `baly-sverka`.

## Session end

- `STATUS.md` — rewrite briefly: what closed, what waits for the user, next step. Don't accumulate history there.
- `ЖУРНАЛ.md` — stage entry: what was done, files, deviations from the design, flags.
- `ПРАВКИ.md` — marks "done, stage Дn".
- New code techniques — `ПРИЁМЫ.md`, new decisions — `ОБЩЕЕ.md`. New pitfalls — into a skill (`~/.claude/skills/figma-express-pitfalls` or `baly-sverka`).
- Stage accepted — move its section from `ЖУРНАЛ.md` to `журнал/<stage>.md` and add a row to the table.
- Git: commit at the end of a stage (on the user's request), tag an accepted stage like `Д3б-принят`.
  Don't push to GitHub (`origin`) without an explicit request. What isn't stored — see `.gitignore` (comparisons, Figma exports, video, paid fonts, secrets).

## Folder map

| Folder | Contents |
|---|---|
| `site/` | **Only what gets uploaded to the server.** No tools, drafts or comparisons |
| `Доработка/вёрстка/` | Plan, journal (`журнал/` — closed stages), techniques, edits, site copy, `tools/` (checks, comparisons, frame generators), `сверка/` |
| `Доработка/целостность/` | Design coherence: `АНАЛИЗ.md` (what breaks after block 01, screen library A–F, rules), `ПЛАН.md` (Ц1–Ц5), `ЖУРНАЛ.md`, `листы/` (site and ore sheets) |
| `Доработка/адаптив/` | `ПЕРЕДАЧА.md` (adaptive 390 / 834; partly outdated — see Р-13 in ПРАВКИ), `БЛОКИ.md` (frame ids per block) |
| `Доработка/фото-тон/` | Photo tone polynomials per section and scripts |
| `Доработка/ore-заголовки/`, `hero-форматы/` | Closed design stages |
| `Доработка/_память-архив-2026-10-07/` | September decision history (system v2, Figma block variants), moved out of Claude's memory |
| `Доработка/_ru-оригиналы-2026-10-07/` | Russian originals of the docs before translation — not read in normal work |
| `Макет/референс/` | ore.co screenshots (13 screens) and `ore-mobile/` |
| `assets/` | Original photos — don't change or delete |
| `Прототип/` | Old design (Manrope, diagrams) — take only meta tags and the privacy text |

## Source of truth

- Figma **Chastnye_baly_system**, Page 2, «Главная · v2 · фото с цветом» (`191:626`) + adaptive frames 390 / 834.
- Copy — **only from Figma**, not from `.docx`.
- Figma and ПЕРЕДАЧА disagree, or desktop contradicts adaptive — ask the user, don't choose yourself.
- Figma is edited only after approval: new variants — a separate section alongside; `191:626` and state frames — only approved work.
- Some layer names in `191:626` are outdated — check a block's state by render, not by names.

## The ore language — don't drift

The user rejected blocks twice for "drifting from ore" (September 2026). The system rests on:

- **two poles**: giant type 150–250 and caps 11–12, nothing in between;
- asymmetry along axes: the edge of one block = the start of the next, staircases;
- photo objects overlapped by a giant word;
- a phrase that starts large and continues in caps from an axis.

Not allowed: diagrams, charts, infographics, callout lines, flourishes, centred paragraphs, 36 px leads as the main voice.
Words of one role — one size (don't fit size to the column; use a staircase instead). Small text — caps.
**No hyphenation in giant words** («ВОСПОМИ- / НАНИЯ» is forbidden). Don't "fix" ore devices in the source with medium sizes.
Don't rebuild working parts of a block unasked; in variants keep "header only" and "header + body" separate;
before building all states of a bold variant, show one rest frame.

## How we work

- Big work: questions → general brief + stage brief → each stage in its own session (agent) → user's "yes" → next stage.
- A / B variants — a Figma section with a recommendation. The user doesn't always take the recommendation — don't transfer before "yes".
- In chat call Figma sections and frames by their visible (Russian) names, id in brackets if needed. Ids in the journal and scripts.
- Figma — via **figma-mcp-express** (the official MCP on the Starter plan hits its limit).
- View the site only via `python tools/serve.py` (run from `Доработка/вёрстка/`) → `http://127.0.0.1:8080/site/` (modules don't load from `file://`).
  Checks — Chrome, device mode; phone and old iOS were dropped from the plan.
- Checks — in Chromium and WebKit (`tools/*_check.py`, Figma comparison — `tools/*_compare.py`), order — skill `baly-sverka`.
- The plugin writes Figma screenshots only inside `VS CODE/.figma-shots/`; that path is hard-coded in `tools/d2_*`, `d3a_*`.

## Saving tokens

- Comparison — deviation table first; open images only for frames over the threshold, cropped. The user judges taste and motion.
- Figma — narrow reads, export the tree to a file once per stage, batches via a generator; check "did it land" by reading nodes, not screenshots.
- Mechanical work from a ready decision (moving coordinates, batches, running checks, CSS per plan) — agent `executor` (Sonnet).
  Decisions, variants, reviews, edit analysis — in the main session.
- Д5 — trial "code first" order: variants via a `?v=` switch on the site, Figma — a note at the end (`ПЛАН-ДОРАБОТКИ.md`, section Д5).
