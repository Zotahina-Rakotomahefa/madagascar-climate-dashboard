import streamlit as st
import pandas as pd
import numpy as np
import json
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ============================================================
# CONFIG
# ============================================================
st.set_page_config(
    page_title="Madagascar Climate Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = Path(__file__).parent / "data"
CSV_PATH = DATA_DIR / "madagascar_climate_processed.csv"
GEOJSON_PATH = DATA_DIR / "madagascar_regions.geojson"

# ============================================================
# DESIGN TOKENS — palette inspired by Madagascar's laterite soil and lagoons
# ============================================================
BG = "#12181A"
PANEL = "#1B2426"
PANEL_LIGHT = "#212C2E"
TEXT = "#F2EDE4"
TEXT_MUTED = "#96A29F"
TEMP_COLOR = "#C1502E"      # laterite red
TEMP_SCALE = ["#2E1A14", "#6B2E1E", "#C1502E", "#E8875C", "#F6C39B"]
RAIN_COLOR = "#1B8A94"      # lagoon blue
RAIN_SCALE = ["#0D2B2E", "#134F55", "#1B8A94", "#5FC2CA", "#B7E7EA"]
GOLD = "#D4A017"
GRID = "#2A3538"
MUTED_BAR = "#3A4548"

GEO_NAME_MAP = {
    "SAVA": "Sava",
    "Haute Matsiatra": "Matsiatra Ambony",
    "Vatovavy": "Vatovavy-Fitovinany",
    "Fitovinany": "Vatovavy-Fitovinany",
}

MONTH_ORDER = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]

# ============================================================
# CSS
# ============================================================
def inject_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

    html, body, [class*="css"] {{ font-family: 'IBM Plex Sans', sans-serif; }}
    .stApp {{ background-color: {BG}; color: {TEXT}; }}
    section[data-testid="stSidebar"] {{ background-color: {PANEL}; border-right: 1px solid {GRID}; }}
    h1, h2, h3 {{ font-family: 'Space Grotesk', sans-serif !important; color: {TEXT} !important; letter-spacing: -0.01em; }}

    .hero-title {{ font-family: 'Space Grotesk', sans-serif; font-size: 2.5rem; font-weight: 700;
        color: {TEXT}; margin-bottom: 0; line-height: 1.15; }}
    .hero-sub {{ color: {TEXT_MUTED}; font-size: 1rem; margin-top: 0.4rem; margin-bottom: 1.4rem; }}
    .eyebrow {{ font-family: 'Space Grotesk', sans-serif; text-transform: uppercase; letter-spacing: 0.14em;
        font-size: 0.72rem; color: {GOLD}; font-weight: 600; }}

    div[data-testid="stMetric"] {{ background-color: {PANEL_LIGHT}; border: 1px solid {GRID};
        border-radius: 10px; padding: 1rem 1.1rem 0.8rem 1.1rem; }}
    div[data-testid="stMetricLabel"] {{ color: {TEXT_MUTED} !important; font-size: 0.76rem !important;
        text-transform: uppercase; letter-spacing: 0.06em; }}
    div[data-testid="stMetricValue"] {{ font-family: 'Space Grotesk', sans-serif !important; color: {TEXT} !important; }}

    .stTabs [data-baseweb="tab-list"] {{ gap: 4px; border-bottom: 1px solid {GRID}; }}
    .stTabs [data-baseweb="tab"] {{ background-color: transparent; color: {TEXT_MUTED};
        font-family: 'Space Grotesk', sans-serif; font-weight: 500; padding: 0.6rem 1rem; }}
    .stTabs [aria-selected="true"] {{ color: {TEXT} !important; border-bottom: 2px solid {GOLD} !important; }}

    div[data-testid="stExpander"] {{ background-color: {PANEL_LIGHT}; border: 1px solid {GRID}; border-radius: 8px; }}
    footer {{visibility: hidden;}}
    #MainMenu {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)


def plotly_layout(fig, height=440):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Sans, sans-serif", color=TEXT, size=13),
        title_font=dict(family="Space Grotesk, sans-serif", size=17, color=TEXT),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_MUTED)),
        margin=dict(l=10, r=10, t=60, b=10),
        height=height,
        hoverlabel=dict(bgcolor=PANEL_LIGHT, font=dict(color=TEXT, family="IBM Plex Sans")),
    )
    fig.update_xaxes(showgrid=True, gridcolor=GRID, zeroline=False, color=TEXT_MUTED)
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False, color=TEXT_MUTED)
    return fig


