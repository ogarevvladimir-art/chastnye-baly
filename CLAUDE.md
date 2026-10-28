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
2. Files of the current stage (named in STATUS):
   - **Ц stages** (design coherence, `Доработка/целостность/`): `ПЛАН.md` — current Ц section; `ЖУРНАЛ.md` — current stage only;
     `АНАЛИЗ.md` — screen library A–F and rules; `ТЕКСТ-короткий.md` — only the lines of the current block;
   - **Д stages** (`Доработка/вёрстка/`): `ПЛАН-ДОРАБОТКИ.md` — current stage section; `ПРАВКИ.md` — open entries; `ЖУРНАЛ.md`;
   - code or behaviour work: `Доработка/вёрстка/ОБЩЕЕ.md` (decisions, stack, behaviour, what not to touch); `ПРИЁМЫ.md` — only the section
     of the stage or block being built (find it by headings).
3. Figma work — skill `figma-express-pitfalls`; site checks and comparison — skill `baly-sverka`.
4. Not at start: closed journals (`журнал/` in both folders), `Доработка/адаптив/` (ЖУРНАЛ ≈23k tokens, ОБЩЕЕ ≈14k),
   `чистка-figma/ОПИСЬ.md` (≈45k). Need a fact from them — grep for the id or word, read only the hit.

## Session end

- `STATUS.md` — rewrite briefly: what closed, what waits for the user, next step. Don't accumulate history there.
- `ЖУРНАЛ.md` — stage entry: what was done, files, deviations from the design, flags.
- `ПРАВКИ.md` — marks "done, stage Дn".
- New code techniques — `ПРИЁМЫ.md`, new decisions — `ОБЩЕЕ.md`. New pitfalls — into a skill (`~/.claude/skills/figma-express-pitfalls` or `baly-sverka`).
- Stage accepted — move its section from `ЖУРНАЛ.md` to `журнал/<stage>.md` (in `вёрстка/` or `целостность/`) and add a row to the table;
  closed П / Р entries and closed plan sections — to `вёрстка/журнал/правки-закрытые.md`, `план-Д1-Д4.md`. Start files keep only open work.
- Git: commit at the end of a stage (on the user's request), tag an accepted stage like `Д3б-принят`.
  Don't push to GitHub (`origin`) without an explicit request. What isn't stored — see `.gitignore` (comparisons, Figma exports, video, paid fonts, secrets).

## Folder map

| Folder | Contents |
|---|---|
| `site/` | **Only what gets uploaded to the server.** No tools, drafts or comparisons |
| `Доработка/вёрстка/` | Plan, journal (`журнал/` — closed stages), techniques, edits, site copy, `tools/` (checks, comparisons, frame generators), `сверка/` |
| `Доработка/целостность/` | Design coherence: `АНАЛИЗ.md` (what breaks after block 01, screen library A–F, rules), `ПЛАН.md` (Ц1–Ц5), `ЖУРНАЛ.md`, `листы/` (site and ore sheets) |
| `Доработка/чистка-figma/` | Figma file inventory and the 2026-10-23 clean-up (pages, removed reactions) |
| `Доработка/адаптив/` | `ПЕРЕДАЧА.md` (adaptive 390 / 834; partly outdated — see the note at its top), `БЛОКИ.md` (frame ids per block) |
| `Доработка/фото-тон/` | Photo tone polynomials per section and scripts |
| `Доработка/ore-заголовки/`, `hero-форматы/` | Closed design stages |
| `Доработка/_память-архив-2026-10-07/` | September decision history (system v2, Figma block variants), moved out of Claude's memory |
| `Доработка/_ru-оригиналы-2026-10-07/` | Russian originals of the docs before translation — not read in normal work |
| `Макет/референс/` | ore.co screenshots (13 screens) and `ore-mobile/` |
| `assets/` | Original photos — don't change or delete |
| `Прототип/` | Old design (Manrope, diagrams) — take only meta tags and the privacy text |

## Source of truth

- Figma **Chastnye_baly_system**, Page 2, «Главная · v2 · фото с цветом» (`191:626`) + adaptive frames 390 / 834.
- Pages (clean-up 2026-10-23): **Page 2** — only what matches the site (desktop «Frame 5», phone / tablet frames, Ц1 library); **«Окна»** — approved fit-to-screen frames on check windows;
  **Drafts** — superseded versions and variants. Rejected or replaced variants go to Drafts, not stay on Page 2. Inventory — `Доработка/чистка-figma/`.
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

Measured 2026-10-27 over 35 sessions: most of the cost is context length — every turn re-sends everything accumulated
(median turn ≈210k, sessions up to 900k without compaction). Single files and images matter much less.

- **One session — one step** (rest frame, desktop, adaptive, code, check). When the step closes or context passes ~150k:
  write the result to ЖУРНАЛ / STATUS and suggest a new session or `/compact` to the user. Don't run a whole stage of 100+ turns in one session.
- **Read narrowly.** No `cat` / `sed` dumps of whole files in Bash. `site/css/blocks.css` (5,200 lines) and `site/index.html`
  (≈32k tokens; line 52 is a 12k-char SVG logo): find the block by its marker — `grep -n "/\* ====" site/css/blocks.css`,
  `grep -n "<!-- " site/index.html`, `// NN` in `js/blocks.js` — then Read with offset / limit. Big docs — grep the headings, read the section.
  Don't re-read a file already in context; after an edit re-read only the changed range.
- **Images** — deviation table first; open only pairs over the threshold, cropped (`pair.py --max-height`); never the same image twice.
  The user judges taste and motion.
- **Figma** — the order and op parameters are in skill `figma-express-pitfalls`; `get_batch_op_spec` only for ops not listed there.
- **Executor.** Mechanical work from a ready decision — Figma build loops (generator → batches → node check), running checks and regression,
  CSS / JS per an approved decision, bookkeeping — agent `executor` with `model: haiku` and a full brief; it returns a short summary.
  Decisions, variants, reviews, edit analysis — in the main session.
- Long script output — to a file, then grep it. Comparison scripts print only rows over the threshold (`--all` — everything).
- Deferred tools — load them in one ToolSearch call (`select:a,b,c`).
- Д5 — trial "code first" order: variants via a `?v=` switch on the site, Figma — a note at the end (`ПЛАН-ДОРАБОТКИ.md`, section Д5).
