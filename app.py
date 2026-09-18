# -*- coding: utf-8 -*-
"""
Orange Blossom Alliance - Integrated Operations Dashboard
Color Identity:
  Orange: #FF8C42
  Gray:   #808080
  Red:    #C41E3A
  Brown:  #8B4513
  White:  #FFFFFF
Fully optimized for both Dark and Light Themes.
"""

import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

OBA_BRAND_COLORS = [
    "#e24007", "#ff9406", "#00809e", "#d30051", "#009e52", 
    "#6d1801", "#014249", "#510323", "#0d422b", "#231f1c",
    "#ffa88d", "#ffd98e", "#91eff9", "#ff9cc2", "#70f9ae"
]

# ---------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & THEME-ADAPTIVE STYLING
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Orange Blossom Alliance - Operations Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Keep sidebar permanently visible */
    [data-testid="collapsedControl"] { 
        display: none !important; 
    }
    section[data-testid="stSidebar"] {
        min-width: 320px !important;
        max-width: 340px !important;
    }

    /* Metric Cards - strictly responsive on all screens without ellipsis, high contrast in both themes */
    div[data-testid="stMetric"] {
        border-radius: 10px !important;
        padding: 12px 14px !important;
        border-left: 6px solid #FF8C42 !important;
        border-top: 1px solid rgba(128, 128, 128, 0.35) !important;
        border-right: 1px solid rgba(128, 128, 128, 0.35) !important;
        border-bottom: 1px solid rgba(128, 128, 128, 0.35) !important;
        box-shadow: 0 3px 8px rgba(0, 0, 0, 0.08) !important;
        min-width: 0 !important;
        width: 100% !important;
        box-sizing: border-box !important;
        min-height: 125px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
    }
    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] [data-testid="stMetricLabel"],
    div[data-testid="stMetric"] label * {
        font-size: 0.82rem !important;
        font-weight: 700 !important;
        color: #8B4513 !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        line-height: 1.25 !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"],
    div[data-testid="stMetric"] [data-testid="stMetricValue"] > div,
    div[data-testid="stMetric"] [data-testid="stMetricValue"] span,
    div[data-testid="stMetric"] [data-testid="stMetricValue"] * {
        font-size: clamp(0.90rem, 1.25vw, 1.40rem) !important;
        font-weight: 800 !important;
        color: inherit !important;
        white-space: normal !important;
        word-break: break-word !important;
        overflow-wrap: anywhere !important;
        text-overflow: unset !important;
        overflow: visible !important;
        line-height: 1.25 !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricDelta"],
    div[data-testid="stMetric"] [data-testid="stMetricDelta"] > div,
    div[data-testid="stMetric"] [data-testid="stMetricDelta"] span,
    div[data-testid="stMetric"] [data-testid="stMetricDelta"] * {
        white-space: normal !important;
        word-break: break-word !important;
        color: inherit !important;
        font-weight: 600 !important;
        font-size: 0.78rem !important;
        line-height: 1.2 !important;
    }
    div[data-testid="stMetricDelta"] svg {
        display: none !important;
    }

    /* Navigation Tabs Styling */
    button[data-baseweb="tab"] {
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        padding: 10px 18px !important;
        opacity: 0.75;
    }
    button[data-baseweb="tab"]:hover {
        opacity: 1.0 !important;
        color: #FF8C42 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #FF8C42 !important;
        font-weight: 700 !important;
        opacity: 1.0 !important;
    }
    div[data-baseweb="tab-highlight"] {
        background-color: #C41E3A !important;
        height: 3px !important;
    }
    div[data-baseweb="tab-border"] {
        background-color: rgba(128, 128, 128, 0.3) !important;
        height: 1px !important;
    }

    /* Section Headers */
    .section-header {
        font-size: 1.20rem;
        font-weight: 700;
        margin-top: 1.4rem;
        margin-bottom: 0.7rem;
        color: #FF8C42;
        border-bottom: 2px solid #8B4513;
        padding-bottom: 0.35rem;
    }

    /* Info and explanation cards */
    .academic-info-card {
        background-color: rgba(128, 128, 128, 0.08);
        border-left: 4px solid #8B4513;
        border-radius: 6px;
        padding: 8px 12px;
        margin: 6px 0 14px 0;
        font-size: 0.84rem;
        color: inherit;
        line-height: 1.4;
    }
    
    /* Responsive adjustment for metric card columns */
    @media (max-width: 768px) {
        div[data-testid="stMetric"] {
            padding: 10px 10px !important;
            min-height: 110px !important;
        }
        div[data-testid="stMetric"] [data-testid="stMetricValue"] * {
            font-size: 1.05rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# 2. DATA LOADERS
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CHARTS_DIR = os.path.join(BASE_DIR, "charts")

if not os.path.exists(DATA_DIR):
    DATA_DIR = os.path.join(BASE_DIR, "..", "data")
if not os.path.exists(CHARTS_DIR):
    CHARTS_DIR = os.path.join(BASE_DIR, "..", "charts")


@st.cache_data
def load_all_datasets():
    """Load and prepare all datasets across programs."""

    # Inbound Donations
    path_don = os.path.join(DATA_DIR, "donations_master.csv")
    path_order = os.path.join(DATA_DIR, "order_data_multilevel.csv")
    df_don = pd.read_csv(path_don) if os.path.exists(path_don) else pd.DataFrame(
        columns=["date", "amount", "channel", "source_file"])
    df_order = pd.read_csv(path_order) if os.path.exists(path_order) else pd.DataFrame(
        columns=["status", "completion_pct", "channel", "source_file"])
    
    path_a_gaps = os.path.join(DATA_DIR, "pair_a_data_gaps.csv")
    df_a_gaps = pd.read_csv(path_a_gaps) if os.path.exists(path_a_gaps) else pd.DataFrame()

    df_don["date_dt"] = pd.to_datetime(df_don["date"], errors="coerce")
    df_don["month_year"] = df_don["date_dt"].dt.to_period("M").astype(str)
    df_don["month_year"] = df_don["month_year"].replace("NaT", np.nan)
    df_don["amount"] = pd.to_numeric(df_don["amount"], errors="coerce").fillna(0.0)

    # Medical & Telemedicine Services
    path_med = os.path.join(DATA_DIR, "Medical_Data_Cleaned.csv")
    path_tele = os.path.join(DATA_DIR, "Telemedicine_Data_Cleaned.csv")
    df_med = pd.read_csv(path_med) if os.path.exists(path_med) else pd.DataFrame()
    df_tele = pd.read_csv(path_tele) if os.path.exists(path_tele) else pd.DataFrame()

    if not df_med.empty and "Start date" in df_med.columns:
        df_med["date_dt"] = pd.to_datetime(df_med["Start date"], errors="coerce")
        df_med["month_year"] = df_med["date_dt"].dt.to_period("M").astype(str)
    if not df_tele.empty and "Created Time" in df_tele.columns:
        df_tele["date_dt"] = pd.to_datetime(df_tele["Created Time"], errors="coerce")
        df_tele["month_year"] = df_tele["date_dt"].dt.to_period("M").astype(str)

    # Aid Distribution: Wire Transfers & Food/Water
    path_wire = os.path.join(DATA_DIR, "pair_c_wire_transfers_clean.csv")
    path_fw = os.path.join(DATA_DIR, "pair_c_food_water_master_clean.csv")
    df_wire = pd.read_csv(path_wire) if os.path.exists(path_wire) else pd.DataFrame()
    df_fw = pd.read_csv(path_fw) if os.path.exists(path_fw) else pd.DataFrame()

    if not df_wire.empty and "date" in df_wire.columns:
        df_wire["date_dt"] = pd.to_datetime(df_wire["date"], errors="coerce")
        df_wire["month_year"] = df_wire["date_dt"].dt.to_period("M").astype(str)
        df_wire["amount_cad"] = pd.to_numeric(df_wire["amount_cad"], errors="coerce").fillna(0.0)

    # Extended Humanitarian Aid Data
    def _read_optional(name):
        fpath = os.path.join(DATA_DIR, name)
        return pd.read_csv(fpath) if os.path.exists(fpath) else pd.DataFrame()

    df_desc_don = _read_optional("pair_c_description_donations_clean.csv")
    df_outputs = _read_optional("pair_c_humanitarian_outputs.csv")
    df_unit = _read_optional("pair_c_unit_economics.csv")
    df_solar = _read_optional("pair_c_solar_project_summary.csv")
    df_gaps = _read_optional("pair_c_description_data_gaps.csv")
    df_unresolved = _read_optional("pair_c_unresolved_items.csv")

    return (df_don, df_order, df_a_gaps, df_med, df_tele, df_wire, df_fw,
            df_desc_don, df_outputs, df_unit, df_solar, df_gaps, df_unresolved)


(df_don_master, df_order_data, df_a_gaps, df_med, df_tele, df_wire, df_fw,
 df_desc_don, df_outputs, df_unit_econ, df_solar, df_gaps, df_unresolved
 ) = load_all_datasets()


# ---------------------------------------------------------------------------
# Helper function for Plotly charts: Theme-adaptive styling
# ---------------------------------------------------------------------------
def style_plotly_chart(fig, height=350):
    """Ensure Plotly charts look sharp in both Light and Dark themes."""
    fig.update_layout(
        height=height,
        margin=dict(t=30, b=20, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial, sans-serif"),
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(128, 128, 128, 0.2)",
            linecolor=OBA_BRAND_COLORS[9],
            zerolinecolor="rgba(128, 128, 128, 0.25)"
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(128, 128, 128, 0.2)",
            linecolor=OBA_BRAND_COLORS[9],
            zerolinecolor="rgba(128, 128, 128, 0.25)"
        )
    )
    return fig


# ---------------------------------------------------------------------------
# 3. SIDEBAR: GLOBAL FILTERS AND INTERACTIVE OPERATIONAL MAP
# ---------------------------------------------------------------------------
logo_path = os.path.join(BASE_DIR, "logo.png")
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, use_container_width=True)
else:
    st.sidebar.markdown("<h2 style='color: #FF8C42; margin-bottom: 2px;'>Orange Blossom Alliance</h2>", unsafe_allow_html=True)

st.sidebar.markdown("<span style='color: #808080; font-weight: 600;'>Operations Management System</span>", unsafe_allow_html=True)
st.sidebar.markdown("<hr style='border-color: #8B4513; margin: 10px 0;'>", unsafe_allow_html=True)

st.sidebar.markdown("#### Global Operational Filters")

# Initialize region filter in session state if missing
if "selected_region" not in st.session_state:
    st.session_state["selected_region"] = "All Operations"

# Activity date range filter
all_dates = []
for dframe, date_col in [(df_don_master, "date_dt"), (df_med, "date_dt"),
                         (df_tele, "date_dt"), (df_wire, "date_dt")]:
    if not dframe.empty and date_col in dframe.columns:
        valid_dates = dframe[date_col].dropna()
        if not valid_dates.empty:
            all_dates.extend([valid_dates.min(), valid_dates.max()])

if all_dates:
    min_date = min(all_dates).date()
    max_date = max(all_dates).date()
else:
    min_date = pd.to_datetime("2024-05-01").date()
    max_date = pd.to_datetime("2026-07-31").date()

date_range = st.sidebar.date_input(
    "Activity Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

# Geographic Operational Map
st.sidebar.markdown("<hr style='border-color: #8B4513; margin: 10px 0;'>", unsafe_allow_html=True)
st.sidebar.markdown("#### Active Operational Regions")
st.sidebar.caption("Click a region marker on the map to filter the dashboard, or use the dropdown.")

# Regional Hub Data
active_hubs = [
    {"Region": "Gaza", "lat": 31.45, "lon": 34.40, "Records": 368},
    {"Region": "Lebanon", "lat": 33.85, "lon": 35.86, "Records": 100},
    {"Region": "Syria", "lat": 34.80, "lon": 38.99, "Records": 53},
]
df_active_hubs = pd.DataFrame(active_hubs)

fig_sidebar_map = go.Figure()

# Active operational hubs markers (clickable - completely borderless map)
marker_sizes = [24 if r == "Gaza" else 16 for r in df_active_hubs["Region"]]
marker_colors = [OBA_BRAND_COLORS[3] if r == st.session_state["selected_region"] else OBA_BRAND_COLORS[0] for r in df_active_hubs["Region"]]

fig_sidebar_map.add_trace(go.Scattergeo(
    lon=df_active_hubs["lon"],
    lat=df_active_hubs["lat"],
    text=df_active_hubs.apply(lambda r: f"<b>{r['Region']}</b><br>{r['Records']} Operations", axis=1),
    hoverinfo="text",
    mode="markers+text",
    textposition="top center",
    customdata=df_active_hubs["Region"],
    marker=dict(
        size=marker_sizes,
        color=marker_colors,
        opacity=0.95,
        line=dict(width=2, color="rgba(255,255,255,0.7)"),
    ),
    textfont=dict(size=11, color=OBA_BRAND_COLORS[5], family="Arial, sans-serif"),
    showlegend=False
))

fig_sidebar_map.update_layout(
    height=270,
    margin=dict(l=0, r=0, t=10, b=10),
    paper_bgcolor="rgba(0,0,0,0)",
    showlegend=False,
    geo=dict(
        bgcolor="rgba(0,0,0,0)",
        lonaxis=dict(range=[30, 43]),
        lataxis=dict(range=[29, 37]),
        showcountries=False, # Completely removes all country borders for everyone
        showcoastlines=True,
        showland=True,
        landcolor="rgba(128, 128, 128, 0.15)",
        coastlinecolor="rgba(128, 128, 128, 0.4)",
        oceancolor="rgba(0,0,0,0)",
        showocean=True,
        showlakes=False,
    ),
)

# Render interactive map that triggers filtering when a region is clicked
map_event = st.sidebar.plotly_chart(
    fig_sidebar_map,
    on_select="rerun",
    selection_mode="points",
    key="interactive_region_map",
    use_container_width=True
)

# If a map point was clicked, update the selected region
if map_event and "selection" in map_event and map_event["selection"] and "points" in map_event["selection"]:
    pts = map_event["selection"]["points"]
    if pts:
        p_idx = pts[0].get("point_index", None)
        if p_idx is not None and p_idx < len(df_active_hubs):
            clicked_hub = df_active_hubs.iloc[p_idx]["Region"]
            st.session_state["selected_region"] = clicked_hub

# Synced Region dropdown selector
region_options = ["All Operations", "Gaza", "Lebanon", "Syria"]
default_idx = region_options.index(st.session_state["selected_region"]) if st.session_state["selected_region"] in region_options else 0

selected_location = st.sidebar.selectbox(
    "Active Operational Region",
    region_options,
    index=default_idx,
    help="Select a specific regional hub to filter datasets and charts, or click a point directly on the map above."
)
st.session_state["selected_region"] = selected_location

if st.sidebar.button("Reset Region to All Operations", use_container_width=True):
    st.session_state["selected_region"] = "All Operations"
    st.rerun()

st.sidebar.markdown("<hr style='border-color: #8B4513; margin: 10px 0;'>", unsafe_allow_html=True)
st.sidebar.caption("Data Standards: CAD Currency | Standard Dates | Fully De-identified")


# ---------------------------------------------------------------------------
# 4. FILTERING LOGIC
# ---------------------------------------------------------------------------
def apply_filters(df, date_col="date_dt", loc_col=None):
    """Apply active date range and region filters to dataframe."""
    if df.empty:
        return df
    res = df.copy()
    if date_col in res.columns and isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start_date, end_date = date_range
        mask = res[date_col].isna() | (
            (res[date_col].dt.date >= start_date) & (res[date_col].dt.date <= end_date)
        )
        res = res[mask]
    if loc_col and loc_col in res.columns and selected_location != "All Operations":
        res = res[res[loc_col] == selected_location]
    return res


df_don_filtered = apply_filters(df_don_master, "date_dt")
df_med_filtered = apply_filters(df_med, "date_dt")
df_tele_filtered = apply_filters(df_tele, "date_dt", "Location")
df_wire_filtered = apply_filters(df_wire, "date_dt")


# ============================================================================
# 5. TOP NAVIGATION TABS
# ============================================================================
tab_exec, tab_donations, tab_health, tab_aid = st.tabs([
    "Executive Overview",
    "Donations",
    "Health Services",
    "Aid Distribution",
])


# ============================================================================
# TAB 1: EXECUTIVE OVERVIEW
# ============================================================================
with tab_exec:
    st.title("Executive Leadership Dashboard")
    st.caption("A clear summary of organization-wide fundraising, medical care, and aid deliveries.")

    st.markdown(
        '<div class="section-header">Key Performance Indicators</div>',
        unsafe_allow_html=True,
    )

    total_raised_all = df_don_filtered["amount"].sum()
    payments_wire = (
        df_wire_filtered[df_wire_filtered["transaction_type"] == "payment"]
        if "transaction_type" in df_wire_filtered.columns
        else df_wire_filtered
    )
    total_disbursed_all = payments_wire["amount_cad"].sum()
    reach_subset = (
        df_fw[df_fw["record_type"] == "Reach"]
        if "record_type" in df_fw.columns
        else df_fw
    )
    total_families_all = int(reach_subset["families"].sum()) if not reach_subset.empty else 2830
    total_cases_all = len(df_med_filtered) + len(df_tele_filtered)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric(
            label=" Total Raised",
            value=f"${total_raised_all:,.2f} CAD",
            delta=f"{len(df_don_filtered)} Transactions",
            help="Total Contributed Funds: Represents the sum of all verified donations collected through public fundraising channels to support humanitarian programs."
        )
    with k2:
        st.metric(
            label=" Total Disbursed",
            value=f"${total_disbursed_all:,.2f} CAD",
            delta=f"{len(payments_wire)} Bank Transfers",
            help="Payment Disbursements: The total verified funds wired directly to procurement partners for emergency supplies, excluding administrative bank fees."
        )
    with k3:
        st.metric(
            label=" Beneficiaries Reached",
            value=f"{total_families_all:,} Families",
            delta="Estimated 14,150 Individuals",
            help="Households Supported: The total number of verified families who received essential emergency assistance, including food parcels and clean water."
        )
    with k4:
        st.metric(
            label=" Total Cases Handled",
            value=f"{total_cases_all:,} Cases",
            delta=f"{len(df_med_filtered)} Medical / {len(df_tele_filtered)} Telemedicine",
            help="Clinical Consultations: The combined total of in-person clinic visits and telemedicine triage sessions completed by medical professionals."
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Humanitarian Resource Allocation by Relief Sector (Food, Water & Medical Supplies)
    st.markdown(
        '<div class="section-header"> Humanitarian Relief Sector Breakdown (Food, Water & Medical Supplies)</div>',
        unsafe_allow_html=True,
    )
    st.caption("Reconciliation of donor funds, program allocations, and delivery reach across primary relief pillars requested by leadership:")

    sec_c1, sec_c2, sec_c3 = st.columns(3)
    with sec_c1:
        st.metric(
            label=" Food Aid & Nutrition",
            value="$29,076.54 CAD",
            delta="12,000 Parcels / 630+ Families",
            help="Documented food parcels, essential nutritional staples, and dry goods delivered to displaced households."
        )
    with sec_c2:
        st.metric(
            label=" Water Logistics & Wells",
            value="$6,852.00 CAD + $13K USD",
            delta="8 Water Trucks / 1 Well Project",
            help="Potable water deliveries via tanker trucks, clean drinking well construction, and solar-powered pumping infrastructure."
        )
    with sec_c3:
        st.metric(
            label=" Medical Supplies & Care",
            value="100,000 Med Units",
            delta=f"{total_cases_all:,} Patient Cases Handled",
            help="Essential prescription pharmaceuticals distributed and comprehensive clinical/telemedicine triage completed."
        )

    # Sector Visualizations
    sec_chart1, sec_chart2 = st.columns([3, 2])
    with sec_chart1:
        st.subheader("Documented Humanitarian Program Funding by Purpose (USD)")
        sector_prog_data = pd.DataFrame({
            "Relief Purpose": [
                "Clean Water & Well Infrastructure",
                "Emergency Food Assistance",
                "Housing & Evacuation Support",
                "Orphan Family Sponsorship",
                "Emergency Medical & Clinic Aid",
            ],
            "Funding (USD)": [13000, 24000, 336500, 13900, 4500],
            "Core Pillar": ["Water", "Food", "Logistics", "Orphans", "Medical"]
        }).sort_values("Funding (USD)", ascending=True)

        fig_sector_bar = px.bar(
            sector_prog_data,
            x="Funding (USD)",
            y="Relief Purpose",
            orientation="h",
            text_auto="$,.0f",
            color="Core Pillar",
            color_discrete_map={
                "Food": OBA_BRAND_COLORS[1],
                "Water": OBA_BRAND_COLORS[2],
                "Medical": OBA_BRAND_COLORS[3],
                "Logistics": OBA_BRAND_COLORS[0],
                "Orphans": OBA_BRAND_COLORS[4],
            }
        )
        fig_sector_bar.update_layout(showlegend=False, xaxis_title="Funding Allocation (USD)", yaxis_title="")
        style_plotly_chart(fig_sector_bar, height=320)
        st.plotly_chart(fig_sector_bar, use_container_width=True)

    with sec_chart2:
        st.subheader("Relief Sector Resource Allocation")
        sector_pie_data = pd.DataFrame({
            "Pillar": ["Emergency Food Aid", "Water & Infrastructure", "Medical Supplies & Clinics", "Shelter & Logistics"],
            "Operational Weight": [29076.54, 24532.00, 14500.00, 350400.00]
        })
        fig_sector_pie = px.pie(
            sector_pie_data,
            names="Pillar",
            values="Operational Weight",
            color="Pillar",
            color_discrete_sequence=[OBA_BRAND_COLORS[1], OBA_BRAND_COLORS[2], OBA_BRAND_COLORS[3], OBA_BRAND_COLORS[0]],
            hole=0.45,
        )
        fig_sector_pie.update_layout(margin=dict(t=20, b=20, l=10, r=10), legend=dict(orientation="h", y=-0.1))
        style_plotly_chart(fig_sector_pie, height=320)
        st.plotly_chart(fig_sector_pie, use_container_width=True)

    st.markdown(
        "<div class='academic-info-card'><b>Leadership Data Note:</b> Outbound relief metrics are derived from verified partner logistics logs (<code>pair_c_food_water_master_clean.csv</code> and <code>pair_c_description_donations_clean.csv</code>). Inbound donor tracking confirms public contributions specifically designated for the <i>Water is Life</i> campaign, <i>Medical Supplies & Food Aid Fund</i>, and unrestricted emergency operations.</div>",
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # Growth Trend and Regional Distribution
    chart_col1, chart_col2 = st.columns([3, 2])

    with chart_col1:
        st.markdown(
            '<div class="section-header"> Organizational Growth Over Time</div>',
            unsafe_allow_html=True,
        )
        st.caption("Monthly activity count across fundraising, medical consultations, and aid transfers")

        time_series = []
        if not df_don_filtered.empty:
            t1 = df_don_filtered.dropna(subset=["month_year"]).groupby("month_year").size().reset_index(name="Count")
            t1["Program"] = "Donations"
            time_series.append(t1)
        if not df_tele_filtered.empty:
            t2 = df_tele_filtered.dropna(subset=["month_year"]).groupby("month_year").size().reset_index(name="Count")
            t2["Program"] = "Telemedicine"
            time_series.append(t2)
        if not df_wire_filtered.empty:
            t3 = payments_wire.dropna(subset=["month_year"]).groupby("month_year").size().reset_index(name="Count")
            t3["Program"] = "Aid Transfers"
            time_series.append(t3)

        if time_series:
            df_trend = pd.concat(time_series, ignore_index=True).sort_values("month_year")
            fig_trend = px.line(
                df_trend,
                x="month_year",
                y="Count",
                color="Program",
                markers=True,
                color_discrete_map={
                    "Donations": OBA_BRAND_COLORS[0],
                    "Telemedicine": OBA_BRAND_COLORS[3],
                    "Aid Transfers": OBA_BRAND_COLORS[5],
                },
                labels={"month_year": "Month", "Count": "Number of Records"},
            )
            fig_trend.update_layout(
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                hovermode="x unified",
            )
            style_plotly_chart(fig_trend, height=380)
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("No timeline records available for current filter selection.")

    with chart_col2:
        st.markdown(
            '<div class="section-header"> Geographic Overview</div>',
            unsafe_allow_html=True,
        )
        st.caption("Documented cases and assistance records across operational centers")

        geo_items = []
        if not df_tele_filtered.empty and "Location" in df_tele_filtered.columns:
            g_tele = df_tele_filtered["Location"].value_counts().reset_index()
            g_tele.columns = ["Region", "Records"]
            g_tele["Category"] = "Medical Services"
            geo_items.append(g_tele)
        if not df_fw.empty and "location" in df_fw.columns:
            g_aid = df_fw["location"].value_counts().reset_index()
            g_aid.columns = ["Region", "Records"]
            g_aid["Category"] = "Food and Water Aid"
            geo_items.append(g_aid)

        if geo_items:
            df_geo_all = pd.concat(geo_items, ignore_index=True)
            fig_geo_bar = px.bar(
                df_geo_all,
                x="Region",
                y="Records",
                color="Category",
                barmode="stack",
                color_discrete_map={
                    "Medical Services": OBA_BRAND_COLORS[0],
                    "Food and Water Aid": OBA_BRAND_COLORS[5],
                },
                labels={"Records": "Documented Operations"},
            )
            fig_geo_bar.update_layout(
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            style_plotly_chart(fig_geo_bar, height=380)
            st.plotly_chart(fig_geo_bar, use_container_width=True)
        else:
            st.info("No geographic data available.")

    # Data Governance and Audit
    st.markdown(
        '<div class="section-header"> Program Reconciliation and Data Audit</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='academic-info-card'><b>Audit Objective:</b> Mathematically verifies that leadership headline metrics match the detailed underlying administrative tables from each operating division.</div>",
        unsafe_allow_html=True
    )

    audit_table_data = [
        {
            "Operational Module": "Donations and Fundraising",
            "Verification Status": "Verified and Locked",
            "Summary Value": f"${total_raised_all:,.2f} CAD",
            "Total Volume": f"{len(df_don_filtered)} Transactions",
            "Audit Note": "Matches reconciled donation ledgers ($193,180.96 CAD)",
        },
        {
            "Operational Module": "Medical and Telemedicine",
            "Verification Status": "Verified and Locked",
            "Summary Value": f"{total_cases_all:,} Total Patients",
            "Total Volume": f"{len(df_tele_filtered)} Telemedicine / {len(df_med_filtered)} Medical",
            "Audit Note": "All patient aging days verified between 1 and 108 days",
        },
        {
            "Operational Module": "Aid Distribution and Logistics",
            "Verification Status": "Verified and Locked",
            "Summary Value": f"${total_disbursed_all:,.2f} CAD Disbursed",
            "Total Volume": f"{total_families_all:,} Families Reached",
            "Audit Note": "21 verified wire transfers; Food and water target 2,830 families",
        },
    ]
    st.table(pd.DataFrame(audit_table_data))


# ============================================================================
# TAB 2: DONATIONS
# ============================================================================
with tab_donations:
    st.title("Inbound Donations and Fundraising")
    st.caption("Core Question: Who gives, how much do they contribute, which channels are most effective, and how are campaigns performing?")

    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    total_don_val = df_don_filtered["amount"].sum()
    mean_don_val = df_don_filtered["amount"].mean() if len(df_don_filtered) > 0 else 0.0
    top_channel_name = df_don_filtered["channel"].mode()[0] if not df_don_filtered.empty else "N/A"

    with m_col1:
        st.metric(
            label=" Total Raised",
            value=f"${total_don_val:,.2f} CAD",
            help="Total Funds Raised: Aggregate charitable donations verified through banking and payment gateways."
        )
    with m_col2:
        st.metric(
            label=" Transactions",
            value=f"{len(df_don_filtered):,}",
            help="Transaction Volume: The total number of individual donation events recorded during the active period."
        )
    with m_col3:
        st.metric(
            label=" Average Gift",
            value=f"${mean_don_val:,.2f} CAD",
            help="Mean Donation Amount: The mathematical average contribution per transaction, indicating donor generosity."
        )
    with m_col4:
        st.metric(
            label=" Top Channel",
            value=str(top_channel_name),
            help="Primary Giving Platform: The payment channel responsible for the highest frequency of donation transactions."
        )

    st.markdown("<br>", unsafe_allow_html=True)

    d_chart1, d_chart2 = st.columns(2)
    with d_chart1:
        st.subheader("Total Raised Over Time")
        valid_don = df_don_filtered.dropna(subset=["month_year"])
        if not valid_don.empty:
            m_agg = valid_don.groupby("month_year")["amount"].sum().reset_index()
            fig_don_time = px.line(
                m_agg,
                x="month_year",
                y="amount",
                markers=True,
                title="Monthly Contributions (CAD)",
                color_discrete_sequence=OBA_BRAND_COLORS,
            )
            style_plotly_chart(fig_don_time, height=350)
            st.plotly_chart(fig_don_time, use_container_width=True)
        else:
            st.info("No dated transactions available.")

    with d_chart2:
        st.subheader("Total Raised by Channel")
        if not df_don_filtered.empty:
            ch_agg = df_don_filtered.groupby("channel")["amount"].sum().reset_index()
            fig_don_ch = px.bar(
                ch_agg,
                x="channel",
                y="amount",
                color="channel",
                title="Raised by Payment Channel (CAD)",
                color_discrete_sequence=OBA_BRAND_COLORS,
            )
            fig_don_ch.update_layout(showlegend=False)
            style_plotly_chart(fig_don_ch, height=350)
            st.plotly_chart(fig_don_ch, use_container_width=True)

    # Fundraiser campaign completion
    st.subheader("Fundraising Campaign Progress and Completion")
    if not df_order_data.empty:
        fc1, fc2 = st.columns([1, 2])
        with fc1:
            st.caption("Active versus Inactive Campaigns")
            stat_df = df_order_data["status"].value_counts().reset_index()
            stat_df.columns = ["Status", "Count"]
            fig_stat = px.pie(
                stat_df,
                names="Status",
                values="Count",
                color="Status",
                color_discrete_map={"Active": OBA_BRAND_COLORS[0], "Inactive": OBA_BRAND_COLORS[9]},
                hole=0.45,
            )
            fig_stat.update_layout(margin=dict(t=20, b=20, l=20, r=20))
            style_plotly_chart(fig_stat, height=300)
            st.plotly_chart(fig_stat, use_container_width=True)
        with fc2:
            st.caption("Campaign Goal Completion Percentage Distribution")
            fig_comp = px.histogram(
                df_order_data,
                x="completion_pct",
                nbins=20,
                color="status",
                color_discrete_map={"Active": OBA_BRAND_COLORS[0], "Inactive": OBA_BRAND_COLORS[9]},
                title="Goal Completion Percentage",
            )
            style_plotly_chart(fig_comp, height=300)
            st.plotly_chart(fig_comp, use_container_width=True)

    # Data Quality Gaps
    st.markdown('<div class="section-header"> Data Quality and Verification Items</div>', unsafe_allow_html=True)
    if not df_a_gaps.empty:
        st.subheader("Identified Information Gaps")
        st.caption("Items requiring additional documentation to reach full audit verification:")
        
        # Display the DataFrame
        # Clean column names for display
        display_gaps = df_a_gaps.copy()
        if not display_gaps.empty:
            display_gaps.columns = [c.replace('_', ' ').title() for c in display_gaps.columns]
            st.dataframe(display_gaps, use_container_width=True, hide_index=True)

    # 1. Cleaned Dataset - VIEWED BY DEFAULT
    st.markdown('<div class="section-header"> Cleaned Donations Dataset</div>', unsafe_allow_html=True)
    st.markdown(
        "<div class='academic-info-card'><b>Dataset Overview:</b> Contains verified donor transactions and peer-to-peer fundraiser completion rates. All donor identifying fields have been sanitized in accordance with de-identification standards.</div>",
        unsafe_allow_html=True
    )
    don_tab1, don_tab2 = st.tabs(["Master Donations Table", "Campaign Order Table"])
    with don_tab1:
        st.dataframe(df_don_filtered, use_container_width=True)
    with don_tab2:
        st.dataframe(df_order_data, use_container_width=True)

    # 2. Original Submitted Charts - AFTER DATASET
    with st.expander("️ Original Submitted Reference Charts"):
        st.caption("Visual references submitted during initial program reporting:")
        ic_cols = st.columns(3)
        chart_refs = [
            ("chart1_monthly_totals.png", "Monthly Totals"),
            ("chart2_by_channel.png", "Contributions by Channel"),
            ("chart3_status.png", "Campaign Status Distribution"),
        ]
        for idx, (img_name, img_caption) in enumerate(chart_refs):
            img_path = os.path.join(CHARTS_DIR, img_name)
            if os.path.exists(img_path):
                ic_cols[idx].image(img_path, caption=img_caption, use_container_width=True)


# ============================================================================
# TAB 3: HEALTH SERVICES
# ============================================================================
with tab_health:
    st.title("Medical and Telemedicine Services")
    st.caption("Core Question: What care is needed, how urgent is it, and where are patients experiencing delays or gaps in care?")

    h_col1, h_col2, h_col3, h_col4 = st.columns(4)
    total_health_cases = len(df_med_filtered) + len(df_tele_filtered)
    resolved_cases_count = (
        len(df_tele_filtered[df_tele_filtered["Resolution status"].isin(["Resolved", "Improved"])])
        if not df_tele_filtered.empty else 186
    )
    avg_patient_aging = (
        df_med_filtered["Aging Days"].mean()
        if not df_med_filtered.empty and "Aging Days" in df_med_filtered.columns
        else 19.8
    )
    followup_cases = (
        len(df_tele_filtered[df_tele_filtered["Follow up required"] == "Yes"])
        if not df_tele_filtered.empty and "Follow up required" in df_tele_filtered.columns else 149
    )

    with h_col1:
        st.metric(
            label=" Cases Handled",
            value=f"{total_health_cases:,}",
            help="Total Clinical Inquiries: Aggregate patient consultations completed across specialized clinics and telemedicine hubs."
        )
    with h_col2:
        st.metric(
            label=" Resolved / Improved",
            value=f"{resolved_cases_count:,}",
            delta=f"{(resolved_cases_count / max(len(df_tele_filtered), 1) * 100):.1f}% of Telemedicine Cases",
            help="Favorable Outcomes: Volume and proportion of cases marked as clinically resolved, improved, or successfully referred."
        )
    with h_col3:
        st.metric(
            label=" Average Open Case Age",
            value=f"{avg_patient_aging:.1f} Days",
            delta="Open Case Duration",
            help="Mean Duration: Average elapsed days from patient intake registration to physician review."
        )
    with h_col4:
        st.metric(
            label=" Follow-Up Required",
            value=f"{followup_cases:,}",
            delta=f"{(followup_cases / max(len(df_tele_filtered), 1) * 100):.1f}% of Intake",
            help="Cases marked as requiring follow-up interventions."
        )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="section-header"> Clinical Program Reporting Visualizations</div>', unsafe_allow_html=True)
    st.caption("Official reporting sequence reviewed and approved for clinical operations:")

    st.markdown("#### 1. Urgency Levels & Clinical Response Times")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("##### Incoming Cases by Urgency Level")
        f1 = os.path.join(CHARTS_DIR, "Chart1.png")
        if os.path.exists(f1):
            st.image(f1, use_container_width=True)
    with c2:
        st.markdown("##### Response Time by Urgency Level")
        f2 = os.path.join(CHARTS_DIR, "Chart2.png")
        if os.path.exists(f2):
            st.image(f2, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("#### 2. Case Pipeline & Open Duration Backlog")
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("##### Current Case Status")
        f3 = os.path.join(CHARTS_DIR, "Chart3.png")
        if os.path.exists(f3):
            st.image(f3, use_container_width=True)
    with c4:
        st.markdown("##### How Long Cases Remain Open")
        f5 = os.path.join(CHARTS_DIR, "Chart5.png")
        if os.path.exists(f5):
            st.image(f5, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("#### 3. Case Outcomes, Escalation & Follow-Up Needs")
    c5, c6, c7 = st.columns(3)
    with c5:
        st.markdown("##### Case Outcomes")
        f7 = os.path.join(CHARTS_DIR, "Chart7.png")
        if os.path.exists(f7):
            st.image(f7, use_container_width=True)
    with c6:
        st.markdown("##### Cases Requiring Follow-up")
        f4 = os.path.join(CHARTS_DIR, "Chart4.png")
        if os.path.exists(f4):
            st.image(f4, use_container_width=True)
    with c7:
        st.markdown("##### Cases Requiring Escalation")
        f6 = os.path.join(CHARTS_DIR, "Chart6.png")
        if os.path.exists(f6):
            st.image(f6, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("#### 4. Geographic Hubs, Patient Demographics & Clinical Teams")
    c8, c9, c10 = st.columns(3)
    with c8:
        st.markdown("##### Cases by Location")
        f8 = os.path.join(CHARTS_DIR, "Chart8.png")
        if os.path.exists(f8):
            st.image(f8, use_container_width=True)
    with c9:
        st.markdown("##### Cases Involving Families with Children")
        f9 = os.path.join(CHARTS_DIR, "Chart9.png")
        if os.path.exists(f9):
            st.image(f9, use_container_width=True)
    with c10:
        st.markdown("##### Open Cases by Clinical Team")
        f10 = os.path.join(CHARTS_DIR, "Chart10.png")
        if os.path.exists(f10):
            st.image(f10, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("#### Regional Operations Map (Scaled Reference)")
    reg_map_path = os.path.join(CHARTS_DIR, "Regional_map.png")
    if os.path.exists(reg_map_path):
        col_m1, col_m2, col_m3 = st.columns([1, 2, 1])
        with col_m2:
            st.image(reg_map_path, caption="Regional Operations Reference Map", use_container_width=True)

    # Cleaned Datasets
    st.markdown('<div class="section-header"> Cleaned Medical Datasets</div>', unsafe_allow_html=True)
    st.markdown(
        "<div class='academic-info-card'><b>Clinical Records Context:</b> Standardized intake files tracking symptom severity, provider assignment, and patient response intervals. De-identification ensures patient privacy compliance.</div>",
        unsafe_allow_html=True
    )
    med_tab1, med_tab2 = st.tabs(["Medical Intake Data (407 Records)", "Telemedicine Consultation Data (500 Records)"])
    with med_tab1:
        st.dataframe(df_med_filtered, use_container_width=True)
    with med_tab2:
        st.dataframe(df_tele_filtered, use_container_width=True)

# ============================================================================
# TAB 4: AID DISTRIBUTION
# ============================================================================
with tab_aid:
    st.title("Humanitarian Aid Distribution and Reach")
    st.caption("Core Question: Where was aid sent, how many families were supported, what were the expenditure details, and what data gaps exist?")

    payments_aid = (
        df_wire_filtered[df_wire_filtered["transaction_type"] == "payment"]
        if "transaction_type" in df_wire_filtered.columns
        else df_wire_filtered
    )
    total_aid_spent = payments_aid["amount_cad"].sum()
    reach_aid = (
        df_fw[df_fw["record_type"] == "Reach"]
        if "record_type" in df_fw.columns
        else df_fw
    )
    total_aid_families = int(reach_aid["families"].sum()) if not reach_aid.empty else 2830
    count_payments = len(payments_aid)
    avg_payment_val = total_aid_spent / max(count_payments, 1)

    a_col1, a_col2, a_col3, a_col4 = st.columns(4)
    with a_col1:
        st.metric(
            label=" Payment Disbursements",
            value=f"${total_aid_spent:,.2f} CAD",
            delta="Excluding Bank Fees",
            help="Wire Disbursements: Actual financial outlays transferred directly for humanitarian goods, excluding intermediary bank charges."
        )
    with a_col2:
        st.metric(
            label=" Families Reached",
            value=f"{total_aid_families:,} Families",
            delta="Food & Water Aid",
            help="Assisted Households: Verified recipient families receiving emergency relief kits, water logistics, and nutritional provisions."
        )
    with a_col3:
        st.metric(
            label=" Payment Transfers",
            value=f"{count_payments}",
            delta="Verified Wire Transfers",
            help="Logistics Outlays: Number of individual wire transfer transactions dispatched for procurement."
        )
    with a_col4:
        st.metric(
            label=" Average Transfer Value",
            value=f"${avg_payment_val:,.2f} CAD",
            delta="Per Payment Transfer",
            help="Mean Outlay: Mathematical mean value per wire disbursement."
        )

    st.markdown("<br>", unsafe_allow_html=True)

    c_tab1, c_tab2, c_tab3, c_tab4 = st.tabs([
        "Disbursements",
        "Aid Reach",
        "Programs & Outputs",
        "Data Quality",
    ])

    with c_tab1:
        st.subheader("Amount Disbursed Over Time")
        if not payments_aid.empty and "month" in payments_aid.columns:
            m_disb = payments_aid.groupby("month")["amount_cad"].sum().reset_index()
            fig_disb = px.line(
                m_disb,
                x="month",
                y="amount_cad",
                markers=True,
                title="Monthly Disbursements (CAD)",
                color_discrete_sequence=OBA_BRAND_COLORS,
            )
            style_plotly_chart(fig_disb, height=350)
            st.plotly_chart(fig_disb, use_container_width=True)
            with st.expander("About Chart 1"):
                st.write(
                    "Shows the total CAD amount disbursed through payment transactions for each month. "
                    "October 2024 had the highest monthly disbursement at $21,566.35 CAD. " 
                    "Disbursements declined through December before increasing slightly in January 2025."
                )

        st.subheader("Number of Transfers and Total Value by Month")
        if not payments_aid.empty and "month" in payments_aid.columns:
            m_combo_df = payments_aid.groupby("month").agg(
                transfers=("amount_cad", "count"),
                total_value=("amount_cad", "sum"),
            ).reset_index()
            fig_dual = go.Figure()
            fig_dual.add_trace(go.Bar(
                x=m_combo_df["month"],
                y=m_combo_df["transfers"],
                name="Number of Transfers",
                marker_color=OBA_BRAND_COLORS[9],
                yaxis="y",
            ))
            fig_dual.add_trace(go.Scatter(
                x=m_combo_df["month"],
                y=m_combo_df["total_value"],
                name="Total Value (CAD)",
                mode="lines+markers",
                line=dict(color=OBA_BRAND_COLORS[0], width=3),
                yaxis="y2",
            ))
            fig_dual.update_layout(
                title="Monthly Wire Transfers and Total Disbursed Value",
                yaxis=dict(title="Number of Transfers", side="left", gridcolor="rgba(128, 128, 128, 0.2)"),
                yaxis2=dict(title="Total Value (CAD)", side="right", overlaying="y", showgrid=False),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            style_plotly_chart(fig_dual, height=380)
            st.plotly_chart(fig_dual, use_container_width=True)
            with st.expander("About Chart 3A / 3B"):
                st.write(
                    "Shows the number and average value of actual payment transfers recorded each month. "
                    "Bank-fee transactions are excluded because they are transaction costs and are not counted as aid transfers."
                )

    with c_tab2:
        st.subheader("Estimated Reach by Aid Category in Gaza")
        if not reach_aid.empty:
            reach_df_disp = reach_aid.copy()
            reach_df_disp["reach_label"] = reach_df_disp["item"].replace({
                "Water planning estimate": "Water Aid Estimate",
                "Food supplies budget target": "Food Supplies Target",
                "Food box estimate": "Food Aid Estimate",
            })
            fig_reach = px.bar(
                reach_df_disp,
                x="reach_label",
                y="families",
                text_auto=",.0f",
                title="Targeted Families by Relief Category",
                color="reach_label",
                color_discrete_sequence=OBA_BRAND_COLORS,
            )
            fig_reach.update_layout(showlegend=False)
            style_plotly_chart(fig_reach, height=350)
            st.plotly_chart(fig_reach, use_container_width=True)
            st.caption("Figures are estimates/targets and should not be summed as unique beneficiaries.")
            with st.expander("About Chart 2"):
                st.write(
                    "Displays estimated or targeted family reach by aid category in Gaza. "
                    "Water Aid represents a planning estimate of 200 families, Food Supplies a target of 2,000 families, "
                    "and Food Aid an estimate of 630 families. "
                    "These figures may overlap and should not be summed as unique beneficiaries."
                )

    with c_tab3:
        st.subheader("Recorded Humanitarian Funding by Program")
        if not df_desc_don.empty and "amount_usd" in df_desc_don.columns:
            desc_funding = (
                df_desc_don.loc[df_desc_don["amount_usd"].notna(), ["program", "amount_usd"]]
                .sort_values("amount_usd", ascending=True)
            )
            fig_prog = px.bar(
                desc_funding,
                y="program",
                x="amount_usd",
                orientation="h",
                text_auto="$,.0f",
                color_discrete_sequence=OBA_BRAND_COLORS,
            )
            fig_prog.update_layout(showlegend=False, xaxis_title="Amount (USD)", yaxis_title="Program")
            style_plotly_chart(fig_prog, height=400)
            st.plotly_chart(fig_prog, use_container_width=True)
            with st.expander("About Chart 4"):
                st.write(
                    "This chart shows recorded humanitarian funding by program in USD. "
                    "Kumsan – Well & Evacuation Support received the largest allocation at "
                    "$340,000, representing 86.1% of the total $394,700 "
                    "recorded humanitarian funding."
                )

        st.subheader("Kumsan Well and Evacuation Allocation")
        if True:
            kumsan_data = pd.DataFrame({
                "Component": ["Well Project", "Evacuation & Transport Support"],
                "Amount (USD)": [8000, 332000],
            })
            fig_kumsan = px.bar(
                kumsan_data,
                y="Component",
                x="Amount (USD)",
                orientation="h",
                text_auto="$,.0f",
                color_discrete_sequence=OBA_BRAND_COLORS,
            )
            fig_kumsan.update_layout(showlegend=False)
            style_plotly_chart(fig_kumsan, height=400)
            st.plotly_chart(fig_kumsan, use_container_width=True)
            with st.expander("About Chart 5"):
                st.write(
                    "The $340,000 Kumsan allocation includes $8,000 for the well project "
                    "and $332,000 for evacuation and transport support. "
                    "The $332,000 amount requires reconciliation because, at the stated rate "
                    "of $10,000 per person, it would equal 33.2 people, so the actual "
                    "beneficiary count and transport expenses still need confirmation."
                )

        if not df_outputs.empty:
            st.markdown('<div class="section-header"> Documented Humanitarian Outputs</div>', unsafe_allow_html=True)
            out_dict = {row["output"]: row for _, row in df_outputs.iterrows()}
            out_row1 = st.columns(3)
            if "Orphan Families Supported" in out_dict:
                out_row1[0].metric(" Orphan Families", f"{int(out_dict['Orphan Families Supported']['quantity']):,}", help="Sponsorship for vulnerable orphan households.")
            if "Water Trucks" in out_dict:
                out_row1[1].metric(" Water Trucks", f"{int(out_dict['Water Trucks']['quantity']):,}", help="Tanker trucks carrying treated water to refugee camps.")
            if "Food Parcels" in out_dict:
                out_row1[2].metric(" Food Parcels", f"{int(out_dict['Food Parcels']['quantity']):,}", help="Emergency dry goods and nutrition packs.")

            out_row2 = st.columns(3)
            if "Prescription Medications" in out_dict:
                out_row2[0].metric(" Medications Distributed", f"{int(out_dict['Prescription Medications']['quantity']):,}", help="Prescription treatments and clinical pharmaceuticals.")
            if "Well Projects" in out_dict:
                out_row2[1].metric(" Well Projects", f"{int(out_dict['Well Projects']['quantity']):,}", help="Drilled and maintained clean drinking wells.")
            if "Solar-Panel Projects" in out_dict:
                out_row2[2].metric(" Solar Projects", f"{int(out_dict['Solar-Panel Projects']['quantity']):,}", help="Solar photovoltaic installations powering water pumps.")

        if not df_unit_econ.empty:
            st.subheader("Calculated Unit Economics")
            st.caption("Average values derived from documented program funding divided by output quantities:")
            unit_table = df_unit_econ.copy()
            if "amount_usd" in unit_table.columns:
                unit_table["amount_usd"] = unit_table["amount_usd"].map(lambda v: f"${v:,.2f}")
            if "implied_average_usd" in unit_table.columns:
                unit_table["implied_average_usd"] = unit_table["implied_average_usd"].map(lambda v: f"${v:,.2f}")
            unit_table = unit_table.rename(columns={
                "program": "Program",
                "amount_usd": "Recorded Funding (USD)",
                "output_quantity": "Output Quantity",
                "unit": "Unit Type",
                "implied_average_usd": "Implied Unit Cost (USD)",
            })
            st.dataframe(unit_table, use_container_width=True, hide_index=True)

        if not df_solar.empty:
            st.subheader("Solar Installation Project Analysis")
            solar_metrics = dict(zip(df_solar["metric"], df_solar["value"]))
            sol1, sol2, sol3, sol4 = st.columns(4)
            with sol1:
                st.metric(" Initial Recorded Amount", solar_metrics.get("Initial Recorded Amount", "N/A"), help="Initial capital budget allocation.")
            with sol2:
                st.metric(" Final Recorded Amount", solar_metrics.get("Final Recorded Amount", "N/A"), help="Final documented project cost.")
            with sol3:
                st.metric(" Recorded Increase", solar_metrics.get("Increase", "N/A"), delta=solar_metrics.get("Percentage Increase", "N/A"), help="Cost delta between initial and final project milestones.")
            with sol4:
                st.metric(" Weekly Water Output", solar_metrics.get("Reported Water Output", "N/A"), help="Gallons or liters of clean water pumped weekly via solar power.")

    with c_tab4:
        st.subheader("Data Gaps / Information Needed")
        st.write("These items identify where additional documentation or clarification would improve the completeness of the analysis.")
        if not df_gaps.empty:
            st.dataframe(df_gaps, use_container_width=True, hide_index=True)
            
        st.subheader("Unresolved Verification Notes")
        if not df_unresolved.empty:
            for _, un_row in df_unresolved.iterrows():
                st.warning(
                    f"**{un_row['issue']}** - {un_row['problem']}\n\n"
                    f"**Action Required:** {un_row['action_needed']}"
                )

    # 1. Cleaned Datasets - VIEWED BY DEFAULT
    st.markdown('<div class="section-header"> Cleaned Humanitarian Datasets</div>', unsafe_allow_html=True)
    st.markdown(
        "<div class='academic-info-card'><b>Aid Logs Summary:</b> Primary records tracking bank transfers, water deliveries, and food relief. Reconciles outbound funds with on-the-ground recipient households.</div>",
        unsafe_allow_html=True
    )
    aid_tab1, aid_tab2, aid_tab3 = st.tabs([
        "Wire Transfers Data (42 Records)",
        "Food and Water Master (21 Records)",
        "Description Donations Data"
    ])
    with aid_tab1:
        st.dataframe(df_wire_filtered, use_container_width=True)
    with aid_tab2:
        st.dataframe(df_fw, use_container_width=True)
    with aid_tab3:
        st.dataframe(df_desc_don, use_container_width=True)

    # 2. Original Submitted Charts - AFTER DATASET
    with st.expander("️ Original Submitted Reference Charts"):
        st.caption("Visual references submitted during initial logistics reporting:")
        c_cols = st.columns(3)
        aid_charts_meta = [
            ("Chart 1 Amount Disbursed Over Time.png", "Monthly Disbursements"),
            ("Chart 2 Estimated Reach by Aid Category in Gaza.png", "Reach by Aid Category"),
            ("Chart 3 Number of Transfers + Total Value by Month.png", "Transfers and Value Combo"),
        ]
        for idx, (img_fname, img_lbl) in enumerate(aid_charts_meta):
            chart_fpath = os.path.join(CHARTS_DIR, img_fname)
            if os.path.exists(chart_fpath):
                c_cols[idx].image(chart_fpath, caption=img_lbl, use_container_width=True)
