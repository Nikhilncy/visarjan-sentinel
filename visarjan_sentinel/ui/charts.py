"""Altair chart builders. Every chart gets a legend in HTML next to it (theme.legend), so
colour never carries meaning alone. Units and the historical period are in the titles the
pages write above each chart."""

from __future__ import annotations

import altair as alt
import pandas as pd

from visarjan_sentinel.ranking import TIER1_DO_THRESHOLD
from visarjan_sentinel.sources import PHASE_LABELS, PHASES

from . import theme as T
from .data import BOD, DO, PH, Model, short

STATUS_SCALE = alt.Scale(domain=T.CAT_ORDER[:3], range=[T.RED, T.AMBER, T.TEAL])
TIP_COMMON = [alt.Tooltip("Event:N"), alt.Tooltip("Phase:N"), alt.Tooltip("Category:N"),
              alt.Tooltip("report_file:N", title="Report"), alt.Tooltip("source_page:N", title="PDF page")]


def selection_param() -> alt.Parameter:
    return alt.selection_point(name="ghat_sel", fields=["site"], on="click", clear=False)


def _ghat_axis(m: Model, labels: bool = True) -> alt.Y:
    return alt.Y("Ghat label:N", sort=m.label_order, title=None,
                 axis=alt.Axis(labelFontSize=12, labelFontWeight=600, labelColor=T.NAVY, labelLimit=260,
                               ticks=False, domain=False) if labels else None)


def queue_chart(m: Model, selected_site: str) -> alt.LayerChart:
    """One stacked bar per ghat: critical / outside / within numeric scored readings, in rank order."""
    sel = selection_param()
    d = m.scored[m.scored["Category"] != T.CAT_MISS]
    counts = d.groupby(["site", "Ghat label", "Category"], as_index=False).size().rename(columns={"size": "n"})
    counts["order"] = counts["Category"].map({c: i for i, c in enumerate(T.CAT_ORDER)})
    x_max = max(g["numeric_scored"] for g in m.ghats) * 1.5
    labels = pd.DataFrame([{"site": g["site"], "Ghat label": m.label(g["site"]), "x": g["numeric_scored"],
                            "text": f"{g['exceedances']} of {g['numeric_scored']} outside"} for g in m.ghats])
    sel_bg = pd.DataFrame([{"site": s, "Ghat label": m.label(s), "x": x_max} for s in m.sites if s == selected_site])
    bg = alt.Chart(sel_bg).mark_bar(color=T.SELECT_BG, size=30).encode(y=_ghat_axis(m), x=alt.X("x:Q"))
    bars = (alt.Chart(counts).mark_bar(size=18, cornerRadiusEnd=3).encode(
        y=_ghat_axis(m),
        x=alt.X("n:Q", title="Numeric readings of DO, BOD and pH", stack="zero",
                scale=alt.Scale(domain=[0, x_max]), axis=alt.Axis(tickMinStep=10)),
        order=alt.Order("order:Q"),
        color=alt.Color("Category:N", scale=STATUS_SCALE),
        tooltip=[alt.Tooltip("Ghat label:N", title="Ghat"), alt.Tooltip("Category:N"), alt.Tooltip("n:Q", title="Readings")],
    ).add_params(sel))
    txt = alt.Chart(labels).mark_text(align="left", dx=6, fontSize=11, color=T.TEXT).encode(
        y=_ghat_axis(m), x="x:Q", text="text:N")
    return T.base_config(alt.layer(bg, bars, txt).properties(height=len(m.sites) * 38 + 10, width="container"))


def coverage_chart(m: Model) -> alt.LayerChart:
    """Expected readings per ghat split into sampled / not sampled / no table. Separate from the score."""
    sel = selection_param()
    rows, labels = [], []
    for s in m.sites:
        c = m.by_site[s]["coverage"]
        for part, n, o in (("Sampled", c["sampled"], 0), ("Not sampled", c["not_sampled"], 1), ("No table", c["absent_table"], 2)):
            rows.append({"site": s, "Ghat label": m.label(s), "Part": part, "n": n, "order": o})
        labels.append({"site": s, "Ghat label": m.label(s), "x": c["expected"], "text": f"{c['sampled_share']:.0%} sampled"})
    x_max = max(m.by_site[s]["coverage"]["expected"] for s in m.sites) * 1.4
    bars = (alt.Chart(pd.DataFrame(rows)).mark_bar(size=18, cornerRadiusEnd=3).encode(
        y=_ghat_axis(m, labels=False),
        x=alt.X("n:Q", title="Expected readings, all 13 tests", stack="zero", scale=alt.Scale(domain=[0, x_max])),
        order=alt.Order("order:Q"),
        color=alt.Color("Part:N", scale=alt.Scale(domain=["Sampled", "Not sampled", "No table"],
                                                  range=[T.SAMPLED, T.GREY, T.GREY_DARK])),
        tooltip=[alt.Tooltip("Ghat label:N", title="Ghat"), alt.Tooltip("Part:N"), alt.Tooltip("n:Q", title="Readings")],
    ).add_params(sel))
    txt = alt.Chart(pd.DataFrame(labels)).mark_text(align="left", dx=6, fontSize=11, color=T.TEXT).encode(
        y=alt.Y("Ghat label:N", sort=m.label_order), x="x:Q", text="text:N")
    return T.base_config(alt.layer(bars, txt).properties(height=len(m.sites) * 38 + 10, width="container"))


