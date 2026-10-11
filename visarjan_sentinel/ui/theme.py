"""Design tokens, CSS and small HTML helpers shared by every page."""

from __future__ import annotations

from pathlib import Path

import altair as alt
import streamlit as st

PRODUCT = "Visarjan Sentinel"
DESCRIPTOR = "Water Quality Intelligence"

NAVY, BLUE, BG, SURFACE = "#142B4A", "#2563EB", "#F5F7FA", "#FFFFFF"
TEXT, MUTED, BORDER, GRID = "#172B4D", "#64748B", "#E2E8F0", "#EEF2F7"
RED, RED_BG = "#B42318", "#FEF3F2"
AMBER, AMBER_TX, AMBER_BG = "#D97706", "#B54708", "#FFFAEB"
GREY, GREY_BG, GREY_DARK = "#94A3B8", "#F1F5F9", "#64748B"
GREEN, GREEN_BG = "#067647", "#ECFDF3"
SELECT_BG = "#EFF6FF"
TEAL, TEAL_BG = "#0D9488", "#CCFBF1"  # neutral data marks (within limit, sampled)
SAMPLED = "#99F6E4"

# Reading categories used everywhere a status is drawn. Colour never travels without the label.
CAT_CRIT = "Critical: dissolved oxygen below 2 mg/l (ranking threshold)"
CAT_OUT = "Outside Class B limit"
CAT_IN = "Within limit"
CAT_MISS = "Missing: not sampled or no table"
CAT_ORDER = [CAT_CRIT, CAT_OUT, CAT_IN, CAT_MISS]
CAT_COLOR = {CAT_CRIT: RED, CAT_OUT: AMBER, CAT_IN: TEAL, CAT_MISS: GREY}

BRAND_SVG = (
    '<svg width="212" height="40" viewBox="0 0 236 40" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
    '<rect x="0.5" y="3.5" width="33" height="33" rx="7" fill="#FFFFFF" fill-opacity="0.12" stroke="#FFFFFF" stroke-opacity="0.35"/>'
    '<path d="M17 10.5c-3.6 4.9-6.2 8.4-6.2 11.6a6.2 6.2 0 0 0 12.4 0c0-3.2-2.6-6.7-6.2-11.6z" fill="#FFFFFF" fill-opacity="0.95"/>'
    '<path d="M8 28.5c2.2-1.6 4.4-1.6 6.6 0 2.2 1.6 4.4 1.6 6.6 0 2.2-1.6 4.4-1.6 6.6 0" stroke="#93C5FD" stroke-width="1.6" stroke-linecap="round" fill="none"/>'
    '<text x="44" y="19" font-family="Inter, -apple-system, Segoe UI, Roboto, sans-serif" font-size="13" font-weight="700" letter-spacing="2" fill="#FFFFFF">VISARJAN SENTINEL</text>'
    '<text x="44" y="34" font-family="Inter, -apple-system, Segoe UI, Roboto, sans-serif" font-size="11.5" fill="#BFD3EE">Water Quality Intelligence</text>'
    "</svg>"
)

MARK_SVG = (
    '<svg width="30" height="30" viewBox="0 0 34 34" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
    f'<rect x="0.5" y="0.5" width="33" height="33" rx="7" fill="{NAVY}"/>'
    '<path d="M17 7.5c-3.6 4.9-6.2 8.4-6.2 11.6a6.2 6.2 0 0 0 12.4 0c0-3.2-2.6-6.7-6.2-11.6z" fill="#FFFFFF" fill-opacity="0.95"/>'
    '<path d="M8 25.5c2.2-1.6 4.4-1.6 6.6 0 2.2 1.6 4.4 1.6 6.6 0 2.2-1.6 4.4-1.6 6.6 0" stroke="#93C5FD" stroke-width="1.6" stroke-linecap="round"/>'
    "</svg>"
)