# ============================================================
# DATA LOADING
# ============================================================
@st.cache_data
def load_data():
    df = pd.read_csv(CSV_PATH)
    df["Date"] = pd.to_datetime(df["Date"])
    df["Month_Name"] = pd.Categorical(df["Month_Name"], categories=MONTH_ORDER, ordered=True)
    df["geo_region"] = df["Region"].map(lambda r: GEO_NAME_MAP.get(r, r))
    return df


@st.cache_data
def load_geojson():
    with open(GEOJSON_PATH, "r") as f:
        return json.load(f)


df = load_data()
geojson = load_geojson()
ALL_REGIONS = sorted(df["Region"].unique())

# ============================================================
# SIDEBAR — FILTERS
# ============================================================
with st.sidebar:
    st.markdown('<div class="eyebrow">Filters</div>', unsafe_allow_html=True)
    st.markdown("### Period & regions")

    year_min, year_max = int(df["Year"].min()), int(df["Year"].max())
    year_range = st.slider("Period (years)", year_min, year_max, (year_min, year_max))

    season_choice = st.multiselect(
        "Season", options=["Rainy", "Dry"], default=["Rainy", "Dry"],
        format_func=lambda s: "Rainy (Nov–Apr)" if s == "Rainy" else "Dry (May–Oct)"
    )

    region_choice = st.multiselect(
        "Regions to compare", options=ALL_REGIONS, default=["Analamanga", "Atsinanana", "Atsimo-Andrefana"]
    )

    st.markdown("---")
    st.caption(
        f"Source: NASA POWER (T2M, PRECTOTCORR)  \n"
        f"Available period: {year_min}–{year_max}  \n"
        f"23 regions of Madagascar"
    )

if not season_choice:
    season_choice = ["Rainy", "Dry"]
if not region_choice:
    region_choice = ALL_REGIONS[:3]

mask = (
    (df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1]) &
    (df["Season"].isin(season_choice))
)
df_f = df[mask].copy()
df_sel = df_f[df_f["Region"].isin(region_choice)].copy()

# ============================================================
# HEADER
# ============================================================
inject_css()
st.markdown('<div class="eyebrow">Climate analysis · 2005–2024</div>', unsafe_allow_html=True)
st.markdown('<p class="hero-title">Climate of Madagascar</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-sub">Temperature and rainfall across Madagascar\'s 23 regions, based on NASA POWER satellite data.</p>',
    unsafe_allow_html=True
)

# ============================================================
# KPIs
# ============================================================
k1, k2, k3, k4 = st.columns(4)

avg_temp = df_f["Temperature"].mean()
avg_rain = df_f["Precipitation"].mean()
region_avg = df_f.groupby("Region")[["Temperature", "Precipitation"]].mean()
warmest = region_avg["Temperature"].idxmax()
wettest = region_avg["Precipitation"].idxmax()

k1.metric("Average temperature", f"{avg_temp:.1f} °C")
k2.metric("Average precipitation", f"{avg_rain:.1f} mm/day")
k3.metric("Warmest region", warmest, f"{region_avg.loc[warmest, 'Temperature']:.1f} °C")
k4.metric("Wettest region", wettest, f"{region_avg.loc[wettest, 'Precipitation']:.1f} mm/day")

st.write("")

# ============================================================
# TABS
# ============================================================
tab_map, tab_time, tab_compare, tab_season, tab_data = st.tabs(
    ["Map", "Time series", "Regional comparison", "Seasons", "Data"]
)

# ---------------- TAB: MAP ----------------
with tab_map:
    c1, c2 = st.columns([3, 1])
    with c2:
        map_var = st.radio("Variable", ["Temperature", "Precipitation"], key="map_var")
        st.caption(
            "Vatovavy and Fitovinany are merged on this map "
            "(average of the two) because the standard geographic "
            "boundaries do not yet distinguish the current 23 regions."
        )

    geo_agg = (
        df_f.groupby("geo_region")[["Temperature", "Precipitation"]]
        .mean()
        .reset_index()
    )

    if map_var == "Temperature":
        color_col, scale, unit = "Temperature", TEMP_SCALE, "°C"
    else:
        color_col, scale, unit = "Precipitation", RAIN_SCALE, "mm/day"

    fig_map = px.choropleth(
        geo_agg,
        geojson=geojson,
        locations="geo_region",
        featureidkey="properties.shapeName",
        color=color_col,
        color_continuous_scale=scale,
        hover_name="geo_region",
        labels={color_col: unit},
    )
    fig_map.update_geos(fitbounds="locations", visible=False, bgcolor="rgba(0,0,0,0)")
    fig_map.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=10, b=0),
        height=560,
        font=dict(family="IBM Plex Sans, sans-serif", color=TEXT),
        coloraxis_colorbar=dict(title=unit, tickfont=dict(color=TEXT_MUTED), title_font=dict(color=TEXT_MUTED)),
    )
    with c1:
        st.plotly_chart(fig_map, use_container_width=True)