def _limit_layers_x(m: Model, param: str, data: pd.DataFrame) -> list:
    """Benchmark marks along a horizontal value axis."""
    if param == PH:
        lo, hi = m.limits[PH]["low"], m.limits[PH]["high"]
        band = alt.Chart(pd.DataFrame({"lo": [lo], "hi": [hi]})).mark_rect(color=T.SELECT_BG, opacity=0.9).encode(x="lo:Q", x2="hi:Q")
        return [band] + [alt.Chart(pd.DataFrame({"x": [v]})).mark_rule(color=T.NAVY, strokeDash=[4, 3], strokeWidth=1.2).encode(x="x:Q") for v in (lo, hi)]
    v = m.do_lim if param == DO else m.bod_lim
    layers = [alt.Chart(pd.DataFrame({"x": [v]})).mark_rule(color=T.NAVY, strokeDash=[4, 3], strokeWidth=1.2).encode(x="x:Q")]
    if param == DO:
        layers.append(alt.Chart(pd.DataFrame({"x": [TIER1_DO_THRESHOLD]})).mark_rule(color=T.RED, strokeDash=[2, 3], strokeWidth=1).encode(x="x:Q"))
    return layers


def _limit_layers_y(m: Model, param: str, data: pd.DataFrame) -> list:
    """Benchmark marks along a vertical value axis, drawn from the same data so they can layer."""
    if param == PH:
        lo, hi = m.limits[PH]["low"], m.limits[PH]["high"]
        band = alt.Chart(data).mark_rect(color=T.SELECT_BG, opacity=0.9).encode(y=alt.datum(lo), y2=alt.datum(hi))
        return [band] + [alt.Chart(data).mark_rule(color=T.NAVY, strokeDash=[4, 3], strokeWidth=1.2).encode(y=alt.datum(v)) for v in (lo, hi)]
    v = m.do_lim if param == DO else m.bod_lim
    layers = [alt.Chart(data).mark_rule(color=T.NAVY, strokeDash=[4, 3], strokeWidth=1.2).encode(y=alt.datum(v))]
    if param == DO:
        layers.append(alt.Chart(data).mark_rule(color=T.RED, strokeDash=[2, 3], strokeWidth=1).encode(y=alt.datum(TIER1_DO_THRESHOLD)))
    return layers


def axis_title(param: str) -> str:
    return {DO: "DO (mg/l)", BOD: "BOD (mg/l)", PH: "pH"}[param]


def strip_chart(m: Model, param: str) -> alt.LayerChart:
    """Every reading of one parameter for all ghats, as dots against the benchmark."""
    sel = selection_param()
    d = m.scored[m.scored["parameter"] == param]
    pts = d[d["Category"] != T.CAT_MISS]
    miss = d[d["Category"] == T.CAT_MISS].groupby(["site", "Ghat label"], as_index=False).size()
    miss["text"] = miss["size"].astype(str) + " missing"
    top = float(pts["value_num"].max()) if len(pts) else 0.0
    hi_ref = {DO: m.do_lim, BOD: m.bod_lim, PH: m.limits[PH]["high"]}[param]
    x_max = max(top, hi_ref) * 1.2
    x_min = -x_max * 0.02 if param != PH else 0
    dots = (alt.Chart(pts).mark_circle(size=70, opacity=0.9, stroke=T.SURFACE, strokeWidth=1.5).encode(
        y=_ghat_axis(m), x=alt.X("value_num:Q", title=axis_title(param), scale=alt.Scale(domain=[x_min, x_max], nice=False)),
        color=alt.Color("Category:N", scale=STATUS_SCALE),
        tooltip=[alt.Tooltip("Ghat:N"), alt.Tooltip("Reading:N", title=axis_title(param))] + TIP_COMMON,
    ).add_params(sel))
    txt = alt.Chart(miss).mark_text(align="right", fontSize=10, color=T.MUTED).encode(
        y=alt.Y("Ghat label:N", sort=m.label_order), x=alt.datum(x_max * 0.995), text="text:N")
    return T.base_config(alt.layer(*_limit_layers_x(m, param, pts), dots, txt)
                         .properties(height=len(m.sites) * 34 + 10, width="container"))


