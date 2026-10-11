# Visarjan Sentinel: product specification (summary)

Single source of truth for product requirements, UI structure, data integrity and
release checks. Condensed from the master product specification and the UI/UX
redesign brief supplied on 11 October 2026.

## Identity and purpose
- Product: **Visarjan Sentinel**. Descriptor: **Water Quality Intelligence**.
- User: a municipal officer prioritising water-quality follow-up at immersion ghats
  in Bhopal.
- Four questions the product answers: which ghats need follow-up first; why each
  is prioritised; how complete the evidence is and what is missing; what follow-up
  action should be considered.
- Not a PDF viewer, not an event poster, not a generic analytics dashboard.

## Pages
1. **Overview**: title "Water Quality Overview"; small historical-data indicator;
   featured highest-priority ghat with verified reasons and an evidence link; four
   explained metrics; one horizontal comparison chart in ranking order (no rotated
   labels); key finding, missing-data warning, limitations; brief preview buttons.
   No full ranking table here.
2. **Ghat Priorities**: all seven ghats in the ranking engine's order with rank,
   tier, concise reason, readings outside limits with denominator, lowest
   historical DO, coverage with definition, warnings. Selecting a ghat shows the
   main finding, evidence and gaps, citations, and a labelled recommendation.
3. **Historical Analysis**: filters for ghat, test (DO, BOD, pH), years, phases;
   readings by year; full-width phase panels with the Class B benchmark and the
   2 mg/l ranking threshold labelled as such; all-ghats comparison; a plain-language
   interpretation under every chart; missing readings visible.
4. **Evidence & Data Gaps**: searchable, filterable records with site and test as
   printed, reading and unit, applicable limit and status, year, festival, phase,
   report file and PDF page, record type (numeric, BDL, not sampled, absent table),
   caveats; sample-coverage grid; record-type definitions; source reports.
5. **Officer Brief**: English / Hindi selector that updates the preview only;
   separate Download and Copy actions; brief generated on the day from the fixed
   templates.

## Visual system
Navy #142B4A, action blue #2563EB, background #F5F7FA, surface #FFFFFF, text
#172B4D, secondary #64748B. Red = critical historical findings (DO below 2 mg/l),
amber = other exceedances and warnings, teal = neutral data marks (within limit,
sampled), grey = missing evidence, green only for a qualified single-parameter
badge. 8px spacing system, one content width, subtle borders, no sticky banners,
no emoji, no gradients. Colour never carries meaning without a label.

## Data integrity (non-negotiable)
- Loader, rules, ranking, citations and brief templates are preserved; the
  seven-ghat order is the validated one.
- Numeric reading (including printed zero), BDL, not sampled and absent table stay
  distinct. Missing is never clean, safe, zero or compliant.
- Coverage is shown beside the rank and never changes it.
- CPCB Class B limits come from the supplied criteria CSV: DO at least 5 mg/l, BOD
  at most 3 mg/l, pH 6.5 to 8.5. No limits are invented for other tests.
- Total coliform was not tested; full Class B compliance cannot be assessed.
- The Rani Kamlapati / Kamla Park medium-confidence site caveat is shown wherever
  that ghat appears.
- Historical readings do not establish current conditions. Recommendations are
  decision support; the decision rests with the responsible authority.

## Reusable context
`settings.toml` holds the organisation, optional target event, dataset paths and
source reports. The permanent header never shows an event date or countdown. Data
years come from the data; the brief date is the generation date.

## Acceptance checks
All pages navigate; ranking identical to the pipeline output; selection carries
across pages; charts show units and benchmarks; language switch updates the preview
without downloading; downloads export the selected language; no clipped text or
horizontal overflow at desktop and phone widths; full test suite passes; checks
that could not be performed are reported honestly.
