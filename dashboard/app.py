import streamlit as st
import pandas as pd
from pathlib import Path
import seaborn as sns
import matplotlib.pyplot as plt
from math import pi
import numpy as np

DATA_PATH = Path("data/bls_data.csv")

st.title("U.S. Labor Market Dashboard")

# Load data
df = pd.read_csv(DATA_PATH, parse_dates=['date'])

# Key Indicator Card
st.subheader("Key Labor Market Indicators")

latest = df.iloc[-1]
prev = df.iloc[-2]
year_ago = df.iloc[-13] if len(df) > 13 else None
def pct_change(new, old):
    return ((new - old) / old) * 100 if old != 0 else 0
col1, col2, col3 = st.columns(3)

# Unemployment Rate
unemp = latest["unemployment_rate"]
unemp_mom = pct_change(unemp, prev["unemployment_rate"])
unemp_yoy = pct_change(unemp, year_ago["unemployment_rate"]) if year_ago is not None else None
prev_rate = prev["unemployment_rate"]
col1.metric(
    "Unemployment Rate",
    f"{unemp:.1f}%",
    f"{unemp_mom:+.1f}% MoM"
)
col1.markdown(
    f"""
    <div style='margin-top:-12px; font-size:15px; opacity:0.85;'>
        <strong>{unemp_yoy:+.1f}% YoY</strong><br>
    """,
    unsafe_allow_html = True
)
# Total Nonfarm Employment
nfp = latest["total_nonfarm_employment"]
nfp_mom = pct_change(nfp, prev["total_nonfarm_employment"])
nfp_yoy = pct_change(nfp, year_ago["total_nonfarm_employment"]) if year_ago is not None else None
col2.metric(
    "Total Nonfarm Employment",
    f"{nfp:,.0f}",
    f"{nfp_mom:+.1f}% MoM"
)
col2.markdown(
    f"""
    <div style='margin-top:-12px; font-size:15px; opacity:0.85;'>
        <strong>{nfp_yoy:+.1f}% YoY</strong>
    </div>
    """,
    unsafe_allow_html=True
)
# Hourly Earnings
ahe = latest["avg_hourly_earnings"]
ahe_mom = pct_change(ahe, prev["avg_hourly_earnings"])
ahe_yoy = pct_change(ahe, year_ago["avg_hourly_earnings"]) if year_ago is not None else None
col3.metric(
    "Avg Hourly Earnings",
    f"${ahe:.2f}",
    f"{ahe_mom:+.1f}% MoM"
)
col3.markdown(
    f"""
    <div style='margin-top:-12px; font-size:15px; opacity:0.85;'>
        <strong>{ahe_yoy:+.1f}% YoY</strong>
    </div>
    """,
    unsafe_allow_html=True
)
# Table Summary of Latest Data
clean_df = df.copy()
clean_df.columns = [col.replace("_", " ").title() for col in clean_df.columns]
clean_df["Date"] = pd.to_datetime(clean_df["Date"]).dt.strftime("%b %Y")
comma_cols = ["Employment", "Labor Force", "Total Nonfarm Employment", "Unemployment"]
for col in comma_cols:
    if col in clean_df.columns:
        clean_df[col] = clean_df[col].apply(lambda x: f"{int(x):,}")

st.write("### Latest Available Data")
st.write(clean_df.tail())

# Two time series charts
st.write("### Unemployment Rate Over Time")
st.line_chart(df.set_index("date")["unemployment_rate"])

st.subheader("Year-over-Year Job Growth (%)")

df["nfp_yoy"] = df["total_nonfarm_employment"].pct_change(12) * 100
yoy_df = df.dropna(subset=["nfp_yoy"]).copy()
x = range(len(yoy_df))
heights = yoy_df["nfp_yoy"].values
colors = ["#4C72B0" if v >= 0 else "#C44E52" for v in heights]
fig, ax = plt.subplots(figsize = (12, 5))
ax.bar(x, heights, color = colors, width = 0.8)
ax.set_xticks(x)
ax.set_xticklabels(
    yoy_df["date"].dt.strftime("%Y-%m"),
    rotation = 45,
    ha = "right")
ax.set_title("Total Non-Farm Employment: Year-over-Year Change", fontsize = 16)
ax.set_ylabel("% Change YoY")
ax.axhline(0, color = "black", linewidth = 1)
plt.tight_layout()
st.pyplot(fig)


# Month-over-Month Heatmap
st.subheader("Month-over-Month % Change Heatmap")

mom = df.set_index("date").pct_change() * 100
better_names = {
    "avg_hourly_earnings": "Avg Hourly Earnings",
    "avg_weekly_hours": "Avg Weekly Hours",
    "employment": "Employment",
    "labor_force": "Labor Force",
    "total_nonfarm_employment": "Total Nonfarm Employment",
    "unemployment": "Unemployment",
    "unemployment_rate": "Unemployment Rate"
}
mom = mom.rename(columns = better_names)
mom.index = mom.index.strftime("%m-%Y")
years = [d.split("-")[1] for d in mom.index]
year_split_positions = [i for i in range(1, len(years)) if years[i] != years[i - 1]]
fig, ax = plt.subplots(figsize = (16, 8))
sns.heatmap(
    mom.T,
    cmap = "seismic_r",
    center = 0,
    annot = True,
    fmt = ".1f",
    linewidths = 0.3,
    cbar = False
)
for pos in year_split_positions:
    ax.axvline(pos, color = "black", linewidth = 2)
plt.title("")
plt.xlabel("")
plt.ylabel("")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()

st.pyplot(fig)

# Year-over-Year Heatmap
st.subheader("Year-over-Year % Change Heatmap")

yoy = df.set_index("date").pct_change(periods = 12) * 100
yoy = yoy.rename(columns = better_names)
yoy.index = yoy.index.strftime("%m-%Y")
years_yoy = [d.split("-")[1] for d in yoy.index]
year_change_positions_yoy = [
    i for i in range(1, len(years_yoy))
    if years_yoy[i] != years_yoy[i - 1]
]
fig2, ax2 = plt.subplots(figsize = (16, 8))
sns.heatmap(
    yoy.T,
    cmap = "seismic_r",
    center = 0,
    annot = True,
    fmt = ".1f",
    linewidths = 0.3,
    cbar = False
)
for pos in year_change_positions_yoy:
    ax2.axvline(pos, color = "black", linewidth = 2)
ax2.set_xlabel("")
ax2.set_ylabel("")
plt.xticks(rotation = 45, ha = "right")
plt.tight_layout()

st.pyplot(fig2)

# Interactive Trends
st.subheader("Interactive Trend Explorer")

viz_df = df.copy()
viz_df["date"] = pd.to_datetime(viz_df["date"])
viz_df = viz_df.rename(columns = better_names)
metric = st.selectbox(
    "Select a labor market indicator to visualize:",
    list(better_names.values())
)
fig, ax = plt.subplots(figsize = (12, 4))
ax.plot(viz_df["date"], viz_df[metric], marker="o", linewidth = 2)
ax.set_title(f"{metric} Over Time")
ax.set_xlabel("")
ax.set_ylabel("")
ax.ticklabel_format(style = 'plain', axis = 'y')
plt.xticks(rotation = 45)
plt.grid(alpha = 0.2)

st.pyplot(fig)
