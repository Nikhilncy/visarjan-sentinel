# Verification of the four zero dissolved-oxygen readings

Checked on 11 October 2026 by extracting page text from the original MPPCB PDFs
(pypdf, no layout). The parsed CSV values match what the reports print.

| CSV row | Report | Page | Printed line |
|---|---|---|---|
| 2023 Ganesh, Bairagarh, after | Idol_immer._Report_23_CPCB.pdf | 26 | `5 D.Oxygen 5.6 4.5 0` |
| 2023 Durga, Bairagarh, pre | Idol_immer._Report_23_CPCB.pdf | 60 | `4 D.Oxygen 0 0 4.2` |
| 2023 Durga, Bairagarh, during | Idol_immer._Report_23_CPCB.pdf | 60 | `4 D.Oxygen 0 0 4.2` |
| 2025 Ganesh, Bairagarh, during | Ganesh_and_Durga_visarjan_report-2025.pdf | 28 | `5 D.Oxygen 0` |

Also checked: Malikhedi kund, 2025 Ganesh, during, DO 0.6 mg/l, page 29, printed
as `5 D.Oxygen 0.6`.

Note on the 2025 Ganesh tables for Bairagarh and Malikhedi: the report prints a
single value per parameter. The pH row carries `*` (pre) and `**` (after),
marking those phases as not sampled. The hackathon parser assigned the single
value to the "during" column by its horizontal position. This tool keeps that
assignment and shows pre and after as "not sampled".