CSS = f"""
<style>
.block-container {{ padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1120px; }}
[data-testid="stToolbar"], .stAppDeployButton, #MainMenu {{ display: none; }}
header[data-testid="stHeader"] {{ background: transparent; height: 1.5rem; pointer-events: none; }}
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], [data-testid="stSidebarCollapseButton"],
[data-testid="stLogo"], [data-testid="stHeaderLogo"] {{ display: none !important; }}
[data-testid="stSidebar"] * {{ color: #E6EEF8; }}
[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"] {{ border-radius: 6px; }}
[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"]:hover {{ background: rgba(255,255,255,0.08); }}
[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"][aria-current="page"] {{ background: rgba(255,255,255,0.14); }}
[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] span {{ color: #FFFFFF; font-weight: 500; }}
[data-testid="stSidebar"] .vs-brand {{ display: flex; align-items: center; gap: 10px; padding: 4px 0 12px 0;
   border-bottom: 1px solid rgba(255,255,255,0.14); margin-bottom: 8px; }}
[data-testid="stSidebar"] .vs-brand .name {{ font-size: 0.85rem; font-weight: 700; letter-spacing: 0.14em; color: #FFFFFF; line-height: 1.1; }}
[data-testid="stSidebar"] .vs-brand .tag {{ font-size: 0.78rem; color: #BFD3EE; margin-top: 2px; }}
[data-testid="stSidebar"] .vs-side-note {{ font-size: 0.75rem; color: #BFD3EE; line-height: 1.5; margin-top: 0; padding-top: 0; }}
[data-testid="stSidebar"] .vs-side-note strong {{ color: #FFFFFF; }}
[data-testid="stVerticalBlockBorderWrapper"] {{ background: {SURFACE}; }}
[data-testid="stMarkdownContainer"] h1 {{ font-size: 1.5rem; font-weight: 600; color: {NAVY}; margin: 0 0 2px 0; padding: 0; letter-spacing: -0.01em; }}
[data-testid="stMarkdownContainer"] h2 {{ font-size: 1.15rem; font-weight: 600; color: {NAVY}; margin: 0 0 2px 0; padding: 0; letter-spacing: -0.01em; }}
[data-testid="stMarkdownContainer"] h3 {{ font-size: 1rem; font-weight: 600; color: {NAVY}; margin: 0 0 4px 0; padding: 0; }}
[data-testid="stMarkdownContainer"] .vs-purpose {{ font-size: 0.9rem; color: {MUTED}; margin: 0 0 16px 0; }}
[data-testid="stMarkdownContainer"] .vs-indicator {{ display: inline-block; font-size: 0.78rem; color: {MUTED}; border: 1px solid {BORDER};
   background: {SURFACE}; border-radius: 999px; padding: 3px 10px; margin: -8px 0 24px 0; }}
[data-testid="stMarkdownContainer"] .vs-indicator .dot {{ display: inline-block; width: 8px; height: 8px; border-radius: 50%;
   background: {AMBER}; margin-right: 6px; vertical-align: middle; }}
[data-testid="stMarkdownContainer"] .vs-feature {{ background: {SURFACE}; border: 1px solid {BORDER}; border-left: 4px solid {RED};
   border-radius: 6px; padding: 16px 20px; margin-bottom: 24px; }}
[data-testid="stMarkdownContainer"] .vs-feature .k {{ font-size: 0.72rem; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; color: {MUTED}; }}
[data-testid="stMarkdownContainer"] .vs-feature .n {{ font-size: 1.35rem; font-weight: 600; color: {NAVY}; margin: 4px 0 6px 0;
   display: flex; align-items: center; flex-wrap: wrap; gap: 8px; }}
[data-testid="stMarkdownContainer"] .vs-feature .n .vs-badge {{ margin: 0; }}
[data-testid="stMarkdownContainer"] .vs-feature .ev {{ font-size: 0.82rem; color: {MUTED}; margin-top: 8px; }}
[data-testid="stMarkdownContainer"] .vs-findings {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; }}
[data-testid="stMarkdownContainer"] .vs-findings > div {{ background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 6px; padding: 14px 16px; font-size: 0.875rem; line-height: 1.55; color: {TEXT}; }}
/* form controls share one height so filter rows line up */
[data-testid="stSegmentedControl"] button, [data-testid="stButtonGroup"] button {{ min-height: 2.5rem; }}
[data-testid="stSegmentedControl"], [data-testid="stButtonGroup"] {{ min-height: 2.5rem; align-items: center; }}
[data-testid="stPageLink"] a {{ padding-left: 0; }}
[data-testid="stPageLink"] a span, [data-testid="stPageLink"] a p {{ font-size: 0.9rem; font-weight: 500; color: {BLUE}; }}
[data-testid="stSidebar"] [data-testid="stLogo"] {{ height: 40px; max-width: 236px; margin: 4px 0 10px 0; }}
[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {{ padding-bottom: 8px; }}
[data-testid="stMarkdownContainer"] .vs-findings .k {{ font-size: 0.72rem; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; color: {MUTED}; margin-bottom: 6px; }}
[data-testid="stMarkdownContainer"] .vs-notice {{ padding: 10px 14px; background: {SURFACE}; border: 1px solid {BORDER};
   border-left: 3px solid {NAVY}; border-radius: 6px; font-size: 0.85rem; color: {TEXT}; margin-bottom: 24px; }}
[data-testid="stMarkdownContainer"] .vs-metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
   gap: 12px; margin-bottom: 32px; }}
[data-testid="stMarkdownContainer"] .vs-metrics > div {{ background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 6px; padding: 12px 14px; }}
[data-testid="stMarkdownContainer"] .vs-metrics .q {{ font-size: 0.72rem; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; color: {MUTED};
   min-height: 2.3em; line-height: 1.15; }}
[data-testid="stMarkdownContainer"] .vs-metrics .a {{ font-size: 1.35rem; font-weight: 600; color: {NAVY}; margin: 6px 0 4px 0; line-height: 1.2;
   font-variant-numeric: tabular-nums; }}
[data-testid="stMarkdownContainer"] .vs-metrics .d {{ font-size: 0.8rem; color: {MUTED}; line-height: 1.45; }}
[data-testid="stMarkdownContainer"] .vs-section {{ margin-top: 32px; }}
[data-testid="stMarkdownContainer"] .vs-gap {{ margin-top: 24px; }}
[data-testid="stMarkdownContainer"] .vs-lead {{ font-size: 0.875rem; color: {MUTED}; margin: 0 0 8px 0; line-height: 1.5; }}
[data-testid="stMarkdownContainer"] .vs-label {{ font-size: 0.72rem; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; color: {MUTED}; margin-bottom: 4px; }}
[data-testid="stMarkdownContainer"] .vs-body {{ font-size: 0.9rem; color: {TEXT}; line-height: 1.55; }}
[data-testid="stMarkdownContainer"] .vs-body ul {{ margin: 4px 0 0 1.1rem; padding: 0; }}
[data-testid="stMarkdownContainer"] .vs-body li {{ margin-bottom: 4px; }}
[data-testid="stMarkdownContainer"] .vs-interp {{ font-size: 0.875rem; color: {TEXT}; background: {SURFACE}; border: 1px solid {BORDER};
   border-radius: 6px; padding: 10px 14px; margin: 4px 0 24px 0; line-height: 1.5; }}
[data-testid="stMarkdownContainer"] .vs-badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem;
   font-weight: 600; vertical-align: middle; margin-right: 6px; border: 1px solid {BORDER}; background: {GREY_BG}; color: {NAVY}; }}
[data-testid="stMarkdownContainer"] .vs-badge.red {{ background: {RED_BG}; color: {RED}; border-color: #F4C7C3; }}
[data-testid="stMarkdownContainer"] .vs-badge.amber {{ background: {AMBER_BG}; color: {AMBER_TX}; border-color: #F5D9A8; }}
[data-testid="stMarkdownContainer"] .vs-badge.green {{ background: {GREEN_BG}; color: {GREEN}; border-color: #C7E7D0; }}
[data-testid="stMarkdownContainer"] .vs-badge.grey {{ background: {GREY_BG}; color: {MUTED}; }}
[data-testid="stMarkdownContainer"] .vs-ghat {{ font-size: 1.25rem; font-weight: 600; color: {NAVY}; margin: 0; }}
[data-testid="stMarkdownContainer"] .vs-reco {{ background: {SELECT_BG}; border: 1px solid #BFDBFE; border-radius: 6px; padding: 12px 14px;
   font-size: 0.9rem; color: {TEXT}; line-height: 1.5; }}
[data-testid="stMarkdownContainer"] .vs-reco .t {{ font-size: 0.72rem; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; color: #1D4ED8; margin-bottom: 4px; }}
[data-testid="stMarkdownContainer"] .vs-legend {{ font-size: 0.8rem; color: {TEXT}; margin: 2px 0 6px 0; line-height: 1.8; }}
[data-testid="stMarkdownContainer"] .vs-legend span.sw {{ display: inline-block; width: 10px; height: 10px; border-radius: 2px; margin: 0 6px 0 0; vertical-align: middle; }}
[data-testid="stMarkdownContainer"] .vs-legend span.it {{ margin-right: 14px; white-space: nowrap; }}
[data-testid="stMarkdownContainer"] .vs-queue {{ width: 100%; border-collapse: collapse; font-size: 0.875rem; }}
[data-testid="stMarkdownContainer"] .vs-queue th {{ text-align: left; font-size: 0.72rem; font-weight: 600; letter-spacing: 0.06em;
   text-transform: uppercase; color: {MUTED}; padding: 0 10px 6px 0; border-bottom: 1px solid {BORDER}; vertical-align: bottom; line-height: 1.15; }}
[data-testid="stMarkdownContainer"] .vs-queue th.num, [data-testid="stMarkdownContainer"] .vs-queue td.num {{ text-align: right; padding-right: 16px; }}
[data-testid="stMarkdownContainer"] .vs-queue td {{ padding: 10px 10px 10px 0; border-bottom: 1px solid {BORDER}; vertical-align: top; color: {TEXT}; }}
[data-testid="stMarkdownContainer"] .vs-queue tr.sel td {{ background: {SELECT_BG}; }}
[data-testid="stMarkdownContainer"] .vs-queue .rk {{ font-weight: 700; color: {NAVY}; width: 28px; padding-left: 8px; }}
[data-testid="stMarkdownContainer"] .vs-queue .nm {{ font-weight: 600; color: {NAVY}; }}
[data-testid="stMarkdownContainer"] .vs-queue .num {{ white-space: nowrap; font-variant-numeric: tabular-nums; }}
[data-testid="stMarkdownContainer"] .vs-queue .bad {{ color: {RED}; font-weight: 600; }}
[data-testid="stMarkdownContainer"] .vs-queue .cov {{ color: {MUTED}; }}
[data-testid="stMarkdownContainer"] .vs-footer {{ font-size: 0.78rem; color: {MUTED}; line-height: 1.5; margin-top: 32px; }}
@media (max-width: 700px) {{
  [data-testid="stMarkdownContainer"] .vs-queue thead {{ display: none; }}
  [data-testid="stMarkdownContainer"] .vs-queue tr {{ display: block; border-bottom: 1px solid {BORDER}; padding: 6px 0; }}
  [data-testid="stMarkdownContainer"] .vs-queue td {{ display: block; border-bottom: none; padding: 2px 8px; }}
  [data-testid="stMarkdownContainer"] .vs-queue .rk {{ display: inline-block; width: auto; }}
  [data-testid="stMarkdownContainer"] .vs-queue .nm {{ display: inline-block; }}
  [data-testid="stMarkdownContainer"] .vs-queue .num {{ white-space: normal; }}
}}
.st-key-brief_preview h1 {{ font-size: 1.25rem !important; font-weight: 600; color: {NAVY}; margin: 0 0 8px 0 !important; padding: 0 !important; }}
.st-key-brief_preview h2 {{ font-size: 1.05rem !important; margin-top: 16px !important; }}
.st-key-brief_preview h3 {{ font-size: 0.95rem !important; margin-top: 12px !important; }}
.st-key-brief_preview p, .st-key-brief_preview li, .st-key-brief_preview td, .st-key-brief_preview th {{ font-size: 0.875rem; }}
[data-testid="stAlert"] p {{ font-size: 0.875rem; }}
/* ---- navigation shell ---- */
.st-key-topnav {{ position: fixed; top: 14px; left: 50%; margin-left: -310px; width: 620px; z-index: 40;
   background: rgba(239,246,255,0.86); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
   border: 1px solid #D6E2F5; border-radius: 999px; padding: 6px 8px; box-shadow: 0 6px 24px rgba(20,43,74,0.08); }}
.st-key-topnav [data-testid="stHorizontalBlock"] {{ flex-wrap: nowrap; }}
.st-key-topnav [data-testid="stPageLink"] a {{ justify-content: center; border-radius: 999px; padding: 8px 10px; }}
.st-key-topnav [data-testid="stPageLink"] a:hover {{ background: {SURFACE}; }}
.st-key-topnav [data-testid="stPageLink"] a span, .st-key-topnav [data-testid="stPageLink"] a p {{ color: {NAVY}; font-weight: 600; font-size: 0.875rem; white-space: nowrap; }}
.st-key-topnav [data-testid="stPageLink"] a [data-testid="stIconMaterial"] {{ color: {BLUE}; }}
/* ---- left rail (inner pages): always visible, independent of the Streamlit sidebar ---- */
@keyframes vs-rail-in {{ from {{ opacity: 0; transform: translateX(-18px); }} to {{ opacity: 1; transform: none; }} }}
@keyframes vs-fade-in {{ from {{ opacity: 0; transform: translateY(6px); }} to {{ opacity: 1; transform: none; }} }}
[data-testid="stColumn"]:has(.st-key-leftnav) {{ flex: 0 0 236px !important; min-width: 236px !important; width: 236px !important; }}
[data-testid="stColumn"]:has(.st-key-pagebar) {{ flex: 1 1 0 !important; min-width: 0 !important; width: auto !important; }}
[data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"] .st-key-leftnav) {{ flex-wrap: nowrap; }}
.st-key-leftnav {{ background: {NAVY}; border-radius: 10px; padding: 16px 12px 24px 12px; width: 236px;
   position: fixed; top: 3.25rem; left: calc(max(0px, (100vw - 1400px) / 2) + 5rem); height: calc(100vh - 4.5rem);
   overflow-y: auto; animation: vs-rail-in 0.35s ease-out; z-index: 20; }}
.st-key-leftnav .vs-rail-brand {{ padding: 2px 4px 14px 4px; border-bottom: 1px solid rgba(255,255,255,0.14); margin-bottom: 10px; }}
.st-key-leftnav .vs-rail-brand svg {{ display: block; max-width: 100%; height: auto; }}
.st-key-leftnav [data-testid="stPageLink"] a {{ padding: 9px 12px; border-radius: 6px; margin-bottom: 2px; transition: background 0.15s ease; }}
.st-key-leftnav [data-testid="stPageLink"] a:hover {{ background: rgba(255,255,255,0.08); }}
.st-key-leftnav [data-testid="stPageLink"] a span, .st-key-leftnav [data-testid="stPageLink"] a p {{ color: #DCE7F5; font-weight: 500; font-size: 0.95rem; }}
.st-key-leftnav [data-testid="stPageLink"] a [data-testid="stIconMaterial"] {{ color: #BFD3EE; }}
.st-key-leftnav .vs-side-divider {{ border-top: 1px solid rgba(255,255,255,0.14); margin: 12px 0 14px 0; }}
.st-key-leftnav .vs-side-note {{ font-size: 0.75rem; color: #BFD3EE; line-height: 1.5; padding: 0 4px; }}
.st-key-leftnav .vs-side-note strong {{ color: #FFFFFF; }}
.st-key-pagebar {{ animation: vs-fade-in 0.3s ease-out; }}
@keyframes vs-drop-in {{ from {{ opacity: 0; transform: translateY(-12px); }} to {{ opacity: 1; transform: none; }} }}
.st-key-topnav {{ animation: vs-drop-in 0.5s cubic-bezier(.2,.8,.2,1); }}
@media (max-width: 900px) {{
  [data-testid="stColumn"]:has(.st-key-leftnav), [data-testid="stColumn"]:has(.st-key-pagebar) {{ flex: 1 1 100% !important; min-width: 0 !important; width: 100% !important; }}
  [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"] .st-key-leftnav) {{ flex-wrap: wrap; }}
  .st-key-leftnav {{ min-height: 0; height: auto; width: auto; position: static; padding: 12px 12px 16px 12px; animation: vs-fade-in 0.3s ease-out; }}
  .st-key-leftnav > div[data-testid="stVerticalBlock"] {{ flex-direction: row; flex-wrap: wrap; align-items: center; gap: 4px 6px; }}
  .st-key-leftnav .vs-rail-brand {{ border-bottom: none; padding: 0 8px 0 0; margin: 0; }}
  .st-key-leftnav .vs-rail-brand svg {{ width: 170px; }}
  .st-key-leftnav [data-testid="stPageLink"] a {{ padding: 6px 10px; margin: 0; }}
  .st-key-leftnav .vs-side-divider, .st-key-leftnav .vs-side-note {{ display: none; }}
}}
/* ---- page bar (inner pages) ---- */
.st-key-pagebar {{ background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 8px; padding: 6px 10px; margin-bottom: 20px; }}
.st-key-pagebar [data-testid="stButton"] button {{ min-height: 2.25rem; border-color: {BORDER}; color: {NAVY}; font-weight: 500; padding-left: 8px; padding-right: 8px; }}
.st-key-pagebar [data-testid="stButton"] button p {{ white-space: nowrap; }}
.st-key-pagebar [data-testid="stPageLink"] a {{ justify-content: center; border: 1px solid {BORDER}; border-radius: 6px; min-height: 2.25rem; padding: 4px 10px; }}
.st-key-pagebar [data-testid="stPageLink"] a:hover {{ background: {SELECT_BG}; border-color: #BFDBFE; }}
.st-key-pagebar [data-testid="stPageLink"] a span, .st-key-pagebar [data-testid="stPageLink"] a p {{ color: {NAVY}; font-weight: 500; font-size: 0.875rem; white-space: nowrap; }}
.st-key-pagebar [data-testid="stPageLink"] a [data-testid="stIconMaterial"] {{ color: {BLUE}; }}
[data-testid="stMarkdownContainer"] .vs-crumb {{ font-size: 0.875rem; color: {MUTED}; display: flex; align-items: center; gap: 8px; height: 20px; line-height: 20px; margin-top: -8px; }}
[data-testid="stMarkdownContainer"] .vs-crumb a {{ color: {BLUE}; text-decoration: none; font-weight: 500; }}
[data-testid="stMarkdownContainer"] .vs-crumb .cur {{ color: {NAVY}; font-weight: 600; }}
[data-testid="stMarkdownContainer"] .vs-crumb .step {{ margin-left: auto; font-size: 0.75rem; color: {MUTED}; border: 1px solid {BORDER}; border-radius: 999px; padding: 1px 8px; }}
header[data-testid="stHeader"] {{ height: 1.5rem; pointer-events: none; }}
header[data-testid="stHeader"] * {{ pointer-events: none; }}
/* ---- landing hero ---- */
[data-testid="stMarkdownContainer"] .vs-hero {{ position: relative; overflow: hidden; background: {SURFACE}; border: 1px solid {BORDER};
   border-radius: 12px; padding: 40px 40px 72px 40px; margin-bottom: 16px; }}
[data-testid="stMarkdownContainer"] .vs-hero .vs-waves {{ position: absolute; left: 0; right: 0; bottom: 0; width: 100%; height: 110px; }}
[data-testid="stMarkdownContainer"] .vs-hero .in {{ position: relative; max-width: 760px; }}
[data-testid="stMarkdownContainer"] .vs-hero .eyebrow {{ display: flex; align-items: center; gap: 10px; font-size: 0.78rem; font-weight: 600;
   letter-spacing: 0.1em; text-transform: uppercase; color: {TEAL}; margin-bottom: 12px; }}
[data-testid="stMarkdownContainer"] .vs-hero .eyebrow .mark svg {{ width: 28px; height: 28px; display: block; }}
[data-testid="stMarkdownContainer"] .vs-hero h1.title {{ font-size: 2.4rem; font-weight: 700; letter-spacing: -0.02em; color: {NAVY}; margin: 0 0 12px 0; padding: 0; }}
[data-testid="stMarkdownContainer"] .vs-hero p.sub {{ font-size: 1.05rem; line-height: 1.6; color: {TEXT}; margin: 0 0 20px 0; }}
[data-testid="stMarkdownContainer"] .vs-hero .facts {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 8px 16px;
   font-size: 0.875rem; color: {MUTED}; max-width: 880px; line-height: 1.4; }}
[data-testid="stMarkdownContainer"] .vs-hero .facts span {{ padding-left: 10px; border-left: 2px solid #D6E2F5; }}
[data-testid="stMarkdownContainer"] .vs-hero .facts strong {{ color: {NAVY}; font-variant-numeric: tabular-nums; }}
[data-testid="stMarkdownContainer"] .vs-tile {{ background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 8px; padding: 16px; min-height: 256px; }}
[data-testid="stMarkdownContainer"] .vs-tile .ic {{ margin-bottom: 8px; }}
[data-testid="stMarkdownContainer"] .vs-tile .ic svg {{ display: block; }}
[data-testid="stMarkdownContainer"] .vs-tile .h {{ font-size: 1rem; font-weight: 600; color: {NAVY}; margin-bottom: 6px; line-height: 1.3; }}
[data-testid="stMarkdownContainer"] .vs-tile .b {{ font-size: 0.85rem; color: {MUTED}; line-height: 1.5; }}
/* ---- landing motion: water ---- */
@keyframes vs-wave {{ from {{ transform: translateX(0); }} to {{ transform: translateX(-1200px); }} }}
@keyframes vs-ripple {{ 0% {{ transform: scale(0.2); opacity: 0.55; }} 100% {{ transform: scale(1); opacity: 0; }} }}
@keyframes vs-bob {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-4px); }} }}
@keyframes vs-reveal {{ from {{ opacity: 0; transform: translateY(14px); }} to {{ opacity: 1; transform: none; }} }}
[data-testid="stMarkdownContainer"] .vs-hero {{ background: {SURFACE} radial-gradient(circle at 88% 18%, rgba(37,99,235,0.10), transparent 42%); }}
[data-testid="stMarkdownContainer"] .vs-hero .vs-waves path {{ will-change: transform; }}
[data-testid="stMarkdownContainer"] .vs-hero .vs-waves .w1 {{ animation: vs-wave 22s linear infinite; }}
[data-testid="stMarkdownContainer"] .vs-hero .vs-waves .w2 {{ animation: vs-wave 15s linear infinite; }}
[data-testid="stMarkdownContainer"] .vs-hero .vs-waves .w3 {{ animation: vs-wave 30s linear infinite reverse; }}
[data-testid="stMarkdownContainer"] .vs-hero .vs-ripple {{ position: absolute; right: 9%; top: 26%; width: 260px; height: 260px; margin: -130px -130px 0 0;
   border-radius: 50%; border: 1.5px solid rgba(37,99,235,0.45); pointer-events: none; animation: vs-ripple 4.5s ease-out infinite; }}
[data-testid="stMarkdownContainer"] .vs-hero .vs-ripple.r2 {{ animation-delay: 1.5s; border-color: rgba(13,148,136,0.45); }}
[data-testid="stMarkdownContainer"] .vs-hero .vs-ripple.r3 {{ animation-delay: 3s; border-color: rgba(20,43,74,0.35); }}
[data-testid="stMarkdownContainer"] .vs-hero .eyebrow .mark svg {{ animation: vs-bob 3.2s ease-in-out infinite; }}
[data-testid="stMarkdownContainer"] .reveal {{ animation: vs-reveal 0.6s cubic-bezier(.2,.8,.2,1) both; }}
[data-testid="stMarkdownContainer"] .reveal.r0 {{ animation-delay: 0.05s; }}
[data-testid="stMarkdownContainer"] .reveal.r1 {{ animation-delay: 0.15s; }}
[data-testid="stMarkdownContainer"] .reveal.r2 {{ animation-delay: 0.28s; }}
[data-testid="stMarkdownContainer"] .reveal.r3 {{ animation-delay: 0.4s; }}
[data-testid="stColumn"]:nth-child(1) .vs-tile.reveal {{ animation-delay: 0.45s; }}
[data-testid="stColumn"]:nth-child(2) .vs-tile.reveal {{ animation-delay: 0.55s; }}
[data-testid="stColumn"]:nth-child(3) .vs-tile.reveal {{ animation-delay: 0.65s; }}
[data-testid="stColumn"]:nth-child(4) .vs-tile.reveal {{ animation-delay: 0.75s; }}
[data-testid="stMarkdownContainer"] .vs-tile {{ transition: transform 0.2s ease, box-shadow 0.2s ease; }}
[data-testid="stMarkdownContainer"] .vs-tile:hover {{ transform: translateY(-3px); box-shadow: 0 10px 24px rgba(20,43,74,0.08); }}
@media (prefers-reduced-motion: reduce) {{
  [data-testid="stMarkdownContainer"] .vs-hero .vs-waves path, [data-testid="stMarkdownContainer"] .vs-hero .vs-ripple,
  [data-testid="stMarkdownContainer"] .vs-hero .eyebrow .mark svg, [data-testid="stMarkdownContainer"] .reveal, .st-key-topnav,
  .st-key-leftnav, .st-key-pagebar {{ animation: none !important; }}
}}
@media (max-width: 700px) {{
  [data-testid="stMarkdownContainer"] .vs-hero {{ padding: 24px 20px 64px 20px; }}
  [data-testid="stMarkdownContainer"] .vs-hero h1.title {{ font-size: 1.8rem; }}
  [data-testid="stMarkdownContainer"] .vs-hero .vs-ripple {{ display: none; }}
  .st-key-topnav {{ position: fixed; left: 10px; right: 10px; width: auto; margin-left: 0; border-radius: 999px; padding: 4px 6px; }}
  .st-key-topnav [data-testid="stHorizontalBlock"] {{ flex-wrap: nowrap; gap: 4px; }}
  .st-key-topnav [data-testid="stColumn"] {{ min-width: 0 !important; }}
  .st-key-topnav [data-testid="stPageLink"] a {{ padding: 6px 4px; }}
  .st-key-topnav [data-testid="stPageLink"] a [data-testid="stIconMaterial"] {{ display: none; }}
  .st-key-topnav [data-testid="stPageLink"] a span, .st-key-topnav [data-testid="stPageLink"] a p {{ font-size: 0.8rem; }}
  [data-testid="stMarkdownContainer"] .vs-hero .facts {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
}}
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def sidebar_brand() -> None:
    """Brand above the navigation via st.logo (sidebar), with the navy mark when the sidebar is collapsed."""
    root = Path(__file__).resolve().parent.parent.parent
    st.logo(str(root / "assets" / "logo.svg"), icon_image=str(root / "assets" / "mark.svg"), size="large")


def page_header(title: str, purpose: str) -> None:
    st.markdown(f"# {title}")
    st.markdown(f'<div class="vs-purpose">{purpose}</div>', unsafe_allow_html=True)


def notice(html: str) -> None:
    st.markdown(f'<div class="vs-notice">{html}</div>', unsafe_allow_html=True)


def section(title: str, lead: str = "") -> None:
    st.markdown('<div class="vs-section"></div>', unsafe_allow_html=True)
    st.markdown(f"## {title}")
    if lead:
        st.markdown(f'<div class="vs-lead">{lead}</div>', unsafe_allow_html=True)


def badge(text: str, kind: str = "") -> str:
    return f'<span class="vs-badge {kind}">{text}</span>'


def legend_html(items: list[tuple[str, str]], note: str = "") -> str:
    spans = "".join(f'<span class="it"><span class="sw" style="background:{c}"></span>{t}</span>' for t, c in items)
    tail = f'<span style="color:{MUTED}">{note}</span>' if note else ""
    return f'<div class="vs-legend">{spans}{tail}</div>'


def legend(items: list[tuple[str, str]], note: str = "") -> None:
    st.markdown(legend_html(items, note), unsafe_allow_html=True)


def status_legend(note: str = "") -> None:
    legend([(CAT_CRIT, RED), (CAT_OUT, AMBER), (CAT_IN, TEAL), (CAT_MISS, GREY)], note)


def interpretation(html: str) -> None:
    st.markdown(f'<div class="vs-interp">{html}</div>', unsafe_allow_html=True)


def base_config(chart):
    return (chart.configure_axis(gridColor=GRID, domainColor=BORDER, tickColor=BORDER, labelColor=TEXT,
                                 titleColor=MUTED, labelFontSize=11, titleFontSize=11, titleFontWeight=500)
            .configure_view(stroke=None).configure(background=SURFACE).configure_legend(disable=True))