def phase_chart(m: Model, site: str, param: str, phase: str, y_max: float, years: list[int] | None = None) -> alt.LayerChart:
    """One full-width panel: a ghat's readings of one parameter in one phase, by festival event."""
    d = m.scored[(m.scored["site"] == site) & (m.scored["parameter"] == param) & (m.scored["phase"] == phase)]
    events = m.events
    if years is not None:
        d = d[d["year"].isin(years)]
        events = [e for e in m.events if int(e.split()[-1]) in years]
    x_axis = alt.X("Event:N", sort=events, title=None, axis=alt.Axis(labelAngle=0, labelFontSize=11, labelPadding=6))
    tip = [alt.Tooltip("Reading:N", title=axis_title(param))] + TIP_COMMON
    y_scale = alt.Scale(domain=[0, y_max]) if param != PH else alt.Scale(domain=[5, 10])
    bars = (alt.Chart(d).transform_filter(alt.datum.Category != T.CAT_MISS)
            .mark_bar(size=26, cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
            .encode(x=x_axis, y=alt.Y("value_num:Q", title=axis_title(param), scale=y_scale, axis=alt.Axis(tickCount=4)),
                    color=alt.Color("Category:N", scale=STATUS_SCALE), tooltip=tip))
    if param == PH:  # bars from the bottom of a zoomed axis mislead; use points for pH
        bars = (alt.Chart(d).transform_filter(alt.datum.Category != T.CAT_MISS)
                .mark_circle(size=110, stroke=T.SURFACE, strokeWidth=1.5)
                .encode(x=x_axis, y=alt.Y("value_num:Q", title=axis_title(param), scale=y_scale, axis=alt.Axis(tickCount=5)),
                        color=alt.Color("Category:N", scale=STATUS_SCALE), tooltip=tip))
    # Value labels sit inside the top of a tall bar (white on the fill) and above a short bar,
    # so they never cross the benchmark line.
    inside_min = y_max * 0.18
    label_in = (alt.Chart(d).transform_filter((alt.datum.Category != T.CAT_MISS) & (alt.datum.value_num >= inside_min))
                .mark_text(fontSize=11, fontWeight=600, color="#FFFFFF", baseline="top", dy=4)
                .encode(x=x_axis, y="value_num:Q", text="Reading:N", tooltip=tip))
    label_out = (alt.Chart(d).transform_filter((alt.datum.Category != T.CAT_MISS) & (alt.datum.value_num < inside_min))
                 .mark_text(fontSize=11, fontWeight=600, color=T.TEXT, baseline="bottom", dy=-4)
                 .encode(x=x_axis, y="value_num:Q", text="Reading:N", tooltip=tip))
    if param == PH:  # points, not bars: always label beside the point
        label_in = alt.Chart(d).transform_filter(alt.datum.value_num < 0).mark_text().encode(x=x_axis, y="value_num:Q")
        label_out = (alt.Chart(d).transform_filter(alt.datum.Category != T.CAT_MISS)
                     .mark_text(fontSize=11, fontWeight=600, color=T.TEXT, baseline="bottom", dy=-9)
                     .encode(x=x_axis, y="value_num:Q", text="Reading:N", tooltip=tip))
    value_labels = alt.layer(label_in, label_out)
    missing = (alt.Chart(d).transform_filter(alt.datum.Category == T.CAT_MISS)
               .mark_text(text="n/s", fontSize=11, color=T.MUTED, baseline="bottom", dy=-3)
               .encode(x=x_axis, y=alt.datum(0 if param != PH else 5),
                       tooltip=[alt.Tooltip("Event:N"), alt.Tooltip("Phase:N"), alt.Tooltip("Reading:N", title="Record")]))
    layers = _limit_layers_y(m, param, d) + [bars, value_labels, missing]
    return T.base_config(alt.layer(*layers).properties(
        height=170, width="container",
        title=alt.Title(PHASE_LABELS[phase], fontSize=12, fontWeight=600, color=T.NAVY, anchor="start")))


def year_chart(m: Model, site: str, param: str, years: list[int] | None = None, phases: list[str] | None = None) -> alt.LayerChart:
    """Readings of one parameter at one ghat per year: how many outside the limit, of how many numeric."""
    d = m.scored[(m.scored["site"] == site) & (m.scored["parameter"] == param) & (m.scored["Category"] != T.CAT_MISS)]
    if years is not None:
        d = d[d["year"].isin(years)]
    if phases is not None:
        d = d[d["phase"].isin(phases)]
    counts = d.groupby(["year", "Category"], as_index=False).size().rename(columns={"size": "n"})
    counts["order"] = counts["Category"].map({c: i for i, c in enumerate(T.CAT_ORDER)})
    tot = d.groupby("year").agg(n=("value_num", "size"), out=("Category", lambda s: int((s != T.CAT_IN).sum()))).reset_index()
    tot["text"] = tot["out"].astype(str) + " of " + tot["n"].astype(str) + " outside"
    years_df = pd.DataFrame({"year": years if years is not None else m.years})
    x = alt.X("year:O", title=None, axis=alt.Axis(labelAngle=0, labelFontSize=11))
    bars = alt.Chart(counts).mark_bar(size=34, cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
        x=x, y=alt.Y("n:Q", title="Numeric readings", stack="zero", axis=alt.Axis(tickMinStep=1)),
        order=alt.Order("order:Q"), color=alt.Color("Category:N", scale=STATUS_SCALE),
        tooltip=[alt.Tooltip("year:O", title="Year"), alt.Tooltip("Category:N"), alt.Tooltip("n:Q", title="Readings")])
    txt = alt.Chart(tot).mark_text(fontSize=11, color=T.TEXT, baseline="bottom", dy=-4).encode(x=x, y="n:Q", text="text:N")
    base = alt.Chart(years_df).mark_text(text="", opacity=0).encode(x=x)  # keeps every selected year on the axis
    return T.base_config(alt.layer(base, bars, txt).properties(height=170, width="container"))


GRID_COLORS = {"Sampled": T.SAMPLED, "Partly sampled": "#FDE68A", "Not sampled": "#CBD5E1", "No table in report": T.GREY_DARK}


def coverage_grid_frame(m: Model, site: str) -> pd.DataFrame:
    ev = m.evidence[m.evidence["site"] == site]
    rows = []
    for e in m.events:
        for ph in PHASES:
            cell = ev[(ev["Event"] == e) & (ev["phase"] == ph)]
            n_exp = len(cell)
            n_samp = int(cell["state"].isin(["numeric", "bdl"]).sum())
            if n_exp and (cell["state"] == "absent_table").all():
                status, txt = "No table in report", "no table"
            elif n_samp == 0:
                status, txt = "Not sampled", "not sampled"
            elif n_samp < n_exp:
                status, txt = "Partly sampled", f"{n_samp} of {n_exp} tests"
            else:
                status, txt = "Sampled", f"{n_samp} tests"
            pages = sorted({p for p in cell["source_page"] if p})
            rows.append({"Event": e, "Phase": PHASE_LABELS[ph], "Status": status, "text": txt, "Page": ", ".join(pages) or "none"})
    return pd.DataFrame(rows)


def coverage_grid(m: Model, site: str) -> alt.LayerChart:
    gdf = coverage_grid_frame(m, site)
    phase_order = [PHASE_LABELS[p] for p in PHASES]
    heat = alt.Chart(gdf).mark_rect(stroke=T.SURFACE, strokeWidth=3, cornerRadius=4).encode(
        x=alt.X("Phase:N", sort=phase_order, title=None,
                axis=alt.Axis(orient="top", labelAngle=0, labelFontSize=12, labelFontWeight=600, labelColor=T.NAVY,
                              ticks=False, domain=False, labelLimit=220)),
        y=alt.Y("Event:N", sort=m.events, title=None,
                axis=alt.Axis(labelFontSize=12, labelFontWeight=600, labelColor=T.NAVY, ticks=False, domain=False)),
        color=alt.Color("Status:N", scale=alt.Scale(domain=list(GRID_COLORS), range=list(GRID_COLORS.values()))),
        tooltip=["Event:N", "Phase:N", "Status:N", alt.Tooltip("text:N", title="Detail"), alt.Tooltip("Page:N", title="Report page")])
    txt = alt.Chart(gdf).mark_text(fontSize=11, fontWeight=500).encode(
        x=alt.X("Phase:N", sort=phase_order), y=alt.Y("Event:N", sort=m.events), text="text:N",
        color=alt.condition(alt.datum.Status == "No table in report", alt.value("#FFFFFF"), alt.value(T.TEXT)))
    return T.base_config(alt.layer(heat, txt).properties(height=len(m.events) * 44 + 40, width="container"))