# ---------------- TAB: TIME SERIES ----------------
with tab_time:
    show_trend = st.checkbox("Show linear trend", value=True)

    monthly = (
        df_sel.groupby(["Date", "Region"])[["Temperature", "Precipitation"]]
        .mean().reset_index()
    )

    colL, colR = st.columns(2)

    with colL:
        fig_t = px.line(
            monthly, x="Date", y="Temperature", color="Region",
            color_discrete_sequence=px.colors.qualitative.Set2,
            title="Monthly temperature"
        )
        fig_t.update_traces(line=dict(width=2))
        if show_trend:
            palette = px.colors.qualitative.Set2
            for i, region in enumerate(region_choice):
                sub = monthly[monthly["Region"] == region].sort_values("Date")
                if len(sub) > 2:
                    x_num = (sub["Date"] - sub["Date"].min()).dt.days.astype(float)
                    coeffs = np.polyfit(x_num, sub["Temperature"], 1)
                    trend_y = np.polyval(coeffs, x_num)
                    fig_t.add_trace(go.Scatter(
                        x=sub["Date"], y=trend_y, mode="lines",
                        line=dict(color=palette[i % len(palette)], width=1.5, dash="dot"),
                        name=f"{region} (trend)", showlegend=False,
                    ))
        st.plotly_chart(plotly_layout(fig_t), use_container_width=True)

    with colR:
        fig_r = px.line(
            monthly, x="Date", y="Precipitation", color="Region",
            color_discrete_sequence=px.colors.qualitative.Set2,
            title="Monthly precipitation"
        )
        fig_r.update_traces(line=dict(width=2))
        st.plotly_chart(plotly_layout(fig_r), use_container_width=True)

    st.caption("Tip: select the regions to display in the sidebar.")

# ---------------- TAB: REGIONAL COMPARISON ----------------
with tab_compare:
    comp_var = st.radio("Rank by", ["Temperature", "Precipitation"], key="comp_var", horizontal=True)
    col_name = comp_var
    color_main = TEMP_COLOR if comp_var == "Temperature" else RAIN_COLOR
    unit = "°C" if comp_var == "Temperature" else "mm/day"

    ranked = df_f.groupby("Region")[col_name].mean().reset_index().sort_values(col_name, ascending=False)
    ranked["highlight"] = ranked["Region"].isin(region_choice)
    ranked["color"] = ranked["highlight"].map({True: color_main, False: MUTED_BAR})

    fig_bar = go.Figure(go.Bar(
        x=ranked[col_name], y=ranked["Region"], orientation="h",
        marker_color=ranked["color"],
        text=[f"{v:.1f}" for v in ranked[col_name]], textposition="outside",
        textfont=dict(color=TEXT_MUTED, size=11),
    ))
    fig_bar.update_layout(
        title=f"Average {comp_var.lower()} by region ({unit})",
        yaxis=dict(autorange="reversed"),
        height=680,
    )
    st.plotly_chart(plotly_layout(fig_bar, height=680), use_container_width=True)
    st.caption("Regions selected in the sidebar are highlighted in color; the rest appear in gray.")

# ---------------- TAB: SEASONS ----------------
with tab_season:
    season_var = st.radio("Variable", ["Temperature", "Precipitation"], key="season_var", horizontal=True)
    col_name = season_var

    season_agg = (
        df_f[df_f["Region"].isin(region_choice)]
        .groupby(["Region", "Season"])[col_name].mean().reset_index()
    )
    season_agg["Season"] = season_agg["Season"].map({"Rainy": "Rainy season", "Dry": "Dry season"})

    fig_season = px.bar(
        season_agg, x="Region", y=col_name, color="Season", barmode="group",
        color_discrete_map={"Rainy season": RAIN_COLOR, "Dry season": TEMP_COLOR},
        title=f"Average {season_var.lower()} — dry vs rainy season"
    )
    st.plotly_chart(plotly_layout(fig_season, height=460), use_container_width=True)
    st.caption("Comparison limited to the regions selected in the sidebar.")

# ---------------- TAB: DATA ----------------
with tab_data:
    st.markdown("#### Filtered data")
    st.dataframe(
        df_sel[["Region", "Date", "Season", "Temperature", "Precipitation"]]
        .sort_values(["Region", "Date"]),
        use_container_width=True, height=420
    )
    csv_export = df_sel.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download filtered data (CSV)",
        data=csv_export,
        file_name="madagascar_climate_filtered.csv",
        mime="text/csv",
    )

st.markdown("---")
st.caption("Dashboard built with Streamlit & Plotly · Data: NASA POWER (power.larc.nasa.gov)")
