import streamlit as st
import pandas as pd
from pathlib import Path

DATA_PATH = Path("data/bls_data.csv")

st.title("U.S. Labor Market Dashboard")

# Loading in the dataset
df = pd.read_csv(DATA_PATH, parse_dates = ['date'])

st.write("### Lateset Available Data")
st.write(df.tail())

# Simple charts
st.write("### Unemployment Rate Over Time")
st.line_chart(df.set_index("date")["unemployment_rate"])

st.write("### Total Non-Farm Employment Rate Over Time")
st.line_chart(df.set_index("date")["total_nonfarm_employment"])
