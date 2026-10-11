"""Fixed facts about the source documents and the seven Bhopal ghats.

Ghat names and fixed notes come from tracks/02-visarjan-ghat-watch/data/DATA_DICTIONARY.md
in the hackathon repo. Report metadata and file paths come from settings.toml.
Nothing is measured or inferred in this file.
"""

from .config import CONTEXT, PROJECT_ROOT, Report  # noqa: F401  (Report re-exported for callers)

DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

# Paths and source reports come from settings.toml so a new event or dataset
# needs no code change. Years in the data must each have a report entry.
READINGS_CSV = CONTEXT.readings_csv
CPCB_CSV = CONTEXT.cpcb_csv
REPORTS = CONTEXT.reports

# Chronological order of festivals within a year.
FESTIVAL_ORDER = {"Ganesh": 0, "Durga": 1}
PHASES = ("pre", "during", "after")
PHASE_LABELS = {"pre": "before immersion", "during": "during immersion", "after": "one week after"}

# The seven standard ghat names used in the Bhopal CSV. The order here is only
# used for stable display when scores tie; it carries no meaning.
BHOPAL_GHATS = (
    "Bairagarh (Sant Hirdaram) kund",
    "Khatlapura ghat",
    "Prempura ghat",
    "Rani Kamlapati ghat / Kamla Park kund",
    "Hathaikheda dam / kund",
    "Malikhedi kund",
    "Shahpura lake ghat",
)

# Short display labels for tight spaces (charts, pills). Display only; the data keeps the full name.
GHAT_SHORT_NAMES = {
    "Bairagarh (Sant Hirdaram) kund": "Bairagarh kund",
    "Khatlapura ghat": "Khatlapura",
    "Prempura ghat": "Prempura",
    "Rani Kamlapati ghat / Kamla Park kund": "Rani Kamlapati / Kamla Park",
    "Hathaikheda dam / kund": "Hathaikheda",
    "Malikhedi kund": "Malikhedi",
    "Shahpura lake ghat": "Shahpura",
}

# Plain-language meaning of each parameter, from the data dictionary. Shown next to the numbers.
PARAMETER_MEANING = {
    "Dissolved oxygen": "Oxygen in the water. Fish and other life need it. Bathing water should have at least 5 mg/l; "
                        "0 mg/l supports no fish life at all.",
    "BOD": "Biochemical oxygen demand: how much organic waste is using up the oxygen. Bathing water should be 3 mg/l or less.",
    "pH": "Whether the water is acidic or alkaline. 7 is neutral; 6.5 to 8.5 is the accepted range.",
    "COD": "Chemical oxygen demand: total pollution that uses oxygen. No Class B limit.",
    "Total solids": "Everything left after the water dries. No Class B limit.",
    "Dissolved solids": "Solids dissolved in the water. No Class B limit.",
    "Suspended solids": "Particles floating in the water. Not tested in every year. No Class B limit.",
    "Turbidity": "Cloudiness. No Class B limit.",
    "Conductivity": "Dissolved salts. No Class B limit (Class E caps it at 2,250).",
    "Chromium": "Heavy metal, often from idol paint. No Class B limit.",
    "Lead": "Heavy metal, often from idol paint. No Class B limit.",
    "Zinc": "Heavy metal, often from idol paint. No Class B limit.",
    "Copper": "Heavy metal, often from idol paint. No Class B limit.",
}

# Plain-language glossary for the interface and briefs.
GLOSSARY = {
    "Readings outside the limit": "How many of the numeric DO, BOD and pH readings fell outside the CPCB Class B "
                                   "(outdoor bathing) limit, out of all numeric readings of those three tests. "
                                   "Missing and BDL readings are in neither number.",
    "Data coverage": "How many of the readings the reports should contain for a ghat were actually sampled: "
                     "every festival event × 3 phases × the tests printed for that event. Shown separately "
                     "from the ranking and never changes it.",
    "BDL": "Below detection limit. The lab looked for it and found less than its instrument can measure. "
           "Very low, but not zero and not missing. Only metals were reported this way.",
    "Not sampled": "The table exists but that cell is blank or marked * / **. No measurement was taken. "
                   "Missing, never clean.",
    "Absent table": "The report has no table at all for that ghat and festival. The whole event is unmeasured. "
                    "Missing, never clean.",
    "Numeric zero": "A printed reading of 0 is a real measurement (for dissolved oxygen it means no oxygen), "
                    "not a gap.",
    "Historical reading": "A measurement taken in a past year. It tells you where problems have been recorded. "
                          "It cannot tell you the condition of the water today; only a fresh sample can.",
}

SITE_MATCH_WARNING = (
    "Site name match is MEDIUM confidence. Ganesh tables in the reports call this "
    "'Rani Kamlapati, Kamla Park, Murti Visarjan Kund' and Durga tables call it "
    "'Rani Kamlapati Visarjan Ghat (Lower Lake)'. These may be two different places. "
    "This tool keeps one combined entry and does not claim they are the same site."
)

UNITS_NOTE = (
    "The MPPCB reports print no units. Units shown are the standard ones for each test "
    "(mg/l for most, NTU for turbidity, µS/cm for conductivity) and are assumed."
)

COLIFORM_NOTE = (
    "CPCB Class B (outdoor bathing) also requires total coliform of 500 MPN/100 ml or "
    "less. Coliform was not tested at any ghat in any year, so full Class B compliance "
    "cannot be assessed from these reports."
)
