# Visarjan Sentinel

Track: 2 Visarjan Ghat Watch
Team: [names]

Evidence-backed decision support for the Bhopal Municipal Corporation officer who
plans Durga visarjan. It turns three years of MPPCB idol-immersion water tests
(2023 to 2025, Ganesh and Durga, 7 Bhopal ghats) into a ranked follow-up queue,
with every number traceable to a report and PDF page, and a forwardable brief in
English and Hindi.

## The user
The BMC officer who decides, before 20 October 2026, where to send extra
cleaning, aeration and water testing at the immersion ghats.

## What it does
Ranks the seven ghats by how often their dissolved oxygen, BOD and pH readings
fell outside CPCB Class B (outdoor bathing) limits, with a severity tier for any
ghat that has recorded dissolved oxygen below 2 mg/l. Shows data coverage and
missing samples separately from the score, so a gap never looks like clean
water. Produces a short English and Hindi brief the officer can forward.

## Demo
[Link to the 2-minute recording]

## How to run
1. `python3 -m venv .venv && source .venv/bin/activate`
2. `pip install -r requirements.txt`
3. `python -m pytest -q` (56 tests, all should pass)
4. `streamlit run app.py` and open the URL it prints (usually http://localhost:8501)

The dashboard re-runs the pipeline on start, so `outputs/` is always current.
To regenerate the files without the dashboard:
`python -m visarjan_sentinel.build` (ranking.json, evidence.csv, validation.json)
and `python -m visarjan_sentinel.brief` (brief_en.md, brief_hi.md).

## Features
Five pages with sidebar navigation, each with one purpose:

1. **Overview** ("Water Quality Overview"): a small historical-data indicator,
   the highest-priority ghat with its verified reasons and evidence summary,
   four explained metrics (ghats assessed, historical readings analysed,
   readings outside the DO/BOD/pH benchmarks, ghats with incomplete evidence),
   one comparison chart (a stacked bar per ghat: red = DO below 2 mg/l, amber =
   outside the Class B limit, teal = within, count written on it), key finding,
   missing-data warning and limitations, and buttons to preview either brief.
2. **Ghat Priorities**: all seven ghats in the ranking engine's order with tier,
   a plain-language reason, readings outside the limit with denominator, lowest
   historical DO, and evidence coverage with its definition. Choosing a ghat
   opens its main finding, evidence and gaps, citations, and a next action
   labelled as a recommendation. The selection follows you to the other pages.
3. **Historical Analysis**: ghat, test (DO, BOD, pH), year and phase filters; readings
   outside the limit by year; full-width panels for before, during and one
   week after immersion with the benchmark line (and the 2 mg/l ranking
   threshold, labelled as such); an all-ghats comparison; a plain-language
   interpretation under every chart; missing readings marked n/s.
4. **Evidence & Data Gaps**: a searchable, filterable record browser (ghat, test,
   year, festival, phase, record type, free text) showing site and test names as printed,
   reading and unit, applicable limit and status, report file and PDF page,
   record type (numeric, BDL, not sampled, absent table) and caveats; a grid of
   which samples exist; definitions of the record types; the source reports.
5. **Officer Brief**: English / हिंदी language control that updates the preview
   only, a Download action for the selected language, and a separate Copy
   action that shows the text with a copy button. Generated on the day from the
   fixed templates.

Colour is never the only signal: every chart has a text legend, bars carry
counts, missing cells read n/s or "no table", and green appears only on a badge
saying pH was in range on every reading for that one parameter. The product
specification is summarised in `SPEC.md`.

## Reusing the tool for another event or dataset
`settings.toml` holds the organisation, the target event name and date, the
dataset paths and the list of source reports (year, file, title, pages, URL).
The target event is optional planning context: it appears in the recommendations,
the briefs and a footnote on the Overview, never in the permanent header, and
there is no countdown. The
years covered are read from the data itself; the brief date is the day it is
generated. To add a future verified dataset: parse the new report with the
hackathon `tools/parse_visarjan.py`, append its rows to the readings CSV, add
the report to `settings.toml`, run the tests. Nothing in the ranking rules is
configurable there.

## How the ranking works
See the docstring in `visarjan_sentinel/ranking.py`. In short:
exceedance share = readings outside Class B limits / numeric readings of DO, BOD
and pH, across all years, festivals and phases. Tier 1 = any DO reading below
2 mg/l. Order = tier, then share, then lowest recorded DO. Missing and BDL
readings are in neither numerator nor denominator. Coverage is shown separately
and does not change the score.

## Project layout
```
app.py                       entry point: theme, navigation, data load
views/                       one file per page (overview, priorities, analysis, evidence, brief)
settings.toml                organisation, optional target event, dataset paths, source reports
visarjan_sentinel/
  config.py                  loads settings.toml into a Context
  ui/theme.py                design tokens, CSS, badges, legends
  ui/data.py                 cached pipeline run, reading categories, plain-language helpers
  ui/charts.py               Altair chart builders
  ui/state.py                selected ghat and brief language across pages
  sources.py                 ghat names, short labels, parameter meanings, glossary, fixed notes
  loader.py                  CSV -> full expected grid with four cell states
  rules.py                   CPCB Class B limits from the criteria CSV, status per reading
  ranking.py                 exceedance share, severity tier, reasons, coverage
  build.py                   writes outputs/ranking.json, evidence.csv, validation.json
  brief.py                   English and Hindi brief templates
data/                        hackathon CSVs, data dictionary, PDF verification note
tests/                       pytest suite, including a Streamlit AppTest smoke test
outputs/                     generated artefacts
```

## What works, what does not
- Works: loader, grid, validation, rule engine, ranking, evidence export,
  dashboard, English and Hindi briefs, central settings file, 56 automated tests.
- Does not work yet: the Hindi text is a template draft and **must be reviewed by
  a fluent Hindi-speaking teammate** before it is forwarded. There is no map view.
  The statewide MP file is not used. On phone-width screens the evidence table
  scrolls sideways inside its own frame.

## Limitations and known gaps
- Readings are historical (2023 to 2025). They do not describe water today, and
  the tool makes no claim about health effects or present-day safety.
- Total coliform, a Class B requirement, was never tested, so full Class B
  compliance cannot be assessed.
- Only DO, BOD and pH have a Class B limit and were measured. COD, solids,
  turbidity, conductivity and the four metals are shown, not scored.
- Metal detection limits and methods appear to differ between years. Metal
  values are not comparable across years.
- Units are not printed in the reports; standard units are assumed.
- Bairagarh and Malikhedi have no Durga 2025 table and only a "during" sample for
  Ganesh 2025, so their most recent data is thin.
- "Rani Kamlapati ghat / Kamla Park kund" is a medium-confidence site match and
  may cover two places. It is kept as one entry with a visible warning.
- One sample per phase per event; no replicates; no sampling dates in the data.

## Data used
- Repo data: `data/bhopal_ghats_2023_2025.csv`, `data/cpcb_water_quality_criteria.csv`,
  `data/DATA_DICTIONARY.md` (copied from the hackathon repo, track 2).
- Source PDFs: MPPCB visarjan reports 2023, 2024 and 2025, links in
  `data/DATA_DICTIONARY.md`.
- The four zero-DO readings were checked against the PDFs: `data/VERIFICATION.md`.
- Extra data: none. No external APIs, no live government systems.

## Licence
MIT, see `LICENSE`.
